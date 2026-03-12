import json
import os
import shutil
from core.models import Player

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def get_state_file(tournament_name: str) -> str:
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

# --- NEW CRUD FUNCTIONS FOR TOURNAMENT FILES ---

def rename_tournament(old_name: str, new_name: str) -> bool:
    old_file = get_state_file(old_name)
    new_file = get_state_file(new_name)
    
    if os.path.exists(old_file):
        # Rename the JSON database file
        os.rename(old_file, new_file)
        
        # Also try to rename the generated HTML output directory if it exists
        old_safe = old_name.replace(" ", "_").lower()
        new_safe = new_name.replace(" ", "_").lower()
        old_out = os.path.join('output', old_safe)
        new_out = os.path.join('output', new_safe)
        
        if os.path.exists(old_out):
            os.rename(old_out, new_out)
            
        return True
    return False

def delete_tournament(tournament_name: str) -> bool:
    state_file = get_state_file(tournament_name)
    success = False
    
    # Delete the JSON database file
    if os.path.exists(state_file):
        os.remove(state_file)
        success = True
        
    # Also clean up the generated HTML output directory
    safe_name = tournament_name.replace(" ", "_").lower()
    out_dir = os.path.join('output', safe_name)
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
        success = True
        
    return success