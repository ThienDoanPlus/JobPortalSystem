// static/js/apply.js

// Hàm này sẽ chạy khi toàn bộ tài liệu HTML đã được tải xong.
document.addEventListener('DOMContentLoaded', function () {
    // --- PHẦN 1: Lấy dữ liệu động từ HTML ---
    // Lấy "cầu nối" dữ liệu mà chúng ta sẽ đặt trong HTML
    const dataContainer = document.getElementById('job-data-container');
    if (!dataContainer) {
        console.error('Không tìm thấy data container. Script không thể chạy.');
        return;
    }

    // Đọc dữ liệu từ các thuộc tính data-*
    const hasCv = dataContainer.dataset.hasCv === 'True'; // Jinja sẽ in ra 'True' hoặc 'False'
    const createCvUrl = dataContainer.dataset.createCvUrl;
    const applyUrl = dataContainer.dataset.applyUrl;
    const applyButton = document.getElementById('btn-apply-submit');
    const modalElement = document.getElementById('applyJobModal');

    // --- PHẦN 2: Định nghĩa các hàm xử lý UI ---
    const frmUpload = document.getElementById('frm-upload');
    const frmSelectOnlineCv = document.getElementById('frm-select-cv-online');

    function showUploadForm() {
        if (frmSelectOnlineCv) frmSelectOnlineCv.style.display = 'none';
        if (frmUpload) frmUpload.style.display = 'block';
    }

    function showSelectOnlineCVForm() {
        if (hasCv) {
            if (frmUpload) frmUpload.style.display = 'none';
            if (frmSelectOnlineCv) frmSelectOnlineCv.style.display = 'block';
        } else {
            alert('Bạn chưa có CV online nào. Vui lòng tải lên CV từ máy tính hoặc tạo mới.');
        }
    }

    // Gán sự kiện cho các link chuyển đổi form
    const switchToUploadLink = document.querySelector('a[href="javascript:showUploadForm()"]');
    if (switchToUploadLink) switchToUploadLink.onclick = (e) => { e.preventDefault(); showUploadForm(); };

    const switchToOnlineCVLink = document.querySelector('a[href="javascript:showSelectOnlineCVForm()"]');
    if (switchToOnlineCVLink) switchToOnlineCVLink.onclick = (e) => { e.preventDefault(); showSelectOnlineCVForm(); };

    // --- PHẦN 3: Quyết định form nào hiển thị mặc định ---
    if (hasCv) {
        // Mặc định ẩn form upload và hiện form chọn CV
        if (frmUpload) frmUpload.style.display = 'none';
        if (frmSelectOnlineCv) frmSelectOnlineCv.style.display = 'block';
    } else {
        // Ngược lại, chỉ hiện form upload
        showUploadForm();
    }

    // --- PHẦN 4: Gán sự kiện cho nút "Nộp CV" ---
    if (!applyButton) return; // Nếu không có nút thì không làm gì cả

    applyButton.addEventListener('click', async (event) => {
        event.preventDefault();

        const form = document.getElementById('form-apply-cv');
        const formData = new FormData(form);
        const modal = bootstrap.Modal.getInstance(modalElement);

        applyButton.disabled = true;
        applyButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Đang nộp...';

        try {
            // Sử dụng URL đã lấy từ data-apply-url
            const response = await fetch(applyUrl, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.success) {
                alert('Ứng tuyển thành công!');
                if (modal) modal.hide();
                // window.location.reload(); // Bỏ comment nếu muốn tải lại trang
            } else {
                alert(data.error || 'Đã có lỗi xảy ra. Vui lòng thử lại.');
            }
        } catch (error) {
            console.error('Fetch Error:', error);
            alert('Không thể kết nối đến máy chủ. Vui lòng kiểm tra lại đường truyền.');
        } finally {
            applyButton.disabled = false;
            applyButton.innerHTML = 'Nộp CV';
        }
    });
});