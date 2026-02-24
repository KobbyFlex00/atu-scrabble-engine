from dataclasses import dataclass, field, asdict
from typing import Set, Optional, List

@dataclass
class Player:
    id: int
    name: str
    club: str
    rating: int
    wins: float = 0.0
    spread: int = 0
    # Use a list instead of a set for easier JSON serialization
    played_against: List[int] = field(default_factory=list)
    
    def add_result(self, opponent_id: int, is_win: bool, is_draw: bool, spread: int):
        if is_win:
            self.wins += 1
        elif is_draw:
            self.wins += 0.5
        self.spread += spread
        
        if opponent_id not in self.played_against:
            self.played_against.append(opponent_id)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

@dataclass
class Match:
    round_num: int
    player1: Player
    player2: Optional[Player]
    board: int