from mission_data import CIVIL_RIGHTS_MISSIONS

def get_mission_guide(mission_id):
    mission = CIVIL_RIGHTS_MISSIONS.get(mission_id)
    if not mission: return "Mission not found."
    return f"MISSION: {mission['question']}\nRECIPE: {mission['recipe']}"

if __name__ == "__main__":
    print(get_mission_guide("CR_M5"))
