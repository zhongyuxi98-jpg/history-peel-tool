import os


def get_template():
    """读取 HTML 模板文件"""
    with open('core/mission_template.html', 'r', encoding='utf-8') as f:
        return f.read()


def create_page(mid, question):
    html = get_template().replace('{mid}', mid).replace('{question}', question)
    with open(f"assets/missions/{mid}_workspace.html", "w", encoding="utf-8") as f:
        f.write(html)

missions = [
    ("CR_M1", "Assess the reasons for the opposition to the Civil Rights movement in the Southern states in the 1950s."),
    ("CR_M2", "Evaluate how successful the Civil Rights movement was in the 1950s."),
    ("CR_M3", "Assess the impact of federal institutions on civil rights in the late 1940s and 1950s."),
    ("CR_M4", "Analyse the effectiveness of the NAACP in promoting civil rights in the late 1940s and 1950s."),
    ("CR_M5", "'Progress towards greater civil rights in the 1950s was mainly brought about by federal institutions.' Evaluate this view.")
]

for m_id, q in missions:
    create_page(m_id, q)
    print(f">>> Updated: {m_id}")