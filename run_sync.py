import os
import json
# 确保你的路径指向正确的 generator 文件
from geekgirl_visual.generator.sticker_generator import generate_svg

def main():
    # 1. 确认数据源路径
    json_path = "knowledge_base/civil_rights_mvp.json"
    if not os.path.exists(json_path):
        print(f"❌ 错误：找不到 {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 2. 确认输出目录
    output_dir = "assets/svg_mvp"
    os.makedirs(output_dir, exist_ok=True)

    print(f"🚀 正在为 {len(data)} 个知识点生成 MVP SVG 贴纸...")

    for item in data:
        level = item.get("level")
        title = item.get("title")
        # ✅ 新增：获取 topic 字段，若缺失则默认为 'civil_rights'
        topic = item.get("topic", "civil_rights")

        if not level or not title:
            print(f"  ⚠️ 跳过无效条目: {item}")
            continue

        # 3. 处理文件名安全字符
        safe_title = title.replace(" ", "_").replace("/", "_").replace(".", "")
        filename = f"{level}_{safe_title}.svg"
        output_path = os.path.join(output_dir, filename)

        # 4. ✅ 核心修正：传入 4 个参数 (level, title, topic, output_path)
        try:
            generate_svg(level, title, topic, output_path)
            print(f"  ✅ 已产出: {filename}")
        except Exception as e:
            print(f"  ❌ 生成失败 {title}: {e}")

    print(f"\n🔥 完成！MVP 贴纸已生成至：{output_dir}/")

if __name__ == "__main__":
    main()
