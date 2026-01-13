import json
import os

# 加载你的黄金数据
def load_data():
    # 假设数据在 knowledge_base/civil_rights_mvp.json
    with open('knowledge_base/civil_rights_mvp.json', 'r') as f:
        content = f.read()
        # 处理可能的混合格式（去掉 Python 变量名部分，只取 JSON 列表）
        if "CIVIL_RIGHTS_MISSIONS =" in content:
            # 如果是混合格式，我们手动提取 Mission 字典
            # 这里简单起见，直接定义在脚本里或确保 JSON 纯净
            pass
    
    # 直接使用你刚刚 cat 出来的 Mission 数据
    missions = {
        "CR_M1": {"question": "Assess the reasons for the opposition to the Civil Rights movement in the Southern states in the 1950s."},
        "CR_M2": {"question": "Evaluate how successful the Civil Rights movement was in the 1950s."},
        "CR_M3": {"question": "Assess the impact of federal institutions on civil rights in the late 1940s and 1950s."},
        "CR_M4": {"question": "Analyse the effectiveness of the NAACP in promoting civil rights in the late 1940s and 1950s."},
        "CR_M5": {"question": "'Progress towards greater civil rights in the 1950s was mainly brought about by federal institutions.' Evaluate this view."}
    }
    return missions

def generate_html(mid, data):
    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Workspace - {mid}</title>
    <style>
        body {{ font-family: 'Inter', sans-serif; background: #f8f9fa; display: flex; height: 100vh; margin: 0; }}
        .main-content {{ flex: 1; padding: 40px; overflow-y: auto; }}
        .sidebar {{ width: 300px; background: #fff; border-left: 1px solid #ddd; padding: 20px; box-shadow: -2px 0 5px rgba(0,0,0,0.05); }}
        .header {{ border-bottom: 2px solid #1d3557; margin-bottom: 20px; padding-bottom: 10px; }}
        .mission-id {{ color: #666; font-size: 12px; text-transform: uppercase; }}
        .question {{ font-size: 20px; font-weight: bold; color: #1d3557; margin-top: 5px; }}
        .editor-group {{ margin-bottom: 20px; }}
        .label {{ color: #e63946; font-weight: bold; font-size: 12px; margin-bottom: 5px; }}
        textarea {{ width: 100%; height: 100px; border: 1px solid #ccc; border-radius: 8px; padding: 12px; font-size: 14px; resize: vertical; }}
        .nav-btns {{ margin-bottom: 20px; display: flex; gap: 10px; }}
        button {{ padding: 8px 15px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }}
        .btn-save {{ background: #2a9d8f; color: white; }}
        .btn-export {{ background: #f4a261; color: white; }}
        .btn-menu {{ background: #457b9d; color: white; }}
        .tag {{ display: inline-block; background: #1d3557; color: white; padding: 4px 10px; border-radius: 4px; font-size: 12px; margin: 3px; cursor: pointer; }}
        .tag-section {{ margin-bottom: 20px; }}
        .tag-section h4 {{ border-left: 4px solid #1d3557; padding-left: 8px; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="main-content">
        <div class="nav-btns">
            <button class="btn-save" onclick="saveData()">💾 SAVE</button>
            <button class="btn-export" onclick="exportData()">📥 EXPORT</button>
            <button class="btn-menu" onclick="window.location.href='../../index.html'">🏠 MENU</button>
        </div>
        <div class="header">
            <div class="mission-id">Mission ID: {mid}</div>
            <div class="question">{data['question']}</div>
        </div>
        
        <div class="editor-group">
            <div class="label">1. POINT (THESIS STATEMENT)</div>
            <textarea id="point" placeholder="Start with a strong point..."></textarea>
        </div>
        <div class="editor-group">
            <div class="label">2. EVIDENCE 1 + MECHANISM</div>
            <textarea id="ev1" placeholder="Provide evidence and explain WHY it matters..."></textarea>
        </div>
        <div class="editor-group">
            <div class="label">3. EVIDENCE 2 + MECHANISM</div>
            <textarea id="ev2" placeholder="Deepen the analysis with more evidence..."></textarea>
        </div>
        <div class="editor-group">
            <div class="label">4. LINK BACK</div>
            <textarea id="link" placeholder="Connect back to the original question..."></textarea>
        </div>
    </div>

    <div class="sidebar">
        <h3>Knowledge Hub</h3>
        <p style="font-size: 11px; color: #666;">Click tags to inspire your writing.</p>
        <div class="tag-section">
            <h4>Evidence Pool</h4>
            <div class="tag" onclick="insertText('Montgomery Bus Boycott')">Montgomery Bus Boycott</div>
            <div class="tag" onclick="insertText('Little Rock Nine 1957')">Little Rock Nine</div>
            <div class="tag" onclick="insertText('Brown v Board 1954')">Brown v Board</div>
        </div>
        <div class="tag-section">
            <h4>Logic Mechanism</h4>
            <div class="tag" style="background: #8338ec" onclick="insertText('Federal Enforcement')">Federal Enforcement</div>
            <div class="tag" style="background: #8338ec" onclick="insertText('Media Exposure')">Media Exposure</div>
        </div>
    </div>

    <script>
        const mid = "{mid}";
        function saveData() {{
            const data = {{
                point: document.getElementById('point').value,
                ev1: document.getElementById('ev1').value,
                ev2: document.getElementById('ev2').value,
                link: document.getElementById('link').value
            }};
            localStorage.setItem(mid, JSON.stringify(data));
            alert("Draft saved locally!");
        }}

        window.onload = function() {{
            const saved = localStorage.getItem(mid);
            if (saved) {{
                const data = JSON.parse(saved);
                document.getElementById('point').value = data.point || "";
                document.getElementById('ev1').value = data.ev1 || "";
                document.getElementById('ev2').value = data.ev2 || "";
                document.getElementById('link').value = data.link || "";
            }}
        }};

        function exportData() {{
            const p = document.getElementById('point').value;
            const e1 = document.getElementById('ev1').value;
            const e2 = document.getElementById('ev2').value;
            const l = document.getElementById('link').value;
            const text = `MISSION: {mid}\\nQUESTION: {data['question']}\\n\\n[POINT]\\n${{p}}\\n\\n[EVIDENCE 1]\\n${{e1}}\\n\\n[EVIDENCE 2]\\n${{e2}}\\n\\n[LINK]\\n${{l}}`;
            const blob = new Blob([text], {{ type: 'text/plain' }});
            const anchor = document.createElement('a');
            anchor.download = `{mid}_draft.txt`;
            anchor.href = window.URL.createObjectURL(blob);
            anchor.click();
        }}

        function insertText(text) {{
            const active = document.activeElement;
            if (active.tagName === "TEXTAREA") {{
                active.value += text + " ";
            }}
        }}
    </script>
</body>
</html>
"""
    with open(f"assets/missions/{mid}_workspace.html", "w") as f:
        f.write(html_template)

# 执行生成
missions = load_data()
for mid, data in missions.items():
    generate_html(mid, data)
print("✅ Day 03 精装版页面已全部生成至 assets/missions/")