:root { --builder-sidebar-width: 260px; --builder-form-panel-width: 40%; }
.cv-builder-workspace { display: grid; grid-template-columns: var(--builder-sidebar-width) 1fr 1.2fr; height: calc(100vh - var(--builder-header-height)); background-color: #e5e7eb; gap: 1px; border-top: 1px solid var(--border-color); }
.builder-sidebar, .builder-form-panel, .builder-preview-panel { background-color: #ffffff; display: flex; flex-direction: column; overflow-y: auto; height: 100%; }
.builder-sidebar { border-right: 1px solid var(--border-color); }
.sidebar-header { padding: 20px; border-bottom: 1px solid var(--border-color); flex-shrink: 0; }
.sidebar-header a { font-weight: 500; }
.sidebar-nav { flex-grow: 1; padding: 10px; }
.sidebar-nav .nav-item { display: flex; align-items: center; gap: 15px; padding: 13px 15px; border-radius: 8px; cursor: pointer; transition: all 0.2s; color: var(--subtle-text-color); font-weight: 500; }
.sidebar-nav .nav-item:hover { background-color: #f3f4f6; color: var(--text-color); }
.sidebar-nav .nav-item.active { background-color: var(--primary-color); color: white; }
.sidebar-nav .nav-item i { width: 20px; text-align: center; font-size: 1.1em; }
.sidebar-footer { padding: 20px; border-top: 1px solid var(--border-color); flex-shrink: 0; }
.sidebar-footer .btn { width: 100%; justify-content: center; }
.form-panel-header { padding: 22px 25px; border-bottom: 1px solid var(--border-color); flex-shrink: 0; }
.form-panel-header h3 { margin: 0; font-size: 1.5rem; }
.form-panel-body { padding: 25px; flex-grow: 1; }
.form-section-item { background: #ffffff; padding: 20px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #e5e7eb; transition: box-shadow 0.2s; }
.item-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid var(--border-color); cursor: grab; }
.item-header h5 { margin: 0; font-size: 1.1rem; }
.item-controls button { background: none; border: none; color: var(--subtle-text-color); cursor: pointer; font-size: 1rem; padding: 5px; }
.btn-add-item { width: 100%; padding: 12px; border: 2px dashed #d1d5db; background: #f9fafb; cursor: pointer; transition: all 0.2s; color: var(--subtle-text-color); font-weight: 500; }
.btn-add-item:hover { background: #e5e7eb; color: var(--text-color); border-color: #9ca3af; }
.builder-preview-panel { background-color: #f3f4f6; }
.preview-panel-header { background: white; padding: 15px 25px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); flex-shrink: 0; }
#save-status { font-style: italic; color: var(--subtle-text-color); transition: color 0.3s; font-size: 0.9rem; }
#save-status.saving { color: #f59e0b; }
#save-status.saved { color: #48BB78; }
.preview-sheet-wrapper { padding: 30px; display: flex; justify-content: center; width: 100%; box-sizing: border-box; }
.cv-preview-sheet { width: 210mm; min-height: 297mm; transform-origin: top center; transform: scale(0.65); background: white; box-shadow: 0 5px 25px rgba(0,0,0,0.15); padding: 20mm; transition: transform 0.3s; margin-bottom: calc(-297mm * (1 - 0.65) + 30px); }
.design-panel { position: fixed; top: var(--builder-header-height); right: -320px; width: 300px; background: white; height: calc(100vh - var(--builder-header-height)); box-shadow: var(--shadow); border-left: 1px solid var(--border-color); transition: right 0.4s cubic-bezier(0.25, 0.8, 0.25, 1); z-index: 1001; padding: 20px; }
.design-panel.active { right: 0; }
.skills-tag-container { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 15px; }
.skill-tag-item { display: flex; align-items: center; background-color: var(--primary-color); color: white; border-radius: 15px; padding: 5px 5px 5px 12px; font-size: 0.9rem; }
.skill-name { outline: 0; min-width: 30px; }
.skill-tag-item .btn-delete-item { background: rgba(0,0,0,0.2); color: white; border-radius: 50%; width: 20px; height: 20px; margin-left: 8px; display: flex; align-items: center; justify-content: center; line-height: 1; font-weight: bold; }
[contenteditable="true"]:hover { background-color: #f0f8ff; outline: 1px dashed var(--primary-color); }
[contenteditable="true"]:focus { background-color: #e6f7ff; outline: 2px solid var(--primary-color); }
.cv-header-preview { text-align: center; border-bottom: 2px solid #f0f0f0; padding-bottom: 20px; margin-bottom: 30px; }
.cv-header-preview h1 { margin: 0; font-size: 2.5rem; color: #111; }
.cv-subtitle-preview { font-size: 1.2rem; color: var(--cv-theme-color, #555); margin-top: 5px; }
.contact-info { margin-top: 15px; display: flex; flex-wrap: wrap; justify-content: center; gap: 10px 20px; font-size: 0.9rem; color: #444; }
.contact-info span { display: flex; align-items: center; gap: 8px; }
.contact-info i { color: var(--cv-theme-color, var(--primary-color)); }
.cv-section-preview { margin-bottom: 30px; }
.section-title-preview { font-size: 1.1rem; color: var(--cv-theme-color, var(--primary-color)); border-bottom: 2px solid var(--cv-theme-color, var(--primary-color)); padding-bottom: 8px; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 1px; }
.cv-item-preview { margin-bottom: 20px; }
.item-title { font-size: 1.1rem; font-weight: 700; color: #222; margin: 0; }
.item-subtitle { font-size: 1rem; font-weight: 500; color: #444; margin: 0 0 8px 0; }
.item-description { color: #555; padding-left: 15px; border-left: 2px solid #eee; }
.skills-list { display: flex; flex-wrap: wrap; gap: 10px; }
.skill-tag { background-color: #eef2f5; color: #374151; padding: 5px 12px; border-radius: 15px; font-size: 0.9rem; }