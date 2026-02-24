import os
from jinja2 import Environment, FileSystemLoader
from core.pairing import generate_swiss_pairings

def build_static_site(players, current_round):
    env = Environment(loader=FileSystemLoader('templates'))
    os.makedirs('output', exist_ok=True)
    
    # 1. Generate Standings
    sorted_players = sorted(players, key=lambda x: (x.wins, x.spread), reverse=True)
    standings_template = env.get_template('standings.html')
    standings_html = standings_template.render(players=sorted_players)
    
    with open(os.path.join('output', 'index.html'), 'w') as f:
        f.write(standings_html)

    # 2. Generate Pairings
    round_pairings = generate_swiss_pairings(players, round_num=current_round)
    pairings_template = env.get_template('pairings.html')
    pairings_html = pairings_template.render(matches=round_pairings, round_num=current_round)
    
    with open(os.path.join('output', 'pairings.html'), 'w') as f:
        f.write(pairings_html)
        
    print(f"\n✅ Build complete! Static files for Round {current_round} updated in output/ directory.")