TOPIC_COLORS = {
    "civil_rights": "#E85D4F",  # 珊瑚橙：民权运动
    "cold_war": "#4F6DE8",     # 宝蓝：冷战
    "economy": "#4FAE8A",      # 翡翠绿：经济
    "default": "#888888"
}

def get_topic_color(topic):
    return TOPIC_COLORS.get(topic.lower(), TOPIC_COLORS["default"])
