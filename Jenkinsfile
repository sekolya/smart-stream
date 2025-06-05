pipeline {
    agent any

    environment {
        AWS_ACCESS_KEY_ID     = credentials('aws-access-key')   // Store in Jenkins credentials
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-key')
        AWS_DEFAULT_REGION    = 'us-east-2'
    }

    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/sekolya/smart-stream.git'
            }
        }

        stage('Terraform Init') {
            steps {
                sh 'terraform init'
            }
        }

        stage('Terraform Plan') {
            steps {
                sh 'terraform plan'
            }
        }

        stage('Terraform Apply') {
            steps {
                input "Apply Terraform changes?"
                sh 'terraform apply -auto-approve'
            }
        }
    }
}

