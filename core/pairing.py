from core.models import Player, Match
from core.standings import calculate_sos_and_sort

def generate_swiss_pairings(players: list[Player], round_num: int) -> list[Match]:
    sorted_players = calculate_sos_and_sort(players)
    pairings = []
    paired_ids = set()
    board = 1
    
    # 1. Handle the Bye FIRST if there is an odd number of players
    if len(sorted_players) % 2 != 0:
        bye_player = None
        # Loop backwards (from lowest ranked to highest)
        for p in reversed(sorted_players):
            if not p.has_had_bye:
                bye_player = p
                break
                
        # If somehow everyone has had a bye, just take the absolute lowest player
        if not bye_player:
            bye_player = sorted_players[-1]
            
        # Create the Bye match on the last board
        # We don't increment the board number yet so the actual matches start at Board 1
        last_board = (len(sorted_players) // 2) + 1
        pairings.append(Match(round_num, bye_player, None, last_board))
        paired_ids.add(bye_player.id)

    # 2. Pair the remaining players
    for i, p1 in enumerate(sorted_players):
        if p1.id in paired_ids:
            continue
            
        opponent = None
        
        # Look for the highest-ranked available opponent they haven't played
        for j in range(i + 1, len(sorted_players)):
            p2 = sorted_players[j]
            if p2.id not in paired_ids and p2.id not in p1.played_against:
                opponent = p2
                break
        
        # Fallback: If everyone left has been played, pair them with the next available person
        if not opponent:
             for j in range(i + 1, len(sorted_players)):
                p2 = sorted_players[j]
                if p2.id not in paired_ids:
                    opponent = p2
                    break

        # Create the match
        if opponent:
            pairings.append(Match(round_num, p1, opponent, board))
            paired_ids.add(p1.id)
            paired_ids.add(opponent.id)
            board += 1
            
    # Sort pairings by board number so the Bye appears at the bottom of the HTML table
    pairings.sort(key=lambda x: x.board)
    return pairings