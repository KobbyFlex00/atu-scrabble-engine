import os
import json

def sync_all_math():
    for filename in os.listdir("data"):
        if filename.endswith(".json"):
            filepath = os.path.join("data", filename)
            with open(filepath, 'r') as f:
                players = json.load(f)
            
            for p in players:
                true_wins = 0.0
                true_spread = 0
                for m in p['history']:
                    if m['opp_id'] != -1:
                        if m['result'] == 'W': true_wins += 1
                        elif m['result'] == 'D': true_wins += 0.5
                        true_spread += m['spread']
                p['wins'] = true_wins
                p['spread'] = true_spread

            with open(filepath, 'w') as f:
                json.dump(players, f, indent=4)
            print(f"✅ Ghost points destroyed. Math synced perfectly for {filename}.")

if __name__ == "__main__":
    sync_all_math()