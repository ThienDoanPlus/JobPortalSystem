// Đây là "Bản Hướng Dẫn Công Việc" cho Jenkins
pipeline {
    agent any // Yêu cầu Jenkins tìm một máy trống để làm việc

    // Chia công việc thành các giai đoạn
    stages {
        // Giai đoạn 1: Lấy mã nguồn
        stage('Checkout Code') {
            steps {
                // Lấy code từ nhánh main của repo này
                git branch: 'main', url: 'https://github.com/ThienDoanPlus/JobPortalSystem.git'
            }
        }

        // Giai đoạn 2: Đóng gói ứng dụng vào "hộp" Docker
        stage('Build Docker Image') {
            steps {
                // Đọc file Dockerfile và build ra một image tên là "thiendoanplus/job-portal"
                sh 'docker build -t nguyenkhoineee/job-portal .'
            }
        }

        // Giai đoạn 3: Chạy kiểm thử tự động
        stage('Run Unit Tests') {
            steps {
                // Chạy các bài test bên trong "hộp" Docker để đảm bảo chất lượng
                sh 'docker run --rm nguyenkhoineee/job-portal python -m pytest'
            }
        }

        // Giai đoạn 4 (Tùy chọn): Đẩy "hộp" lên kho chứa
        stage('Push to Docker Hub') {
            steps {
                // Dùng credentials đã lưu trong Jenkins để đăng nhập và đẩy image lên
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                    sh 'docker push nguyenkhoineee/job-portal'
                }
            }
        }

        // Giai đoạn 5: Triển khai ứng dụng lên server
        stage('Deploy Application') {
            steps {
                // Dừng và xóa container cũ (nếu có)
                sh 'docker stop job-portal-container || true'
                sh 'docker rm job-portal-container || true'
                // Chạy container mới từ image vừa build
                sh 'docker run -d --name job-portal-container -p 5000:5000 nguyenkhoineee/job-portal'
            }
        }
    }
}