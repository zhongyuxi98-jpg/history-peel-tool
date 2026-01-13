# geekgirl_visual/tokens/colors.py

# 重新定义层级能量 (Level Energy)
# L0 (核心): 暖色调, 极高亮度, 极高饱和度
# L4 (边缘): 冷色调, 低亮度, 低饱和度
LEVEL_MAPPING = {
    "L0": {"hue_shift": 0, "lightness": 0.50, "saturation": 1.0},  # 能量中心 (红/暖)
    "L1": {"hue_shift": 30, "lightness": 0.45, "saturation": 0.8},  # 橙/黄
    "L2": {"hue_shift": 120, "lightness": 0.40, "saturation": 0.6},  # 绿/中性
    "L3": {"hue_shift": 200, "lightness": 0.35, "saturation": 0.5},  # 蓝/冷
    "L4": {"hue_shift": 240, "lightness": 0.30, "saturation": 0.3}  # 深紫/冷灰 (最不重要)
}


def get_sticker_color(level):
    """
    基于人类本能的颜色计算：越重要越暖/越亮
    """
    config = LEVEL_MAPPING.get(level, LEVEL_MAPPING["L2"])
    h = config["hue_shift"] / 360.0
    s = config["saturation"]
    l = config["lightness"]

    import colorsys
    rgb = colorsys.hls_to_rgb(h, l, s)
    return '#%02x%02x%02x' % tuple(int(x * 255) for x in rgb)