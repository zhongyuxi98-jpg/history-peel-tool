import os

MISSIONS_DATA = {
    "CR_M1": {"name": "Opposition to Civil Rights", "tags": ["White Citizens' Councils", "Southern Manifesto", "Social Inertia", "KKK"]},
    "CR_M2": {"name": "Success in 1950s", "tags": ["Montgomery Bus Boycott", "1957 Act", "Reality Gap", "Emmett Till"]},
    "CR_M3": {"name": "Federal Institutions", "tags": ["EO 9981", "Brown v. Board", "Little Rock Nine", "Supreme Court"]},
    "CR_M4": {"name": "NAACP Effectiveness", "tags": ["Thurgood Marshall", "Litigation", "Sweatt v. Painter", "Legal Fund"]},
    "CR_M5": {"name": "Federal vs Grassroots", "tags": ["SCLC & CORE", "Executive Action", "Grassroots Pressure", "L3 Strategy"]}
}

# 这里的 MENU 链接我改成了相对 assets/missions 文件夹的正确跳级
TEMPLATE = """<!DOCTYPE html>
<html lang="en" translate="no">
<head>
    <meta charset="UTF-8"><title>{id} Workspace</title>
    <style>
        body {{ display: flex; height: 100vh; margin: 0; font-family: sans-serif; background: #f0f2f5; }}
        .left {{ flex: 1; padding: 25px; overflow-y: auto; background: white; }}
        .right {{ width: 300px; padding: 20px; background: #e9ecef; border-left: 1px solid #ccc; }}
        textarea {{ width: 100%; height: 90px; margin: 10px 0 15px 0; border: 1px solid #bbb; border-radius: 6px; padding: 12px; font-size: 15px; box-sizing: border-box; }}
        .btn {{ padding: 10px 15px; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; margin-right: 5px; }}
        .tag {{ background: #1d3557; color: white; padding: 6px 10px; margin: 4px; display: inline-block; cursor: pointer; border-radius: 4px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="left">
        <div style="margin-bottom:20px;">
            <button class="btn" style="background:#2a9d8f" onclick="saveData()">💾 SAVE</button>
            <button class="btn" style="background:#e76f51" onclick="downloadData()">📥 EXPORT</button>
            <button class="btn" style="background:#457b9d" onclick="goHome()">🏠 MENU</button>
        </div>
        <h2>{name} ({id})</h2>
        <textarea id="p1" onfocus="window.cur='p1'" placeholder="POINT"></textarea>
        <textarea id="e1" onfocus="window.cur='e1'" placeholder="EVIDENCE 1"></textarea>
        <textarea id="e2" onfocus="window.cur='e2'" placeholder="EVIDENCE 2"></textarea>
        <textarea id="l1" onfocus="window.cur='l1'" placeholder="LINK"></textarea>
    </div>
    <div class="right"><h3>Knowledge Hub</h3>{tags_html}</div>
    <script>
        window.cur = 'p1';
        function goHome() {{
            // 尝试返回根目录的 index.html
            window.location.href = '../../index.html';
        }}
        function insertTag(t) {{
            const el = document.getElementById(window.cur);
            el.value += t; saveData();
        }}
        function saveData() {{
            const d = {{p:document.getElementById('p1').value, e1:document.getElementById('e1').value, e2:document.getElementById('e2').value, l:document.getElementById('l1').value}};
            localStorage.setItem('draft_{id}', JSON.stringify(d));
        }}
        function downloadData() {{
            const p=document.getElementById('p1').value, e1=document.getElementById('e1').value, e2=document.getElementById('e2').value, l=document.getElementById('l1').value;
            const content = "MISSION: {id}\\n\\nPOINT:\\n"+p+"\\n\\nEVIDENCE:\\n"+e1+"\\n"+e2+"\\n\\nLINK:\\n"+l;
            const blob = new Blob([content], {{ type: 'text/plain' }});
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = '{id}_draft.txt';
            document.body.appendChild(a); a.click(); document.body.removeChild(a);
        }}
        window.onload = function() {{
            const s = localStorage.getItem('draft_{id}');
            if(s) {{
                const d = JSON.parse(s);
                document.getElementById('p1').value = d.p || '';
                document.getElementById('e1').value = d.e1 || '';
                document.getElementById('e2').value = d.e2 || '';
                document.getElementById('l1').value = d.l || '';
            }}
        }};
    </script>
</body>
</html>"""

os.makedirs("assets/missions", exist_ok=True)
for mid, info in MISSIONS_DATA.items():
    ev_list = []
    for t in info["tags"]:
        tag_str = '<div class="tag" onclick="insertTag(\'' + t + '\')">' + t + '</div>'
        ev_list.append(tag_str)
    tags_html = "".join(ev_list)
    filepath = os.path.join("assets/missions", mid + "_workspace.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(TEMPLATE.format(id=mid, name=info["name"], tags_html=tags_html))

print("🎉 DONE! Please refresh your browser.")