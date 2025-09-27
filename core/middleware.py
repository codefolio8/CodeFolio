#---not being used -----------------#
class SessionCleanupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.cleanup_rules = {
            '/signup/': ['otp', 'otp_success'],
            '/password-reset/': ['pswd_otp', 'pswd_otp_success', 'docid'],
        }

    def __call__(self, request):
        path = request.path

        # Determine which cleanup keys are allowed on this path
        allowed_keys = set()
        for allowed_path, keys in self.cleanup_rules.items():
            print(path,allowed_path)
            if path.startswith(allowed_path):
                print("insode if match")
                allowed_keys.update(keys)

        # Collect all keys in session that match any cleanup key
        session_keys = set(request.session.keys())
        cleanup_keys = set(k for keys in self.cleanup_rules.values() for k in keys)
        present_cleanup_keys = session_keys & cleanup_keys
        print(session_keys,cleanup_keys,present_cleanup_keys)
        # If any cleanup key is present but not allowed on current path — flush
        if present_cleanup_keys and not present_cleanup_keys & allowed_keys:
            print("inside if 2 flushed")
            request.session.flush()

        return self.get_response(request)
