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

    def _sync_stats(self):
        """CRITICAL FIX: Recalculates wins, spread, and opponents directly from the history array. Destroys Ghost Points."""
        self.wins = 0.0
        self.spread = 0
        self.played_against = []
        self.has_had_bye = False
        
        for m in self.history:
            if m['opp_id'] == -1: continue # Skip empty placeholders
            
            if m['result'] == 'W': self.wins += 1
            elif m['result'] == 'D': self.wins += 0.5
            
            self.spread += m['spread']
            
            if m['opp_id'] == 0:
                self.has_had_bye = True
            elif m['opp_id'] not in self.played_against:
                self.played_against.append(m['opp_id'])

    def add_result(self, opponent_id: int, opponent_name: str, is_win: bool, is_draw: bool, spread: int):
        target_idx = next((i for i, m in enumerate(self.history) if m['opp_id'] == -1), len(self.history))
        self.insert_result(target_idx, opponent_id, opponent_name, is_win, is_draw, spread)

    def add_bye(self):
        target_idx = next((i for i, m in enumerate(self.history) if m['opp_id'] == -1), len(self.history))
        self.insert_bye(target_idx)

    def remove_match_safely(self, round_idx: int, expected_opp_id: int):
        if round_idx < len(self.history) and self.history[round_idx]['opp_id'] == expected_opp_id:
            idx_to_remove = round_idx
        else:
            idx_to_remove = next((i for i, m in enumerate(self.history) if m['opp_id'] == expected_opp_id), None)
        
        if idx_to_remove is None: return None
        match_to_remove = self.history[idx_to_remove]
        
        if match_to_remove['opp_id'] == -1: return None 
        
        # Replace with blank placeholder
        self.history[idx_to_remove] = {"opp_id": -1, "opp_name": "NONE", "result": "-", "spread": 0}
        
        self._sync_stats() # Force math recalculation
        return match_to_remove['opp_id']

    def edit_match_safely(self, round_idx: int, expected_opp_id: int, new_result_char: str, new_spread: int):
        if round_idx < len(self.history) and self.history[round_idx]['opp_id'] == expected_opp_id:
            idx_to_edit = round_idx
        else:
            idx_to_edit = next((i for i, m in enumerate(self.history) if m['opp_id'] == expected_opp_id), None)
            
        if idx_to_edit is None: return None
        match_to_edit = self.history[idx_to_edit]
        
        match_to_edit['result'] = new_result_char
        match_to_edit['spread'] = new_spread
        
        self._sync_stats() # Force math recalculation
        return match_to_edit['opp_id']

    def insert_result(self, round_idx: int, opponent_id: int, opponent_name: str, is_win: bool, is_draw: bool, spread: int):
        result_char = "W" if is_win else ("D" if is_draw else "L")
        new_match = {"opp_id": opponent_id, "opp_name": opponent_name, "result": result_char, "spread": spread}
        
        self._pad_history(round_idx)
        self.history[round_idx] = new_match
        self._sync_stats() # Force math recalculation

    def insert_bye(self, round_idx: int):
        new_match = {"opp_id": 0, "opp_name": "BYE", "result": "W", "spread": 50}
        self._pad_history(round_idx)
        self.history[round_idx] = new_match
        self._sync_stats() # Force math recalculation

    @classmethod
    def from_dict(cls, data: dict):
        if 'current_rating' not in data:
            data['current_rating'] = data.get('rating', 0)
        return cls(**data)

# --- This is the class that was accidentally cut off! ---
@dataclass
class Match:
    round_num: int
    player1: Player
    player2: Optional[Player]
    board: int