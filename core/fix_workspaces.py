import os
import re

# 目标文件夹
target_dir = "assets/missions"

# 100% 安全的下载函数模板
def get_safe_js(mission_id):
    return f"""
    function downloadData() {{
        const p = document.getElementById('box-p1').value;
        const e1 = document.getElementById('box-e1').value;
        const e2 = document.getElementById('box-e2').value;
        const l = document.getElementById('box-l1').value;

        const text =
            "MISSION: {mission_id}\n\n" +
            "--- POINT ---\n" + p + "\n\n" +
            "--- EVIDENCE 1 ---\n" + e1 + "\n\n" +
            "--- EVIDENCE 2 ---\n" + e2 + "\n\n" +
            "--- LINK ---\n" + l;

        const blob = new Blob([text], {{ type: 'text/plain' }});
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = '{mission_id}_essay.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }}
    """

if os.path.exists(target_dir):
    for filename in os.listdir(target_dir):
        if filename.endswith("_workspace.html"):
            mission_id = filename.replace("_workspace.html", "")
            filepath = os.path.join(target_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # 使用正则替换整个 downloadData 函数
            pattern = r"function downloadData\(\) \{.*?\}\n"
            new_func = get_safe_js(mission_id)
            
            # 如果没搜到带换行的，尝试搜简单定义的
            fixed_content = re.sub(r"function downloadData\(\) \{.*?\}(?=\s*window\.onload)", new_func, content, flags=re.DOTALL)
            
            # 如果正则匹配失败，回退到更粗暴的替换方式（针对你目前的 HTML 结构）
            if fixed_content == content:
                # 寻找下载函数的位置并强制替换
                start_marker = "function downloadData()"
                end_marker = "window.onload"
                if start_marker in content:
                    parts = content.split(start_marker)
                    sub_parts = parts[1].split(end_marker)
                    fixed_content = parts[0] + new_func + "\n        " + end_marker + sub_parts[1]

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"✅ Fixed: {filename}")
else:
    print("❌ 找不到 assets/missions 文件夹，请在项目根目录运行。")

print("\n🚀 所有 HTML 修复完成！请刷新浏览器查看效果。")
