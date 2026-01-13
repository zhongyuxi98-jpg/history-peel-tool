from geekgirl_visual.generator.sticker_generator import generate_svg, META_STICKERS
import os

def build_meta_pack():
    print("开始生成 [META] 元认知逻辑贴纸包...")
    output_dir = "assets/preview/v1.0-alpha/meta_logic"

    os.makedirs(output_dir, exist_ok=True)

    for item in META_STICKERS:
        # 构造文件名，例如: M1_CAUSE.svg
        file_name = f"{item['id']}_{item['type']}.svg"
        path = f"{output_dir}/{file_name}"

        # 调用 generate_svg
        generate_svg(
            level="L0",          # META 视觉用 L0 边框最稳
            title=item['text'],
            topic="META",
            period=None,
            output_path=path
        )

        print(f"✅ 已生成: {file_name}")

if __name__ == "__main__":
    build_meta_pack()
