import os
from jinja2 import Environment, FileSystemLoader
from core.pairing import generate_swiss_pairings
from core.standings import calculate_sos_and_sort, calculate_team_standings

def build_static_site(players, current_round):
    env = Environment(loader=FileSystemLoader('templates'))
    os.makedirs('output', exist_ok=True)
    
    # Sort players by wins, then spread, then SOS
    sorted_players = calculate_sos_and_sort(players)
    
    # 1. Generate Standings (index.html)
    standings_template = env.get_template('standings.html')
    standings_html = standings_template.render(players=sorted_players)
    with open(os.path.join('output', 'index.html'), 'w') as f:
        f.write(standings_html)

    # 2. Generate Pairings (pairings.html)
    round_pairings = generate_swiss_pairings(players, round_num=current_round)
    pairings_template = env.get_template('pairings.html')
    pairings_html = pairings_template.render(matches=round_pairings, round_num=current_round)
    with open(os.path.join('output', 'pairings.html'), 'w') as f:
        f.write(pairings_html)
        
    # 3. Generate Wallchart (wallchart.html)
    max_rounds = max((len(p.history) for p in players), default=0)
    wallchart_template = env.get_template('wallchart.html')
    wallchart_html = wallchart_template.render(players=sorted_players, max_rounds=max_rounds)
    with open(os.path.join('output', 'wallchart.html'), 'w') as f:
        f.write(wallchart_html)

    # 4. Generate Team Standings (teams.html)
    team_standings = calculate_team_standings(players)
    teams_template = env.get_template('teams.html')
    teams_html = teams_template.render(teams=team_standings)
    with open(os.path.join('output', 'teams.html'), 'w') as f:
        f.write(teams_html)
        
    print(f"\n✅ Build complete! Static files for Round {current_round} updated in output/ directory.")