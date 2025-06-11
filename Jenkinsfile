pipeline {
    agent { label 'master' }

    environment {
        AWS_ACCESS_KEY_ID     = credentials('aws-access-key')
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

        stage('AI Suggestion (ChatGPT)') {
            steps {
                withCredentials([string(credentialsId: 'openai-api-key', variable: 'OPENAI_API_KEY')]) {
                    sh '''
                        python3 -m venv sm-env
                        . sm-env/bin/activate
                        pip install openai

                        # Fetch Jenkins log
                        curl -s http://3.20.253.231:8080/job/${JOB_NAME}/${BUILD_NUMBER}/consoleText > build.log

                        # Run AI suggestion
                        export OPENAI_API_KEY=$OPENAI_API_KEY
                        python send_to_chatgpt.py build.log > chatgpt_output.txt

                        # Parse output or fallback
                        grep ">>> Suggestion:" chatgpt_output.txt > suggestion.txt || \
                        echo ">>> Suggestion: We couldn't automatically identify this issue. Please contact your DevOps team: devops@example.com" > suggestion.txt

                        # Create report
                        mkdir -p artifacts
                        cp chatgpt_output.txt artifacts/
                        cp suggestion.txt artifacts/
                        cp resources/robot.png artifacts/

                        echo "<html><body style='font-family: Arial; text-align: center;'>" > artifacts/suggestion.html
                        echo "<img src='robot.png' alt='SmartStream Bot' style='height: 40px; margin-bottom: 20px;'/>" >> artifacts/suggestion.html
                        echo "<h2>SmartStream Suggestion</h2>" >> artifacts/suggestion.html
                        echo "<div style='text-align: left; max-width: 600px; margin: auto;'><pre>" >> artifacts/suggestion.html
                        cat suggestion.txt >> artifacts/suggestion.html
                        echo "</pre></div></body></html>" >> artifacts/suggestion.html
                    '''
                }
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

        failure {
            script {
                def suggestion = readFile('artifacts/suggestion.txt').trim()
                emailext(
                    subject: "SmartStream Suggestion - Build #${env.BUILD_NUMBER}",
                    body: """<p>Hi Team,</p>
                             <p>Here is the SmartStream suggestion from the failed build:</p>
                             <pre>${suggestion}</pre>
                             <p><a href="${env.BUILD_URL}">View Full Build</a></p>
                             <p>If no fix is clear, please contact: <b>dulatseil@gmail.com</b></p>""",
                    mimeType: 'text/html',
                    to: 'team@example.com'
                )
            }
        }
    }
}

