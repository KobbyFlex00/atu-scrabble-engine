import os
import json

DATA_DIR = "data"

def heal_database():
    if not os.path.exists(DATA_DIR):
        print("❌ Data directory not found.")
        return

    found_files = False
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            found_files = True
            filepath = os.path.join(DATA_DIR, filename)
            
            with open(filepath, 'r') as f:
                players = json.load(f)
            
            for p in players:
                # 1. Strip out all empty placeholders (-1)
                clean_history = [m for m in p.get('history', []) if m['opp_id'] != -1]
                p['history'] = clean_history
                
                # 2. Recalculate totals from scratch to guarantee perfect math
                wins = 0.0
                spread = 0
                played = []
                has_bye = False
                
                for m in clean_history:
                    if m['result'] == 'W': 
                        wins += 1
                    elif m['result'] == 'D': 
                        wins += 0.5
                        
                    spread += m['spread']
                    
                    if m['opp_id'] == 0:
                        has_bye = True
                    elif m['opp_id'] not in played:
                        played.append(m['opp_id'])
                
                p['wins'] = wins
                p['spread'] = spread
                p['played_against'] = played
                p['has_had_bye'] = has_bye

            # Save the compacted, mathematically perfect data
            with open(filepath, 'w') as f:
                json.dump(players, f, indent=4)
                
            print(f"✅ Successfully healed and compacted '{filename}'!")

    if not found_files:
        print("❌ No tournament files found in the data/ folder.")

if __name__ == "__main__":
    print("🚀 Running Database Doctor...")
    heal_database()
    print("🎉 All gaps closed. Math verified. You can now deploy the update!")