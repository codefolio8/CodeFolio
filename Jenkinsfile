pipeline {
    agent any

    triggers {
        pollSCM('H/2 * * * *')
    }

    environment {
        GIT_CREDENTIALS = 'github-token'   // Jenkins credential ID
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
                bat """
                git config user.email "jenkins@ci.local"
                git config user.name "Jenkins CI"
                git remote set-url origin ${REPO_URL}
                git fetch origin develop
                git fetch origin bugfix
                git checkout develop
                git merge origin/bugfix --no-edit
                git push origin develop
                """
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
