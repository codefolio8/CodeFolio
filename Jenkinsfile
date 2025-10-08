pipeline {
    agent any

    // Poll SCM every 5 minutes for changes
    triggers {
        pollSCM('H/3 * * * *')
    }

    environment {
        GIT_CREDENTIALS = 'github-token'   // Jenkins credential ID for GitHub PAT/SSH
        REPO_URL = 'https://github.com/codefolio8/CodeFolio.git'
    }

    stages {
        stage('Clone develop branch') {
            steps {
                git branch: 'develop', url: "${REPO_URL}", credentialsId: "${GIT_CREDENTIALS}"
            }
        }

        stage('Merge bugfix into develop') {
            steps {
                sh '''
                git config user.email "jenkins@ci.local"
                git config user.name "Jenkins CI"

                # Add remote again (ensures clean)
                git remote set-url origin ${REPO_URL}

                # Fetch latest branches
                git fetch origin develop
                git fetch origin bugfix

                # Checkout develop
                git checkout develop

                # Merge bugfix branch
                git merge origin/bugfix --no-edit || true

                # Push the merged develop branch back to GitHub
                git push origin develop
                '''
            }
        }
    }

    post {
        success {
            echo '✅ Successfully merged bugfix into develop!'
        }
        failure {
            echo '❌ Merge failed. Please resolve conflicts manually.'
        }
    }
}