// /static/js/cv_editor.js
document.addEventListener('DOMContentLoaded', () => {
    // --- 1. KHỞI TẠO ---
    const cvId = window.location.pathname.split('/')[2];
    const cvSheet = document.getElementById('cv-sheet');
    const formContent = document.getElementById('form-content');
    const panelTitle = document.getElementById('form-panel-title');
    const navTabs = document.querySelectorAll('.nav-tab');
    const sidebarPanels = document.querySelectorAll('.sidebar-panel');
    const saveStatus = document.getElementById('save-status');
    const designPanel = document.getElementById('design-panel');
    const designButton = document.getElementById('btn-design');
    const downloadPdfButton = document.getElementById('btn-download-pdf');

    let cvData = {};
    let activeElement = null;
    let activeSection = null; // Đã thêm khai báo
    let debounceTimer;
    let isDataLoaded = false;

    // --- 2. TEMPLATES ---
    const formTemplates = {
        default: '<h4>Chọn một mục trên CV để chỉnh sửa</h4><p>Hoặc thêm mục mới từ các nút bấm trên CV.</p>',
        info: p => `<form data-type="info"><div class="form-group"><label>Họ và tên</label><input name="full_name" class="form-control" value="${p.full_name||''}"></div><div class="form-group"><label>Vị trí ứng tuyển</label><input name="title" class="form-control" value="${cvData.title||''}"></div><div class="form-group"><label>Email</label><input class="form-control" value="${p.email||''}" disabled></div><div class="form-group"><label>SĐT</label><input name="phone_number" class="form-control" value="${p.phone_number||''}"></div></form>`,
        experience: item => `<h4>Chỉnh sửa Kinh nghiệm</h4><form data-type="experience" data-id="${item.id}"><div class="form-group"><label>Chức danh</label><input name="job_title" class="form-control" value="${item.job_title||''}"></div><div class="form-group"><label>Công ty</label><input name="company_name" class="form-control" value="${item.company_name||''}"></div><div class="form-group"><label>Mô tả</label><textarea name="description" class="form-control" rows="5">${item.description||''}</textarea></div></form>`,
        education: item => `<h4>Chỉnh sửa Học vấn</h4><form data-type="education" data-id="${item.id}"><div class="form-group"><label>Trường</label><input name="institution_name" class="form-control" value="${item.institution_name||''}"></div><div class="form-group"><label>Bằng cấp</label><input name="degree" class="form-control" value="${item.degree||''}"></div><div class="form-group"><label>Chuyên ngành</label><input name="major" class="form-control" value="${item.major||''}"></div></form>`,
        skills: () => `<div id="skills-list-form"><p>Nhập kỹ năng và nhấn Enter:</p><div class="form-group"><input type="text" id="new-skill-input" class="form-control" placeholder="Ví dụ: Python"></div><div class="skills-tag-container">${(cvData.skills||[]).map(s=>`<div class="skill-tag-item" data-id="${s.id}"><span class="skill-name" contenteditable="true">${s.skill_name}</span><button class="btn-delete-item" data-type="skill">&times;</button></div>`).join('')}</div></div>`,
    };

    // --- 3. CÁC HÀM XỬ LÝ ---
    const handleReorder = e => {
        const container = e.target;
        const type = container.closest('.cv-section-preview').dataset.type;
        const ids = Array.from(container.children).map(i => i.dataset.id);
        const data = cvData[type + 's'];
        if (data) {
            data.sort((a, b) => ids.indexOf(String(a.id)) - ids.indexOf(String(b.id)));
            data.forEach((item, idx) => item.order = idx);
            saveOrder(type + 's', ids);
        }
    };

    const handleNavClick = e => {
        e.preventDefault();
        const item = e.currentTarget;
        navTabs.forEach(n => n.classList.remove('active'));
        item.classList.add('active');
        switchTab(item.dataset.panel);
    };

    const handleLiveUpdate = e => {
        const input = e.target;
        const itemEl = input.closest('[data-id]');
        const field = input.name;

        if (itemEl) {
            const id = itemEl.dataset.id;
            const type = input.closest('form').dataset.type;
            const item = cvData[type + 's']?.find(i => i.id == id);
            if (item) {
                item[field] = input.value;
                if (field === 'job_title' || field === 'institution_name') {
                    itemEl.querySelector('h5').textContent = input.value;
                }
            }
        } else {
            const form = input.closest('form');
            if (form?.dataset.type === 'info') {
                if (!cvData.candidate_profile) return;
                if (field === 'title') {
                    cvData.title = input.value;
                } else {
                    cvData.candidate_profile[field] = input.value;
                }
            }
        }
        renderCV(); // Thay thế renderPreview bằng renderCV
        autoSave();
    };

    const handleDynamicClick = async e => {
        const btn = e.target.closest('button');
        if (!btn) return;

        if (btn.classList.contains('btn-add-item')) {
            const type = btn.dataset.type;
            const res = await fetch(`/api/cv/${cvId}/${type}`, {method: 'POST'});
            if (res.ok) {
                const newItem = await res.json();
                cvData[type + 's'].push(newItem);
                renderForm(type);
                renderCV();
            }
        }

        if (btn.classList.contains('btn-delete-item')) {
            const itemEl = btn.closest('[data-id]');
            const id = itemEl.dataset.id;
            const type = btn.dataset.type;
            if (confirm('Bạn chắc chắn muốn xóa?')) {
                itemEl.style.opacity = '0.5';
                const res = await fetch(`/api/${type}/${id}`, {method: 'DELETE'});
                if (res.ok) {
                    cvData[type + 's'] = cvData[type + 's'].filter(i => i.id != id);
                    renderForm(type);
                    renderCV();
                }
            }
        }
    };

    const handleSkillEvents = async e => {
        const target = e.target;
        if (target.id === 'new-skill-input' && e.type === 'keydown' && e.key === 'Enter') {
            e.preventDefault();
            const name = target.value.trim();
            if (name) {
                const res = await fetch(`/api/cv/${cvId}/skill`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({skill_name: name})
                });
                if (res.ok) {
                    const newSkill = await res.json();
                    cvData.skills.push(newSkill);
                    renderForm('skills');
                    renderCV();
                }
            }
        }

        if (target.classList.contains('skill-name') && e.type === 'blur') {
            const itemEl = target.closest('[data-id]');
            const id = itemEl.dataset.id;
            const newName = target.textContent.trim();
            const skill = cvData.skills.find(s => s.id == id);
            if (skill && skill.skill_name !== newName) {
                skill.skill_name = newName;
                renderCV();
                autoSave();
            }
        }
    };

    const handleDesignPanel = () => {
        designPanel.classList.toggle('active');
    };

    const handleStyleChange = () => {
        cvData.style = cvData.style || {};
        cvData.style.font_family = document.getElementById('font-family-select').value;
        cvData.style.theme_color = document.getElementById('theme-color').value;
        renderCV();
        autoSave(null, 'style');
    };

    const handleDownloadPdf = () => {
        if (!cvSheet) return;

        const element = cvSheet;
        const originalScale = element.style.transform;
        element.style.transform = 'scale(1)';

        const opt = {
            margin: 0,
            filename: `${cvData.candidate_profile?.full_name || 'CV'}_CV.pdf`,
            image: {type: 'jpeg', quality: 0.98},
            html2canvas: {scale: 2, useCORS: true},
            jsPDF: {unit: 'mm', format: 'a4', orientation: 'portrait'}
        };

        html2pdf().from(element).set(opt).save().then(() => {
            element.style.transform = originalScale;
        });
    };

    // --- 4. CÁC HÀM RENDER ---
    function renderCV() {
        const { candidate_profile: p = {}, title, experiences = [], educations = [], skills = [] } = cvData;

        cvSheet.innerHTML = `
        <header class="cv-section-preview" data-type="info">
            <h1 data-key="candidate_profile.full_name" contenteditable="true">${p.full_name || ''}</h1>
            <p data-key="title" contenteditable="true">${title || ''}</p>
            <div class="contact-info">
                <span><i class="fas fa-envelope"></i> ${p.email || ''}</span>
                <span><i class="fas fa-phone"></i> ${p.phone_number || ''}</span>
            </div>
        </header>
        <section class="cv-section-preview" data-type="experience">
            <h2 class="section-title-preview">KINH NGHIỆM</h2>
            <div class="section-action-bar"><button class="btn-add-section-item" title="Thêm kinh nghiệm"><i class="fas fa-plus"></i></button></div>
            <div class="sortable-container">${experiences.map(e => `
                <div class="cv-item-preview" data-id="${e.id}" data-type="experience">
                    <div class="item-action-bar">
                        <button class="handle-sort"><i class="fas fa-grip-vertical"></i></button>
                        <button class="btn-delete-item"><i class="fas fa-trash-alt"></i></button>
                    </div>
                    <h3 data-key="job_title" contenteditable="true">${e.job_title || ''}</h3>
                    <p class="company-name">${e.company_name || ''}</p>
                    <div class="item-description" data-key="description" contenteditable="true">${e.description || ''}</div>
                </div>`).join('')}
            </div>
        </section>
        <section class="cv-section-preview" data-type="education">
            <h2 class="section-title-preview">HỌC VẤN</h2>
            <div class="section-action-bar"><button class="btn-add-section-item" title="Thêm học vấn"><i class="fas fa-plus"></i></button></div>
            <div class="sortable-container">${educations.map(e => `
                <div class="cv-item-preview" data-id="${e.id}" data-type="education">
                    <div class="item-action-bar">
                        <button class="handle-sort"><i class="fas fa-grip-vertical"></i></button>
                        <button class="btn-delete-item"><i class="fas fa-trash-alt"></i></button>
                    </div>
                    <h3 data-key="institution_name" contenteditable="true">${e.institution_name || ''}</h3>
                    <p class="degree-info">${e.degree || ''} - ${e.major || ''}</p>
                </div>`).join('')}
            </div>
        </section>
        <section class="cv-section-preview" data-type="skills">
            <h2 class="section-title-preview">KỸ NĂNG</h2>
            <div class="section-action-bar"><button class="btn-add-section-item" title="Thêm kỹ năng"><i class="fas fa-plus"></i></button></div>
            <div class="skills-container">
                ${skills.map(s => `<span class="skill-tag" data-id="${s.id}">${s.skill_name || ''}</span>`).join('')}
            </div>
        </section>`;

        initSortable();
    }

    function renderContentForm() {
        if (!activeSection) {
            contentFormContainer.innerHTML = formTemplates.default;
            return;
        }

        const type = activeSection.dataset.type;
        const id = activeSection.dataset.id;
        let itemData = {};

        if (type === 'info') {
            itemData = cvData.candidate_profile || {};
            itemData.title = cvData.title || '';
        } else {
            const items = cvData[type + 's'] || [];
            itemData = items.find(i => i.id == id) || {};
        }

        if (formTemplates[type]) {
            contentFormContainer.innerHTML = formTemplates[type](itemData);
        }
    }

    function renderForm(type) {
        if (activeSection && activeSection.dataset.type === type) {
            renderContentForm();
        }
    }

    // --- 5. HÀM XỬ LÝ SỰ KIỆN ---
    const initSortable = () => {
        document.querySelectorAll('.sortable-container').forEach(el => {
            new Sortable(el, {
                handle: '.handle-sort',
                animation: 150,
                onEnd: handleReorder
            });
        });
    };

    const switchTab = panelId => {
        sidebarPanels.forEach(p => p.classList.remove('active'));
        document.getElementById(panelId)?.classList.add('active');
        navTabs.forEach(t => t.classList.toggle('active', t.dataset.panel === panelId));
    };

    function handleCVInteraction(e) {
        const target = e.target;

        // Xử lý click vào một mục để hiện form
        const item = target.closest('.cv-item-preview, .cv-header-preview');
        if (item) {
            if (activeElement) activeElement.classList.remove('active');
            activeElement = item;
            activeElement.classList.add('active');
            activeSection = item;
            switchTab('content-panel');
            renderContentForm();
        }

        // Xử lý nút Thêm
        const addBtn = target.closest('.btn-add-section-item');
        if (addBtn) {
            const type = addBtn.closest('.cv-section-preview').dataset.type;
            fetch(`/api/cv/${cvId}/${type}`, {method: 'POST'})
                .then(r => r.json())
                .then(newItem => {
                    cvData[type + 's'] = cvData[type + 's'] || [];
                    cvData[type + 's'].push(newItem);
                    renderCV();
                });
        }
    };

    // --- 6. LƯU TRỮ & KHỞI ĐỘNG ---
    const updateSaveStatus = text => {
        saveStatus.className = text.includes('Đang') ? 'saving' : 'saved';
        saveStatus.textContent = text;
    };

    const autoSave = () => {
        clearTimeout(debounceTimer);
        updateSaveStatus('Đang thay đổi...');
        debounceTimer = setTimeout(async () => {
            updateSaveStatus('Đang lưu...');
            await fetch(`/api/cv/${cvId}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(cvData)
            });
            updateSaveStatus('Đã lưu!');
        }, 2000);
    };

    const saveOrder = async (type, ids) => {
        updateSaveStatus('Đang lưu thứ tự...');
        await fetch(`/api/cv/${cvId}/${type}/reorder`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ids: ids})
        });
        updateSaveStatus('Đã lưu!');
    };

    function initEventListeners() {
        navTabs.forEach(item => item.addEventListener('click', handleNavClick));
        contentFormContainer.addEventListener('input', handleLiveUpdate);
        contentFormContainer.addEventListener('click', handleDynamicClick);
        contentFormContainer.addEventListener('keydown', handleSkillEvents);
        contentFormContainer.addEventListener('blur', handleSkillEvents, true);
        designButton.addEventListener('click', handleDesignPanel);
        designPanel.addEventListener('change', handleStyleChange);
        designPanel.addEventListener('input', handleStyleChange);
        downloadPdfButton.addEventListener('click', handleDownloadPdf);
        cvSheet.addEventListener('click', handleCVInteraction);
        cvSheet.addEventListener('input', handleLiveUpdate);
    }

    async function init() {
            // --- BẮT ĐẦU DEBUG CHI TIẾT ---
        console.log("Initializing CV Editor...");

        const elements = {
            cvSheet: document.getElementById('cv-sheet'),
            contentFormContainer: document.getElementById('form-content'), // <-- Sửa lại cho đúng
            saveStatus: document.getElementById('save-status'),
            panelTitle: document.getElementById('form-panel-title'),
            designPanel: document.getElementById('design-panel'),
            designButton: document.getElementById('btn-design'),
            downloadPdfButton: document.getElementById('btn-download-pdf')
        };

        let missingElement = null;
        for (const key in elements) {
            if (!elements[key]) {
                missingElement = key;
                break;
            }
        }

        if (missingElement) {
            const errorMessage = `Lỗi khởi tạo: Không tìm thấy phần tử DOM quan trọng với ID: '${missingElement}'. Hãy kiểm tra lại file cv_edit.html.`;
            console.error(errorMessage);
            if (elements.cvSheet) {
                elements.cvSheet.innerHTML = `<p class="text-danger">${errorMessage}</p>`;
            }
            return; // Dừng thực thi
        }

        console.log("All essential DOM elements found.");
        // --- KẾT THÚC DEBUG CHI TIẾT ---

        if (!cvId) {
            elements.cvSheet.innerHTML = '<p class="text-danger">Lỗi: Không tìm thấy ID của CV.</p>';
            return;
        }
        try {
            const res = await fetch(`/api/cv/${cvId}`);
            if (!res.ok) throw new Error('Tải CV thất bại');
            cvData = await res.json();
            isDataLoaded = true;
            if(cvData.experiences) cvData.experiences.sort((a,b)=>a.order-b.order);
            if(cvData.educations) cvData.educations.sort((a,b)=>a.order-b.order);

            renderCV();
            renderContentForm('info');
            initEventListeners();

            // Cập nhật giá trị ban đầu cho panel thiết kế
            if (cvData.style) {
                document.getElementById('font-family-select').value = cvData.style.font_family;
                document.getElementById('theme-color').value = cvData.style.theme_color;
            }
        } catch (error) {
            console.error('Lỗi trong quá trình init:', error);
            if(elements.cvSheet) elements.cvSheet.innerHTML = `<p class="text-danger">${error.message}</p>`;
        }
    }

    init();
});
