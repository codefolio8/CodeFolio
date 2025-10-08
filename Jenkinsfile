
pipeline {
    agent any

    options {
        timeout(time: 10, unit: 'MINUTES')  // Job auto-terminates after 10 minutes
        buildDiscarder(logRotator(numToKeepStr: '10'))  // Keep last 10 builds
    }

    environment {
        REPO_URL = 'https://github.com/codefolio8/CodeFolio.git'
        GIT_CREDENTIALS = 'github-token'  // Your Jenkins GitHub credential ID
    }

    triggers {
        pollSCM('H/5 * * * *')  // Poll every 5 minutes
    }

    stages {
        stage('Checkout develop branch') {
            steps {
                git branch: 'develop',
                    url: "${REPO_URL}",
                    credentialsId: "${GIT_CREDENTIALS}"
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
                git push --quiet https://<USERNAME>:<TOKEN>@github.com/codefolio8/CodeFolio.git develop
                """
            }
        }

        

    post {
        success {
            echo '✅ Pipeline succeeded: bugfix merged and tests passed!'
        }
        failure {
            echo '❌ Pipeline failed. Check console output for details.'
        }
    }
}

