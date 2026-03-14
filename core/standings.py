from core.models import Player

def recalculate_ratings(players: list[Player]):
    """Calculates dynamic Elo ratings strictly based on match history."""
    # 1. Start everyone at their initial base rating
    current_ratings = {p.id: p.rating for p in players}
    max_rounds = max((len(p.history) for p in players), default=0)

    # 2. Replay the tournament chronologically, round by round
    for round_idx in range(max_rounds):
        processed = set()
        changes = {p.id: 0 for p in players}

        for p in players:
            if len(p.history) > round_idx:
                match = p.history[round_idx]
                opp_id = match['opp_id']

                # BYEs and Deleted Placeholders do not impact Elo rating
                if opp_id in [0, -1]:
                    continue

                # Ensure we only process each 1v1 match once per round
                pair_key = tuple(sorted([p.id, opp_id]))
                if pair_key in processed:
                    continue
                processed.add(pair_key)

                rating_a = current_ratings[p.id]
                rating_b = current_ratings[opp_id]

                res_a = match['result']
                actual_a = 1 if res_a == 'W' else (0.5 if res_a == 'D' else 0)
                actual_b = 1 - actual_a

                # Standard Elo mathematical probability
                expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
                expected_b = 1 - expected_a

                # Standard K-factor (20 is standard for active tournaments)
                k = 20  
                changes[p.id] += k * (actual_a - expected_a)
                changes[opp_id] += k * (actual_b - expected_b)

        # 3. Apply all rating swings at the very end of the round
        for pid, change in changes.items():
            current_ratings[pid] += change

    # 4. Save the finalized, rounded ratings back to the player models
    for p in players:
        p.current_rating = int(round(current_ratings[p.id]))

def calculate_sos_and_sort(players: list[Player]) -> list[Player]:
    # Calculate SOS (Sum of Opponents' Wins)
    for p in players:
        opp_wins = 0
        for opp_id in p.played_against:
            if opp_id not in [0, -1]:
                opp = next((o for o in players if o.id == opp_id), None)
                if opp:
                    opp_wins += opp.wins
        p.sos = opp_wins

    # Trigger the Elo rating recalculation
    recalculate_ratings(players)

    # Sort the final leaderboard: Wins -> Spread -> SOS -> Current Rating
    return sorted(players, key=lambda p: (p.wins, p.spread, p.sos, p.current_rating), reverse=True)

def calculate_team_standings(players: list[Player]) -> list[dict]:
    teams = {}
    for p in players:
        if p.club not in teams:
            teams[p.club] = {'wins': 0, 'spread': 0}
        teams[p.club]['wins'] += p.wins
        teams[p.club]['spread'] += p.spread
        
    team_list = [{'name': k, 'wins': v['wins'], 'spread': v['spread']} for k, v in teams.items()]
    return sorted(team_list, key=lambda t: (t['wins'], t['spread']), reverse=True)