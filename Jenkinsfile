pipeline {
    agent any

    environment {
        PROJECT_ID = 'your-gcp-project-id'
        REGION = 'asia-southeast1'
        REPOSITORY = 'legal-repo'
        BACKEND_SERVICE = 'legal-backend'
        FRONTEND_SERVICE = 'legal-frontend'
        GCP_CREDS_ID = 'gcp-sa-key-id' // ID của Google Service Account Key lưu trong Jenkins Credentials
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Set up Environment') {
            steps {
                sh 'python3 -m venv venv'
                sh './venv/bin/pip install -r requirements.txt'
            }
        }

        stage('Test & Evaluation') {
            steps {
                script {
                    // Chạy unit tests
                    sh './venv/bin/pytest tests/'
                    // Chạy MLOps Evaluation
                    withCredentials([string(credentialsId: 'openai-api-key', variable: 'OPENAI_API_KEY')]) {
                        sh './venv/bin/python RUN_EVALUATION.py'
                    }
                }
            }
        }

        stage('Build & Push Docker Images') {
            steps {
                script {
                    // Authenticate Docker with GCP
                    sh 'gcloud auth configure-docker ${REGION}-docker.pkg.dev'
                    
                    // Build Backend
                    sh "docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${BACKEND_SERVICE}:${env.BUILD_NUMBER} -f Dockerfile.backend ."
                    sh "docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${BACKEND_SERVICE}:${env.BUILD_NUMBER}"
                    
                    // Build Frontend
                    sh "docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${FRONTEND_SERVICE}:${env.BUILD_NUMBER} -f Dockerfile.frontend ."
                    sh "docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${FRONTEND_SERVICE}:${env.BUILD_NUMBER}"
                }
            }
        }

        stage('Deploy to Cloud Run') {
            steps {
                script {
                    // Deploy Backend
                    sh """
                    gcloud run deploy ${BACKEND_SERVICE} \
                        --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${BACKEND_SERVICE}:${env.BUILD_NUMBER} \
                        --region ${REGION} \
                        --platform managed \
                        --allow-unauthenticated
                    """
                    
                    // Deploy Frontend
                    sh """
                    gcloud run deploy ${FRONTEND_SERVICE} \
                        --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${FRONTEND_SERVICE}:${env.BUILD_NUMBER} \
                        --region ${REGION} \
                        --platform managed \
                        --allow-unauthenticated
                    """
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo 'Deployment successful!'
        }
        failure {
            echo 'Deployment failed. Check logs.'
        }
    }
}
