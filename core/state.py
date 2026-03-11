import json
import os
from core.models import Player

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True) # Ensure the data folder exists

def get_state_file(tournament_name: str) -> str:
    # Converts a name like "Division 1" into "division_1.json"
    safe_name = tournament_name.replace(" ", "_").lower()
    return os.path.join(DATA_DIR, f"{safe_name}.json")

def load_players(tournament_name: str) -> list[Player]:
    state_file = get_state_file(tournament_name)
    if not os.path.exists(state_file):
        return []
    
    with open(state_file, 'r') as f:
        data = json.load(f)
        return [Player.from_dict(p) for p in data]

def save_players(players: list[Player], tournament_name: str):
    state_file = get_state_file(tournament_name)
    with open(state_file, 'w') as f:
        from dataclasses import asdict
        json.dump([asdict(p) for p in players], f, indent=4)

def clear_players(tournament_name: str):
    state_file = get_state_file(tournament_name)
    if os.path.exists(state_file):
        os.remove(state_file)