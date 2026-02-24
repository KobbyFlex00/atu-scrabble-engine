from core.models import Player, Match

def generate_swiss_pairings(players: list[Player], round_num: int) -> list[Match]:
    # 1. Sort standings: Wins descending, then Spread descending
    sorted_players = sorted(players, key=lambda x: (x.wins, x.spread), reverse=True)
    
    pairings = []
    paired_ids = set()
    board = 1
    
    for i, p1 in enumerate(sorted_players):
        # Skip if player is already paired this round
        if p1.id in paired_ids:
            continue
            
        opponent = None
        
        # 2. Look for the highest-ranked available opponent they haven't played
        for j in range(i + 1, len(sorted_players)):
            p2 = sorted_players[j]
            if p2.id not in paired_ids and p2.id not in p1.played_against:
                opponent = p2
                break
        
        # 3. Fallback: If everyone left has been played, pair them with the next available person anyway
        if not opponent:
             for j in range(i + 1, len(sorted_players)):
                p2 = sorted_players[j]
                if p2.id not in paired_ids:
                    opponent = p2
                    break

        # 4. Create the match
        if opponent:
            pairings.append(Match(round_num, p1, opponent, board))
            paired_ids.add(p1.id)
            paired_ids.add(opponent.id)
            board += 1
        else:
            # If no opponent is found (odd number of players total), player gets a Bye
            pairings.append(Match(round_num, p1, None, board))
            paired_ids.add(p1.id)
            
    return pairings