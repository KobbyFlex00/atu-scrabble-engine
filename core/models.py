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
    current_rating: int = 0  
    played_against: List[int] = field(default_factory=list)
    history: List[dict] = field(default_factory=list) 
    has_had_bye: bool = False  
    
    def _pad_history(self, round_idx: int):
        """Ensures the history array reaches the target round to prevent shifting."""
        while len(self.history) <= round_idx:
            self.history.append({"opp_id": -1, "opp_name": "NONE", "result": "-", "spread": 0})

    def add_result(self, opponent_id: int, opponent_name: str, is_win: bool, is_draw: bool, spread: int):
        # Find the first available blank slot (a placeholder) or append to the end
        target_idx = next((i for i, m in enumerate(self.history) if m['opp_id'] == -1), len(self.history))
        self.insert_result(target_idx, opponent_id, opponent_name, is_win, is_draw, spread)

    def add_bye(self):
        target_idx = next((i for i, m in enumerate(self.history) if m['opp_id'] == -1), len(self.history))
        self.insert_bye(target_idx)

    def remove_match_safely(self, round_idx: int, expected_opp_id: int):
        """Surgically finds and removes a match, ensuring it targets the correct opponent."""
        if round_idx < len(self.history) and self.history[round_idx]['opp_id'] == expected_opp_id:
            idx_to_remove = round_idx
        else:
            idx_to_remove = next((i for i, m in enumerate(self.history) if m['opp_id'] == expected_opp_id), None)
        
        if idx_to_remove is None: return None
        match_to_remove = self.history[idx_to_remove]
        
        if match_to_remove['opp_id'] == -1: return None # Already empty

        if match_to_remove['result'] == 'W': self.wins -= 1
        elif match_to_remove['result'] == 'D': self.wins -= 0.5
        self.spread -= match_to_remove['spread']
        
        # Replace with a blank placeholder instead of popping/shifting the array!
        self.history[idx_to_remove] = {"opp_id": -1, "opp_name": "NONE", "result": "-", "spread": 0}
        
        self.played_against = [m['opp_id'] for m in self.history if m['opp_id'] not in [-1, 0]]
        if 0 not in [m['opp_id'] for m in self.history]:
            self.has_had_bye = False
            
        return match_to_remove['opp_id']

    def edit_match_safely(self, round_idx: int, expected_opp_id: int, new_result_char: str, new_spread: int):
        """Surgically finds and edits a match, ensuring it targets the correct opponent."""
        if round_idx < len(self.history) and self.history[round_idx]['opp_id'] == expected_opp_id:
            idx_to_edit = round_idx
        else:
            idx_to_edit = next((i for i, m in enumerate(self.history) if m['opp_id'] == expected_opp_id), None)
            
        if idx_to_edit is None: return None
        match_to_edit = self.history[idx_to_edit]
        
        if match_to_edit['result'] == 'W': self.wins -= 1
        elif match_to_edit['result'] == 'D': self.wins -= 0.5
        self.spread -= match_to_edit['spread']
        
        if new_result_char == 'W': self.wins += 1
        elif new_result_char == 'D': self.wins += 0.5
        self.spread += new_spread
        
        match_to_edit['result'] = new_result_char
        match_to_edit['spread'] = new_spread
        return match_to_edit['opp_id']

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
            
        new_match = {"opp_id": opponent_id, "opp_name": opponent_name, "result": result_char, "spread": spread}
        
        self._pad_history(round_idx)
        # Overwrite the blank slot instead of inserting/shifting the array!
        self.history[round_idx] = new_match

    def insert_bye(self, round_idx: int):
        self.wins += 1
        self.spread += 50
        self.has_had_bye = True
        new_match = {"opp_id": 0, "opp_name": "BYE", "result": "W", "spread": 50}
        
        self._pad_history(round_idx)
        self.history[round_idx] = new_match

    @classmethod
    def from_dict(cls, data: dict):
        if 'current_rating' not in data:
            data['current_rating'] = data.get('rating', 0)
        return cls(**data)

@dataclass
class Match:
    round_num: int
    player1: Player
    player2: Optional[Player]
    board: int