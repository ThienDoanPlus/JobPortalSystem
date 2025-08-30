// /static/js/cv_builder.js

document.addEventListener('DOMContentLoaded', () => {
    // --- 1. KHỞI TẠO & LẤY CÁC ELEMENT CẦN THIẾT ---
    const cvSheet = document.getElementById('cv-sheet');
    const controlPanel = document.querySelector('.control-panel');
    const saveButton = document.getElementById('btn-save-cv');

    // Lấy ID của CV từ URL (ví dụ: /cv/15/edit -> lấy số 15)
    const pathParts = window.location.pathname.split('/');
    const cvId = pathParts[2];

    // Biến toàn cục để lưu trữ trạng thái hiện tại của CV, đây là "Single Source of Truth"
    let cvData = {};

    // --- 2. HÀM CHÍNH: TẢI DỮ LIỆU BAN ĐẦU ---
    async function initializeCVBuilder() {
        if (!cvId) {
            cvSheet.innerHTML = '<p class="text-danger">Lỗi: Không tìm thấy ID của CV trên URL.</p>';
            return;
        }

        try {
            // Hiển thị thông báo loading
            cvSheet.innerHTML = '<p>Đang tải dữ liệu CV...</p>';

            // Gọi API để lấy dữ liệu
            const response = await fetch(`/api/cv/${cvId}`);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Không thể tải dữ liệu CV.');
            }
            cvData = await response.json();

            // Khi có dữ liệu, bắt đầu render và cài đặt
            renderAllSections();
            applyAllStyles();
            initControllers();
            initEventListeners();

        } catch (error) {
            cvSheet.innerHTML = `<p class="text-danger">Đã xảy ra lỗi: ${error.message}</p>`;
        }
    }

    // --- 3. LOGIC RENDER: BIẾN DỮ LIỆU JSON THÀNH HTML ---
    function renderAllSections() {
        cvSheet.innerHTML = ''; // Xóa sạch nội dung cũ

        // Render các thành phần theo thứ tự
        renderHeader();
        renderExperiences();
        renderEducations();
        // (Thêm các hàm render cho Skills, Projects... ở đây nếu có)
    }

    function renderHeader() {
        const html = `
            <header class="cv-header-preview">
                <h1 contenteditable="true" data-field="candidate_name">${cvData.candidate_name || ''}</h1>
                <p class="cv-subtitle-preview" contenteditable="true" data-field="title">${cvData.title || ''}</p>
                <!-- Thêm thông tin liên hệ nếu cần -->
            </header>
        `;
        cvSheet.insertAdjacentHTML('beforeend', html);
    }

    function renderExperiences() {
        const html = `
            <section class="cv-section-preview" data-section="experiences">
                <h2 class="section-title-preview">KINH NGHIỆM LÀM VIỆC</h2>
                ${cvData.experiences.map(exp => `
                    <div class="cv-item-preview" data-id="${exp.id}">
                        <div class="item-header">
                            <h3 class="item-title" contenteditable="true">${exp.job_title}</h3>
                            <span class="item-date" contenteditable="true">DD/YYYY - DD/YYYY</span>
                        </div>
                        <h4 class="item-subtitle" contenteditable="true">${exp.company_name}</h4>
                        <p class="item-description" contenteditable="true">${exp.description}</p>
                        <div class="item-controls">
                            <button class="btn-delete-item" data-type="experience" title="Xóa mục này"><i class="fas fa-trash-alt"></i></button>
                        </div>
                    </div>
                `).join('')}
            </section>
        `;
        cvSheet.insertAdjacentHTML('beforeend', html);
    }

    function renderEducations() {
        const html = `
            <section class="cv-section-preview" data-section="educations">
                <h2 class="section-title-preview">HỌC VẤN</h2>
                 ${cvData.educations.map(edu => `
                    <div class="cv-item-preview" data-id="${edu.id}">
                         <div class="item-header">
                            <h3 class="item-title" contenteditable="true">${edu.institution_name}</h3>
                            <span class="item-date" contenteditable="true">YYYY</span>
                        </div>
                        <h4 class="item-subtitle" contenteditable="true">${edu.degree} - ${edu.major}</h4>
                        <div class="item-controls">
                            <button class="btn-delete-item" data-type="education" title="Xóa mục này"><i class="fas fa-trash-alt"></i></button>
                        </div>
                    </div>
                `).join('')}
            </section>
        `;
        cvSheet.insertAdjacentHTML('beforeend', html);
    }

    // --- 4. LOGIC STYLE: ÁP DỤNG THAY ĐỔI GIAO DIỆN ---
    function applyAllStyles() {
        if (!cvData.style) return;
        const style = cvData.style;
        cvSheet.style.fontFamily = style.font_family;
        document.documentElement.style.setProperty('--cv-theme-color', style.theme_color);
        // (Thêm code áp dụng font-size, line-spacing ở đây)
    }

    // --- 5. LOGIC CONTROLLERS: GẮN SỰ KIỆN CHO SIDEBAR ---
    function initControllers() {
        if (!controlPanel || !cvData.style) return;

        // Bộ chọn Font
        const fontSelect = controlPanel.querySelector('#font-family-select');
        if (fontSelect) {
            fontSelect.value = cvData.style.font_family;
            fontSelect.addEventListener('change', (e) => {
                cvData.style.font_family = e.target.value;
                applyAllStyles();
            });
        }

        // Bộ chọn Màu
        const colorPicker = controlPanel.querySelector('#theme-color');
        if (colorPicker) {
            colorPicker.value = cvData.style.theme_color;
            colorPicker.addEventListener('input', (e) => {
                cvData.style.theme_color = e.target.value;
                applyAllStyles();
            });
        }
    }

    // --- 6. LOGIC EVENT LISTENERS: GẮN SỰ KIỆN CHO CÁC MỤC ĐỘNG ---
    function initEventListeners() {
        // Sử dụng event delegation để xử lý các sự kiện trên các element được tạo động
        cvSheet.addEventListener('click', (e) => {
            // Xử lý nút xóa
            if (e.target.closest('.btn-delete-item')) {
                const button = e.target.closest('.btn-delete-item');
                const item = button.closest('.cv-item-preview');
                const id = item.dataset.id;
                const type = button.dataset.type; // 'experience' or 'education'

                if (confirm('Bạn có chắc chắn muốn xóa mục này?')) {
                    handleDeleteItem(id, type);
                }
            }
        });

        // (Thêm code xử lý sự kiện 'blur' cho các trường contenteditable ở đây để lưu thay đổi)
    }

    // --- 7. CÁC HÀM XỬ LÝ HÀNH ĐỘNG (Actions) ---
    async function handleDeleteItem(id, type) {
        // Tạm thời xóa khỏi giao diện để người dùng thấy ngay
        const itemElement = cvSheet.querySelector(`.cv-item-preview[data-id='${id}']`);
        itemElement.style.opacity = '0.5';

        try {
            // Gọi API để xóa trong database
            const response = await fetch(`/api/${type}/${id}`, { method: 'DELETE' });
            const result = await response.json();

            if (!response.ok) throw new Error(result.error);

            // Nếu API xóa thành công, xóa hẳn khỏi giao diện
            itemElement.remove();
            // Cập nhật lại dữ liệu trong biến cvData
            cvData[type + 's'] = cvData[type + 's'].filter(item => item.id != id);

        } catch (error) {
            alert(`Lỗi khi xóa: ${error.message}`);
            itemElement.style.opacity = '1'; // Khôi phục lại nếu xóa thất bại
        }
    }

    // Xử lý nút Lưu CV
    if (saveButton) {
        saveButton.addEventListener('click', async () => {
            const originalText = saveButton.innerHTML;
            saveButton.innerHTML = 'Đang lưu...';
            saveButton.disabled = true;

            try {
                // (Thêm logic thu thập dữ liệu từ các trường contenteditable ở đây)

                // Gửi các thay đổi về style
                await fetch(`/api/cv/${cvId}/style`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(cvData.style)
                });

                // (Thêm các fetch request để lưu thay đổi nội dung)

                alert('Đã lưu CV thành công!');
            } catch (error) {
                alert(`Lỗi khi lưu: ${error.message}`);
            } finally {
                saveButton.innerHTML = originalText;
                saveButton.disabled = false;
            }
        });
    }

    // --- BẮT ĐẦU CHẠY ---
    initializeCVBuilder();
});