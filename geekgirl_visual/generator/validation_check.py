import json
import os

VALID_LEVELS = ["L0", "L1", "L2", "L3", "MECHANISM"]
VALID_PERIODS = ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "FOREIGN"]
VALID_TOPICS = ["CIVIL_RIGHTS", "VIETNAM", "ECONOMY", "FOREIGN_POLICY"]

def validate_knowledge_base(file_path):
    if not os.path.exists(file_path):
        print(f"❌ 找不到文件: {file_path}")
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print("❌ JSON 格式错误")
            return False

    errors = []

    for i, item in enumerate(data):
        title = item.get("title", "Unknown")

        lv = item.get("level")
        if lv not in VALID_LEVELS:
            errors.append(f"{title}: Level {lv} 不合法")

        pd = item.get("period")
        if pd not in VALID_PERIODS:
            errors.append(f"{title}: Period {pd} 不合法")

        tp = item.get("topic")
        if tp not in VALID_TOPICS:
            errors.append(f"{title}: Topic {tp} 不合法")

    if errors:
        print("🚨 发现数据错误：")
        for e in errors:
            print(" -", e)
        return False

    print("✅ JSON 质检通过")
    return True

