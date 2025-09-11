// /static/js/cv_editor.js

document.addEventListener('DOMContentLoaded', () => {
    // ---------- Helpers ----------
    const getCvIdFromPath = () => {
        const m = window.location.pathname.match(/\/cv\/(\d+)/);
        return m ? m[1] : null;
    };

    const cvId = getCvIdFromPath();
    if (!cvId) {
        console.error('Không xác định cvId từ URL');
        return;
    }

    const editorContainer = document.querySelector('.cv-editor-container');
    const cvSheet = document.getElementById('cv-sheet');
    const contentFormContainer = document.getElementById('content-form-container');
    const saveStatus = document.getElementById('save-status');
    const downloadPdfButton = document.getElementById('btn-download-pdf');
    const fontFamilySelect = document.getElementById('font-family-select');
    const themeColorInput = document.getElementById('theme-color');
    const saveCvButton = document.getElementById('btn-save-cv');
    const sidebarNav = document.querySelector('.sidebar-main-nav'); // <<< THÊM MỚI
    const sidebarPanels = document.querySelectorAll('.sidebar-panel'); // <<< THÊM MỚI


    let cvData = { experiences: [], educations: [], skills: [] };
    let activeElement = null;
    let debounceTimer = null;

    function updateSaveStatus(text) {
        if (!saveStatus) return;
        saveStatus.className = 'status-indicator';
        const lower = (text || '').toLowerCase();
        if (lower.includes('đang') || lower.includes('saving')) saveStatus.classList.add('saving');
        else if (lower.includes('lỗi') || lower.includes('error')) saveStatus.classList.add('error');
        else saveStatus.classList.add('saved');
        saveStatus.textContent = text;
    }

    function escapeHtml(s) {
        if (s == null) return '';
        return String(s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function pluralSection(type) {
        // type: experience|education|skill
        if (type === 'experience') return 'experiences';
        if (type === 'education') return 'educations';
        return 'skills';
    }

    function endpointForDelete(type, id) {
        // type should be 'experience' | 'education' | 'skill'
        return `/api/${type}/${id}`;
    }

    function endpointForAdd(type) {
        // type: 'experience' | 'education' | 'skills'
        // backend expects POST /api/cv/<cv_id>/experience  OR .../education OR .../skill
        const apiName = (type === 'skills') ? 'skill' : type;
        return `/api/cv/${cvId}/${apiName}`;
    }

    function endpointForReorder(sectionPlural) {
        // sectionPlural: experiences|educations|skills
        return `/api/cv/${cvId}/${sectionPlural}/reorder`;
    }

    // ---------- Render ----------
    function renderCV() {
        const p = cvData.candidate_profile || { user: {} };
        const title = cvData.title || '';

        cvSheet.innerHTML = `
            <header class="cv-section-preview cv-header-preview" data-type="info">
                <h1 data-key="full_name" contenteditable="true">${escapeHtml(p.full_name || '')}</h1>
                <p data-key="title" contenteditable="true">${escapeHtml(title)}</p>
                <div class="contact-info">
                    <span data-key="email"><i class="fas fa-envelope"></i> <span contenteditable="true" data-key="email">${escapeHtml(p.user?.email || '')}</span></span>
                    <span data-key="phone_number"><i class="fas fa-phone"></i> <span contenteditable="true" data-key="phone_number">${escapeHtml(p.phone_number || '')}</span></span>
                </div>
            </header>

            <section class="cv-section-preview" data-type="experience">
                <h2 class="section-title-preview">KINH NGHIỆM</h2>
                <div class="section-action-bar no-print"><button class="btn-add-section-item" title="Thêm kinh nghiệm"><i class="fas fa-plus"></i></button></div>
                <div class="sortable-container"></div>
            </section>

            <section class="cv-section-preview" data-type="education">
                <h2 class="section-title-preview">HỌC VẤN</h2>
                <div class="section-action-bar no-print"><button class="btn-add-section-item" title="Thêm học vấn"><i class="fas fa-plus"></i></button></div>
                <div class="sortable-container"></div>
            </section>

            <section class="cv-section-preview" data-type="skills">
                <h2 class="section-title-preview">KỸ NĂNG</h2>
                <div class="section-action-bar no-print"><button class="btn-add-section-item" title="Thêm kỹ năng"><i class="fas fa-plus"></i></button></div>
                <div class="skills-container"></div>
            </section>
        `;

        renderSectionItems('experience');
        renderSectionItems('education');
        renderSectionItems('skills');

        initSortable(); // attach Sortable after DOM elements created
    }

    function renderSectionItems(type) {
        // type: 'experience' | 'education' | 'skills'
        let container;
        if (type === 'skills') {
            container = cvSheet.querySelector('[data-type="skills"] .skills-container');
            container.innerHTML = (cvData.skills || []).sort((a,b) => (a.order||0)-(b.order||0)).map(s => `
                <div class="skill-tag-item" data-id="${s.id}" data-type="skill">
                    <span class="skill-name" data-key="skill_name" contenteditable="true">${escapeHtml(s.skill_name)}</span>
                    <button class="btn-delete-item no-print" data-type="skill" title="Xóa">×</button>
                </div>
            `).join('');
        } else {
            container = cvSheet.querySelector(`[data-type="${type}"] .sortable-container`);
            const arr = (type === 'experience') ? cvData.experiences : cvData.educations;
            container.innerHTML = (arr || []).sort((a,b) => (a.order||0)-(b.order||0)).map(item => {
                if (type === 'experience') {
                    return `
                    <div class="cv-item-preview" data-id="${item.id}" data-type="experience">
                        <div class="item-action-bar no-print">
                            <button class="handle-sort" title="Kéo thả"><i class="fas fa-grip-vertical"></i></button>
                            <button class="btn-delete-item" data-type="experience" title="Xóa"><i class="fas fa-trash-alt"></i></button>
                        </div>
                        <h3 data-key="job_title" contenteditable="true">${escapeHtml(item.job_title)}</h3>
                        <p class="company-name" data-key="company_name" contenteditable="true">${escapeHtml(item.company_name)}</p>
                        <div class="item-description" data-key="description" contenteditable="true">${escapeHtml(item.description)}</div>
                    </div>
                    `;
                } else {
                    return `
                    <div class="cv-item-preview" data-id="${item.id}" data-type="education">
                        <div class="item-action-bar no-print">
                            <button class="handle-sort" title="Kéo thả"><i class="fas fa-grip-vertical"></i></button>
                            <button class="btn-delete-item" data-type="education" title="Xóa"><i class="fas fa-trash-alt"></i></button>
                        </div>
                        <h3 data-key="institution_name" contenteditable="true">${escapeHtml(item.institution_name)}</h3>
                        <p class="degree-info"><span data-key="degree" contenteditable="true">${escapeHtml(item.degree)}</span> - <span data-key="major" contenteditable="true">${escapeHtml(item.major)}</span></p>
                    </div>
                    `;
                }
            }).join('');
        }
    }
    // THÊM HÀM NÀY VÀO
    function applyStyles() {
        if (cvData.style) {
            if (fontFamilySelect) fontFamilySelect.value = cvData.style.font_family;
            if (themeColorInput) themeColorInput.value = cvData.style.theme_color;

            cvSheet.style.fontFamily = cvData.style.font_family;
            document.documentElement.style.setProperty('--theme-color', cvData.style.theme_color);
        }
        if (cvData.layout) {
            cvSheet.className = 'cv-preview-sheet'; // Reset class về mặc định
            cvSheet.classList.add(`layout-${cvData.layout}`);

            // Đánh dấu lựa chọn layout đang active
            const layoutOptions = document.querySelectorAll('.layout-option');
            layoutOptions.forEach(opt => {
                opt.classList.toggle('active', opt.dataset.layout === cvData.layout);
            });
        }
    }

    // ---------- CRUD actions ----------

    async function addItem(type) {
        // type: 'experience'|'education'|'skills' (DOM uses 'skills' for skills section)
        updateSaveStatus('Đang thêm...');
        const url = endpointForAdd(type);
        try {
            const res = await fetch(url, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({}) });
            if (!res.ok) {
                const err = await res.json().catch(()=>({error: 'Server error'}));
                throw new Error(err.error || 'Tạo mục mới thất bại');
            }
            const newItem = await res.json();
            const arrName = (type === 'skills') ? 'skills' : `${type}s`;
            if (!cvData[arrName]) cvData[arrName] = [];
            cvData[arrName].push(newItem);
            renderSectionItems(type);
            updateSaveStatus('Đã lưu!');
        } catch (err) {
            console.error('Add item error:', err);
            updateSaveStatus('Lỗi!');
            alert('Lỗi khi thêm mục: ' + err.message);
        }
    }

    async function deleteItemById(id, type, elementToRemove) {
        // type: 'experience'|'education'|'skill'
        if (!confirm('Bạn chắc chắn muốn xóa mục này?')) return;
        elementToRemove && (elementToRemove.style.opacity = '0.5');
        const url = endpointForDelete(type, id);
        try {
            const res = await fetch(url, { method: 'DELETE' });
            // Some backends return 204 No Content; still res.ok true
            if (!res.ok) {
                const err = await res.json().catch(()=>({error: 'Server error'}));
                throw new Error(err.error || `Xóa ${type} thất bại`);
            }
            // Remove from local cvData
            const arrName = (type === 'skill') ? 'skills' : `${type}s`;
            if (cvData[arrName]) {
                cvData[arrName] = cvData[arrName].filter(it => String(it.id) !== String(id));
            }
            // Remove DOM element (if provided) or rerender section
            if (elementToRemove) elementToRemove.remove();
            else renderSectionItems(type === 'skill' ? 'skills' : type);
            updateSaveStatus('Đã xóa!');
        } catch (err) {
            console.error('Delete error:', err);
            elementToRemove && (elementToRemove.style.opacity = '1');
            updateSaveStatus('Lỗi!');
            alert('Lỗi khi xóa: ' + err.message);
        }
    }

    async function updateItemInline(type, id, field, value) {
        // type: 'experience'|'education'|'skill'|'info'
        if (type === 'info') {
            // info changes -> autosave full cv api
            const payload = {};
            // If editing title (cvData.title) we send { title }, else send candidate_profile
            if (field === 'title') {
                payload.title = value;
            } else {
                // candidate_profile field
                const cp = cvData.candidate_profile || {};
                cp[field] = value;
                payload.candidate_profile = cp;
            }
            try {
                updateSaveStatus('Đang lưu...');
                const res = await fetch(`/api/cv/${cvId}`, {
                    method: 'PUT',
                    headers: {'Content-Type':'application/json'},
                    body: JSON.stringify(payload)
                });
                if (!res.ok) {
                    const err = await res.json().catch(()=>({error:'Server error'}));
                    throw new Error(err.error || 'Lưu thất bại');
                }
                updateSaveStatus('Đã lưu!');
            } catch (err) {
                console.error('Update info error:', err);
                updateSaveStatus('Lỗi!');
            }
            return;
        }

        const endpoint = (type === 'skill') ? `/api/skill/${id}` : `/api/${type}/${id}`;
        const body = (type === 'skill') ? { skill_name: value } : { [field]: value };
        // Debounce to avoid flooding server on each key, but for contenteditable we use blur -> immediate
        try {
            updateSaveStatus('Đang lưu...');
            const res = await fetch(endpoint, {
                method: 'PUT',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify(body)
            });
            if (!res.ok) {
                const err = await res.json().catch(()=>({error:'Server error'}));
                throw new Error(err.error || 'Lưu thất bại');
            }
            // Reflect change in cvData
            if (type === 'skill') {
                const s = (cvData.skills || []).find(x => String(x.id) === String(id));
                if (s) s.skill_name = value;
            } else {
                const arrName = `${type}s`;
                const it = (cvData[arrName] || []).find(x => String(x.id) === String(id));
                if (it) it[field] = value;
            }
            updateSaveStatus('Đã lưu!');
        } catch (err) {
            console.error('Update item error:', err);
            updateSaveStatus('Lỗi!');
            alert('Lỗi lưu: ' + err.message);
        }
    }

    // ---------- Sortable (drag & drop) ----------
    function initSortable() {
        // init for sortable-container (experience/education items)
        document.querySelectorAll('.sortable-container').forEach(container => {
            if (container._sortableInitialized) return;
            container._sortableInitialized = true;
            new Sortable(container, {
                handle: '.handle-sort',
                animation: 150,
                onEnd: function (evt) {
                    const sectionEl = container.closest('[data-type]');
                    const sectionType = sectionEl ? sectionEl.dataset.type : null; // 'experience' or 'education'
                    const sectionPluralName = pluralSection(sectionType);
                    const ids = Array.from(container.children).map(ch => ch.dataset.id);
                    // update local order
                    const arrName = (sectionType === 'experience') ? 'experiences' : 'educations';
                    if (cvData[arrName]) {
                        cvData[arrName].forEach(item => {
                            item.order = ids.indexOf(String(item.id));
                        });
                    }
                    // call API
                    saveOrder(sectionPluralName, ids);
                }
            });
        });

        // init for skills-container
        document.querySelectorAll('.skills-container').forEach(container => {
            if (container._sortableInitialized) return;
            container._sortableInitialized = true;
            new Sortable(container, {
                animation: 150,
                onEnd: function () {
                    const ids = Array.from(container.children).map(ch => ch.dataset.id);
                    if (cvData.skills) cvData.skills.forEach(s => s.order = ids.indexOf(String(s.id)));
                    saveOrder('skills', ids);
                }
            });
        });
    }

    async function saveOrder(sectionPluralName, ids) {
        updateSaveStatus('Đang lưu thứ tự...');
        try {
            const res = await fetch(endpointForReorder(sectionPluralName), {
                method: 'PUT',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify({ ids })
            });
            if (!res.ok) {
                const err = await res.json().catch(()=>({error:'Server error'}));
                throw new Error(err.error || 'Lưu thứ tự thất bại');
            }
            updateSaveStatus('Đã lưu!');
        } catch (err) {
            console.error('Save order error:', err);
            updateSaveStatus('Lỗi!');
            alert('Lỗi khi lưu thứ tự: ' + err.message);
        }
    }

    // ---------- Event delegation ----------
    editorContainer.addEventListener('click', (e) => {
        const delBtn = e.target.closest('.btn-delete-item');
        if (delBtn) {
            // prefer dataset.type on button, otherwise use parent element's data-type
            const type = delBtn.dataset.type || delBtn.closest('[data-type]')?.dataset.type || delBtn.closest('[data-id]')?.dataset.type;
            const itemEl = delBtn.closest('[data-id]');
            const id = itemEl ? itemEl.dataset.id : null;
            if (!id || !type) {
                console.error('Không xác định id/type khi xóa', { id, type });
                return;
            }
            // normalize 'skills' => 'skill'
            const apiType = (type === 'skills') ? 'skill' : type;
            deleteItemById(id, apiType, itemEl);
            return;
        }

        const addBtn = e.target.closest('.btn-add-section-item');
        if (addBtn) {
            const section = addBtn.closest('[data-type]');
            const type = section ? section.dataset.type : null; // 'experience'|'education'|'skills'
            if (!type) return;
            addItem(type);
            return;
        }

        // clicking on preview item => mark active and show sidebar form
        const editable = e.target.closest('.cv-item-preview, .skill-tag-item, .cv-header-preview');
        if (editable) {
            if (activeElement && activeElement !== editable) activeElement.classList.remove('active');
            activeElement = editable;
            activeElement.classList.add('active');
            renderContentFormForActive();
            // ensure content panel visible
            document.querySelectorAll('.sidebar-panel').forEach(p => p.classList.remove('active'));
            document.getElementById('content-panel')?.classList.add('active');
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.toggle('active', t.dataset.panel === 'content-panel'));
            return;
        }
    });

    // input/blur handlers for contenteditable & sidebar inputs
    editorContainer.addEventListener('blur', (e) => {
        const ce = e.target.closest('[contenteditable="true"]');
        if (!ce) return;
        // determine which parent item contains this contenteditable
        const parent = ce.closest('[data-id], .cv-header-preview');
        if (!parent) return;
        const type = parent.dataset.type || (parent.classList.contains('cv-header-preview') ? 'info' : null);
        const id = parent.dataset.id;
        const field = ce.dataset.key;
        const value = ce.textContent.trim();
        if (!field) return;
        updateItemInline(type, id, field, value);
    }, true);

    // also watch input events inside sidebar forms (for quick auto-save)
    editorContainer.addEventListener('input', (e) => {
        const inputEl = e.target;
        const form = inputEl.closest('form[data-type]');
        if (!form) return;
        const type = form.dataset.type; // info | experience | education
        const id = form.dataset.id;
        const field = inputEl.name;
        const value = inputEl.value;
        // small debounce per field
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            if (type === 'info') {
                // update local
                if (!cvData.candidate_profile) cvData.candidate_profile = {};
                if (field === 'title') cvData.title = value; else cvData.candidate_profile[field] = value;
                updateItemInline('info', null, field, value);
            } else {
                // update specific item
                const arrName = `${type}s`;
                const item = (cvData[arrName] || []).find(it => String(it.id) === String(id));
                if (item) item[field] = value;
                updateItemInline(type, id, field, value);
            }
        }, 600);
    });

    // new-skill-input Enter handled at capture keydown to prevent form submit
    editorContainer.addEventListener('keydown', (e) => {
        const el = e.target;
        if (el && el.id === 'new-skill-input' && e.key === 'Enter') {
            e.preventDefault();
            // reuse add skill endpoint to create new with name
            const name = el.value.trim();
            if (!name) return;
            (async () => {
                try {
                    const res = await fetch(`/api/cv/${cvId}/skill`, {
                        method: 'POST',
                        headers: {'Content-Type':'application/json'},
                        body: JSON.stringify({ skill_name: name })
                    });
                    if (!res.ok) {
                        const err = await res.json().catch(()=>({error:'Server error'}));
                        throw new Error(err.error || 'Không thể thêm kỹ năng');
                    }
                    const newSkill = await res.json();
                    cvData.skills = cvData.skills || [];
                    cvData.skills.push(newSkill);
                    renderSectionItems('skills');
                    renderContentFormForActive();
                    el.value = '';
                    updateSaveStatus('Đã lưu!');
                } catch (err) {
                    console.error('Add skill error:', err);
                    alert('Lỗi thêm skill: ' + err.message);
                    updateSaveStatus('Lỗi!');
                }
            })();
        }
    });

    // ---------- Sidebar content rendering ----------
    function renderContentFormForActive() {
        if (!activeElement) {
            contentFormContainer.innerHTML = '<p class="panel-guide">Chọn một mục trên CV để chỉnh sửa.</p>';
            return;
        }
        const type = activeElement.dataset.type || (activeElement.classList.contains('cv-header-preview') ? 'info' : null);
        const id = activeElement.dataset.id;
        if (type === 'info') {
            const p = cvData.candidate_profile || { user: {} };
            contentFormContainer.innerHTML = `
                <h4>Thông tin cá nhân</h4>
                <form data-type="info">
                    <div class="form-group"><label>Họ & tên</label><input name="full_name" class="form-control" value="${escapeHtml(p.full_name||'')}"/></div>
                    <div class="form-group"><label>Vị trí</label><input name="title" class="form-control" value="${escapeHtml(cvData.title||'')}"/></div>
                    <div class="form-group"><label>Email</label><input name="email" class="form-control" value="${escapeHtml(p.user?.email||'')}"/></div>
                    <div class="form-group"><label>SĐT</label><input name="phone_number" maxlength="15" pattern="[0-9+\\- ]*" class="form-control" name="phone_number" value="${escapeHtml(p.phone_number||'')}"/></div>
                </form>
            `;
            return;
        }

        if (type === 'skill') {
            // show skills editor (input + tags)
            contentFormContainer.innerHTML = `
                <div id="skills-list-form">
                    <h4>Chỉnh sửa Kỹ năng</h4>
                    <p>Nhập kỹ năng và nhấn Enter:</p>
                    <div class="form-group"><input type="text" id="new-skill-input" class="form-control" placeholder="Ví dụ: Python"></div>
                    <div class="skills-tag-container">
                        ${(cvData.skills || []).map(s => `<div class="skill-tag-item" data-id="${s.id}"><span class="skill-name" data-key="skill_name" contenteditable="true">${escapeHtml(s.skill_name)}</span><button class="btn-delete-item no-print" data-type="skill" title="Xóa">×</button></div>`).join('')}
                    </div>
                </div>
            `;
            return;
        }

        if (type === 'experience' || type === 'education') {
            const arrName = (type === 'experience') ? 'experiences' : 'educations';
            const item = (cvData[arrName] || []).find(i => String(i.id) === String(id)) || {};
            if (type === 'experience') {
                contentFormContainer.innerHTML = `
                    <h4>Chỉnh sửa Kinh nghiệm</h4>
                    <form data-type="experience" data-id="${item.id}">
                        <div class="form-group"><label>Chức danh</label><input name="job_title" class="form-control" value="${escapeHtml(item.job_title||'')}"></div>
                        <div class="form-group"><label>Công ty</label><input name="company_name" class="form-control" value="${escapeHtml(item.company_name||'')}"></div>
                        <div class="form-group"><label>Mô tả</label><textarea name="description" class="form-control" rows="4">${escapeHtml(item.description||'')}</textarea></div>
                    </form>
                `;
            } else {
                contentFormContainer.innerHTML = `
                    <h4>Chỉnh sửa Học vấn</h4>
                    <form data-type="education" data-id="${item.id}">
                        <div class="form-group"><label>Trường</label><input name="institution_name" class="form-control" value="${escapeHtml(item.institution_name||'')}"></div>
                        <div class="form-group"><label>Bằng cấp</label><input name="degree" class="form-control" value="${escapeHtml(item.degree||'')}"></div>
                        <div class="form-group"><label>Chuyên ngành</label><input name="major" class="form-control" value="${escapeHtml(item.major||'')}"></div>
                    </form>
                `;
            }
            return;
        }

        contentFormContainer.innerHTML = '<p class="panel-guide">Chọn một mục trên CV để chỉnh sửa.</p>';
    }

    // ---------- PDF / Style / Layout handlers ----------
    function handleDownloadPdf() {
        if (!cvSheet) return;

        // Tạm thời ẩn các phần tử không cần in
        const noPrintElements = document.querySelectorAll('.no-print');
        noPrintElements.forEach(el => el.style.display = 'none');

        // Tạo filename từ tên ứng viên
        const filename = `${cvData.candidate_profile?.full_name || 'CV'}_${new Date().toISOString().slice(0,10)}.pdf`;

        const opt = {
            margin: 0,
            filename,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: {
                scale: 2,
                useCORS: true,
                letterRendering: true,
                allowTaint: true
            },
            jsPDF: {
                unit: 'mm',
                format: 'a4',
                orientation: 'portrait',
                hotfixes: ["px_scaling"] // Fix lỗi kích thước trên một số trình duyệt
            },
            pagebreak: {
                mode: ['avoid-all', 'css'] // Ưu tiên không ngắt trang
            }
        };

        // Thêm lớp tạm thời để tối ưu in ấn
        cvSheet.classList.add('printing');

        html2pdf()
            .set(opt)
            .from(cvSheet)
            .toPdf()
            .get('pdf')
            .then((pdf) => {
                // Tùy chỉnh thêm cho PDF (nếu cần)
                const totalPages = pdf.internal.getNumberOfPages();
                for (let i = 1; i <= totalPages; i++) {
                    pdf.setPage(i);
                    pdf.setFontSize(10);
                    pdf.setTextColor(150);
                    pdf.text(
                        `Trang ${i} của ${totalPages}`,
                        pdf.internal.pageSize.getWidth() - 20,
                        pdf.internal.pageSize.getHeight() - 10
                    );
                }
            })
            .save()
            .then(() => {
                // Khôi phục trạng thái ban đầu
                cvSheet.classList.remove('printing');
                noPrintElements.forEach(el => el.style.display = '');
            })
            .catch(err => {
                console.error('PDF generation error:', err);
                alert('Lỗi khi tạo PDF: ' + err.message);
            });
    }

    if (downloadPdfButton) downloadPdfButton.addEventListener('click', handleDownloadPdf);
    if (fontFamilySelect) fontFamilySelect.addEventListener('change', () => {
        cvData.style = cvData.style || {};
        cvData.style.font_family = fontFamilySelect.value;
        fetch(`/api/cv/${cvId}/style`, { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ font_family: fontFamilySelect.value, theme_color: cvData.style.theme_color || '' })});
    });
    if (themeColorInput) themeColorInput.addEventListener('input', () => {
        cvData.style = cvData.style || {};
        cvData.style.theme_color = themeColorInput.value;
        fetch(`/api/cv/${cvId}/style`, { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ font_family: cvData.style.font_family || '', theme_color: themeColorInput.value })});
    });


    async function loadCvData() {
        updateSaveStatus('Đang tải dữ liệu...');
        try {
            const res = await fetch(`/api/cv/${cvId}`);
            if (!res.ok) {
                const err = await res.json().catch(()=>({error:'Server error'}));
                throw new Error(err.error || 'Tải CV thất bại');
            }
            cvData = await res.json();
            // ensure arrays exist
            cvData.experiences = cvData.experiences || [];
            cvData.educations = cvData.educations || [];
            cvData.skills = cvData.skills || [];
            renderCV();
            applyStyles(); // Áp dụng style và layout ban đầu

            updateSaveStatus('Đã tải');
        } catch (err) {
            console.error('Load CV error:', err);
            cvSheet.innerHTML = `<p class="text-danger">Lỗi: ${escapeHtml(err.message)}</p>`;
            updateSaveStatus('Lỗi tải dữ liệu');
        }
    }
    // ---- Logic xử lý Style ----
    function handleStyleChange() {
        if (!cvData.style) cvData.style = {};
        // 1. Cập nhật dữ liệu local từ các ô input
        cvData.style.font_family = fontFamilySelect.value;
        cvData.style.theme_color = themeColorInput.value;

        // 2. Cập nhật giao diện ngay lập tức
        applyStyles();

        // 3. Gọi API để lưu (có debounce để tránh gọi liên tục)
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            updateSaveStatus('Đang lưu...');
            fetch(`/api/cv/${cvId}/style`, {
                method: 'PUT',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify(cvData.style)
            }).then(res => {
                if (res.ok) updateSaveStatus('Đã lưu!');
                else updateSaveStatus('Lỗi!');
            });
        }, 600);
    }

    function handleLayoutChange(newLayout) {
        // 1. Cập nhật dữ liệu local
        cvData.layout = newLayout;
        // 2. Cập nhật giao diện
        applyStyles();
        // 3. Gọi API để lưu
        updateSaveStatus('Đang lưu...');
        fetch(`/api/cv/${cvId}/layout`, {
            method: 'PUT',
            headers: {'Content-Type':'application/json'},
            // Gửi cả style và layout để gộp chung API
            handleLayoutChange
        }).then(res => {
            if (res.ok) updateSaveStatus('Đã lưu!');
            else updateSaveStatus('Lỗi!');
        });
    }
    function init() {
        if (sidebarNav) {
            sidebarNav.addEventListener('click', (e) => {
                const tab = e.target.closest('.nav-tab');
                if (!tab) return;

                // Lấy tên panel từ data attribute
                const panelName = tab.dataset.panel;
                if (!panelName) return;

                // Xóa active class khỏi tất cả các tab
                sidebarNav.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
                // Thêm active class cho tab được click
                tab.classList.add('active');

                // Xóa active class khỏi tất cả các panel
                sidebarPanels.forEach(p => p.classList.remove('active'));
                // Thêm active class cho panel tương ứng
                const panelToShow = document.getElementById(panelName);
                if (panelToShow) {
                    panelToShow.classList.add('active');
                }
            });
        }
        if (downloadPdfButton) {
            downloadPdfButton.addEventListener('click', handleDownloadPdf);
        }
        if (fontFamilySelect) {
            fontFamilySelect.addEventListener('change', handleStyleChange);
        }
        if (themeColorInput) {
            themeColorInput.addEventListener('input', handleStyleChange);
        }
        document.querySelectorAll('.layout-option').forEach(option => {
            option.addEventListener('click', () => {
                handleLayoutChange(option.dataset.layout);
            });
        });

        // Tải dữ liệu CV
        loadCvData();
    }
    init();
    // Start
    loadCvData();
});
