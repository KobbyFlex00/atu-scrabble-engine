import os
import json

def boost_ratings():
    for filename in os.listdir("data"):
        if filename.endswith(".json"):
            filepath = os.path.join("data", filename)
            with open(filepath, 'r') as f:
                players = json.load(f)
            
            for p in players:
                p['rating'] = 1200
                p['current_rating'] = 1200
                
            with open(filepath, 'w') as f:
                json.dump(players, f, indent=4)
            print(f"✅ Ratings restored to 1200 for {filename}")

if __name__ == "__main__":
    boost_ratings()