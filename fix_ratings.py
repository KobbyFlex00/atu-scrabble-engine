import os
import json

DATA_DIR = "data"

def bulk_update_ratings():
    if not os.path.exists(DATA_DIR):
        print("❌ Data directory not found.")
        return

    found_files = False
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            found_files = True
            filepath = os.path.join(DATA_DIR, filename)
            
            # Load the data
            with open(filepath, 'r') as f:
                players = json.load(f)
            
            # Boost everyone to 1200
            for player in players:
                player['rating'] = 1200
                player['current_rating'] = 1200
            
            # Save it back
            with open(filepath, 'w') as f:
                json.dump(players, f, indent=4)
                
            print(f"✅ Successfully updated {len(players)} players in '{filename}' to a 1200 base rating.")

    if not found_files:
        print("❌ No tournament files found in the data/ folder.")

if __name__ == "__main__":
    print("🚀 Running rating calibration...")
    bulk_update_ratings()
    print("🎉 All done! You can delete this script now if you want.")