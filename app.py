import os
import json
import traceback
from flask import Flask, render_template, request, redirect, url_for, flash
from core.state import load_players, save_players, DATA_DIR
from core.models import Player
from build import build_static_site, build_master_portal
from core.deploy import deploy_to_s3, deploy_master_portal

app = Flask(__name__)
app.secret_key = "super_secret_td_key" 

def get_tournaments():
    if not os.path.exists(DATA_DIR):
        return []
    files = os.listdir(DATA_DIR)
    return [f.replace('.json', '').replace('_', ' ').title() for f in files if f.endswith('.json')]

def get_matches_by_round(players):
    max_round = max((len(p.history) for p in players), default=0)
    rounds = {}
    for r in range(max_round):
        round_matches = []
        processed = set()
        for p in players:
            if p.id in processed: continue
            if len(p.history) > r:
                match = p.history[r]
                opp_id = match['opp_id']
                if opp_id == -1: continue # Skip placeholders
                if opp_id == 0:
                    round_matches.append({'p1': p, 'p2': None, 'res': match['result'], 'spread': match['spread']})
                    processed.add(p.id)
                else:
                    opp = next((o for o in players if o.id == opp_id), None)
                    if opp:
                        round_matches.append({'p1': p, 'p2': opp, 'res': match['result'], 'spread': match['spread']})
                        processed.add(p.id)
                        processed.add(opp_id)
        rounds[r + 1] = round_matches
    return rounds

def get_matches_for_ui(players):
    """Packages all matches into a JSON-friendly format so the Dropdown menu can update instantly."""
    max_round = max((len(p.history) for p in players), default=0)
    rounds_data = {}
    for r in range(max_round):
        round_matches = []
        processed = set()
        for p in players:
            if p.id in processed: continue
            if len(p.history) > r:
                match = p.history[r]
                opp_id = match['opp_id']
                if opp_id == -1: continue # Skip placeholders
                opp_name = match['opp_name']
                round_matches.append({
                    'p1_id': p.id,
                    'p1_name': p.name,
                    'p2_id': opp_id,
                    'p2_name': opp_name,
                    'res': match['result'],
                    'spread': match['spread']
                })
                processed.add(p.id)
                processed.add(opp_id)
        rounds_data[r + 1] = round_matches
    return json.dumps(rounds_data)

@app.route('/')
def index():
    tournaments = get_tournaments()
    return render_template('admin_home.html', tournaments=tournaments)

@app.route('/tournament/<name>')
def tournament_dashboard(name):
    active_tab = request.args.get('tab', 'overview')
    players = load_players(name)
    max_round = max((len(p.history) for p in players), default=0)
    history = get_matches_by_round(players)
    rounds_json = get_matches_for_ui(players)
    return render_template('admin_dashboard.html', tournament_name=name, players=players, max_round=max_round, history=history, rounds_json=rounds_json, active_tab=active_tab)

@app.route('/tournament/<name>/add_match', methods=['POST'])
def add_match(name):
    players = load_players(name)
    try:
        p1_id = int(request.form.get('winner_id'))
        p2_id = int(request.form.get('loser_id'))
        spread = int(request.form.get('spread', 0))

        if p2_id == 0:
            p1 = next((p for p in players if p.id == p1_id), None)
            if p1: p1.add_bye()
            flash(f"✅ BYE scored for {p1.name}!", "success")
        else:
            p1 = next((p for p in players if p.id == p1_id), None)
            p2 = next((p for p in players if p.id == p2_id), None)
            if p1 and p2:
                p1.add_result(p2.id, p2.name, True, False, spread)
                p2.add_result(p1.id, p1.name, False, False, -spread)
                flash(f"✅ Result added: {p1.name} beat {p2.name} by {spread}", "success")
            else:
                flash("❌ Error: One or both players not found.", "danger")
                
        save_players(players, name)
    except Exception as e:
        flash(f"❌ Error adding match: {e}", "danger")
        
    return redirect(url_for('tournament_dashboard', name=name, tab='scores'))

@app.route('/tournament/<name>/manage_match', methods=['POST'])
def manage_match(name):
    players = load_players(name)
    action = request.form.get('action')
    round_num = int(request.form.get('round_num'))
    round_idx = round_num - 1
    
    match_selection = request.form.get('match_selection')
    if not match_selection:
        flash("❌ No match selected.", "danger")
        return redirect(url_for('tournament_dashboard', name=name, tab='edit'))
        
    p1_id, p2_id = map(int, match_selection.split('|'))
    
    p1 = next((p for p in players if p.id == p1_id), None)
    p2 = None if p2_id == 0 else next((p for p in players if p.id == p2_id), None)

    if not p1:
        flash("❌ Target Player 1 not found.", "danger")
        return redirect(url_for('tournament_dashboard', name=name, tab='edit'))

    if action == 'delete':
        removed_opp_id = p1.remove_match_safely(round_idx, p2_id)
        if removed_opp_id is not None:
            if p2:
                p2.remove_match_safely(round_idx, p1_id)
            save_players(players, name)
            flash(f"✅ Exact match (Round {round_num}) successfully deleted.", "success")
        else:
            flash("❌ Failed to find specific match to delete.", "danger")

    elif action == 'edit':
        new_res = request.form.get('new_res')
        new_spread = int(request.form.get('new_spread', 0))
        
        if p2_id == 0:
            flash("❌ Cannot edit a BYE's score. Delete it and re-add if necessary.", "danger")
        else:
            if p1.edit_match_safely(round_idx, p2_id, new_res, new_spread) is not None:
                if p2:
                    p2_res = 'W' if new_res == 'L' else ('L' if new_res == 'W' else 'D')
                    p2.edit_match_safely(round_idx, p1_id, p2_res, -new_spread)
                save_players(players, name)
                flash(f"✅ Round {round_num} score updated successfully.", "success")
            else:
                flash("❌ Match not found in history to edit.", "danger")
                
    elif action == 'replace':
        new_opp_id = int(request.form.get('new_opponent_id'))
        new_res = request.form.get('new_res')
        new_spread = int(request.form.get('new_spread', 0))
        
        # 1. Safely Delete the bad match
        removed_opp_id = p1.remove_match_safely(round_idx, p2_id)
        if removed_opp_id is not None and p2:
            p2.remove_match_safely(round_idx, p1_id)
        
        # 2. Wedge the correct match directly into that same round slot
        if new_opp_id == 0:
            p1.insert_bye(round_idx)
        else:
            new_p2 = next((p for p in players if p.id == new_opp_id), None)
            if new_p2:
                is_win = (new_res == 'W')
                is_draw = (new_res == 'D')
                p1.insert_result(round_idx, new_p2.id, new_p2.name, is_win, is_draw, new_spread)
                
                p2_is_win = (new_res == 'L')
                p2_is_draw = (new_res == 'D')
                new_p2.insert_result(round_idx, p1.id, p1.name, p2_is_win, p2_is_draw, -new_spread)
            
        save_players(players, name)
        flash(f"✅ Round {round_num} pairing mismatch successfully fixed.", "success")

    return redirect(url_for('tournament_dashboard', name=name, tab='edit'))

@app.route('/tournament/<name>/insert_match', methods=['POST'])
def insert_match(name):
    players = load_players(name)
    try:
        round_num = int(request.form.get('round_num'))
        p1_id = int(request.form.get('winner_id'))
        p2_id = int(request.form.get('loser_id'))
        spread = int(request.form.get('spread', 0))
        round_idx = round_num - 1

        p1 = next((p for p in players if p.id == p1_id), None)
        if p2_id == 0:
            if p1:
                p1.insert_bye(round_idx)
                save_players(players, name)
                flash(f"✅ BYE inserted for {p1.name} in Round {round_num}.", "success")
        else:
            p2 = next((p for p in players if p.id == p2_id), None)
            if p1 and p2:
                p1.insert_result(round_idx, p2.id, p2.name, True, False, spread)
                p2.insert_result(round_idx, p1.id, p1.name, False, False, -spread)
                save_players(players, name)
                flash(f"✅ Inserted: {p1.name} beat {p2.name} by {spread} exactly at Round {round_num}.", "success")
            else:
                flash("❌ Players not found.", "danger")
    except Exception as e:
        flash(f"❌ Error inserting match: {e}", "danger")

    return redirect(url_for('tournament_dashboard', name=name, tab='scores'))

@app.route('/tournament/<name>/build_deploy', methods=['POST'])
def build_deploy(name):
    players = load_players(name)
    round_num = int(request.form.get('round_num'))
    pairing_sys = request.form.get('pairing_sys')
    
    try:
        build_static_site(players, round_num, name, pairing_system=pairing_sys)
        deploy_to_s3(name)
        flash(f"🚀 {name} Round {round_num} successfully built and deployed to AWS!", "success")
    except Exception as e:
        print(traceback.format_exc())
        flash(f"❌ Deployment failed check terminal for errors.", "danger")
        
    return redirect(url_for('tournament_dashboard', name=name, tab='deploy'))

if __name__ == '__main__':
    app.run(debug=True)