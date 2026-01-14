import os

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>PEEL Workspace - {mid}</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #f4f7f6; display: flex; height: 100vh; margin: 0; color: #333; }}
        .main {{ flex: 1; padding: 40px; overflow-y: auto; }}

        /* 右侧双窗口：上方知识区可滚动；下方 explainer-window 固定 */
        .sidebar {{
            width: 380px;
            background: #fff;
            border-left: 1px solid #dee2e6;
            padding: 25px;
            box-shadow: -5px 0 15px rgba(0, 0, 0, 0.05);
            display: flex;
            flex-direction: column;
            gap: 14px;
            box-sizing: border-box;
        }}
        .sidebar-content {{
            flex: 1;
            overflow-y: auto;
            padding-right: 6px; /* 给滚动条留空间 */
        }}
        .header {{ border-bottom: 3px solid #1d3557; margin-bottom: 25px; padding-bottom: 15px; }}
        .q-text {{ font-size: 20px; font-weight: 700; color: #1d3557; }}
        .nav-bar {{ margin-bottom: 25px; display: flex; gap: 10px; }}
        
        button {{ border: none; border-radius: 6px; cursor: pointer; font-weight: 600; transition: 0.2s; }}
        .btn-save {{ background: #2a9d8f; color: white; padding: 10px 18px; }}
        .btn-export {{ background: #f4a261; color: white; padding: 10px 18px; }}

        /* Section tabs (minimal style) */
        .section-tabs {{ display: flex; gap: 8px; margin: 12px 0 18px 0; }}
        .section-tab {{ padding: 8px 12px; border-radius: 999px; border: 1px solid #ced4da; background: #fff; color: #1d3557; font-size: 13px; }}
        .section-tab.active {{ background: #1d3557; color: #fff; border-color: #1d3557; }}
        .section-hint {{ color:#6c757d; font-size:12px; margin-bottom: 10px; }}
        
        /* 💡 显式按钮样式 */
        .tag-row {{ display: flex; align-items: center; gap: 5px; margin-bottom: 8px; }}
        .tag {{ flex: 1; padding: 8px; border-radius: 4px; font-size: 12px; cursor: pointer; border: 1px solid #ddd; background: #fff; border-left: 4px solid #457b9d; text-align: left; }}
        .tag:hover {{ background: #f8f9fa; }}
        .explain-btn {{ background: #457b9d; color: white; padding: 8px; font-size: 12px; border-radius: 4px; width: 35px; }}
        
        .editor-box {{ margin-bottom: 15px; }}
        .label {{ color: #e63946; font-size: 11px; font-weight: 800; text-transform: uppercase; margin-bottom: 5px; }}
        textarea {{ width: 100%; height: 95px; border: 1.5px solid #ced4da; border-radius: 8px; padding: 12px; font-size: 14px; resize: none; line-height: 1.5; box-sizing: border-box; }}

        /* Essay constructor layout */
        #module-toolbar {{ display:flex; flex-wrap:wrap; gap:8px; margin: 8px 0 16px 0; }}
        .toolbar-btn {{ padding:8px 12px; border-radius:999px; border:none; background:#1d3557; color:#fff; font-size:13px; cursor:pointer; }}
        .toolbar-btn.secondary {{ background:#6c757d; }}
        .toolbar-btn:hover {{ opacity:0.9; transform:translateY(-1px); }}

        #essay-constructor {{ display:flex; flex-direction:column; gap:14px; }}
        .essay-module {{ border:1px solid #dee2e6; border-radius:10px; padding:12px 14px; background:#fff; }}
        .module-header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; }}
        .module-tag {{ font-size:12px; font-weight:700; text-transform:uppercase; color:#1d3557; }}
        .module-delete {{ border:none; background:#fff; color:#e63946; cursor:pointer; font-size:14px; }}

        #merge-view {{ margin-top:16px; }}
        
        /* 👨‍🏫 右侧讲解老师窗口 */
        #explainer-window {{
            position: sticky;
            bottom: 0;
            background: #1d3557; /* 蓝色窗口 */
            border-radius: 12px;
            padding: 14px 14px 12px 14px;
            border: 1px solid rgba(255,255,255,0.18);
            box-shadow: 0 10px 30px rgba(29,53,87,0.25);
        }}
        #explain-box {{ font-size: 13px; line-height: 1.6; color: #f1faee; min-height: 110px; white-space: pre-wrap; }}

        /* 🚀 底部 AI Review 样式 */
        .ai-review-trigger {{ background: #e63946; color: white; width: 100%; padding: 20px; font-size: 18px; margin: 30px 0; box-shadow: 0 4px 15px rgba(230,57,70,0.3); }}
        #ai-review-result {{ border: 2px solid #e63946; border-radius: 12px; background: white; margin-bottom: 40px; overflow: hidden; }}
    </style>
</head>

<body>
    <div class="main">
        <div class="nav-bar">
            <button class="btn-save" onclick="save()">💾 SAVE</button>
            <select id="language-setting" style="padding: 10px; border-radius: 6px; border: 1.5px solid #007bff;">
                <option value="dual" selected>🌓 Dual-Language</option>
                <option value="en">🇬🇧 English Only</option>
                <option value="zh">🇨🇳 Chinese Only</option>
            </select>
            <button class="btn-export" onclick="exportDoc()">📥 EXPORT + FEEDBACK</button>
        </div>

        <div class="header">
            <div style="color:#6c757d; font-size:11px; margin-bottom:5px;">MISSION ID: {mid}</div>
            <div style="display:flex; align-items:center; gap:10px;">
                <h1 class="q-text" id="question-title" contenteditable="true" spellcheck="false" style="outline:none; margin:0; flex:1;">{question}</h1>
                <span title="Click to edit the question" style="font-size:18px; color:#457b9d;">✏️</span>
            </div>
        </div>

        <div id="module-toolbar">
            <button class="toolbar-btn" onclick="addModule('intro')">+ Add Intro</button>
            <button class="toolbar-btn" onclick="addModule('body')">+ Add Body (PEEL)</button>
            <button class="toolbar-btn" onclick="addModule('conclusion')">+ Add Conclusion</button>
            <button class="toolbar-btn secondary" onclick="toggleMergeView()">👁 Merge View</button>
        </div>

        <div id="essay-constructor"></div>

        <div id="merge-view" style="display:none;">
            <div class="label">Essay Preview (read-only)</div>
            <textarea id="merge-content" readonly style="height:140px;"></textarea>
        </div>

        <button class="ai-review-trigger" id="ai-btn" onclick="submitReview()">🚀 SUBMIT FOR AI TEACHER'S REVIEW</button>

        <div id="ai-review-result" style="display: none;">
            <div style="background: #e63946; color: white; padding: 12px 20px; font-weight: bold;">🎯 ACADEMIC REVIEW</div>
            <div id="ai-content" style="padding: 25px; line-height: 1.8; font-size: 15px;">AI is analyzing...</div>
        </div>
    </div>

    <div class="sidebar">
        <div class="sidebar-content">
            <h3 style="margin:0 0 14px 0; color:#1d3557;">Knowledge Hub</h3>
            
            <div class="kb-section">
                <div style="font-size:12px; font-weight:800; color:#1d3557; margin-bottom:10px; border-bottom:1px solid #eee;">⚖️ LEGAL MILESTONES</div>
                <div class="tag-row"><div class="tag" onclick="add('Brown v. Board (1954)')">Brown v. Board</div><button class="explain-btn" onclick="getExplanation('Brown v. Board')">💡</button></div>
                <div class="tag-row"><div class="tag" onclick="add('Civil Rights Act (1957)')">1957 CR Act</div><button class="explain-btn" onclick="getExplanation('Civil Rights Act 1957')">💡</button></div>
            </div>

            <div class="kb-section" style="margin-top:20px;">
                <div style="font-size:12px; font-weight:800; color:#1d3557; margin-bottom:10px; border-bottom:1px solid #eee;">✊ DIRECT ACTION</div>
                <div class="tag-row"><div class="tag" onclick="add('Montgomery Bus Boycott (1955–56)')">Bus Boycott</div><button class="explain-btn" onclick="getExplanation('Montgomery Bus Boycott')">💡</button></div>
                <div class="tag-row"><div class="tag" onclick="add('Little Rock Nine (1957)')">Little Rock 9</div><button class="explain-btn" onclick="getExplanation('Little Rock Nine')">💡</button></div>
                <div class="tag-row"><div class="tag" onclick="add('Jim Crow laws')">Jim Crow</div><button class="explain-btn" onclick="getExplanation('Jim Crow laws')">💡</button></div>
            </div>
        </div>

        <div id="explainer-window">
            <div style="font-weight:800; color:#a8dadc; font-size:11px; margin-bottom:8px; display:flex; justify-content:space-between;">
                <span>👨‍🏫 KNOWLEDGE EXPLORER</span>
                <span style="cursor:pointer" onclick="document.getElementById('explain-box').innerText='Select a topic...'">Reset</span>
            </div>
            <div id="explain-box">Click the 💡 button for detailed context.</div>
        </div>
    </div>

    <script>
        const ID = "{mid}";

        // --- 0. 全局状态 ---
        let currentLanguageMode = document.getElementById('language-setting').value || 'dual';
        let modules = []; // {{ id, type: 'intro'|'body'|'conclusion', boxes: [] }}
        let activeTextarea = null;

        const STORAGE_KEY = `GGV1_STATE::${{ID}}`;
        let saveDebounceTimer = null;

        // --- 0.1 实用函数 ---
        function getLanguageConstraint() {{
            if (currentLanguageMode === 'en') return "Constraint: You must respond in 100% English. Do not use any Chinese characters.";
            if (currentLanguageMode === 'zh') return "约束：必须 100% 使用中文回答，即使问题是英文。";
            return "约束：使用双语回答。采用‘中文核心解释 + 括号内对应英文专业术语’的格式。";
        }}

        function getCurrentQuestion() {{
            const title = document.getElementById('question-title');
            const text = (title?.innerText || "").trim();
            return text || "{question}";
        }}

        function setActiveTextarea(el) {{
            activeTextarea = el;
        }}

        // --- 0.2 模块与占位符 ---
        function makeModuleId() {{
            return 'm_' + Math.random().toString(36).slice(2, 9) + Date.now().toString(36);
        }}

        function getBoxConfig(type) {{
            if (type === 'intro') {{
                return [
                    {{ label: "Intro Box 1", placeholder: "Define issue & background... (e.g., The issue of [topic] was significant...)" }},
                    {{ label: "Intro Box 2", placeholder: "Show debate... (e.g., Historians have debated...)" }},
                    {{ label: "Intro Box 3", placeholder: "Thesis statement... (e.g., This essay will argue that...)" }}
                ];
            }} else if (type === 'conclusion') {{
                return [
                    {{ label: "Conclusion Box 1", placeholder: "Direct answer (In conclusion...)" }},
                    {{ label: "Conclusion Box 2", placeholder: "Weighting judgement (Their impact was mainly...)" }},
                    {{ label: "Conclusion Box 3", placeholder: "Final evaluation (While [success], [limitation]...)" }}
                ];
            }} else {{
                return [
                    {{ label: "PEEL Box 1", placeholder: "Point (One important way...)" }},
                    {{ label: "PEEL Box 2", placeholder: "Evidence (This can be seen in...)" }},
                    {{ label: "PEEL Box 3", placeholder: "Explain (This was important because...)" }},
                    {{ label: "PEEL Box 4", placeholder: "Link back (Therefore, this shows...)" }}
                ];
            }}
        }}

        function createEmptyModule(type) {{
            const cfg = getBoxConfig(type);
            return {{
                id: makeModuleId(),
                type,
                boxes: new Array(cfg.length).fill("")
            }};
        }}

        // --- 0.3 保存 / 恢复 ---
        function getState() {{
            return {{
                question: getCurrentQuestion(),
                language: currentLanguageMode,
                modules,
                updatedAt: Date.now()
            }};
        }}

        function saveToLocal() {{
            try {{
                localStorage.setItem(STORAGE_KEY, JSON.stringify(getState()));
            }} catch (e) {{}}
        }}

        function scheduleSave() {{
            if (saveDebounceTimer) clearTimeout(saveDebounceTimer);
            saveDebounceTimer = setTimeout(() => saveToLocal(), 2000);
        }}

        function loadFromLocal() {{
            try {{
                const raw = localStorage.getItem(STORAGE_KEY);
                if (!raw) return;
                const s = JSON.parse(raw);
                if (s.question) document.getElementById('question-title').innerText = s.question;
                if (s.language) {{
                    currentLanguageMode = s.language;
                    document.getElementById('language-setting').value = s.language;
                }}
                if (Array.isArray(s.modules) && s.modules.length) {{
                    modules = s.modules;
                }}
            }} catch (e) {{}}
        }}

        // --- 1. 模块渲染与编辑 ---
        function renderModules() {{
            const container = document.getElementById('essay-constructor');
            if (!container) return;

            if (!modules.length) {{
                container.innerHTML = '<div style="color:#6c757d; font-size:13px;">Use the buttons above to add an Intro, Body paragraph, or Conclusion.</div>';
                return;
            }}

            let bodyIndex = 0;
            const html = modules.map((m) => {{
                const cfg = getBoxConfig(m.type);
                let label = "";
                if (m.type === 'intro') label = "Intro";
                else if (m.type === 'conclusion') label = "Conclusion";
                else {{
                    bodyIndex += 1;
                    label = "Body Paragraph " + bodyIndex;
                }}

                const boxesHtml = cfg.map((boxCfg, idx) => {{
                    const value = (m.boxes && typeof m.boxes[idx] === 'string') ? m.boxes[idx] : "";
                    return `
                        <div class="editor-box">
                            <div class="label">${{boxCfg.label}}</div>
                            <textarea 
                                data-module="${{m.id}}" 
                                data-box="${{idx}}" 
                                placeholder="${{boxCfg.placeholder}}"
                                onfocus="setActiveTextarea(this)"
                                oninput="onBoxInput('${{m.id}}', ${{idx}}, this.value)"
                            >${{value}}</textarea>
                        </div>
                    `;
                }}).join("");

                return `
                    <div class="essay-module" data-id="${{m.id}}">
                        <div class="module-header">
                            <span class="module-tag">${{label}}</span>
                            <button class="module-delete" onclick="removeModule('${{m.id}}')">✕</button>
                        </div>
                        ${{boxesHtml}}
                    </div>
                `;
            }}).join("");

            container.innerHTML = html;
        }}

        function addModule(type) {{
            modules.push(createEmptyModule(type));
            renderModules();
            saveToLocal();
        }}

        function removeModule(id) {{
            modules = modules.filter(m => m.id !== id);
            renderModules();
            saveToLocal();
        }}

        function onBoxInput(id, index, value) {{
            const m = modules.find(m => m.id === id);
            if (!m) return;
            if (!Array.isArray(m.boxes)) m.boxes = [];
            m.boxes[index] = value;
            scheduleSave();
        }}

        // --- 2. 合并视图与全文构建 ---
        function buildEssayText() {{
            const parts = [];
            modules.forEach((m) => {{
                if (!Array.isArray(m.boxes)) return;
                const text = m.boxes.map(b => (b || "").trim()).filter(Boolean).join(" ");
                if (!text) return;
                let prefix = "";
                if (m.type === 'intro') prefix = "[Intro] ";
                else if (m.type === 'conclusion') prefix = "[Conclusion] ";
                else prefix = "[Body] ";
                parts.push(prefix + text);
            }});
            return parts.join("\\n\\n");
        }}

        function getStructureSummary() {{
            return modules.map((m) => ({{
                type: m.type,
                text: Array.isArray(m.boxes) ? m.boxes.join(" ").trim() : ""
            }}));
        }}

        function toggleMergeView() {{
            const panel = document.getElementById('merge-view');
            const box = document.getElementById('merge-content');
            if (!panel || !box) return;
            if (panel.style.display === 'none' || panel.style.display === '') {{
                box.value = buildEssayText();
                panel.style.display = 'block';
            }} else {{
                panel.style.display = 'none';
            }}
        }}

        // --- 3. 语言与自动保存事件 ---
        document.getElementById('language-setting').addEventListener('change', (e) => {{
            currentLanguageMode = e.target.value;
            saveToLocal();
        }});

        document.getElementById('question-title').addEventListener('blur', () => saveToLocal());

        // --- 4. 知识 Hub 插入：针对当前激活 textarea ---
        function add(text) {{
            if (!activeTextarea) return;
            const start = activeTextarea.selectionStart ?? activeTextarea.value.length;
            const end = activeTextarea.selectionEnd ?? start;
            const v = activeTextarea.value;
            activeTextarea.value = v.substring(0, start) + text + " " + v.substring(end);
            activeTextarea.focus();

            const mId = activeTextarea.getAttribute('data-module');
            const idxStr = activeTextarea.getAttribute('data-box');
            const idx = idxStr ? parseInt(idxStr, 10) : NaN;
            if (mId && !Number.isNaN(idx)) {{
                onBoxInput(mId, idx, activeTextarea.value);
            }}
        }}

        // --- 5. 侧边栏讲解老师 ---
        async function getExplanation(topic) {{
            const box = document.getElementById('explain-box');
            const lang = currentLanguageMode;
            const constraint = getLanguageConstraint();
            const essay_question = getCurrentQuestion();
            box.innerHTML = `<i style="color:#666">🔍 Searching...</i>`;
            try {{
                const response = await fetch('/api/explain', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ 
                        topic,
                        language: lang,
                        essay_question,
                        structure: getStructureSummary(),
                        constraint
                    }})
                }});
                const result = await response.json();
                box.innerText = result.explanation || "No explanation found.";
            }} catch (e) {{ box.innerText = "⚠️ Connection error."; }}
        }}

        // --- 6. 底部批改：整篇 Essay 级别 ---
        async function submitReview() {{
            const btn = document.getElementById('ai-btn');
            const resultDiv = document.getElementById('ai-review-result');
            const contentDiv = document.getElementById('ai-content');
            const essay_question = getCurrentQuestion();
            const constraint = getLanguageConstraint();
            const essay_full = buildEssayText();
            const structure = getStructureSummary();

            const data = {{ 
                essay_question,
                essay_full,
                structure,
                language: currentLanguageMode,
                constraint
            }};
            
            btn.innerText = "⌛ Teacher is grading..."; btn.disabled = true;
            resultDiv.style.display = 'block';
            resultDiv.scrollIntoView({{ behavior: 'smooth' }});

            try {{
                const response = await fetch('/api/review', {{ 
                    method: 'POST', 
                    headers: {{ 'Content-Type': 'application/json' }}, 
                    body: JSON.stringify(data) 
                }});
                const result = await response.json();
                contentDiv.innerText = result.review || "Feedback failed.";
            }} catch (e) {{ contentDiv.innerText = "⚠️ Connection failed."; }}
            finally {{ btn.innerText = "🚀 SUBMIT FOR AI TEACHER'S REVIEW"; btn.disabled = false; }}
        }}

        // 传统 SAVE / EXPORT 适配整篇 essay
        function save() {{
            saveToLocal();
            alert("Work Saved!");
        }}

        function exportDoc() {{
            const aiContent = document.getElementById('ai-content').innerText;
            const essayText = buildEssayText();
            const content = `WORK: ${{ID}}\\nQUESTION: ${{getCurrentQuestion()}}\\n\\n[ESSAY]\\n${{essayText}}\\n\\n[AI FEEDBACK]\\n${{aiContent}}`;
            const blob = new Blob([content], {{ type: 'text/plain' }});
            const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = `Submission_${{ID}}.txt`; a.click();
        }}

        // 初始恢复 + 默认 body 模块
        window.addEventListener('load', () => {{
            loadFromLocal();
            if (!modules.length) {{
                modules.push(createEmptyModule('body'));
            }}
            renderModules();
        }});
    </script>
</body>
</html>"""


def create_page(mid, question):
    html = HTML_TEMPLATE.format(mid=mid, question=question)
    with open(f"assets/missions/{mid}_workspace.html", "w", encoding="utf-8") as f:
        f.write(html)

missions = [
    ("CR_M1", "Assess the reasons for the opposition to the Civil Rights movement in the Southern states in the 1950s."),
    ("CR_M2", "Evaluate how successful the Civil Rights movement was in the 1950s."),
    ("CR_M3", "Assess the impact of federal institutions on civil rights in the late 1940s and 1950s."),
    ("CR_M4", "Analyse the effectiveness of the NAACP in promoting civil rights in the late 1940s and 1950s."),
    ("CR_M5", "'Progress towards greater civil rights in the 1950s was mainly brought about by federal institutions.' Evaluate this view.")
]

for m_id, q in missions:
    create_page(m_id, q)
    print(f">>> Updated: {m_id}")