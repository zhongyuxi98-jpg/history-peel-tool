import os

def create_page(mid, question):
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>PEEL Workspace - {mid}</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #f4f7f6; display: flex; height: 100vh; margin: 0; color: #333; }}
        .main {{ flex: 1; padding: 40px; overflow-y: auto; }}
        .sidebar {{ width: 340px; background: #fff; border-left: 1px solid #dee2e6; padding: 25px; box-shadow: -5px 0 15px rgba(0, 0, 0, 0.05); overflow-y: auto; }}
        .sidebar.hidden {{ display: none; }}
        .header {{ border-bottom: 3px solid #1d3557; margin-bottom: 30px; padding-bottom: 15px; }}
        .q-text {{ font-size: 20px; font-weight: 700; color: #1d3557; }}
        .nav-bar {{ margin-bottom: 25px; display: flex; gap: 10px; }}
        button {{ padding: 10px 18px; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; color: white; transition: 0.2s; }}
        .btn-save {{ background: #2a9d8f; }}
        .btn-export {{ background: #f4a261; }}
        .btn-menu {{ background: #457b9d; }}
        button:hover {{ opacity: 0.9; transform: translateY(-1px); }}
        .editor-box {{ margin-bottom: 20px; }}
        .label {{ color: #e63946; font-size: 11px; font-weight: 800; text-transform: uppercase; margin-bottom: 5px; }}
        textarea {{ width: 100%; height: 95px; border: 1.5px solid #ced4da; border-radius: 8px; padding: 12px; font-size: 14px; resize: none; line-height: 1.5; }}
        .kb-section {{ margin-bottom: 25px; }}
        .sec-title {{ font-size: 12px; font-weight: 800; color: #1d3557; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-bottom: 10px; display: flex; align-items: center; gap: 5px; }}
        .tag-group {{ display: flex; flex-wrap: wrap; gap: 6px; }}
        .tag {{ padding: 6px 12px; border-radius: 4px; font-size: 12px; cursor: pointer; border: 1px solid #ddd; background: #fff; transition: 0.2s; border-left: 4px solid #ddd; }}
        .tag:hover {{ background: #1d3557; color: white; transform: scale(1.05); }}
        .ctx {{ border-left-color: #457b9d; }}
        .entity {{ border-left-color: #e63946; }}
        .impact {{ border-left-color: #2a9d8f; }}
        .hist {{ border-left-color: #8338ec; }}
    </style>
</head>

<body>
    <div class="main">
        <div class="nav-bar">
            <button class="btn-save" onclick="save()">💾 SAVE</button>
            <button class="nav-btn ai-btn" id="ai-btn" onclick="reviewAI()" style="background: #007bff; color: white;">🤖 AI Review</button>
            <select id="language-setting" style="padding: 10px; border-radius: 6px; border: 1.5px solid #007bff; background: white; font-weight: 600; cursor: pointer;">
                <option value="dual" selected>🌓 双语 (Bilingual)</option>
                <option value="en">🇬🇧 外教 (English Only)</option>
                <option value="zh">🇨🇳 中教 (Chinese)</option>
            </select>
            <button class="btn-export" onclick="exportDoc()">📥 EXPORT</button>
            <button class="btn-menu" onclick="location.href='../../index.html'">🏠 MENU</button>
            <button class="btn-menu" style="background:#6c757d;" onclick="toggleHub()">📂 HUB</button>
        </div>

        <div class="header">
            <div style="color:#6c757d; font-size:11px; margin-bottom:5px;">MISSION ID: {mid}</div>
            <div class="q-text">{question}</div>
        </div>

        <div class="editor-box"><div class="label">1. Point (Thesis Statement)</div><textarea id="p"></textarea></div>
        <div class="editor-box"><div class="label">2. Evidence 1 + Mechanism</div><textarea id="e1"></textarea></div>
        <div class="editor-box"><div class="label">3. Evidence 2 + Mechanism</div><textarea id="e2"></textarea></div>
        <div class="editor-box"><div class="label">4. Link Back</div><textarea id="l"></textarea></div>

        <div id="ai-review-result" style="display: none; margin-top: 30px; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.15); border: 1px solid #ddd;">
            <div style="background: #2d3436; color: white; padding: 12px 20px; font-weight: bold; display: flex; justify-content: space-between; align-items: center;">
                <span>🤖 AI TEACHER'S RESPONSE</span>
                <button onclick="document.getElementById('ai-review-result').style.display='none'" style="background:none; border:none; color:white; cursor:pointer; font-size:20px;">×</button>
            </div>
            <div id="ai-content" style="background: #fff; padding: 25px; line-height: 1.8; color: #2d3436; min-height: 100px; white-space: pre-wrap;">AI is thinking...</div>
        </div>
    </div>

    <div class="sidebar">
        <h3 style="margin:0 0 5px 0; color:#1d3557;">Knowledge Hub</h3>
        <p style="font-size:10px; color:#666; margin-bottom:15px;">💡 Left-click to use | Right-click for AI Guide</p>
        <div class="kb-section">
            <div class="sec-title">⚖️ LEGAL MILESTONES</div>
            <div class="tag-group">
                <div class="tag ctx" onclick="add('Plessy v. Ferguson')" oncontextmenu="explain(event, 'Plessy v. Ferguson')">Plessy v. Ferguson</div>
                <div class="tag ctx" onclick="add('Brown v. Board')" oncontextmenu="explain(event, 'Brown v. Board 1954')">Brown v. Board</div>
                <div class="tag ctx" onclick="add('Brown II')" oncontextmenu="explain(event, 'Brown II 1955')">Brown II</div>
            </div>
        </div>
        <div class="kb-section">
            <div class="sec-title">✊ DIRECT ACTION</div>
            <div class="tag-group">
                <div class="tag entity" onclick="add('Montgomery Bus Boycott')" oncontextmenu="explain(event, 'Montgomery Bus Boycott')">Bus Boycott</div>
                <div class="tag entity" onclick="add('Little Rock 9')" oncontextmenu="explain(event, 'Little Rock Nine 1957')">Little Rock 9</div>
                <div class="tag entity" onclick="add('Emmett Till')" oncontextmenu="explain(event, 'Emmett Till Case')">Emmett Till</div>
            </div>
        </div>
    </div>

    <script>
        const ID = "{mid}";
        let activeEditor = document.getElementById('p');

        document.querySelectorAll('textarea').forEach(tx => {{ tx.onfocus = () => activeEditor = tx; }});

        function add(text) {{
            const start = activeEditor.selectionStart;
            activeEditor.value = activeEditor.value.substring(0, start) + text + " " + activeEditor.value.substring(start);
            activeEditor.focus();
        }}

        // --- 核心：右键讲解功能 ---
        async function explain(event, topic) {{
            event.preventDefault(); // 阻止浏览器菜单
            const resDiv = document.getElementById('ai-review-result');
            const conDiv = document.getElementById('ai-content');
            resDiv.style.display = 'block';
            conDiv.innerText = "🔍 AI正在查阅史料档案: " + topic + "...";
            
            try {{
                const response = await fetch('/api/explain', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ topic: topic }})
                }});
                const result = await response.json();
                conDiv.innerText = result.explanation || "未找到相关讲解";
            }} catch (e) {{
                conDiv.innerText = "⚠️ 连接失败，请确保后端服务已启动并支持 /api/explain";
            }}
        }}

        async function reviewAI() {{
            const btn = document.getElementById('ai-btn');
            const resultDiv = document.getElementById('ai-review-result');
            const contentDiv = document.getElementById('ai-content');
            const data = {{ point: document.getElementById('p').value, e1: document.getElementById('e1').value, e2: document.getElementById('e2').value, l: document.getElementById('l').value }};
            btn.innerText = "⌛ Thinking..."; btn.disabled = true;
            resultDiv.style.display = 'block';
            try {{
                const response = await fetch('/api/review', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify(data) }});
                const result = await response.json();
                contentDiv.innerText = result.review || "反馈生成失败";
            }} catch (e) {{ contentDiv.innerText = "⚠️ 连接失败"; }}
            finally {{ btn.innerText = "🤖 AI Review"; btn.disabled = false; }}
        }}

        function save() {{
            const data = {{ p: document.getElementById('p').value, e1: document.getElementById('e1').value, e2: document.getElementById('e2').value, l: document.getElementById('l').value }};
            localStorage.setItem(ID, JSON.stringify(data));
            alert("Draft Saved!");
        }}
        function toggleHub() {{ document.querySelector('.sidebar').classList.toggle('hidden'); }}
    </script>
</body>
</html>"""
    with open(f"assets/missions/{{mid}}_workspace.html", "w", encoding="utf-8") as f:
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
    print(f">>> Successfully updated: {{m_id}}")