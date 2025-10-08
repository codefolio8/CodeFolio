pipeline {
    agent any

    options {
        timeout(time:5, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        REPO_URL = 'https://github.com/codefolio8/CodeFolio.git'
        GIT_CREDENTIALS = 'github-token'
    }

    triggers {
        pollSCM('H/3 * * * *')
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
                git push origin develop
                """
            }
        }

        
    }

    post {
        success {
            echo 'Pipeline succeeded: bugfix merged and tests passed!'
        }
        failure {
            echo 'Pipeline failed. Check console output for details.'
        }
    }
}
