pipeline {
    agent any

    stages {
        // GIAI DOAN 1: Lay ma nguon (Kích hoạt lại khi push lên Git)
        /*
        stage('Checkout Code') {
            steps {
                dir('D:\\StudyUni\\HK9\\QLDAPM\\JobPortalSystem') {
                    git branch: 'main', url: 'https://github.com/ThienDoanPlus/JobPortalSystem.git'
                    echo '✅ Da lay ma nguon thanh cong.'
                }
            }
        }
        */

        // GIAI DOAN 2: Build Docker Image
        stage('Build Docker Image') {
            steps {
                dir('D:\\StudyUni\\HK9\\QLDAPM\\JobPortalSystem') {
                    echo '🚀 Bat dau build Docker image...'
                    bat 'docker build -t nguyenkhoineee/job-portal-system .'
                    echo '✅ Da build xong image.'
                }
            }
        }

        // GIAI DOAN 3: Chay Unit Test
        stage('Run Unit Tests') {
            steps {
                echo '🔬 Bat dau chay unit tests...'
                bat 'docker run --rm nguyenkhoineee/job-portal-system python -m pytest'
                echo '✅ Tat ca cac test da qua!'
            }
        }

        // GIAI DOAN 4: Day Image len Docker Hub
        stage('Push to Docker Hub') {
            steps {
                echo '📦 Dang day image len Docker Hub...'
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCK-ER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    bat 'echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin'
                    bat 'docker push nguyenkhoineee/job-portal-system'
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
                bat 'docker run -d --name job-portal-container -p 5000:5000 nguyenkhoineee/job-portal-system'
                echo '🎉 Ung dung da duoc trien khai thanh cong va dang chay!'
            }
        }
    }
}