from sticker_generator import generate_svg, LINK_STICKERS


def build_link_pack():
    print("开始生成 [LINK] 元认知回扣贴纸包...")
    output_dir = "assets/preview/v1.0-alpha/meta_logic"  # 与 META 统一目录

    for item in LINK_STICKERS:
        # 构造文件名，例如: LK1_DIRECT.svg
        file_name = f"LK{item['id']}_{item['type']}.svg"
        path = f"{output_dir}/{file_name}"

        generate_svg(
            level="LINK",
            title=item["text"],
            topic="LINK",
            period=None,
            output_path=path
        )

        print(f"✅ 已生成: {file_name}")


if __name__ == "__main__":
    build_link_pack()
