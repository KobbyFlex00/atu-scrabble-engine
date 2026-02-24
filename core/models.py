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
    has_had_bye: bool = False  # NEW: Track if they've received a Bye
    
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

    # NEW: Dedicated method to score a Bye
    def add_bye(self):
        self.wins += 1
        self.spread += 50
        self.has_had_bye = True
        self.history.append({
            "opp_id": 0, # 0 indicates no opponent
            "opp_name": "BYE",
            "result": "W",
            "spread": 50
        })

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

@dataclass
class Match:
    round_num: int
    player1: Player
    player2: Optional[Player]
    board: int