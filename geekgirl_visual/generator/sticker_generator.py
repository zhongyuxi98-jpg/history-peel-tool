import os

# 1. ✅ 离散色轴 (年代感颜色)
DISCRETE_PALETTE = {
    "P1": "#E63946",  # 1945-52: 深暖红
    "P2": "#F4A261",  # 1953-60: 暖橙
    "P3": "#E9C46A",  # 1961-68: 金黄 (Civil Rights 高峰)
    "P4": "#8AB17D",  # 1969-79: 橄榄绿 (转折期)
    "P5": "#2A9D8F",  # 1980-88: 青蓝 (保守主义)
    "P6": "#457B9D",  # 1989-2000: 冷蓝
    "FOREIGN": "#6D597A"
}

# 2. ✅ 单元图标映射 (增加 META 和 LINK 标签)
UNIT_ICONS = {
    "CIVIL_RIGHTS": "CR",
    "VIETNAM": "VN",
    "ECONOMY": "EC",
    "META": "PT",  # Point Template
    "LINK": "LK",  # Link Template (新增)
    "DEFAULT": "••"
}

# 3. ✅ 工程统一尺寸 (增加 LINK 尺寸)
SIZE_MAP = {
    "L0": (60, 30),
    "L1": (60, 30),
    "L2": (60, 30),
    "L3": (60, 30),
    "MECHANISM": (45, 18),
    "META": (60, 30),
    "LINK": (60, 15)  # 新增 Link 贴纸尺寸
}

# 4. ✅ META 元认知贴纸配置
META_CONFIG = {
    "color": "#1D3557",  # 深蓝
    "font_color": "#FFFFFF",  # 白字
    "label": "[META] Point Template"
}

# 5. ✅ LINK 元认知贴纸配置 (新增)
LINK_CONFIG = {
    "color": "#BDC3C7",  # 中性灰
    "font_color": "#1D3557",  # 深蓝字 (与 Point 呼应)
    "label": "[LINK] Link Back Template"
}


def wrap_text(text, max_chars=14):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        if len(cur + " " + w) <= max_chars:
            cur = (cur + " " + w).strip()
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines[:3]


def get_border_svg(level, w, h, is_meta=False, is_link=False):
    """
    边框逻辑：META 和 LINK 贴纸有特殊处理
    """
    if is_meta:
        return f'<rect x="2" y="2" width="{w - 4}" height="{h - 4}" rx="1" fill="none" stroke="white" stroke-width="0.3" stroke-opacity="0.5" />'
    if is_link:  # Link 使用更细的边框，或根据需要不显示边框
        return f'<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="1" fill="none" stroke="currentColor" stroke-width="0.5" stroke-dasharray="2,1" />'

    rect_base = f'<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="2" fill="none" '
    if level == "L0":
        inner = f'<rect x="3.5" y="3.5" width="{w - 7}" height="{h - 7}" rx="1" fill="none" stroke="currentColor" stroke-width="0.5"/>'
        return f'<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="2" fill="none" stroke="currentColor" stroke-width="1.5"/>' + inner
    elif level == "L1":
        return rect_base + 'stroke="currentColor" stroke-width="1.5" stroke-dasharray="4,2" />'
    elif level == "L2":
        return rect_base + 'stroke="currentColor" stroke-width="2" stroke-dasharray="1,2" />'
    elif level == "L3":
        return rect_base + 'stroke="currentColor" stroke-width="2.5" />'
    elif level == "MECHANISM":
        return rect_base + 'stroke="currentColor" stroke-width="1" />'
    return rect_base + 'stroke="currentColor" stroke-width="1" />'


def generate_svg(level, title, topic, period, output_path):
    # ✅ META 和 LINK 强制配色与标识判断
    is_meta = (topic == "META")
    is_link = (topic == "LINK")

    if is_meta:
        raw_color = META_CONFIG["color"]
        font_color = META_CONFIG["font_color"]
        unit_tag = UNIT_ICONS["META"]
        w, h = SIZE_MAP["META"]
        level_display = "POINT"  # META贴纸显示为POINT
    elif is_link:
        raw_color = LINK_CONFIG["color"]
        font_color = LINK_CONFIG["font_color"]
        unit_tag = UNIT_ICONS["LINK"]
        w, h = SIZE_MAP["LINK"]
        level_display = "LINK"  # LINK贴纸显示为LINK
    else:
        raw_color = "#9333EA" if level == "MECHANISM" else DISCRETE_PALETTE.get(period, "#333333")
        font_color = raw_color
        unit_tag = UNIT_ICONS.get(topic, UNIT_ICONS["DEFAULT"])
        w, h = SIZE_MAP.get(level, (60, 30))
        level_display = level

    # 背景逻辑处理
    bg_color = raw_color if (is_meta or is_link) else "white"

    # 字体与排版
    font_size = 4.8 if not is_link else 3.5  # Link贴纸字号稍小
    line_height = font_size * 1.2
    max_chars_for_link = 20  # Link贴纸可以容纳更多文字
    lines = wrap_text(title, max_chars=max_chars_for_link if is_link else (16 if (level == "L3" or is_meta) else 14))
    total_h = len(lines) * line_height
    start_y = (h / 2) - (total_h / 2) + (font_size * 0.85)

    text_content = ""
    for i, line in enumerate(lines):
        text_content += f'<text x="{w / 2}" y="{start_y + i * line_height}" text-anchor="middle" font-family="Arial, sans-serif" font-size="{font_size}" font-weight="bold" fill="{font_color}">{line}</text>'

    # 组装 SVG
    svg_content = f'''<svg width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">
        <rect width="{w}" height="{h}" fill="{bg_color}" stroke="#EEEEEE" stroke-width="0.2" rx="2" />
        <g color="{raw_color}">
            {get_border_svg(level, w, h, is_meta, is_link)}
            {text_content}
            <text x="3" y="6.5" font-family="Arial" font-size="2.5" fill="{font_color}" fill-opacity="0.6">[{level_display}]</text>
            <g transform="translate({w - 10}, 2.5)">
                <rect width="7.5" height="4.5" rx="1" fill="{font_color}" fill-opacity="0.1" />
                <text x="3.75" y="3.3" text-anchor="middle" font-family="Arial" font-size="2.8" font-weight="bold" fill="{font_color}">{unit_tag}</text>
            </g>
        </g>
    </svg>'''

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    return w, h


# =========================
# LINK: 元认知贴纸数据 (新增)
# =========================
LINK_STICKERS = [
    {"id": "L1", "type": "DIRECT", "text": "This directly proves that the core argument of..."},
    {"id": "L2", "type": "IMPACT", "text": "Therefore, this highlights the profound impact of..."},
    {"id": "L3", "type": "SUMMARY", "text": "In conclusion, this evidence strongly supports..."},
    {"id": "L4", "type": "BALANCE", "text": "While some argue [X], this demonstrates [Y] was more..."},
    {"id": "L5", "type": "FUTURE", "text": "This laid the crucial groundwork for future developments in..."}
]
