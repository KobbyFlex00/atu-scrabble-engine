from core.models import Player, Match
from core.standings import calculate_sos_and_sort

def generate_swiss_pairings(players: list[Player], round_num: int) -> list[Match]:
    sorted_players = calculate_sos_and_sort(players)
    pairings = []
    paired_ids = set()
    board = 1
    
    if len(sorted_players) % 2 != 0:
        bye_player = None
        for p in reversed(sorted_players):
            if not p.has_had_bye:
                bye_player = p
                break
                
        if not bye_player:
            bye_player = sorted_players[-1]
            
        last_board = (len(sorted_players) // 2) + 1
        pairings.append(Match(round_num, bye_player, None, last_board))
        paired_ids.add(bye_player.id)

    for i, p1 in enumerate(sorted_players):
        if p1.id in paired_ids:
            continue
            
        opponent = None
        
        for j in range(i + 1, len(sorted_players)):
            p2 = sorted_players[j]
            if p2.id not in paired_ids and p2.id not in p1.played_against:
                opponent = p2
                break
        
        if not opponent:
             for j in range(i + 1, len(sorted_players)):
                p2 = sorted_players[j]
                if p2.id not in paired_ids:
                    opponent = p2
                    break

        if opponent:
            pairings.append(Match(round_num, p1, opponent, board))
            paired_ids.add(p1.id)
            paired_ids.add(opponent.id)
            board += 1
            
    pairings.sort(key=lambda x: x.board)
    return pairings

def generate_round_robin_pairings(players: list[Player], round_num: int) -> list[Match]:
    """Generates perfect Round Robin pairings using the Circle Method."""
    # Sort by ID so the rotation is consistent across different rounds
    fixed_players = sorted(players, key=lambda p: p.id)
    
    # If odd number of players, add a dummy player to represent the BYE
    if len(fixed_players) % 2 != 0:
        dummy = Player(id=0, name="BYE", club="", rating=0)
        fixed_players.append(dummy)
        
    n = len(fixed_players)
    
    # The Circle Method shifts the array by 1 position every round (excluding the first player)
    shift = (round_num - 1) % (n - 1)
    rotated_players = [fixed_players[0]] + fixed_players[1+shift:] + fixed_players[1:1+shift]
    
    pairings = []
    board = 1
    
    for i in range(n // 2):
        p1 = rotated_players[i]
        p2 = rotated_players[n - 1 - i]
        
        # If one of the players is the dummy, the other gets a BYE
        if p1.id == 0:
            pairings.append(Match(round_num, p2, None, board))
        elif p2.id == 0:
            pairings.append(Match(round_num, p1, None, board))
        else:
            pairings.append(Match(round_num, p1, p2, board))
            
        board += 1
            
    # Move the BYE match to the bottom of the table
    pairings.sort(key=lambda m: 1 if m.player2 is None else 0)
    
    # Clean up board numbers
    for idx, match in enumerate(pairings):
        match.board = idx + 1
        
    return pairings