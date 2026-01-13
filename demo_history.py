# demo_history.py
from geekgirl_visual.generator.sticker_generator import generate_svg
  # 假设你的函数在这里
import os

# 模拟 Extractor 提取出的历史逻辑 JSON
history_nodes = [
    {"level": "L0", "title": "杜鲁门主义", "desc": "冷战正式开始标志"},
    {"level": "L1", "title": "马歇尔计划", "desc": "欧洲复兴"},
    {"level": "L4", "title": "莫洛托夫计划", "desc": "苏联的回应"}
]

for node in history_nodes:
    path = f"assets/svg/history_{node['title']}.svg"
    generate_svg(node['level'], node['title'], path)
    print(f"✅ 已生成历史原子贴纸: {path}")