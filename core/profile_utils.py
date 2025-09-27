import requests
import json
from datetime import datetime, timezone
from .firebase_config import db
from firebase_admin import firestore
from collections import defaultdict
from .keywordmap import KEYWORD_TOPIC_MAP

BASE_URLS = {
    "leetcode": "https://competeapi.vercel.app/user/leetcode",
    "gfg_user": "https://geeks-for-geeks-api.vercel.app",
    "gfg_calendar": "https://mygfg-api.vercel.app",
    "codeforces_info": "https://codeforces.com/api/user.info?handles=",
    "codeforces_rating": "https://codeforces.com/api/user.rating?handle="
}
def fetch_leetcode_calendar_graphql(username):
    """
    Fetches a user's LeetCode submission calendar data using the GraphQL API.
    Converts Unix timestamps in the submissionCalendar to YYYY-MM-DD date strings.
    Combines all years into a single calendar.

    Args:
        username (str): The LeetCode username.

    Returns:
        dict: A dictionary containing user calendar data, including activeYears,
              streak, totalActiveDays, and submissionCalendar with dates as keys.
              Returns an empty dictionary if an error occurs or data is not found.
    """
    url = "https://leetcode.com/graphql"
    headers = {
        "Content-Type": "application/json",
        "Referer": f"https://leetcode.com/{username}/"
    }

    # Step 1: Fetch active years
    query = """
    query userProfileCalendar($username: String!, $year: Int) {
      matchedUser(username: $username) {
        userCalendar(year: $year) {
          activeYears
        }
      }
    }
    """
    variables = {"username": username, "year": None}
    payload = {
        "query": query,
        "variables": variables,
        "operationName": "userProfileCalendar"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        user_calendar = (
            data.get("data", {})
                .get("matchedUser", {})
                .get("userCalendar", None)
        )
        if not user_calendar or "activeYears" not in user_calendar:
            return {}
        active_years = user_calendar["activeYears"]
    except Exception as e:
        print(f"Error fetching active years: {e}")
        return {}

    # Step 2: For each year, fetch the calendar and merge
    combined_calendar = {}
    total_streak = 0
    total_active_days = 0
    for year in active_years:
        query = """
        query userProfileCalendar($username: String!, $year: Int) {
          matchedUser(username: $username) {
            userCalendar(year: $year) {
              streak
              totalActiveDays
              submissionCalendar
            }
          }
        }
        """
        variables = {"username": username, "year": year}
        payload = {
            "query": query,
            "variables": variables,
            "operationName": "userProfileCalendar"
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            year_calendar = (
                data.get("data", {})
                    .get("matchedUser", {})
                    .get("userCalendar", None)
            )
            if not year_calendar:
                continue
            # Update streak and active days (optional: you can choose how to aggregate)
            total_streak = max(total_streak, year_calendar.get("streak", 0))
            total_active_days += year_calendar.get("totalActiveDays", 0)
            # Parse and merge submission calendar
            calendar_json = year_calendar.get("submissionCalendar", "{}")
            try:
                calendar = json.loads(calendar_json)
            except Exception:
                calendar = {}
            for timestamp_str, submissions_count in calendar.items():
                try:
                    timestamp_int = int(timestamp_str)
                    dt_object_utc = datetime.fromtimestamp(timestamp_int, tz=timezone.utc)
                    formatted_date = dt_object_utc.strftime('%Y-%m-%d')
                    combined_calendar[formatted_date] = combined_calendar.get(formatted_date, 0) + submissions_count
                except Exception:
                    continue
        except Exception as e:
            print(f"Error fetching calendar for year {year}: {e}")
            continue

    # Step 3: Return the combined result
    result = {
        "activeYears": active_years,
        "streak": total_streak,
        "totalActiveDays": total_active_days,
        "submissionCalendar": combined_calendar
    }
    return result

def fetch_leetcode_skill_stats(username):
    """
    Fetches topic-wise problem counts (by skill level) for a given LeetCode username.
    Returns a dict with keys: 'fundamental', 'intermediate', 'advanced'.
    Each key maps to a list of dicts: {tagName, tagSlug, problemsSolved}
    """
    url = "https://leetcode.com/graphql"
    headers = {
        "Content-Type": "application/json",
        "Referer": f"https://leetcode.com/{username}/"
    }

    query = """
    query skillStats($username: String!) {
      matchedUser(username: $username) {
        tagProblemCounts {
          advanced {
            tagName
            tagSlug
            problemsSolved
          }
          intermediate {
            tagName
            tagSlug
            problemsSolved
          }
          fundamental {
            tagName
            tagSlug
            problemsSolved
          }
        }
      }
    }
    """

    variables = {"username": username}
    payload = {
        "query": query,
        "variables": variables,
        "operationName": "skillStats"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        tag_counts = data.get("data", {}).get("matchedUser", {}).get("tagProblemCounts", {})
        # Ensure all levels are present as lists
        return {
            "fundamental": tag_counts.get("fundamental", []),
            "intermediate": tag_counts.get("intermediate", []),
            "advanced": tag_counts.get("advanced", [])
        }
    except Exception:
        return {
            "fundamental": [],
            "intermediate": [],
            "advanced": []
        }
    
def infer_topic_from_title(title):
    title_lower = title.lower()
    matched_topics = set()
    for keyword, topic in KEYWORD_TOPIC_MAP.items():
        if keyword in title_lower:
            matched_topics.add(topic)
    return list(matched_topics) if matched_topics else ["Unknown"]

def get_topic_wise_stats_from_titles(stats):
    all_questions = stats.get("easy", {}).get("questions", []) + \
                    stats.get("medium", {}).get("questions", []) + \
                    stats.get("hard", {}).get("questions", [])

    topic_counter = defaultdict(int)
    for q in all_questions:
        title = q.get("question", "")
        topics = infer_topic_from_title(title)
        for topic in topics:
            topic_counter[topic] += 1

    return dict(topic_counter)

def fetch_platform_data(platform, username):
    try:
        if platform == "leetcode":
            response = requests.get(f"{BASE_URLS['leetcode']}/{username}/", timeout=10)
            response.raise_for_status()
            data = response.json().get("data", {}).get("matchedUser", {})
            if not data:
                return {}

            # profile = data.get("profile", {})
            badges = data.get("badges", [])
            language_stats = data.get("languageProblemCount", [])
            submit_stats = data.get("submitStats", {}).get("acSubmissionNum", [])
            user_calendar = data.get("userCalendar", {})
            contest = data.get("userContestRanking", {})

            total_solved = next((item["count"] for item in submit_stats if item["difficulty"] == "All"), 0)
            solved_easy = next((item["count"] for item in submit_stats if item["difficulty"] == "Easy"), 0)
            solved_medium = next((item["count"] for item in submit_stats if item["difficulty"] == "Medium"), 0)
            solved_hard = next((item["count"] for item in submit_stats if item["difficulty"] == "Hard"), 0)

            calendar_data = fetch_leetcode_calendar_graphql(username)
            skill_stats = fetch_leetcode_skill_stats(username)
            leetcode_data = {
                # "real_name": data.get("username", ""),
                # "avatar": profile.get("userAvatar", ""),
                "badges": badges,
                "language_stats": language_stats,
                "total_solved": total_solved,
                "solved_easy": solved_easy,
                "solved_medium": solved_medium,
                "solved_hard": solved_hard,
                "streak": user_calendar.get("streak", 0),
                "total_active_days": user_calendar.get("totalActiveDays", 0),
                "contest_data": {
                    "rating": contest.get("rating"),
                    "ranking": contest.get("globalRanking"),
                    "attendedContestsCount": contest.get("attendedContestsCount"),
                    "topPercentage": contest.get("topPercentage"),
                    "totalParticipants": contest.get("totalParticipants"),
                },
                "calendar": calendar_data,
                "skill_stats": skill_stats
            }

            

            return leetcode_data

        elif platform == "gfg":
            
                response = requests.get(f"{BASE_URLS['gfg_user']}/{username}", timeout=10)
                response.raise_for_status()
                gfg_response = response.json()

                calendar_response = requests.get(f"{BASE_URLS['gfg_calendar']}/{username}/calendar", timeout=10)
                calendar_response.raise_for_status()
                calendar_data = calendar_response.json().get("Submission Dates", {})
                if not isinstance(calendar_data, dict):
                   calendar_data = {}
                info = gfg_response.get("info", {})
                stats = gfg_response.get("solvedStats", {})

                if not info.get("fullName"):
                    return {}
                skill_stats = get_topic_wise_stats_from_titles(stats)

                return {
                    # "real_name": info.get("fullName"),
                    # # "avatar": info.get("profilePicture", ""),
                    # "institute": info.get("institute", ""),
                    # "institute_rank": info.get("instituteRank", ""),
                    "coding_score": info.get("codingScore", 0),
                    "total_solved": info.get("totalProblemsSolved", 0),
                    "max_streak": info.get("maxStreak", 0),
                    "current_streak": info.get("currentStreak", 0),
                    "solved_easy": stats.get("easy", {}).get("count", 0),
                    "solved_medium": stats.get("medium", {}).get("count", 0),
                    "solved_hard": stats.get("hard", {}).get("count", 0),
                    "calendar": calendar_data,
                    "skill_stats": skill_stats
                }

        elif platform == "codeforces":
            r = requests.get(f"{BASE_URLS['codeforces_info']}{username}").json()
            rating_response = requests.get(f"{BASE_URLS['codeforces_rating']}{username}").json()

            if r.get("status") != "OK" or rating_response.get("status") != "OK":
                return {}

            user = r.get("result", [{}])[0]
            rating_history = rating_response.get("result", [])
            # latest_rating = rating_history[-1] if rating_history else {}

            return {
                # "real_name": f"{user.get('firstName', '')} {user.get('lastName', '')}".strip(),
                # # "avatar": user.get("avatar", ""),
                # "organization": user.get("organization", ""),
                # "country": user.get("country", ""),
                # "city": user.get("city", ""),
                "rank": user.get("rank", ""),
                "rating": user.get("rating", 0),
                "max_rank": user.get("maxRank", ""),
                "max_rating": user.get("maxRating", 0),
                "contribution": user.get("contribution", 0),
                # "friend_of_count": user.get("friendOfCount", 0),
                "rating_history": rating_history
            }

        else:
            return {}

    except Exception as e:
        print(f"[ERROR] Failed to fetch {platform} data for {username}: {e}")
        return {}

def store_verified_platform(user_id, platform, username, performance):
    user_ref = db.collection("User").document(user_id)
    user_doc = user_ref.get()

    # Handle Profile_list updates
    profile_list = []
    if user_doc.exists:
        user_data = user_doc.to_dict()
        profile_list = user_data.get("Profile_list", [])
        # Remove previous entry for platform
        profile_list = [p for p in profile_list if p.get("name") != platform]

    profile_list.append({
        "name": platform,
        "username": username,
        "verified": True
    })

    # Data to write
    data = {
        f"profileList.{platform}": username,
        "Profile_list": profile_list,
        "Last_Updated": firestore.SERVER_TIMESTAMP
    }

    # Create or update Firestore document
    if user_doc.exists:
        user_ref.update(data)
    else:
        user_ref.set(data)

    # Write performance data
    user_ref.collection("performance").document(platform).set(performance)