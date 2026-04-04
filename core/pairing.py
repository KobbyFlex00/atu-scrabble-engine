from core.models import Player, Match

def generate_swiss_pairings(players, round_num):
    """Swiss System: Rank-based, avoids repeat opponents."""
    sorted_players = sorted(players, key=lambda p: (p.wins, p.spread, p.current_rating), reverse=True)
    unpaired = sorted_players.copy()
    matches = []
    board = 1
    
    if len(unpaired) % 2 != 0:
        for i in reversed(range(len(unpaired))):
            if not unpaired[i].has_had_bye:
                bye_player = unpaired.pop(i)
                matches.append(Match(round_num=round_num, player1=bye_player, player2=None, board=0))
                break
        else:
            bye_player = unpaired.pop(-1)
            matches.append(Match(round_num=round_num, player1=bye_player, player2=None, board=0))

    while unpaired:
        p1 = unpaired.pop(0)
        best_opp_idx = -1
        for i, p2 in enumerate(unpaired):
            if p2.id not in p1.played_against:
                best_opp_idx = i
                break
        
        if best_opp_idx == -1:
            best_opp_idx = 0
            
        p2 = unpaired.pop(best_opp_idx)
        matches.append(Match(round_num=round_num, player1=p1, player2=p2, board=board))
        board += 1
        
    return matches

def generate_koh_pairings(players, round_num):
    """King of the Hill: Strict 1v2, 3v4, ignoring past history."""
    sorted_players = sorted(players, key=lambda p: (p.wins, p.spread, p.current_rating), reverse=True)
    matches = []
    board = 1
    
    unpaired = sorted_players.copy()
    if len(unpaired) % 2 != 0:
        bye_player = unpaired.pop(-1)
        matches.append(Match(round_num=round_num, player1=bye_player, player2=None, board=0))
        
    while unpaired:
        p1 = unpaired.pop(0)
        p2 = unpaired.pop(0)
        matches.append(Match(round_num=round_num, player1=p1, player2=p2, board=board))
        board += 1
        
    return matches

def generate_round_robin_pairings(players, round_num):
    """Smart Round Robin: Detects 2-Team Battles vs Standard Individual RR."""
    clubs = list(set(p.club for p in players if p.club and p.club.strip() != ""))
    
    if len(clubs) == 2:
        return _generate_team_battle_rr(players, clubs, round_num)
    else:
        return _generate_standard_rr(players, round_num)

def generate_double_round_robin_pairings(players, round_num):
    """Double Round Robin: Wraps the cycle and swaps P1/P2 for the rematch."""
    clubs = list(set(p.club for p in players if p.club and p.club.strip() != ""))
    
    # Calculate how many rounds are in a single "cycle"
    if len(clubs) == 2:
        team1 = [p for p in players if p.club == clubs[0]]
        team2 = [p for p in players if p.club == clubs[1]]
        cycle_length = max(len(team1), len(team2))
    else:
        n = len(players)
        if n % 2 != 0: n += 1
        cycle_length = n - 1

    # Determine which cycle we are in (0 = First Half, 1 = Rematch Half, etc.)
    cycle_index = (round_num - 1) // cycle_length
    effective_round = ((round_num - 1) % cycle_length) + 1
    
    # Generate the base pairings for this round
    if len(clubs) == 2:
        base_matches = _generate_team_battle_rr(players, clubs, effective_round)
    else:
        base_matches = _generate_standard_rr(players, effective_round)

    # If we are in an odd cycle (the Rematch Half), perfectly swap P1 and P2!
    if cycle_index % 2 != 0:
        for match in base_matches:
            if match.player2 is not None:
                match.player1, match.player2 = match.player2, match.player1
                
    # Ensure the Match object records the actual round number, not the base cycle round
    for match in base_matches:
        match.round_num = round_num

    return base_matches

def _generate_team_battle_rr(players, clubs, round_num):
    team1 = [p for p in players if p.club == clubs[0]]
    team2 = [p for p in players if p.club == clubs[1]]
    
    max_len = max(len(team1), len(team2))
    while len(team1) < max_len: team1.append(None)
    while len(team2) < max_len: team2.append(None)
    
    team1 = sorted(team1, key=lambda p: p.current_rating if p else -1, reverse=True)
    team2 = sorted(team2, key=lambda p: p.current_rating if p else -1, reverse=True)

    matches = []
    board = 1
    
    shift = (round_num - 1) % max_len
    rotated_team2 = team2[-shift:] + team2[:-shift]
    
    for i in range(max_len):
        p1 = team1[i]
        p2 = rotated_team2[i]
        
        if p1 is None and p2 is None: continue
            
        if p1 is None: p1, p2 = p2, p1
            
        b = 0 if p2 is None else board
        matches.append(Match(round_num=round_num, player1=p1, player2=p2, board=b))
        
        if p2 is not None: board += 1
        
    return matches

def _generate_standard_rr(players, round_num):
    if not players: return []
    
    rr_players = sorted(players, key=lambda p: p.id)
    if len(rr_players) % 2 != 0: rr_players.append(None) 
        
    n = len(rr_players)
    fixed = rr_players[0]
    rotatable = rr_players[1:]
    
    shift = (round_num - 1) % (n - 1)
    rotated = rotatable[-shift:] + rotatable[:-shift]
    current_round_players = [fixed] + rotated
    
    matches = []
    board = 1
    for i in range(n // 2):
        p1 = current_round_players[i]
        p2 = current_round_players[n - 1 - i]
        
        if p1 is None and p2 is None: continue
        if p1 is None: p1, p2 = p2, p1
        
        b = 0 if p2 is None else board
        matches.append(Match(round_num=round_num, player1=p1, player2=p2, board=b))
        if p2 is not None: board += 1
        
    return matches