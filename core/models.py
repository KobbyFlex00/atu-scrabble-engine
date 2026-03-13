from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Player:
    id: int
    name: str
    club: str
    rating: int
    wins: float = 0.0
    spread: int = 0
    sos: float = 0.0  
    played_against: List[int] = field(default_factory=list)
    history: List[dict] = field(default_factory=list) 
    has_had_bye: bool = False  
    
    def add_result(self, opponent_id: int, opponent_name: str, is_win: bool, is_draw: bool, spread: int):
        if is_win:
            self.wins += 1
            result_char = "W"
        elif is_draw:
            self.wins += 0.5
            result_char = "D"
        else:
            result_char = "L"
            
        self.spread += spread
        
        if opponent_id not in self.played_against:
            self.played_against.append(opponent_id)
            
        self.history.append({
            "opp_id": opponent_id,
            "opp_name": opponent_name,
            "result": result_char,
            "spread": spread
        })

    def add_bye(self):
        self.wins += 1
        self.spread += 50
        self.has_had_bye = True
        self.history.append({
            "opp_id": 0, 
            "opp_name": "BYE",
            "result": "W",
            "spread": 50
        })

    def remove_result(self, opponent_id: int):
        match_to_remove = next((m for m in self.history if m['opp_id'] == opponent_id), None)
        if not match_to_remove: return False

        if match_to_remove['result'] == 'W':
            self.wins -= 1
        elif match_to_remove['result'] == 'D':
            self.wins -= 0.5

        self.spread -= match_to_remove['spread']

        self.history.remove(match_to_remove)
        if opponent_id in self.played_against:
            self.played_against.remove(opponent_id)
        
        if opponent_id == 0:
            self.has_had_bye = False
            
        return True

    def edit_result(self, opponent_id: int, new_result_char: str, new_spread: int):
        match_to_edit = next((m for m in self.history if m['opp_id'] == opponent_id), None)
        if not match_to_edit: return False

        # Reverse the old stats
        if match_to_edit['result'] == 'W':
            self.wins -= 1
        elif match_to_edit['result'] == 'D':
            self.wins -= 0.5
        self.spread -= match_to_edit['spread']

        # Apply the new stats
        if new_result_char == 'W':
            self.wins += 1
        elif new_result_char == 'D':
            self.wins += 0.5
        self.spread += new_spread

        # Update the history dictionary
        match_to_edit['result'] = new_result_char
        match_to_edit['spread'] = new_spread

        return True

    # --- NEW METHODS: INSERTING A FORGOTTEN MATCH INTO A SPECIFIC ROUND ---
    def insert_result(self, round_idx: int, opponent_id: int, opponent_name: str, is_win: bool, is_draw: bool, spread: int):
        if is_win:
            self.wins += 1
            result_char = "W"
        elif is_draw:
            self.wins += 0.5
            result_char = "D"
        else:
            result_char = "L"
            
        self.spread += spread
        
        if opponent_id not in self.played_against:
            self.played_against.append(opponent_id)
            
        new_match = {
            "opp_id": opponent_id,
            "opp_name": opponent_name,
            "result": result_char,
            "spread": spread
        }
        
        # If they are just catching up, append. If we are wedging it into the past, insert.
        if round_idx >= len(self.history):
            self.history.append(new_match)
        else:
            self.history.insert(round_idx, new_match)

    def insert_bye(self, round_idx: int):
        self.wins += 1
        self.spread += 50
        self.has_had_bye = True
        new_match = {
            "opp_id": 0, 
            "opp_name": "BYE",
            "result": "W",
            "spread": 50
        }
        
        if round_idx >= len(self.history):
            self.history.append(new_match)
        else:
            self.history.insert(round_idx, new_match)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

@dataclass
class Match:
    round_num: int
    player1: Player
    player2: Optional[Player]
    board: int