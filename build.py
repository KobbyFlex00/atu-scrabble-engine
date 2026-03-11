import os
from jinja2 import Environment, FileSystemLoader
from core.pairing import generate_swiss_pairings
from core.standings import calculate_sos_and_sort, calculate_team_standings

def build_static_site(players, current_round, tournament_name):
    env = Environment(loader=FileSystemLoader('templates'))
    
    # Create a specific output folder for this tournament
    safe_name = tournament_name.replace(" ", "_").lower()
    out_dir = os.path.join('output', safe_name)
    os.makedirs(out_dir, exist_ok=True)
    
    sorted_players = calculate_sos_and_sort(players)
    
    # 1. Generate Standings
    standings_template = env.get_template('standings.html')
    standings_html = standings_template.render(players=sorted_players, tournament_name=tournament_name)
    with open(os.path.join(out_dir, 'index.html'), 'w') as f:
        f.write(standings_html)

    # 2. Generate Pairings
    round_pairings = generate_swiss_pairings(players, round_num=current_round)
    pairings_template = env.get_template('pairings.html')
    pairings_html = pairings_template.render(matches=round_pairings, round_num=current_round, tournament_name=tournament_name)
    with open(os.path.join(out_dir, 'pairings.html'), 'w') as f:
        f.write(pairings_html)
        
    # 3. Generate Wallchart
    max_rounds = max((len(p.history) for p in players), default=0)
    wallchart_template = env.get_template('wallchart.html')
    wallchart_html = wallchart_template.render(players=sorted_players, max_rounds=max_rounds, tournament_name=tournament_name)
    with open(os.path.join(out_dir, 'wallchart.html'), 'w') as f:
        f.write(wallchart_html)

    # 4. Generate Team Standings
    team_standings = calculate_team_standings(players)
    teams_template = env.get_template('teams.html')
    teams_html = teams_template.render(teams=team_standings, tournament_name=tournament_name)
    with open(os.path.join(out_dir, 'teams.html'), 'w') as f:
        f.write(teams_html)
        
    print(f"\n✅ Build complete! Static files for {tournament_name} saved in {out_dir}/")

def build_master_portal(tournament_names):
    """Generates the root index.html lobby linking to all active tournaments."""
    env = Environment(loader=FileSystemLoader('templates'))
    os.makedirs('output', exist_ok=True)
    
    tournaments = []
    for name in tournament_names:
        safe_name = name.replace(" ", "_").lower()
        tournaments.append({
            'name': name,
            'path': safe_name
        })
        
    template = env.get_template('portal.html')
    html = template.render(tournaments=tournaments)
    
    # Save this to the root of the output directory
    with open(os.path.join('output', 'index.html'), 'w') as f:
        f.write(html)
        
    print("✅ Master Portal built at output/index.html")