// /static/js/profile_dashboard.js

document.addEventListener('DOMContentLoaded', () => {
    const navItems = document.querySelectorAll('.dashboard-nav .nav-item');
    const tabPanes = document.querySelectorAll('.dashboard-content .tab-pane');

    // --- XỬ LÝ CHUYỂN TAB ---
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();

            // Biến tabId được định nghĩa an toàn ở đây
            const tabId = item.dataset.tab;

            // Cập nhật trạng thái active cho nút nav
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');

            // Hiển thị tab content tương ứng
            tabPanes.forEach(pane => {
                pane.classList.remove('active');
                if (pane.id === tabId) {
                    pane.classList.add('active');
                }
            });

            // GỌI HÀM TẢI DỮ LIỆU TỪ BÊN TRONG SỰ KIỆN CLICK
            if (tabId === 'applied') {
                loadAppliedJobs();
            } else if (tabId === 'cvs') {
                loadCvManagement();
            }
        });
    });

    // --- HÀM TẢI DANH SÁCH VIỆC LÀM ĐÃ ỨNG TUYỂN ---
    async function loadAppliedJobs() {
        const listContainer = document.getElementById('applied-jobs-list');
        // Chỉ tải nếu chưa có nội dung (hoặc đang hiển thị thông báo loading)
        if (listContainer.children.length > 0 && !listContainer.textContent.includes('Đang tải')) {
            return;
        }

        listContainer.innerHTML = '<p>Đang tải...</p>';

        try {
            const response = await fetch('/api/candidate/applied-jobs');
            const jobs = await response.json();

            if (!response.ok) {
                throw new Error(jobs.error || 'Failed to fetch applied jobs');
            }

            if (jobs.length === 0) {
                listContainer.innerHTML = '<p>Bạn chưa ứng tuyển vào công việc nào.</p>';
                return;
            }

            const html = jobs.map(job => `
                <div class="job-card-list">
                    <div class="job-card-list-logo">
                        <img src="${job.company_logo || '/static/image/default_logo.png'}" alt="${job.company_name}">
                    </div>
                    <div class="job-card-list-content">
                        <h5><a href="/job/${job.job_id}">${job.job_title}</a></h5>
                        <p>${job.company_name}</p>
                        <p>Ngày nộp: ${job.applied_date}</p>
                    </div>
                    <div class="job-card-list-status">
                        <span>Trạng thái: <strong>${job.status}</strong></span>
                    </div>
                </div>
            `).join('');
            listContainer.innerHTML = html;
        } catch (error) {
            console.error('Failed to load applied jobs:', error);
            listContainer.innerHTML = '<p class="text-danger">Lỗi khi tải dữ liệu.</p>';
        }
    }

    // --- HÀM TẢI TRANG QUẢN LÝ CV ---
    async function loadCvManagement() {
        const cvContainer = document.getElementById('cv-management-content');
        const url = cvContainer.dataset.url; // Đọc URL từ data attribute

        if (!url) {
            cvContainer.innerHTML = '<p class="text-danger">Lỗi: Không tìm thấy URL để tải dữ liệu.</p>';
            return;
        }

        // Chỉ tải nếu chưa có nội dung
        if (cvContainer.innerHTML && !cvContainer.textContent.includes('Đang tải')) {
            return;
        }

        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }

            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const content = doc.querySelector('.cv-management-page');

            if (content) {
                cvContainer.innerHTML = content.innerHTML;
            } else {
                cvContainer.innerHTML = '<p>Không có nội dung để hiển thị.</p>';
            }
        } catch (error) {
            console.error("Failed to load CV management content:", error);
            cvContainer.innerHTML = '<p class="text-danger">Lỗi khi tải danh sách CV.</p>';
        }
    }

    // (Code xử lý modal chỉnh sửa hồ sơ của bạn có thể đặt ở đây)
});