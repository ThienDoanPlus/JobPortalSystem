pipeline {
    agent any

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
                echo "✅ Da checkout code thanh cong."
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Bat dau build Docker image...'
                bat 'docker build -t nguyenkhoineee/job-portal-system .' // <-- Thay đổi Docker Hub ID nếu cần
                echo 'Da build xong image.'
            }
        }

        stage('Run Unit Tests') {
            steps {
                echo 'Bat dau chay unit tests...'
                bat 'docker run --rm nguyenkhoineee/job-portal-system python -m pytest' // <-- Thay đổi Docker Hub ID nếu cần
                echo 'Tat ca cac test da qua!'
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo '📦 Dang chuan bi xac thuc voi Docker Hub...'
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    script {
                        // Tạo chuỗi xác thực Base64
                        def auth = "${DOCKER_USER}:${DOCKER_PASS}".bytes.encodeBase64().toString()
                        def config = """{"auths":{"https://index.docker.io/v1/":{"auth":"${auth}"}}}"""

                        // Ghi file config.json vào thư mục home của user đang chạy Jenkins
                        bat """
                            mkdir %USERPROFILE%\\.docker 2>nul || exit 0
                            echo ${config} > %USERPROFILE%\\.docker\\config.json
                        """
                    }

                    // Chạy docker push
                    echo '📦 Dang day image len Docker Hub...'
                    bat 'docker push nguyenkhoineee/job-portal-system'
                }
                echo 'Da day image thanh cong.'
            }
        }

        stage('Deploy Application') {
            steps {
                echo 'Bat dau trien khai ung dung...'
                bat 'docker stop job-portal-container || exit 0'
                bat 'docker rm job-portal-container || exit 0'
                bat '''
                        docker run -d --name job-portal-container -p 5000:5000 -e "DB_HOST=host.docker.internal" nguyenkhoineee/job-portal-system:latest
                    '''
                echo 'Ung dung da duoc trien khai thanh cong va dang chay!'
            }
        }
    }
}