pipeline {
    agent any

    stages {
        stage('Checkout bugfix branch') {
            steps {
                // Checkout the bugfix branch
                git branch: 'bugfix', url: 'https://github.com/codefolio8/CodeFolio.git'
            }
        }

        stage('Configure Git') {
            steps {
                sh '''
                git config --global user.email "ci-bot@jenkins.local"
                git config --global user.name "Jenkins CI Bot"
                '''
            }
        }

        stage('Merge bugfix into develop') {
            steps {
                script {
                    sh '''
                    git fetch origin develop
                    git checkout develop
                    git merge origin/bugfix --no-edit || true
                    '''
                }
            }
        }

        stage('Push changes to develop') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'github-token', usernameVariable: 'USER', passwordVariable: 'TOKEN')]) {
                    sh '''
                    git push https://${USER}:${TOKEN}@github.com/codefolio8/CodeFolio.git develop
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "Successfully merged 'bugfix' into 'develop'!"
        }
        failure {
            echo "Merge or push failed — check the logs for conflicts."
        }
    }
}