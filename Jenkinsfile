pipeline {
    agent any

    environment {
        VENV_DIR = '.venv'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'dev_JA',
                    credentialsId: 'github-creds-id',
                    url: 'https://github.com/djakubandrzejewski/scrapping_just_join.git'
            }
        }

        stage('Setup Python') {
            steps {
                sh '''
                python3 -m venv $VENV_DIR
                . $VENV_DIR/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Run tests') {
            steps {
                sh '''
                . $VENV_DIR/bin/activate
                PYTHONPATH=. pytest
                '''
            }
        }
    }

    post {
        always {
            junit '**/test-results.xml' // jeśli później użyjesz np. pytest-junit
        }
    }
}