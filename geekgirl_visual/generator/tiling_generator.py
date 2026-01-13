VERSION = "v1.0-alpha"
MODULE_NAME = "civil_rights"
OUTPUT_DIR = f"assets/preview/{VERSION}/{MODULE_NAME}"
import json
import os
import sys

# =========================
# 路径与模块导入设置
# =========================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sticker_generator import get_border_svg, SIZE_MAP, wrap_text
from geekgirl_visual.tokens.topics import get_topic_color

# （可选）开启 JSON 质量校验
try:
    from geekgirl_visual.generator.validation_check import validate_knowledge_base
    ENABLE_VALIDATION = True
except Exception:
    ENABLE_VALIDATION = False


# =========================
# 主函数
# =========================

def run_tiling():
    # 1. 路径设置
    json_path = os.path.join(PROJECT_ROOT, "knowledge_base", "civil_rights_mvp.json")
    output_dir = os.path.join(PROJECT_ROOT, "assets", "preview")

    if not os.path.exists(json_path):
        print(f"❌ 错误：找不到数据源 {json_path}")
        return

    # 2. JSON 质量校验（如启用）
    if ENABLE_VALIDATION:
        print("🔍 运行数据质检...")
        ok = validate_knowledge_base(json_path)
        if not ok:
            print("❌ JSON 数据未通过校验，终止生成")
            return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # =========================
    # 拼版参数
    # =========================

    PAGE_W, PAGE_H = 210, 297
    CELL_W, CELL_H = 62, 34
    COLS, ROWS = 3, 8

    MARGIN_LEFT = 12
    MARGIN_TOP = 15
    GAP_X = 2
    GAP_Y = 2

    os.makedirs(output_dir, exist_ok=True)

    HEADER = f'<svg width="{PAGE_W}mm" height="{PAGE_H}mm" viewBox="0 0 {PAGE_W} {PAGE_H}" xmlns="http://www.w3.org/2000/svg">'

    def start_new_page():
        return HEADER + '<rect width="100%" height="100%" fill="white"/>'

    current_page_idx = 1
    content = start_new_page()

    print(f"🚀 正在拼版：3x8 长方形阵列 (60x30mm)... 项目共 {len(data)} 个词条")

    # =========================
    # 主循环
    # =========================

    for i, item in enumerate(data):
        idx_on_page = i % (COLS * ROWS)

        if i > 0 and idx_on_page == 0:
            page_path = os.path.join(output_dir, f"sheet_{current_page_idx}.svg")
            with open(page_path, "w", encoding="utf-8") as f:
                f.write(content + "</svg>")

            current_page_idx += 1
            content = start_new_page()

        col = idx_on_page % COLS
        row = idx_on_page // COLS

        x_pos = MARGIN_LEFT + col * (CELL_W + GAP_X)
        y_pos = MARGIN_TOP + row * (CELL_H + GAP_Y)

        lv = item.get("level")
        tit = item.get("title")
        top = item.get("topic")

        sticker_w, sticker_h = SIZE_MAP.get(lv, (60, 30))

        offset_x = x_pos + (CELL_W - sticker_w) / 2
        offset_y = y_pos + (CELL_H - sticker_h) / 2

        color = "#9333EA" if lv == "MECHANISM" else get_topic_color(top)

        content += f'\n<g transform="translate({offset_x},{offset_y})">'
        content += f'<rect width="{sticker_w}" height="{sticker_h}" fill="white" stroke="#EEE" stroke-width="0.1" rx="2" />'
        content += f'<g color="{color}">{get_border_svg(lv, sticker_w, sticker_h)}'

        # 文本
        f_size = 4.8 if lv != "MECHANISM" else 3.8
        lines = wrap_text(tit, max_chars=14 if lv != "L3" else 16)

        total_text_h = len(lines) * f_size * 1.2
        text_start_y = (sticker_h / 2) - (total_text_h / 2) + (f_size * 0.85)

        for j, line in enumerate(lines):
            content += (
                f'<text x="{sticker_w/2}" y="{text_start_y + j*f_size*1.2}" '
                f'text-anchor="middle" font-family="Arial" font-size="{f_size}" '
                f'font-weight="bold" fill="{color}">{line}</text>'
            )

        # 角标
        content += f'<text x="2" y="5" font-family="Arial" font-size="2" fill="{color}" fill-opacity="0.6">[{lv}]</text>'
        content += '</g></g>'

    # =========================
    # 写入最后一页
    # =========================

    final_path = os.path.join(output_dir, f"sheet_{current_page_idx}.svg")
    with open(final_path, "w", encoding="utf-8") as f:
        f.write(content + "</svg>")

    print(f"✅ 拼版完成！预览: {final_path}")


# =========================
# 入口
# =========================

if __name__ == "__main__":
    run_tiling()

