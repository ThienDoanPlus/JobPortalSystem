pipeline {
    agent any

    stages {
        // GIAI DOAN 1: Lay ma nguon tu GitHub
        stage('Checkout Code') {
            steps {
                // Lệnh này sẽ tự động checkout code từ cấu hình của job
                // Jenkins sẽ tự động di chuyển vào thư mục workspace chứa code này
                checkout scm
                echo "✅ Da checkout code thanh cong."
            }
        }

        // GIAI DOAN 2: Build Docker Image
        stage('Build Docker Image') {
            steps {
                // Không cần dir(...) nữa vì Jenkins đã ở đúng thư mục workspace
                echo '🚀 Bat dau build Docker image...'
                bat 'docker build -t nguyenkhoineee/job-portal-system .' // <-- Thay đổi Docker Hub ID nếu cần
                echo '✅ Da build xong image.'
            }
        }

        // GIAI DOAN 3: Chay Unit Test
        stage('Run Unit Tests') {
            steps {
                echo '🔬 Bat dau chay unit tests...'
                bat 'docker run --rm nguyenkhoineee/job-portal-system python -m pytest' // <-- Thay đổi Docker Hub ID nếu cần
                echo '✅ Tat ca cac test da qua!'
            }
        }

        // GIAI DOAN 4: Day Image len Docker Hub
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
                    bat 'docker push nguyenkhoineee/job-portal-system' // <-- Thay đổi Docker Hub ID nếu cần
                }
                echo '✅ Da day image thanh cong.'
            }
        }

        // GIAI DOAN 5: Trien khai ung dung
        stage('Deploy Application') {
            steps {
                echo '🚚 Bat dau trien khai ung dung...'
                bat 'docker stop job-portal-container || exit 0'
                bat 'docker rm job-portal-container || exit 0'
                bat 'docker run -d --name job-portal-container -p 5000:5000 nguyenkhoineee/job-portal-system' // <-- Thay đổi Docker Hub ID nếu cần
                echo '🎉 Ung dung da duoc trien khai thanh cong va dang chay!'
            }
        }
    }
}