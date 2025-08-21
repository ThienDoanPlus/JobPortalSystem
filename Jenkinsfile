// Đây là bản hướng dẫn công việc theo phương pháp Docker
pipeline {
    agent any // Chạy trên bất kỳ agent nào có sẵn

    stages {
        // Giai đoạn 1: Lấy mã nguồn từ GitHub
        stage('Checkout Code') {
            steps {
                // Lấy code từ nhánh main của repo
                git branch: 'main', url: 'https://github.com/ThienDoanPlus/JobPortalSystem.git'
                echo '✅ Đã lấy mã nguồn thành công.'
            }
        }

        // Giai đoạn 2: Build "hộp" Docker
        stage('Build Docker Image') {
            steps {
                echo '🚀 Bắt đầu build Docker image...'
                // NHỚ THAY THẾ 'nguyenkhoineee' BẰNG DOCKER HUB ID CỦA BẠN!
                sh 'docker build -t nguyenkhoineee/job-portal-system .'
                echo '✅ Đã build xong image.'
            }
        }

        // Giai đoạn 3: Chạy Unit Test bên trong "hộp"
        stage('Run Unit Tests') {
            steps {
                echo '🔬 Bắt đầu chạy unit tests...'
                // Chạy test bên trong container vừa build để đảm bảo môi trường nhất quán
                // NHỚ THAY THẾ 'nguyenkhoineee' BẰNG DOCKER HUB ID CỦA BẠN!
                sh 'docker run --rm nguyenkhoineee/job-portal-system python -m pytest'
                echo '✅ Tất cả các test đã qua!'
            }
        }

        // Giai đoạn 4: Đẩy "hộp" lên kho chứa Docker Hub
        stage('Push to Docker Hub') {
            steps {
                echo '📦 Đang đẩy image lên Docker Hub...'
                // Sử dụng credentials đã lưu trong Jenkins
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                    // NHỚ THAY THẾ 'nguyenkhoineee' BẰNG DOCKER HUB ID CỦA BẠN!
                    sh 'docker push nguyenkhoineee/job-portal-system'
                }
                echo '✅ Đã đẩy image thành công.'
            }
        }

        // Giai đoạn 5: Triển khai ứng dụng
        stage('Deploy Application') {
            steps {
                echo '🚚 Bắt đầu triển khai ứng dụng...'
                // Dừng và xóa container cũ nếu đang chạy
                sh 'docker stop job-portal-container || true'
                sh 'docker rm job-portal-container || true'
                
                // Chạy container mới từ image vừa đẩy lên
                // NHỚ THAY THẾ 'nguyenkhoineee' BẰNG DOCKER HUB ID CỦA BẠN!
                sh 'docker run -d --name job-portal-container -p 5000:5000 nguyenkhoineee/job-portal-system'
                echo '🎉 Ứng dụng đã được triển khai thành công và đang chạy!'
            }
        }
    }
}