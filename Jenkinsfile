pipeline {
    agent { label 'master' }

    environment {
        AWS_ACCESS_KEY_ID     = credentials('aws-access-key')        // Stored in Jenkins credentials
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-key')
        AWS_DEFAULT_REGION    = 'us-east-2'
        DEPLOYER_PUBLIC_KEY   = credentials('deployer-public-key') 
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
                sh "terraform plan -var=\"deployer_public_key=${DEPLOYER_PUBLIC_KEY}\""
            }
        }

        stage('Terraform Apply') {
            steps {
                sh "terraform apply -auto-approve -var='deployer_public_key=${DEPLOYER_PUBLIC_KEY}'"
            }
        }

        stage('Send to SageMaker') {
            steps {
                sh '''
                    python3 -m venv sm-env
                    . sm-env/bin/activate
                    pip install boto3

                    # Fetch console log and send to SageMaker
                    curl -s http://3.148.224.153:8080/job/${JOB_NAME}/${BUILD_NUMBER}/consoleText > build.log
                    python send_to_sagemaker.py build.log > sagemaker_output.txt

                    # Extract suggestion
                    grep ">>> Suggestion:" sagemaker_output.txt || echo ">>> Suggestion: No suggestion found." > suggestion.txt

                    # Archive results
                    mkdir -p artifacts
                    cp sagemaker_output.txt artifacts/
                    cp suggestion.txt artifacts/

                    # Create HTML summary
                    echo "<html><body><h2>SmartStream Suggestion</h2><pre>" > artifacts/suggestion.html
                    cat suggestion.txt >> artifacts/suggestion.html
                    echo "</pre></body></html>" >> artifacts/suggestion.html
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'artifacts/*', fingerprint: true
            publishHTML(target: [
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'artifacts',
                reportFiles: 'suggestion.html',
                reportName: 'SmartStream Suggestion'
            ])
        }

        success {
            script {
                def suggestion = readFile('artifacts/suggestion.txt').trim()
                emailext(
                    subject: "SmartStream Suggestion - Build #${env.BUILD_NUMBER}",
                    body: """<p>Hi Team,</p>
                             <p>Here is the SmartStream suggestion from the latest build:</p>
                             <pre>${suggestion}</pre>
                             <p><a href="${env.BUILD_URL}">View Full Build</a></p>""",
                    mimeType: 'text/html',
                    to: 'team@example.com'
                )
            }
        }
    }
}

