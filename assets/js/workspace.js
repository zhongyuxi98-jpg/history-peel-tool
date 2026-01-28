        const ID = MISSION_CONFIG.id;
        
        // API 配置：根据环境自动判断 API 地址
        const API_BASE_URL = window.location.hostname === 'localhost' && window.location.port === '8000' 
            ? 'http://localhost:5501' 
            : '';

        // --- 0. 全局状态 ---
        let currentLanguageMode = document.getElementById('language-setting').value || 'dual';
        let modules = []; // { id, type: 'intro'|'body'|'conclusion', boxes: [] }
        let activeTextarea = null;
        let workspaceMode = 'practice'; // 'audit' or 'practice'
        let selectedExamType = MISSION_CONFIG.defaultExamType || 'alevel'; // 'alevel' | 'ielts' | 'toefl' | 'ib'

        const STORAGE_KEY = `GGV1_STATE::${ID}`;
        let saveDebounceTimer = null;

        // 考试类型选择器事件
        document.querySelectorAll('.exam-type-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.exam-type-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                selectedExamType = btn.dataset.exam;
                console.log('Selected exam type:', selectedExamType);
            });
        });

        // --- 0.0 模式检测与初始化 ---
        function detectWorkspaceMode() {
            const mode = localStorage.getItem('workspaceMode') || 'practice';
            workspaceMode = mode;
            
            // 显示模式标签
            const badge = document.getElementById('mode-badge');
            if (badge) {
                if (mode === 'audit') {
                    badge.className = 'mode-badge audit';
                    badge.innerText = 'Audit Mode';
                    badge.style.display = 'inline-block';
                } else {
                    badge.className = 'mode-badge practice';
                    badge.innerText = 'Practice Mode';
                    badge.style.display = 'inline-block';
                }
            }
            
            // Audit Mode：隐藏题目背景和 Knowledge Hub
            if (mode === 'audit') {
                const header = document.getElementById('header-section');
                const sidebar = document.querySelector('.sidebar');
                const sidebarToggle = document.getElementById('sidebar-toggle');
                const toolbar = document.getElementById('module-toolbar');
                
                if (header) header.style.display = 'none';
                if (sidebar) sidebar.style.display = 'none';
                if (sidebarToggle) sidebarToggle.style.display = 'none';
                if (toolbar) toolbar.style.display = 'none';
            }
            
            return mode;
        }

        // --- 0.1 实用函数 ---
        function getLanguageConstraint() {
            if (currentLanguageMode === 'en') return "Constraint: You must respond in 100% English. Do not use any Chinese characters.";
            if (currentLanguageMode === 'zh') return "约束：必须 100% 使用中文回答，即使问题是英文。";
            return "约束：使用双语回答。采用‘中文核心解释 + 括号内对应英文专业术语’的格式。";
        }

        function getCurrentQuestion() {
            const title = document.getElementById('question-title');
            const text = (title?.innerText || "").trim();
            return text || MISSION_CONFIG.title;
        }

        function setActiveTextarea(el) {
            activeTextarea = el;
        }

        // --- 0.2 模块与占位符 ---
        function makeModuleId() {
            return 'm_' + Math.random().toString(36).slice(2, 9) + Date.now().toString(36);
        }

        function getBoxConfig(type) {
            if (type === 'intro') {
                return [
                    { label: "Intro Box 1", placeholder: "Define issue & background... (e.g., The issue of [topic] was significant...)" },
                    { label: "Intro Box 2", placeholder: "Show debate... (e.g., Historians have debated...)" },
                    { label: "Intro Box 3", placeholder: "Thesis statement... (e.g., This essay will argue that...)" }
                ];
            } else if (type === 'conclusion') {
                return [
                    { label: "Conclusion Box 1", placeholder: "Direct answer (In conclusion...)" },
                    { label: "Conclusion Box 2", placeholder: "Weighting judgement (Their impact was mainly...)" },
                    { label: "Conclusion Box 3", placeholder: "Final evaluation (While [success], [limitation]...)" }
                ];
            } else {
                return [
                    { label: "PEEL Box 1", placeholder: "Point (One important way...)" },
                    { label: "PEEL Box 2", placeholder: "Evidence (This can be seen in...)" },
                    { label: "PEEL Box 3", placeholder: "Explain (This was important because...)" },
                    { label: "PEEL Box 4", placeholder: "Link back (Therefore, this shows...)" }
                ];
            }
        }

        function createEmptyModule(type) {
            const cfg = getBoxConfig(type);
            return {
                id: makeModuleId(),
                type,
                boxes: new Array(cfg.length).fill(""),
                mode: 'guided',
                freeText: ""
            };
        }

        // --- 0.3 保存 / 恢复 ---
        function getState() {
            return {
                question: getCurrentQuestion(),
                language: currentLanguageMode,
                examType: currentExamType,
                modules,
                updatedAt: Date.now()
            };
        }

        function saveToLocal() {
            try {
                localStorage.setItem(STORAGE_KEY, JSON.stringify(getState()));
            } catch (e) {}
        }

        function scheduleSave() {
            if (saveDebounceTimer) clearTimeout(saveDebounceTimer);
            saveDebounceTimer = setTimeout(() => saveToLocal(), 2000);
        }

        function loadFromLocal() {
            try {
                const raw = localStorage.getItem(STORAGE_KEY);
                if (!raw) return;
                const s = JSON.parse(raw);
                if (s.question) document.getElementById('question-title').innerText = s.question;
                if (s.language) {
                    currentLanguageMode = s.language;
                    document.getElementById('language-setting').value = s.language;
                }
                if (s.examType) {
                    currentExamType = s.examType;
                    const examSelector = document.getElementById('exam-type-selector');
                    if (examSelector) examSelector.value = s.examType;
                }
                if (Array.isArray(s.modules) && s.modules.length) {
                    modules = s.modules;
                }
            } catch (e) {}
        }

        // --- 1. 模块渲染与编辑 ---
        function renderModules() {
            const container = document.getElementById('essay-constructor');
            if (!container) return;

            if (!modules.length) {
                container.innerHTML = '<div style="color:#6c757d; font-size:13px;">Use the buttons above to add an Intro, Body paragraph, or Conclusion.</div>';
                return;
            }

            let bodyIndex = 0;
            let introIndex = 0;
            let conclusionIndex = 0;
            const html = modules.map((m) => {
                const cfg = getBoxConfig(m.type);
                const isFree = m.mode === 'free';
                let label = "";
                let blockId = "";
                if (m.type === 'intro') {
                    introIndex += 1;
                    label = "Intro";
                    blockId = `intro-${introIndex}`;
                } else if (m.type === 'conclusion') {
                    conclusionIndex += 1;
                    label = "Conclusion";
                    blockId = `conclusion-${conclusionIndex}`;
                } else {
                    bodyIndex += 1;
                    label = "Body Paragraph " + bodyIndex;
                    blockId = `body-${bodyIndex}`;
                }

                const modeLabel = isFree ? 'Free' : 'Guided';
                const modeIcon = isFree ? '📝' : '🧩';

                let bodyHtml = "";
                if (isFree) {
                    const freeText = (m.freeText || (Array.isArray(m.boxes) ? m.boxes.join(" ") : ""));
                    const hintLines = getBoxConfig(m.type).map((c, i) => (i + 1) + '. ' + c.placeholder).join('<br>');
                    const wordCount = countWords(freeText);
                    bodyHtml = `
                        <div class="editor-box">
                            <div class="label">Freeform ${label}</div>
                            <textarea
                                data-module="${m.id}"
                                data-free="1"
                                placeholder="Write your ${label.toLowerCase()} in full sentences here..."
                                onfocus="setActiveTextarea(this)"
                                oninput="onFreeInput('${m.id}', this.value); updateWordCount(this);"
                            >${freeText}</textarea>
                            <div class="word-count">${wordCount} words</div>
                            <div class="free-hint">${hintLines}</div>
                        </div>
                    `;
                } else {
                    const boxesHtml = cfg.map((boxCfg, idx) => {
                        const value = (m.boxes && typeof m.boxes[idx] === 'string') ? m.boxes[idx] : "";
                        const wordCount = countWords(value);
                        return `
                            <div class="editor-box">
                                <div class="label">${boxCfg.label}</div>
                                <textarea 
                                    data-module="${m.id}" 
                                    data-box="${idx}" 
                                    placeholder="${boxCfg.placeholder}"
                                    onfocus="setActiveTextarea(this)"
                                    oninput="onBoxInput('${m.id}', ${idx}, this.value); updateWordCount(this);"
                                >${value}</textarea>
                                <div class="word-count">${wordCount} words</div>
                            </div>
                        `;
                    }).join("");
                    bodyHtml = boxesHtml;
                }

                return `
                    <div class="essay-module" data-id="${m.id}" data-block-id="${blockId}">
                        <div class="module-header">
                            <div class="module-controls-left">
                                <button class="move-btn" onclick="moveModule('${m.id}', -1)">↑</button>
                                <button class="move-btn" onclick="moveModule('${m.id}', 1)">↓</button>
                                <span class="module-tag">${label}</span>
                            </div>
                            <div class="module-controls-right">
                                <button class="focus-btn" onclick="openFocusMode('${m.id}')" title="Focus Mode">🔍</button>
                                <button class="mode-toggle" onclick="toggleModuleMode('${m.id}')">${modeIcon} ${modeLabel}</button>
                                <button class="module-delete" onclick="confirmRemoveModule('${m.id}')">✕</button>
                            </div>
                        </div>
                        ${bodyHtml}
                    </div>
                `;
            }).join("");

            container.innerHTML = html;
        }

        function addModule(type) {
            modules.push(createEmptyModule(type));
            renderModules();
            saveToLocal();
        }

        function removeModule(id) {
            modules = modules.filter(m => m.id !== id);
            renderModules();
            saveToLocal();
        }

        function confirmRemoveModule(id) {
            if (confirm('Delete this module? This action cannot be undone.')) {
                removeModule(id);
            }
        }

        function onBoxInput(id, index, value) {
            const m = modules.find(m => m.id === id);
            if (!m) return;
            if (!Array.isArray(m.boxes)) m.boxes = [];
            m.boxes[index] = value;
            scheduleSave();
            updateGlobalWordCount();
        }
        
        function onFreeInput(id, value) {
            const m = modules.find(m => m.id === id);
            if (!m) return;
            m.freeText = value;
            scheduleSave();
            updateGlobalWordCount();
        }
        
        // --- 核心计算逻辑（与 DOM 解耦，便于迁移到小程序）---
        
        /**
         * 计算文本字数（纯函数，无 DOM 依赖）
         * @param {string} text - 待统计的文本
         * @returns {number} 字数
         */
        function countWords(text) {
            if (!text || !text.trim()) return 0;
            return text.trim().split(/\s+/).filter(w => w.length > 0).length;
        }
        
        /**
         * 计算单个模块的字数（纯函数）
         * @param {Object} module - 模块对象
         * @returns {number} 该模块的字数
         */
        function calculateModuleWordCount(module) {
            if (!module) return 0;
            if (module.mode === 'free') {
                return countWords(module.freeText || '');
            } else if (Array.isArray(module.boxes)) {
                return module.boxes.reduce((total, box) => total + countWords(box || ''), 0);
            }
            return 0;
        }
        
        /**
         * 计算所有模块的总字数（纯函数）
         * @param {Array} modulesArray - 模块数组
         * @returns {number} 总字数
         */
        function calculateTotalWordCount(modulesArray) {
            if (!Array.isArray(modulesArray)) return 0;
            return modulesArray.reduce((total, m) => total + calculateModuleWordCount(m), 0);
        }
        
        /**
         * 分析 PEEL 结构（纯函数）
         * @param {Array} modulesArray - 模块数组
         * @returns {Object} 结构分析结果
         */
        function analyzePEELStructure(modulesArray) {
            if (!Array.isArray(modulesArray)) return { intro: 0, body: 0, conclusion: 0, total: 0 };
            
            const analysis = {
                intro: 0,
                body: 0,
                conclusion: 0,
                total: modulesArray.length,
                modules: modulesArray.map(m => ({
                    type: m.type,
                    wordCount: calculateModuleWordCount(m),
                    mode: m.mode || 'guided'
                }))
            };
            
            modulesArray.forEach(m => {
                if (m.type === 'intro') analysis.intro++;
                else if (m.type === 'body') analysis.body++;
                else if (m.type === 'conclusion') analysis.conclusion++;
            });
            
            return analysis;
        }
        
        /**
         * 构建完整 Essay 文本（纯函数）
         * @param {Array} modulesArray - 模块数组
         * @returns {string} 完整的 Essay 文本
         */
        function buildEssayTextFromModules(modulesArray) {
            if (!Array.isArray(modulesArray)) return '';
            
            const parts = [];
            modulesArray.forEach((m) => {
                let text = "";
                if (m.mode === 'free') {
                    // Free 模式：直接使用 freeText
                    text = (m.freeText || "").trim();
                } else if (Array.isArray(m.boxes)) {
                    // Guided 模式：遍历所有 boxes（P, E, E, L），确保完整合并
                    text = m.boxes
                        .map(b => (b || "").trim())
                        .filter(Boolean)
                        .join(" ");
                }
                if (!text) return;
                let prefix = "";
                if (m.type === 'intro') prefix = "[Intro] ";
                else if (m.type === 'conclusion') prefix = "[Conclusion] ";
                else prefix = "[Body] ";
                parts.push(prefix + text);
            });
            return parts.join("\n\n");
        }
        
        /**
         * 获取结构摘要（纯函数）
         * @param {Array} modulesArray - 模块数组
         * @returns {Array} 结构摘要数组
         */
        function getStructureSummaryFromModules(modulesArray) {
            if (!Array.isArray(modulesArray)) return [];
            
            return modulesArray.map((m) => ({
                type: m.type,
                text: m.mode === 'free'
                    ? (m.freeText || "").trim()
                    : (Array.isArray(m.boxes) ? m.boxes.join(" ").trim() : "")
            }));
        }
        
        // --- DOM 更新函数（依赖核心计算逻辑）---
        
        function updateWordCount(textarea) {
            const wordCountEl = textarea.parentElement.querySelector('.word-count');
            if (wordCountEl) {
                const count = countWords(textarea.value);
                wordCountEl.textContent = count + ' words';
            }
        }
        
        function updateGlobalWordCount() {
            const globalCountEl = document.getElementById('global-word-count');
            if (!globalCountEl) return;
            
            const totalWords = calculateTotalWordCount(modules);
            globalCountEl.textContent = totalWords + ' words';
        }
        
        // --- Focus Mode 功能 ---
        let currentFocusModuleId = null;
        
        function openFocusMode(moduleId) {
            const m = modules.find(m => m.id === moduleId);
            if (!m) return;
            
            currentFocusModuleId = moduleId;
            const modal = document.getElementById('focus-modal');
            const textarea = document.getElementById('focus-textarea');
            const title = document.getElementById('focus-modal-title');
            
            if (!modal || !textarea || !title) return;
            
            // 确定标签
            let label = "";
            if (m.type === 'intro') label = "Intro";
            else if (m.type === 'conclusion') label = "Conclusion";
            else {
                const bodyIdx = modules.filter(mm => mm.type === 'body' && modules.indexOf(mm) <= modules.indexOf(m)).length;
                label = "Body Paragraph " + bodyIdx;
            }
            
            title.textContent = `Focus Mode: ${label}`;
            
            // 获取内容
            let content = "";
            if (m.mode === 'free') {
                content = m.freeText || "";
            } else if (Array.isArray(m.boxes)) {
                content = m.boxes.map(b => (b || "").trim()).filter(Boolean).join("\n\n");
            }
            
            textarea.value = content;
            updateFocusWordCount();
            
            modal.classList.add('visible');
            textarea.focus();
        }
        
        function closeFocusMode() {
            const modal = document.getElementById('focus-modal');
            if (modal) {
                modal.classList.remove('visible');
            }
            currentFocusModuleId = null;
        }
        
        function onFocusInput() {
            // Focus Mode 下的输入实时更新（但不立即保存到模块，等 Save 时再保存）
        }
        
        function updateFocusWordCount() {
            const textarea = document.getElementById('focus-textarea');
            const countEl = document.getElementById('focus-word-count');
            if (textarea && countEl) {
                const count = countWords(textarea.value);
                countEl.textContent = count + ' words';
            }
        }
        
        function saveFocusMode() {
            if (!currentFocusModuleId) return;
            
            const m = modules.find(m => m.id === currentFocusModuleId);
            const textarea = document.getElementById('focus-textarea');
            if (!m || !textarea) return;
            
            const content = textarea.value;
            
            if (m.mode === 'free') {
                m.freeText = content;
            } else {
                // 如果是 Guided 模式，按段落拆分回 boxes
                const paragraphs = content.split(/\n{2,}|\n/).filter(p => p.trim());
                const cfg = getBoxConfig(m.type);
                m.boxes = new Array(cfg.length).fill("");
                for (let i = 0; i < cfg.length && i < paragraphs.length; i++) {
                    m.boxes[i] = paragraphs[i];
                }
            }
            
            saveToLocal();
            renderModules();
            updateGlobalWordCount();
            closeFocusMode();
        }

        function toggleModuleMode(id) {
            // 致命 Bug 修复：切换前强制保存
            saveToLocal();
            
            const m = modules.find(m => m.id === id);
            if (!m) return;
            const cfg = getBoxConfig(m.type);
            if (!m.mode || m.mode === 'guided') {
                const parts = Array.isArray(m.boxes) ? m.boxes.map(b => (b || '').trim()).filter(Boolean) : [];
                m.freeText = parts.join("\n\n");
                m.mode = 'free';
            } else {
                const maxBoxes = cfg.length;
                const src = (m.freeText || '').split(/\n{2,}|\n/).filter(Boolean);
                m.boxes = new Array(maxBoxes).fill("");
                for (let i = 0; i < maxBoxes; i++) {
                    if (i < src.length - 1) {
                        m.boxes[i] = src[i];
                    } else if (i === maxBoxes - 1 && src.length) {
                        m.boxes[i] = src.slice(i).join(' ');
                        break;
                    }
                }
                m.mode = 'guided';
            }
            
            // 渲染新模式的 DOM
            renderModules();
            
            // 重新绑定事件监听器（确保字数统计等功能正常工作）
            setTimeout(() => {
                updateGlobalWordCount();
                // 重新绑定所有 textarea 的 input 事件
                document.querySelectorAll('textarea[data-module]').forEach(textarea => {
                    if (!textarea.hasAttribute('data-listener-bound')) {
                        textarea.setAttribute('data-listener-bound', 'true');
                        textarea.addEventListener('input', () => {
                            updateGlobalWordCount();
                            updateWordCount(textarea);
                        });
                    }
                });
            }, 100);
        }

        function moveModule(id, direction) {
            const idx = modules.findIndex(m => m.id === id);
            if (idx === -1) return;
            const next = idx + direction;
            if (next < 0 || next >= modules.length) return;
            const tmp = modules[idx];
            modules[idx] = modules[next];
            modules[next] = tmp;
            renderModules();
            saveToLocal();
        }

        // --- 2. 全文构建（使用核心计算逻辑）---
        function buildEssayText() {
            return buildEssayTextFromModules(modules);
        }

        function getStructureSummary() {
            return getStructureSummaryFromModules(modules);
        }

        function buildEssayHtml() {
            const parts = [];
            let bodyIndex = 0;
            modules.forEach((m) => {
                let title = "";
                if (m.type === 'intro') title = "Introduction";
                else if (m.type === 'conclusion') title = "Conclusion";
                else {
                    bodyIndex += 1;
                    title = "Body Paragraph " + bodyIndex;
                }
                let text = "";
                if (m.mode === 'free') {
                    text = (m.freeText || "").trim();
                } else if (Array.isArray(m.boxes)) {
                    text = m.boxes.map(b => (b || "").trim()).filter(Boolean).join(" ");
                }
                if (!text) return;
                const safe = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>');
                parts.push(
                    `<h4 style="margin:8px 0 4px 0;">${title}</h4>` +
                    `<p style="margin:0 0 8px 0;">${safe}</p>`
                );
            });
            return parts.join('');
        }

        // --- 3. 语言与自动保存事件 ---
        document.getElementById('language-setting').addEventListener('change', (e) => {
            currentLanguageMode = e.target.value;
            saveToLocal();
        });

        const examTypeSelector = document.getElementById('exam-type-selector');
        if (examTypeSelector) {
            examTypeSelector.addEventListener('change', (e) => {
                currentExamType = e.target.value;
                saveToLocal();
            });
        }

        document.getElementById('question-title').addEventListener('blur', () => saveToLocal());

        // --- 4. 知识 Hub 插入：针对当前激活 textarea ---
        function add(text) {
            if (!activeTextarea) return;
            const start = activeTextarea.selectionStart ?? activeTextarea.value.length;
            const end = activeTextarea.selectionEnd ?? start;
            const v = activeTextarea.value;
            activeTextarea.value = v.substring(0, start) + text + " " + v.substring(end);
            activeTextarea.focus();

            const mId = activeTextarea.getAttribute('data-module');
            const idxStr = activeTextarea.getAttribute('data-box');
            const idx = idxStr ? parseInt(idxStr, 10) : NaN;
            if (mId && !Number.isNaN(idx)) {
                onBoxInput(mId, idx, activeTextarea.value);
            }
        }

        // --- 5. 侧边栏讲解老师 ---
        async function getExplanation(topic) {
            const box = document.getElementById('explain-box');
            const lang = currentLanguageMode;
            const constraint = getLanguageConstraint();
            const essay_question = getCurrentQuestion();
            box.innerHTML = `<i style="color:#666">🔍 Searching...</i>`;
            try {
                const response = await fetch('/api/explain', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        topic,
                        language: lang,
                        essay_question,
                        structure: getStructureSummary(),
                        constraint
                    })
                });
                const result = await response.json();
                box.innerText = result.explanation || "No explanation found.";
            } catch (e) { box.innerText = "⚠️ Connection error."; }
        }

        // --- 6. 预览视图逻辑（精简流程：直接显示，无 Modal） ---
        function showPreviewView() {
            const previewView = document.getElementById('preview-view');
            const content = document.getElementById('preview-content');
            if (!previewView || !content) return;
            
            const essayText = buildEssayText();
            if (!essayText.trim()) {
                alert('Please write something before previewing.');
                return;
            }
            
            // 格式化文本：按段落清晰排版
            const formatted = essayText
                .split('\n\n')
                .map(p => p.trim())
                .filter(p => p.length > 0)
                .join('\n\n');
            
            content.innerText = formatted;
            
            // 隐藏编辑区，显示预览视图
            document.getElementById('essay-constructor').style.display = 'none';
            document.getElementById('module-toolbar').style.display = 'none';
            document.querySelector('.review-actions').style.display = 'none';
            previewView.style.display = 'block';
            previewView.scrollIntoView({ behavior: 'smooth' });
        }

        function backFromPreview() {
            const previewView = document.getElementById('preview-view');
            const constructor = document.getElementById('essay-constructor');
            const toolbar = document.getElementById('module-toolbar');
            const actions = document.querySelector('.review-actions');
            
            if (previewView) previewView.style.display = 'none';
            if (constructor) constructor.style.display = 'block';
            if (toolbar) toolbar.style.display = 'flex';
            if (actions) actions.style.display = 'flex';
            
            constructor.scrollIntoView({ behavior: 'smooth' });
        }

        function confirmSubmitFromPreview() {
            // 直接提交，无需关闭预览
            submitReview();
        }

        // --- 7. 底部批改：整篇 Essay 级别（同屏对照修改） ---
        let isResubmit = false;
        let previousReview = "";
        
        async function submitReview(isResubmitFlag = false) {
            isResubmit = isResubmitFlag;
            const btn = document.getElementById('ai-btn');
            const feedbackView = document.getElementById('feedback-view');
            const editableArea = document.getElementById('feedback-essay-editable');
            const contentDiv = document.getElementById('ai-content');
            const resubmitBtn = document.getElementById('resubmit-btn');
            const essay_question = getCurrentQuestion();
            const constraint = getLanguageConstraint();
            const essay_full = buildEssayText();
            const structure = getStructureSummary();

            // 获取当前选定的考试类型
            const examSelector = document.getElementById('exam-type-selector');
            const examType = examSelector ? examSelector.value : currentExamType;
            
            /// 准备发送给 API 的数据，API 期望 { essay: string, examType: string }
            const apiData = {
                essay: essay_full,
                examType: selectedExamType
            };
            
            // 隐藏编辑区，显示批改视图
            document.getElementById('essay-constructor').style.display = 'none';
            document.getElementById('module-toolbar').style.display = 'none';
            document.querySelector('.review-actions').style.display = 'none';
            feedbackView.style.display = 'block';
            
            // 左侧显示可编辑的模块（PEEL 格子模式）
            renderEditableModules(editableArea);
            
            btn.innerText = "⌛ Teacher is grading..."; btn.disabled = true;
            contentDiv.innerText = "AI is analyzing your essay...";
            if (resubmitBtn) resubmitBtn.style.display = 'none';

            try {
                const response = await fetch(`${API_BASE_URL}/api/review`, { 
                    method: 'POST', 
                    headers: { 'Content-Type': 'application/json' }, 
                    body: JSON.stringify(apiData) 
                });
                
                // 检查响应状态
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
                    contentDiv.innerHTML = `<div style="color:#dc3545; padding:15px; background:#f8d7da; border-radius:8px;">
                        <strong>⚠️ Error ${response.status}:</strong><br>
                        ${errorData.error || errorData.message || 'Server error'}
                        ${errorData.message ? `<br><small>${errorData.message}</small>` : ''}
                    </div>`;
                    return;
                }
                
                const result = await response.json();
                // console.log("result", result);
                // 保存原始 JSON 数据用于重新提交
                previousReview = result.review || formatReviewResponse(result);
                
                // 直接传递 JSON 对象给渲染函数
                renderAIFeedback(contentDiv, result);
                if (resubmitBtn) resubmitBtn.style.display = 'block';
            } catch (e) { 
                console.error('Fetch error:', e);
                contentDiv.innerHTML = `<div style="color:#dc3545; padding:15px; background:#f8d7da; border-radius:8px;">
                    <strong>⚠️ Connection failed:</strong><br>
                    ${e.message || 'Unable to connect to server. Please check your connection.'}
                </div>`;
            }
            finally { 
                btn.innerText = "🚀 SUBMIT FOR AI TEACHER'S REVIEW"; 
                btn.disabled = false;
                feedbackView.scrollIntoView({ behavior: 'smooth' });
            }
        }

        // 渲染可编辑模块（在 Review 页面左侧）
        function renderEditableModules(container) {
            if (!container) return;
            let bodyIndex = 0;
            let introIndex = 0;
            let conclusionIndex = 0;
            const html = modules.map((m) => {
                const cfg = getBoxConfig(m.type);
                let label = "";
                let blockId = "";
                if (m.type === 'intro') {
                    introIndex += 1;
                    label = "Intro";
                    blockId = `intro-${introIndex}`;
                } else if (m.type === 'conclusion') {
                    conclusionIndex += 1;
                    label = "Conclusion";
                    blockId = `conclusion-${conclusionIndex}`;
                } else {
                    bodyIndex += 1;
                    label = "Body Paragraph " + bodyIndex;
                    blockId = `body-${bodyIndex}`;
                }
                
                if (m.mode === 'free') {
                    const freeText = (m.freeText || "").trim();
                    return `
                        <div class="essay-module" data-id="${m.id}" data-type="${m.type}" data-block-id="${blockId}">
                            <div class="module-header">
                                <span class="module-tag">${label}</span>
                            </div>
                            <div class="editor-box">
                                <textarea 
                                    data-module="${m.id}"
                                    data-free="1"
                                    style="width:100%; min-height:120px; padding:12px; border:1.5px solid #ced4da; border-radius:8px; font-size:14px; line-height:1.5;"
                                    oninput="onFreeInput('${m.id}', this.value)"
                                >${freeText}</textarea>
                            </div>
                        </div>
                    `;
                } else {
                    const boxesHtml = cfg.map((boxCfg, idx) => {
                        const value = (m.boxes && typeof m.boxes[idx] === 'string') ? m.boxes[idx] : "";
                        return `
                            <div class="editor-box">
                                <div class="label">${boxCfg.label}</div>
                                <textarea 
                                    data-module="${m.id}" 
                                    data-box="${idx}" 
                                    style="width:100%; height:95px; padding:12px; border:1.5px solid #ced4da; border-radius:8px; font-size:14px; line-height:1.5;"
                                    oninput="onBoxInput('${m.id}', ${idx}, this.value)"
                                >${value}</textarea>
                            </div>
                        `;
                    }).join("");
                    return `
                        <div class="essay-module" data-id="${m.id}" data-type="${m.type}" data-block-id="${blockId}">
                            <div class="module-header">
                                <span class="module-tag">${label}</span>
                            </div>
                            ${boxesHtml}
                        </div>
                    `;
                }
            }).join("");
            container.innerHTML = html;
        }

        // 切换编辑视图模式（PEEL 格子 / 纯文本）
        let editViewMode = 'peel'; // 'peel' or 'text'
        function toggleEditViewMode() {
            const container = document.getElementById('feedback-essay-editable');
            const toggleBtn = document.getElementById('view-mode-toggle');
            if (!container) return;
            
            editViewMode = editViewMode === 'peel' ? 'text' : 'peel';
            
            if (editViewMode === 'text') {
                // 切换到纯文本模式
                const essayText = buildEssayText();
                container.innerHTML = `
                    <textarea 
                        id="essay-text-editor"
                        style="width:100%; min-height:400px; padding:20px; border:1.5px solid #ced4da; border-radius:8px; font-size:14px; line-height:1.8; font-family:inherit;"
                        oninput="onTextEditorInput(this.value)"
                    >${essayText}</textarea>
                `;
                if (toggleBtn) toggleBtn.innerText = 'Switch to PEEL Mode';
            } else {
                // 切换回 PEEL 格子模式
                renderEditableModules(container);
                if (toggleBtn) toggleBtn.innerText = 'Switch to Text Mode';
            }
        }

        function onTextEditorInput(value) {
            // 纯文本模式下的输入同步到 modules（简单实现：按段落拆分）
            const paragraphs = value.split('\n\n').map(p => p.trim()).filter(p => p.length > 0);
            // 这里可以更智能地匹配到现有模块，暂时简单处理
            scheduleSave();
        }

        // 将 API 返回的结构化数据格式化为字符串
        function formatReviewResponse(data) {
            if (!data) return "";
            
            let text = "";
            
            // 总体分析
            if (data.overall_analysis) {
                const oa = data.overall_analysis;
                text += `## Overall Analysis\n\n`;
                text += `Score: ${oa.score}/100 | Grade: ${oa.grade}\n\n`;
                
                if (oa.ao_scores) {
                    text += `AO Scores:\n`;
                    text += `- AO1 (Knowledge): ${oa.ao_scores.AO1_Knowledge || 0}\n`;
                    text += `- AO2 (Application): ${oa.ao_scores.AO2_Application || 0}\n`;
                    text += `- AO3 (Analysis): ${oa.ao_scores.AO3_Analysis || 0}\n`;
                    text += `- AO4 (Evaluation): ${oa.ao_scores.AO4_Evaluation || 0}\n\n`;
                }
                
                if (oa.summary && Array.isArray(oa.summary)) {
                    text += `Summary:\n${oa.summary.map(s => `- ${s}`).join('\n')}\n\n`;
                }
            }
            
            // 段落评审
            if (data.paragraph_reviews && Array.isArray(data.paragraph_reviews) && data.paragraph_reviews.length > 0) {
                text += `## Paragraph Reviews\n\n`;
                data.paragraph_reviews.forEach((pr, idx) => {
                    text += `### ${pr.paragraph_id || `Paragraph ${idx + 1}`}\n\n`;
                    if (pr.strengths && pr.strengths.length > 0) {
                        text += `Strengths:\n${pr.strengths.map(s => `- ${s}`).join('\n')}\n\n`;
                    }
                    if (pr.problems && pr.problems.length > 0) {
                        text += `Problems:\n${pr.problems.map(p => `- ${p}`).join('\n')}\n\n`;
                    }
                    if (pr.suggestions && pr.suggestions.length > 0) {
                        text += `Suggestions:\n${pr.suggestions.map(s => `- ${s}`).join('\n')}\n\n`;
                    }
                    if (pr.rewrite_hint) {
                        text += `Rewrite Hint: ${pr.rewrite_hint}\n\n`;
                    }
                });
            }
            
            // 行动建议
            if (data.action_items && Array.isArray(data.action_items) && data.action_items.length > 0) {
                text += `## Action Items\n\n`;
                data.action_items.forEach(ai => {
                    text += `- [${ai.target || 'General'}] ${ai.action || ''}\n`;
                });
                text += `\n`;
            }
            
            // 模型范文
            if (data.model_essay) {
                text += `## Model Essay\n\n`;
                if (data.model_essay.intro) {
                    text += `### Introduction\n${data.model_essay.intro}\n\n`;
                }
                if (data.model_essay.body && Array.isArray(data.model_essay.body)) {
                    data.model_essay.body.forEach((para, idx) => {
                        text += `### Body Paragraph ${idx + 1}\n${para}\n\n`;
                    });
                }
                if (data.model_essay.conclusion) {
                    text += `### Conclusion\n${data.model_essay.conclusion}\n\n`;
                }
            }
            
            // 错误信息
            if (data.error) {
                text += `\n\n⚠️ Note: ${data.error}\n`;
            }
            
            return text.trim();
        }

        // 渲染 AI 反馈（支持 JSON 格式，生成三个卡片）
        function renderAIFeedback(container, data) {
            if (!container) return;
            
            let html = '';
            
            // 如果传入的是字符串（旧格式），使用原来的逻辑
            if (typeof data === 'string') {
                const blockIdPattern = /\[block_id:\s*([a-z]+-\d+)\]/gi;
                const bodyPattern = /Body\s+(?:Paragraph\s+)?(\d+)/gi;
                
                html = '<div class="ai-feedback-card">';
                const paragraphs = data.split('\n\n').filter(p => p.trim());
                
                paragraphs.forEach(para => {
                    const blockIdMatches = [...para.matchAll(blockIdPattern)];
                    const blockIds = [...new Set(blockIdMatches.map(m => m[1]))];
                    const paraMatches = [...para.matchAll(bodyPattern)];
                    const paraBodyRefs = [...new Set(paraMatches.map(m => parseInt(m[1])))];
                    const displayText = para.replace(/\[block_id:[^\]]+\]/gi, '').trim();
                    html += `<p style="margin:0 0 12px 0; line-height:1.8;">${displayText}</p>`;
                    
                    if (blockIds.length > 0) {
                        blockIds.forEach(blockId => {
                            const displayName = blockId.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());
                            html += `<button class="locate-btn" onclick="locateIssue('${blockId}')">📍 Locate ${displayName}</button> `;
                        });
                    }
                    
                    if (paraBodyRefs.length > 0 && blockIds.length === 0) {
                        paraBodyRefs.forEach(bodyNum => {
                            html += `<button class="locate-btn" onclick="locateIssue('body-${bodyNum}')">📍 Locate Body ${bodyNum}</button> `;
                        });
                    }
                });
                
                html += '</div>';
                container.innerHTML = html;
                return;
            }
            
            // 新格式：处理 JSON 对象，生成三个卡片
            
            // 卡片 1: Overall Analysis
            if (data.overall_analysis) {
                const oa = data.overall_analysis;
                html += '<div class="ai-feedback-card">';
                html += '<h3 style="margin:0 0 15px 0; color:#e63946; font-size:18px;">📊 Overall Analysis</h3>';
                
                html += `<div style="margin-bottom:15px;">
                    <strong>Score:</strong> <span style="font-size:20px; color:#e63946; font-weight:bold;">${oa.score}/100</span> 
                    | <strong>Grade:</strong> <span style="font-size:18px; color:#e63946; font-weight:bold;">${oa.grade}</span>
                </div>`;
                
                if (oa.ao_scores) {
                    html += '<div style="margin-bottom:15px;"><strong>AO Scores:</strong><ul style="margin:8px 0; padding-left:20px;">';
                    html += `<li>AO1 (Knowledge): ${oa.ao_scores.AO1_Knowledge || 0}</li>`;
                    html += `<li>AO2 (Application): ${oa.ao_scores.AO2_Application || 0}</li>`;
                    html += `<li>AO3 (Analysis): ${oa.ao_scores.AO3_Analysis || 0}</li>`;
                    html += `<li>AO4 (Evaluation): ${oa.ao_scores.AO4_Evaluation || 0}</li>`;
                    html += '</ul></div>';
                }
                
                if (oa.summary && Array.isArray(oa.summary) && oa.summary.length > 0) {
                    html += '<div style="margin-bottom:15px;"><strong>Summary:</strong><ul style="margin:8px 0; padding-left:20px;">';
                    oa.summary.forEach(s => {
                        html += `<li style="margin-bottom:8px; line-height:1.6;">${s}</li>`;
                    });
                    html += '</ul></div>';
                }
                
                // 添加 Action Items
                if (data.action_items && Array.isArray(data.action_items) && data.action_items.length > 0) {
                    html += '<div style="margin-top:20px; padding-top:15px; border-top:2px solid #e0e0e0;"><strong style="color:#667eea;">📋 Action Items:</strong><ul style="margin:8px 0; padding-left:20px;">';
                    data.action_items.forEach(ai => {
                        const target = ai.target || 'General';
                        const action = ai.action || '';
                        html += `<li style="margin-bottom:10px; line-height:1.6;"><strong>[${target}]</strong> ${action}</li>`;
                    });
                    html += '</ul></div>';
                }
                
                html += '</div>';
            }
            
            // 卡片 2: Paragraph Reviews
            if (data.paragraph_reviews && Array.isArray(data.paragraph_reviews) && data.paragraph_reviews.length > 0) {
                html += '<div class="ai-feedback-card">';
                html += '<h3 style="margin:0 0 15px 0; color:#e63946; font-size:18px;">📝 Paragraph Reviews</h3>';
                
                data.paragraph_reviews.forEach((pr, idx) => {
                    const paraId = pr.paragraph_id || `paragraph-${idx + 1}`;
                    const blockId = paraId.includes('-') ? paraId : `${paraId}-1`;
                    
                    html += `<div style="margin-bottom:20px; padding-bottom:15px; border-bottom:${idx < data.paragraph_reviews.length - 1 ? '1px solid #e0e0e0' : 'none'};">`;
                    html += `<h4 style="margin:0 0 10px 0; color:#667eea; font-size:16px;">${paraId.charAt(0).toUpperCase() + paraId.slice(1)}</h4>`;
                    
                    if (pr.strengths && pr.strengths.length > 0) {
                        html += '<div style="margin-bottom:10px;"><strong style="color:#28a745;">✓ Strengths:</strong><ul style="margin:5px 0; padding-left:20px;">';
                        pr.strengths.forEach(s => {
                            html += `<li style="margin-bottom:5px; line-height:1.6;">${s}</li>`;
                        });
                        html += '</ul></div>';
                    }
                    
                    if (pr.problems && pr.problems.length > 0) {
                        html += '<div style="margin-bottom:10px;"><strong style="color:#dc3545;">✗ Problems:</strong><ul style="margin:5px 0; padding-left:20px;">';
                        pr.problems.forEach(p => {
                            html += `<li style="margin-bottom:5px; line-height:1.6;">${p}</li>`;
                        });
                        html += '</ul></div>';
                    }
                    
                    if (pr.suggestions && pr.suggestions.length > 0) {
                        html += '<div style="margin-bottom:10px;"><strong style="color:#ffc107;">💡 Suggestions:</strong><ul style="margin:5px 0; padding-left:20px;">';
                        pr.suggestions.forEach(s => {
                            html += `<li style="margin-bottom:5px; line-height:1.6;">${s}</li>`;
                        });
                        html += '</ul></div>';
                    }
                    
                    if (pr.rewrite_hint) {
                        html += `<div style="margin-top:10px; padding:10px; background:#f8f9fa; border-left:3px solid #667eea; border-radius:4px;">
                            <strong>Rewrite Hint:</strong> <span style="line-height:1.6;">${pr.rewrite_hint}</span>
                        </div>`;
                    }
                    
                    // 添加 Locate 按钮
                    html += `<div style="margin-top:10px;">
                        <button class="locate-btn" onclick="locateIssue('${blockId}')">📍 Locate ${blockId.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}</button>
                    </div>`;
                    
                    html += '</div>';
                });
                
                html += '</div>';
            }
            
            // 卡片 3: Model Essay
            if (data.model_essay) {
                html += '<div class="ai-feedback-card">';
                html += '<h3 style="margin:0 0 15px 0; color:#e63946; font-size:18px;">📚 Model Essay</h3>';
                
                if (data.model_essay.intro) {
                    html += '<div style="margin-bottom:20px;">';
                    html += '<h4 style="margin:0 0 10px 0; color:#667eea; font-size:16px;">Introduction</h4>';
                    html += `<p style="margin:0; line-height:1.8; padding:12px; background:#f8f9fa; border-radius:6px;">${data.model_essay.intro}</p>`;
                    html += '</div>';
                }
                
                if (data.model_essay.body && Array.isArray(data.model_essay.body)) {
                    data.model_essay.body.forEach((para, idx) => {
                        html += '<div style="margin-bottom:20px;">';
                        html += `<h4 style="margin:0 0 10px 0; color:#667eea; font-size:16px;">Body Paragraph ${idx + 1}</h4>`;
                        html += `<p style="margin:0; line-height:1.8; padding:12px; background:#f8f9fa; border-radius:6px;">${para}</p>`;
                        html += '</div>';
                    });
                }
                
                if (data.model_essay.conclusion) {
                    html += '<div style="margin-bottom:20px;">';
                    html += '<h4 style="margin:0 0 10px 0; color:#667eea; font-size:16px;">Conclusion</h4>';
                    html += `<p style="margin:0; line-height:1.8; padding:12px; background:#f8f9fa; border-radius:6px;">${data.model_essay.conclusion}</p>`;
                    html += '</div>';
                }
                
                html += '</div>';
            }
            
            // 错误信息（如果有）
            if (data.error) {
                html += '<div class="ai-feedback-card" style="border-left-color:#ffc107;">';
                html += `<p style="margin:0; color:#856404; background:#fff3cd; padding:12px; border-radius:6px;">⚠️ Note: ${data.error}</p>`;
                html += '</div>';
            }
            
            container.innerHTML = html;
        }

        // Locate 功能：高亮对应模块（通用函数，支持所有 block 类型）
        function locateIssue(blockId) {
            if (!blockId) return;
            
            // 查找对应的 DOM 元素
            const moduleEl = document.querySelector(`[data-block-id="${blockId}"]`);
            
            if (moduleEl) {
                // 移除之前的高亮
                document.querySelectorAll('.essay-module').forEach(el => {
                    el.classList.remove('highlight');
                    el.classList.remove('active-glow');
                });
                
                // 滚动到目标元素
                moduleEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
                
                // 添加高亮动画
                moduleEl.classList.add('active-glow');
                
                // 2 秒后移除高亮（动画时长）
                setTimeout(() => {
                    moduleEl.classList.remove('active-glow');
                }, 2000);
            } else {
                // 如果找不到，尝试向后兼容的 locateBodyParagraph
                const match = blockId.match(/body-(\d+)/);
                if (match) {
                    const bodyNum = parseInt(match[1], 10);
                    locateBodyParagraph(bodyNum);
                }
            }
        }
        
        // 向后兼容：Locate Body 段落（保留旧函数）
        function locateBodyParagraph(bodyNum) {
            locateIssue(`body-${bodyNum}`);
        }

        // Re-submit 逻辑
        async function resubmitForReview() {
            await submitReview(true);
        }

        // --- 11. Mission Lab 抽屉 ---
        function showMissionLab() {
            const drawer = document.getElementById('mission-lab-drawer');
            if (drawer) drawer.style.display = 'block';
        }

        function closeMissionLab() {
            const drawer = document.getElementById('mission-lab-drawer');
            if (drawer) drawer.style.display = 'none';
        }

        // 点击抽屉外部关闭
        document.addEventListener('DOMContentLoaded', () => {
            const drawer = document.getElementById('mission-lab-drawer');
            if (drawer) {
                drawer.onclick = (e) => {
                    if (e.target === drawer) closeMissionLab();
                };
            }
        });
        
        // --- 12. 侧边栏折叠/展开控制 ---
        function toggleSidebar() {
            const sidebar = document.getElementById('knowledge-sidebar');
            const toggle = document.getElementById('sidebar-toggle');
            const overlay = document.getElementById('sidebar-overlay');
            
            if (!sidebar || !toggle) return;
            
            const isExpanded = sidebar.classList.contains('expanded');
            
            if (isExpanded) {
                closeSidebar();
            } else {
                sidebar.classList.add('expanded');
                toggle.classList.remove('collapsed');
                toggle.classList.add('expanded');
                overlay.classList.add('visible');
            }
        }
        
        function closeSidebar() {
            const sidebar = document.getElementById('knowledge-sidebar');
            const toggle = document.getElementById('sidebar-toggle');
            const overlay = document.getElementById('sidebar-overlay');
            
            if (!sidebar || !toggle) return;
            
            sidebar.classList.remove('expanded');
            toggle.classList.remove('expanded');
            toggle.classList.add('collapsed');
            overlay.classList.remove('visible');
        }
        
        // 检查 URL 参数，如果是 view-hub 模式，自动展开侧边栏
        window.addEventListener('load', () => {
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.get('view') === 'hub') {
                setTimeout(() => {
                    toggleSidebar();
                }, 300);
            }
        });
        
        // --- 13. 计时器功能 ---
        let timerInterval = null;
        let timerSeconds = 0;
        let timerMode = 'up'; // 'up' or 'down'
        let timerCountdownMinutes = 45;
        let timerIsRunning = false;
        let timerStartTime = null;
        
        function toggleTimerPanel() {
            const panel = document.getElementById('timer-panel');
            if (panel) {
                panel.classList.toggle('visible');
            }
        }
        
        function setTimerMode(mode) {
            timerMode = mode;
            const upBtn = document.getElementById('timer-mode-up');
            const downBtn = document.getElementById('timer-mode-down');
            const inputContainer = document.getElementById('timer-countdown-input-container');
            
            if (upBtn && downBtn) {
                if (mode === 'up') {
                    upBtn.classList.add('active');
                    downBtn.classList.remove('active');
                    if (inputContainer) inputContainer.style.display = 'none';
                } else {
                    upBtn.classList.remove('active');
                    downBtn.classList.add('active');
                    if (inputContainer) inputContainer.style.display = 'block';
                }
            }
            
            // 如果切换模式时计时器正在运行，需要重置
            if (timerIsRunning) {
                resetTimer();
            } else {
                updateTimerDisplay();
            }
        }
        
        function startTimer() {
            if (timerIsRunning) return;
            
            timerIsRunning = true;
            timerStartTime = Date.now();
            
            const startBtn = document.getElementById('timer-start-btn');
            const pauseBtn = document.getElementById('timer-pause-btn');
            
            if (startBtn) startBtn.style.display = 'none';
            if (pauseBtn) pauseBtn.style.display = 'block';
            
            // 如果是倒计时模式，读取设置的分钟数
            if (timerMode === 'down') {
                const input = document.getElementById('timer-countdown-input');
                if (input) {
                    const minutes = parseInt(input.value, 10);
                    if (minutes > 0 && minutes <= 180) {
                        timerCountdownMinutes = minutes;
                        timerSeconds = minutes * 60;
                    }
                }
            }
            
            timerInterval = setInterval(() => {
                if (timerMode === 'up') {
                    timerSeconds++;
                } else {
                    timerSeconds--;
                    if (timerSeconds <= 0) {
                        timerSeconds = 0;
                        pauseTimer();
                        // 时间到，可以添加提示
                        showToast('⏰ Time is up! Please finish your conclusion.');
                    }
                }
                
                updateTimerDisplay();
            }, 1000);
            
            updateTimerDisplay();
        }
        
        function pauseTimer() {
            if (!timerIsRunning) return;
            
            timerIsRunning = false;
            
            if (timerInterval) {
                clearInterval(timerInterval);
                timerInterval = null;
            }
            
            const startBtn = document.getElementById('timer-start-btn');
            const pauseBtn = document.getElementById('timer-pause-btn');
            
            if (startBtn) startBtn.style.display = 'block';
            if (pauseBtn) pauseBtn.style.display = 'none';
        }
        
        function resetTimer() {
            pauseTimer();
            
            if (timerMode === 'up') {
                timerSeconds = 0;
            } else {
                const input = document.getElementById('timer-countdown-input');
                if (input) {
                    const minutes = parseInt(input.value, 10);
                    if (minutes > 0 && minutes <= 180) {
                        timerCountdownMinutes = minutes;
                        timerSeconds = minutes * 60;
                    } else {
                        timerSeconds = timerCountdownMinutes * 60;
                    }
                } else {
                    timerSeconds = timerCountdownMinutes * 60;
                }
            }
            
            updateTimerDisplay();
        }
        
        function updateTimerDisplay() {
            const display = document.getElementById('timer-display');
            if (!display) return;
            
            let hours = Math.floor(timerSeconds / 3600);
            let minutes = Math.floor((timerSeconds % 3600) / 60);
            let seconds = timerSeconds % 60;
            
            const timeString = 
                String(hours).padStart(2, '0') + ':' +
                String(minutes).padStart(2, '0') + ':' +
                String(seconds).padStart(2, '0');
            
            display.textContent = timeString;
            
            // 倒计时模式：剩余 5 分钟时变红并闪烁
            if (timerMode === 'down' && timerSeconds > 0 && timerSeconds <= 300) {
                display.classList.add('warning');
                if (timerSeconds === 300) {
                    showToast('⚠️ 5 minutes remaining! Time to write your conclusion.');
                }
            } else {
                display.classList.remove('warning');
            }
        }
        
        // 点击外部关闭计时器面板
        document.addEventListener('click', (e) => {
            const panel = document.getElementById('timer-panel');
            const btn = document.querySelector('.timer-btn');
            if (panel && btn && !panel.contains(e.target) && !btn.contains(e.target)) {
                panel.classList.remove('visible');
            }
        });
        
        // --- 14. 返回 Workspace ---
        function backToWorkspace() {
            // 确保当前内容已保存
            saveToLocal();
            // 跳转回首页
            window.location.href = '../index.html';
        }

        // 传统 SAVE / EXPORT 适配整篇 essay
        function save() {
            saveToLocal();
            alert("Work Saved!");
        }

        function exportDoc() {
            const aiContent = document.getElementById('ai-content').innerText;
            const essayText = buildEssayText();
            const content = `WORK: ${ID}\nQUESTION: ${getCurrentQuestion()}\n\n[ESSAY]\n${essayText}\n\n[AI FEEDBACK]\n${aiContent}`;
            const blob = new Blob([content], { type: 'text/plain' });
            const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = `Submission_${ID}.txt`; a.click();

            const preview = document.getElementById('export-preview');
            const container = document.getElementById('export-essay');
            if (preview && container) {
                container.innerHTML = buildEssayHtml();
                preview.style.display = 'block';
                preview.scrollIntoView({ behavior: 'smooth' });
            }
        }

        // --- 9. Toast 提示函数 ---
        function showToast(message) {
            const container = document.getElementById('toast-container');
            if (!container) return;
            
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.innerHTML = `<span class="toast-icon">✅</span><span>${message}</span>`;
            
            container.innerHTML = '';
            container.appendChild(toast);
            
            // 3 秒后自动移除
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 3000);
        }

        // --- 10. 自动拆解投喂逻辑 ---
        function processQuickAuditData() {
            // 检查是否有 Quick Audit 的待处理数据
            const pendingIntro = localStorage.getItem('pendingIntro');
            const pendingConclusion = localStorage.getItem('pendingConclusion');
            const pendingBodiesRaw = localStorage.getItem('pendingBodies');
            
            if (!pendingIntro && !pendingConclusion && !pendingBodiesRaw) {
                return false; // 没有待处理数据
            }
            
            // 清空现有模块（确保清除所有输入框）
            modules = [];
            
            let moduleCount = 0;
            
            // 创建 Intro 模块（如果有）
            if (pendingIntro) {
                const introMod = createEmptyModule('intro');
                introMod.mode = 'free';
                introMod.freeText = pendingIntro;
                modules.push(introMod);
                moduleCount++;
            }
            
            // 创建 Body 模块（根据 pendingBodies 的长度自动生成）
            if (pendingBodiesRaw) {
                try {
                    const bodies = JSON.parse(pendingBodiesRaw);
                    if (Array.isArray(bodies) && bodies.length > 0) {
                        bodies.forEach(bodyText => {
                            if (bodyText && bodyText.trim()) {
                                const bodyMod = createEmptyModule('body');
                                bodyMod.mode = 'free';
                                bodyMod.freeText = bodyText.trim();
                                modules.push(bodyMod);
                                moduleCount++;
                            }
                        });
                    }
                } catch (e) {
                    console.error('Failed to parse pendingBodies:', e);
                }
            }
            
            // 创建 Conclusion 模块（如果有）
            if (pendingConclusion) {
                const conclMod = createEmptyModule('conclusion');
                conclMod.mode = 'free';
                conclMod.freeText = pendingConclusion;
                modules.push(conclMod);
                moduleCount++;
            }
            
            // 清除 localStorage 中的待处理数据（防止下次打开页面误触发）
            localStorage.removeItem('pendingIntro');
            localStorage.removeItem('pendingConclusion');
            localStorage.removeItem('pendingBodies');
            
            // 保存到当前任务的状态
            saveToLocal();
            
            // 渲染模块
            renderModules();
            
            // 显示 Toast 反馈提示
            showToast("Audit Complete: We've split your text into PEEL blocks. Review the logic below!");
            
            // Audit Mode：自动提交批改
            if (workspaceMode === 'audit') {
                setTimeout(() => {
                    showPreviewView();
                    setTimeout(() => {
                        confirmSubmitFromPreview();
                    }, 500);
                }, 1000);
            }
            
            return true; // 成功处理
        }

        // 初始恢复 + 默认 body 模块 + Quick Audit 数据导入
        window.addEventListener('load', () => {
            // 首先检测模式
            detectWorkspaceMode();
            
            // 优先处理 Quick Audit 数据
            const hasQuickAuditData = processQuickAuditData();
            
            if (!hasQuickAuditData) {
                // 如果没有 Quick Audit 数据，正常加载本地保存的状态
                loadFromLocal();
            }
            
            // 如果没有模块，创建默认 body 模块（仅在 Practice Mode）
            if (!modules.length && workspaceMode === 'practice') {
                modules.push(createEmptyModule('body'));
            }
            
            renderModules();
            updateGlobalWordCount();
            
            // 监听所有 textarea 的输入，实时更新全局字数
            document.addEventListener('input', (e) => {
                if (e.target.tagName === 'TEXTAREA' && e.target.hasAttribute('data-module')) {
                    updateGlobalWordCount();
                }
            });
        });
    </script>
