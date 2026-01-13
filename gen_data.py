import json
import os

civil_rights_data = [
    # L0: Concepts
    {"level": "L0", "title": "Civil Rights Movement", "attr": "Concept"},
    {"level": "L0", "title": "Federal Institutions", "attr": "Concept"},

    # L1: Events
    {"level": "L1", "title": "Brown v. Board 1954", "attr": "Event"},
    {"level": "L1", "title": "Little Rock Nine 1957", "attr": "Event"},
    {"level": "L1", "title": "Montgomery Bus Boycott", "attr": "Event"},

    # L2: Actors
    {"level": "L2", "title": "NAACP", "attr": "Actor"},
    {"level": "L2", "title": "MLK / SCLC", "attr": "Actor"},
    {"level": "L2", "title": "Eisenhower", "attr": "Actor"},

    # L3: Institutional
    {"level": "L3", "title": "Jim Crow Laws", "attr": "Institutional"},
    {"level": "L3", "title": "Civil Rights Act 1964", "attr": "Institutional"},

    # L4: Evaluation
    {"level": "L4", "title": "Success vs Failure", "attr": "Eval"},
    {"level": "L4", "title": "Southern Resistance", "attr": "Eval"},

    # Mechanisms
    {"level": "MECHANISM", "title": "Federal Enforcement", "attr": "Mech"},
    {"level": "MECHANISM", "title": "Media Exposure", "attr": "Mech"},
    {"level": "MECHANISM", "title": "Implementation Gap", "attr": "Mech"}
]

os.makedirs("knowledge_base", exist_ok=True)

with open("knowledge_base/civil_rights.json", "w", encoding="utf-8") as f:
    json.dump(civil_rights_data, f, ensure_ascii=False, indent=2)

print("✅ 第一步完成：civil_rights.json 已生成到 knowledge_base 目录。")
