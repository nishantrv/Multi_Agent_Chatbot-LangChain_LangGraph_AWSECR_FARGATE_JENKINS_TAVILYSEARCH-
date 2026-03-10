pipeline {
    agent any

    environment {
        SONAR_PROJECT_KEY  = 'llmops'
        SONAR_SCANNER_HOME = tool 'sonarcube-scan'
        AWS_REGION         = 'us-east-1'
        ECR_REPO           = 'my-repo'
        IMAGE_TAG          = 'latest'
    }

    stages {

        stage('Cloning Github repo to Jenkins') {
            steps {
                script {
                    echo 'Cloning Github repo to Jenkins............'
                    checkout scmGit(
                        branches: [[name: '*/main']],
                        extensions: [[$class: 'CleanBeforeCheckout']],  // ✅ wipes workspace before clone
                        userRemoteConfigs: [[
                            credentialsId: 'github-mulit-agent-token',
                            url: 'https://github.com/nishantrv/Multi_Agent_Chatbot-LangChain_LangGraph_AWSECR_FARGATE_JENKINS_TAVILYSEARCH-' 
                        ]]
                    )
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
                    withSonarQubeEnv('sonarqube') {
                        sh """
                        ${SONAR_SCANNER_HOME}/bin/sonar-scanner \
                        -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                        -Dsonar.sources=. \
                        -Dsonar.host.url=http://sonarqube-dind:9000 \
                        -Dsonar.login=${SONAR_TOKEN}
                        """
                    }
                }
            }
        }

        stage('Quality Gate') {  // ✅ added - waits for Sonar result before proceeding
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build and Push Docker Image to ECR') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-token']]) {
                    script {
                        def accountId = sh(
                            script: "aws sts get-caller-identity --query Account --output text",
                            returnStdout: true
                        ).trim()
                        def ecrUrl = "${accountId}.dkr.ecr.${env.AWS_REGION}.amazonaws.com/${env.ECR_REPO}"

                        sh """
                        aws ecr get-login-password --region ${AWS_REGION} | \
                            docker login --username AWS --password-stdin ${ecrUrl}
                        docker build -t ${env.ECR_REPO}:${IMAGE_TAG} .
                        docker tag ${env.ECR_REPO}:${IMAGE_TAG} ${ecrUrl}:${IMAGE_TAG}
                        docker push ${ecrUrl}:${IMAGE_TAG}
                        """
                    }
                }
            }
        }

        stage('Deploy to ECS Fargate') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-token']]) {
                    script {
                        sh """
                        aws ecs update-service \
                          --cluster able-bird-emufac \
                          --service multi-ai-agent-101-service-czlo7vxp \
                          --force-new-deployment \
                          --region ${AWS_REGION}
                        """
                    }
                }
            }
        }
    }

    post {  // ✅ added - always clean up workspace after run
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed — check logs above.'
        }
    }
}