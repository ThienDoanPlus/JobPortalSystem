// Jenkinsfile phiên bản "bat" dành riêng cho Windows
pipeline {
    agent any

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/ThienDoanPlus/JobPortalSystem.git'
                echo '✅ Da lay ma nguon thanh cong.'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo '🚀 Bat dau build Docker image...'
                // THAY sh BANG bat
                bat 'docker build -t nguyenkhoineee/job-portal-system .'
                echo '✅ Da build xong image.'
            }
        }

        stage('Run Unit Tests') {
            steps {
                echo '🔬 Bat dau chay unit tests...'
                // THAY sh BANG bat
                bat 'docker run --rm nguyenkhoineee/job-portal-system python -m pytest'
                echo '✅ Tat ca cac test da qua!'
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo '📦 Dang day image len Docker Hub...'
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    // THAY sh BANG bat VA THAY DOI CU PHAP BIEN MOI TRUONG
                    bat 'echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin'
                    bat 'docker push nguyenkhoineee/job-portal-system'
                }
                echo '✅ Da day image thanh cong.'
            }
        }

        stage('Deploy Application') {
            steps {
                echo '🚚 Bat dau trien khai ung dung...'
                // THAY sh BANG bat VA THAY DOI CACH XU LY LOI
                bat 'docker stop job-portal-container || exit 0'
                bat 'docker rm job-portal-container || exit 0'
                bat 'docker run -d --name job-portal-container -p 5000:5000 nguyenkhoineee/job-portal-system'
                echo '🎉 Ung dung da duoc trien khai thanh cong va dang chay!'
            }
        }
    }
}