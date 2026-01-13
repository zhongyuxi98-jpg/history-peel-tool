import json

# 定义 Mission 数据
missions = {
    "CR_M1": {"title": "Opposition in the 1950s", "question": "Assess the reasons for the opposition to the Civil Rights movement in the Southern states in the 1950s."},
    "CR_M2": {"title": "Success in the 1950s", "question": "Evaluate how successful the Civil Rights movement was in the 1950s."},
    "CR_M3": {"title": "Federal Institutions", "question": "Assess the impact of federal institutions on civil rights in the late 1940s and 1950s."},
    "CR_M4": {"title": "NAACP Effectiveness", "question": "Analyse the effectiveness of the NAACP in promoting civil rights in the late 1940s and 1950s."},
    "CR_M5": {"title": "Federal vs Grassroots", "question": "'Progress towards greater civil rights in the 1950s was mainly brought about by federal institutions.' Evaluate this view."}
}

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Civil Rights Writing Hub</title>
    <style>
        body { font-family: 'Inter', -apple-system, sans-serif; background: #f0f2f5; color: #1d3557; display: flex; flex-direction: column; align-items: center; padding: 50px; }
        h1 { margin-bottom: 10px; font-size: 2.5em; }
        .subtitle { color: #457b9d; margin-bottom: 40px; font-size: 1.1em; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 25px; max-width: 1200px; width: 100%; }
        .card { 
            background: white; padding: 30px; border-radius: 15px; 
            box-shadow: 0 10px 20px rgba(0,0,0,0.05); cursor: pointer; 
            transition: all 0.3s ease; border: 1px solid #e1e4e8;
            display: flex; flex-direction: column; justify-content: space-between;
        }
        .card:hover { transform: translateY(-8px); box-shadow: 0 15px 30px rgba(0,0,0,0.1); border-color: #457b9d; }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .mid-badge { background: #f1faee; color: #e63946; padding: 4px 8px; border-radius: 5px; font-size: 0.8em; font-weight: bold; }
        .card h3 { margin: 0; font-size: 1.4em; color: #1d3557; }
        .card p { color: #495057; font-size: 0.95em; line-height: 1.5; font-style: italic; margin-top: 15px; border-top: 1px solid #eee; padding-top: 15px; }
        .footer-note { margin-top: 50px; font-size: 0.8em; color: #adb5bd; }
    </style>
</head>
<body>
    <h1>Civil Rights Writing Hub</h1>
    <p class="subtitle">Select a Mission to begin your PEEL writing practice.</p>
    <div class="grid">
"""

for mid, info in missions.items():
    html_content += f'''
        <div class="card" onclick="window.location.href='assets/missions/{{mid}}_workspace.html'">
            <div class="card-header">
                <h3>{{info['title']}}</h3>
                <span class="mid-badge">{{mid}}</span>
            </div>
            <p>"{{info['question']}}"</p>
        </div>
    '''

html_content += """
    </div>
    <p class="footer-note">GeekGirl Visual Engine v2.0 • Data-Driven Mode</p>
</body>
</html>
"""

with open("index.html", "w") as f:
    f.write(html_content)
print("✅ 首页 index.html 已完成精装修生成！")
