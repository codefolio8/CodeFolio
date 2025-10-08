pipeline {
    agent any

    options {
        timeout(time: 5, unit: 'MINUTES') // Timeout for each build
        buildDiscarder(logRotator(numToKeepStr: '10')) // Keep last 10 builds
    }

    environment {
        REPO_URL = 'https://github.com/codefolio8/CodeFolio.git'
        GIT_CREDENTIALS = 'Jenkins-CI' // Username+Password credential ID
    }

    triggers {
        pollSCM('H/3 * * * *') // Poll every 3 minutes
    }

    stages {

        stage('Checkout develop branch') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${GIT_CREDENTIALS}", 
                                                 usernameVariable: 'GIT_USER', 
                                                 passwordVariable: 'GIT_PASS')]) {
                    bat """
                    git config user.email "jenkins@ci.local"
                    git config user.name "Jenkins CI"
                    git clone https://%GIT_USER%:%GIT_PASS%@github.com/codefolio8/CodeFolio.git
                    cd CodeFolio
                    git checkout develop
                    """
                }
            }
        }

        stage('Merge bugfix into develop') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${GIT_CREDENTIALS}", 
                                                 usernameVariable: 'GIT_USER', 
                                                 passwordVariable: 'GIT_PASS')]) {
                    bat """
                    cd CodeFolio
                    git fetch origin develop
                    git fetch origin bugfix
                    git checkout develop
                    git merge origin/bugfix --no-edit
                    """
                }
            }
        }

        stage('Push changes') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${GIT_CREDENTIALS}", 
                                                 usernameVariable: 'GIT_USER', 
                                                 passwordVariable: 'GIT_PASS')]) {
                    bat """
                    cd CodeFolio
                    git remote set-url origin https://%GIT_USER%:%GIT_PASS%@github.com/codefolio8/CodeFolio.git
                    git push origin develop
                    """
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline succeeded: bugfix merged and changes pushed to develop!'
        }
        failure {
            echo 'Pipeline failed. Check console output for details.'
        }
    }
}
