import os
import json

DATA_DIR = "data"

def reset_database():
    if not os.path.exists(DATA_DIR):
        print("❌ Data directory not found.")
        return

    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(DATA_DIR, filename)
            
            with open(filepath, 'r') as f:
                players = json.load(f)
            
            for p in players:
                # 1. Wipe the tangled history
                p['history'] = []
                p['played_against'] = []
                
                # 2. Reset stats
                p['wins'] = 0.0
                p['spread'] = 0
                p['has_had_bye'] = False
                
                # 3. Lock base rating at 1200
                p['rating'] = 1200
                p['current_rating'] = 1200

            with open(filepath, 'w') as f:
                json.dump(players, f, indent=4)
                
            print(f"✅ Wiped history and restored 1200 ratings for '{filename}'.")

if __name__ == "__main__":
    print("🚀 Running Clean Slate Protocol...")
    reset_database()
    print("🎉 Done! You can now use the Dashboard to rapidly re-enter the accurate scores.")