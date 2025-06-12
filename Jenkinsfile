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
                sh "terraform apply -auto-approve -var=\"deployer_public_key=${DEPLOYER_PUBLIC_KEY}\""
            }
        }

        stage('AI Suggestion (ChatGPT)') {
            steps {
                withCredentials([
                    string(credentialsId: 'openai-api-key', variable: 'OPENAI_API_KEY'),
                    string(credentialsId: 'slack-bot-token', variable: 'SLACK_BOT_TOKEN'),
                    string(credentialsId: 'slack-channel', variable: 'SLACK_CHANNEL')
                ]) {
                    sh '''
                        echo "[INFO] 🧠 Running SmartStream AI Suggestion..."

                        rm -rf sm-env
                        python3 -m venv sm-env
                        . sm-env/bin/activate
                        pip install --upgrade pip
                        pip install openai slack_sdk rich

                        echo "[INFO] 📥 Fetching Jenkins console logs..."
                        curl -s http://localhost:8080/job/${JOB_NAME}/${BUILD_NUMBER}/consoleText > build.log

                        export OPENAI_API_KEY=$OPENAI_API_KEY
                        export SLACK_BOT_TOKEN=$SLACK_BOT_TOKEN
                        export SLACK_CHANNEL=$SLACK_CHANNEL

                        echo "[INFO] 🤖 Running ChatGPT AI analysis..."
                        python send_to_chatgpt.py build.log || true

                        grep ">>> Suggestion:" chatgpt_output.txt > suggestion.txt || \
                        echo ">>> Suggestion: We couldn't automatically identify this issue. Please contact your DevOps team: devops@example.com" > suggestion.txt

                        echo "[INFO] 📦 Preparing HTML report..."
                        mkdir -p artifacts
                        cp chatgpt_output.txt artifacts/
                        cp suggestion.txt artifacts/
                        cp resources/robot.png artifacts/

                        cat <<EOF > artifacts/suggestion.html
<html>
  <head>
    <meta charset="UTF-8">
  </head>
  <body style='font-family: Arial; text-align: center;'>
    <img src='robot.png' alt='SmartStream Bot' style='height: 40px; margin-bottom: 20px;'/>
    <h2>SmartStream Suggestion</h2>
    <div style='text-align: left; max-width: 600px; margin: auto;'><pre>
$(cat suggestion.txt)
    </pre></div>
  </body>
</html>
EOF
                    '''
                }
            }
        }
    }

    post {
        always {
            echo "[INFO] 📁 Archiving AI suggestion artifacts..."
            archiveArtifacts artifacts: 'artifacts/*', fingerprint: true

            echo "[INFO] 🌐 Publishing HTML report..."
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
            echo "[INFO] ✉️ Sending failure notification with AI suggestion..."
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
