from core.models import Player

def calculate_sos_and_sort(players: list[Player]) -> list[Player]:
    # Create a quick dictionary to look up players by their ID
    player_dict = {p.id: p for p in players}
    
    for p in players:
        # Sum the wins of every opponent this player has faced in their history
        p.sos = sum(player_dict[match['opp_id']].wins for match in p.history if match['opp_id'] in player_dict)
        
    # Sort by Wins (descending), then Spread (descending), then SOS (descending)
    return sorted(players, key=lambda x: (x.wins, x.spread, x.sos), reverse=True)

def calculate_team_standings(players: list[Player]) -> list[dict]:
    teams = {}
    
    for p in players:
        if p.club not in teams:
            # Initialize the team dictionary if we haven't seen this club yet
            teams[p.club] = {
                'name': p.club,
                'player_count': 0,
                'total_wins': 0.0,
                'total_spread': 0
            }
            
        # Add the player's stats to their team
        teams[p.club]['player_count'] += 1
        teams[p.club]['total_wins'] += p.wins
        teams[p.club]['total_spread'] += p.spread
        
    # Convert the dictionary to a list and sort it by Wins, then Spread
    sorted_teams = sorted(list(teams.values()), key=lambda x: (x['total_wins'], x['total_spread']), reverse=True)
    
    return sorted_teams