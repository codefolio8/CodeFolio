pipeline {
    agent any

    options {
        timeout(time: 5, unit: 'MINUTES') // Set timeout for each build
        buildDiscarder(logRotator(numToKeepStr: '10')) // Keep last 10 builds
    }

    environment {
        REPO_URL = 'https://github.com/codefolio8/CodeFolio.git'
        GIT_CREDENTIALS = 'github-token'
    }

    triggers {
        pollSCM('H/3 * * * *') // Poll every 3 minutes
    }

    stages {

        stage('Checkout develop branch') {
            steps {
                // Checkout develop branch securely
                git branch: 'develop',
                    url: "${REPO_URL}",
                    credentialsId: "${GIT_CREDENTIALS}"
            }
        }

        stage('Merge bugfix into develop') {
            steps {
                // Merge bugfix branch into develop locally
                bat """
                git config user.email "jenkins@ci.local"
                git config user.name "Jenkins CI"
                git fetch origin develop
                git fetch origin bugfix
                git checkout develop
                git merge origin/bugfix --no-edit
                """
            }
        }

        stage('Push changes') {
            steps {
                // Push merged changes securely using token
                withCredentials([string(credentialsId: 'github-token', variable: 'GITHUB_TOKEN')]) {
                    bat """
                    git remote set-url origin https://$GITHUB_TOKEN@github.com/codefolio8/CodeFolio.git
                    git push origin develop
                    """
                }
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline succeeded: bugfix merged and changes pushed to develop!'
        }
        failure {
            echo '❌ Pipeline failed. Check console output for details.'
        }
    }
}
