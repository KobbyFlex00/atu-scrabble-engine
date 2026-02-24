import json
import os
from core.models import Player

STATE_FILE = "tournament.json"

def load_players() -> list[Player]:
    if not os.path.exists(STATE_FILE):
        return []
    
    with open(STATE_FILE, 'r') as f:
        data = json.load(f)
        return [Player.from_dict(p) for p in data]

def save_players(players: list[Player]):
    with open(STATE_FILE, 'w') as f:
        from dataclasses import asdict
        json.dump([asdict(p) for p in players], f, indent=4)

def clear_players():
    """Wipes the tournament data clean."""
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)