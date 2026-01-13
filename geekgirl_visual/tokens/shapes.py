# demo_history.py
from geekgirl_visual.generator.svg_generator import generate_svg
import os

history_nodes = [
    {"level": "L0", "title": "杜鲁门主义", "desc": "冷战正式开始标志"},
    {"level": "L1", "title": "马歇尔计划", "desc": "欧洲复兴"},
    {"level": "L4", "title": "莫洛托夫计划", "desc": "苏联的回应"}
]

os.makedirs("assets/svg", exist_ok=True)

for node in history_nodes:
    filename = f"history_{node['title']}.svg"
    path = os.path.join("assets", "svg", filename)
    generate_svg(node["level"], node["title"], path)
    print(f"✅ 已生成历史原子贴纸: {path}")
