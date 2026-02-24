import os
from core.state import load_players, save_players, clear_players
from core.models import Player
from build import build_static_site
from core.deploy import deploy_to_s3

def main():
    players = load_players()

    while True:
        print("\n=== SCRABBLE TOURNAMENT MANAGER ===")
        print("1. Add a Player")
        print("2. Enter Match Result")
        print("3. Generate HTML & Deploy to Web")
        print("4. Reset Tournament (Clear Data)")
        print("5. Exit")
        
        choice = input("Select an option: ")
        
        if choice == '1':
            p_id = len(players) + 1
            name = input("Player Name: ")
            club = input("Club/University: ")
            rating = int(input("Rating (e.g., 1200): "))
            
            new_player = Player(id=p_id, name=name, club=club, rating=rating)
            players.append(new_player)
            save_players(players)
            print(f"✅ Added {name} successfully!")

        elif choice == '2':
            if not players:
                print("No players in the tournament yet. Add players first.")
                continue
                
            print("\n--- ENTER MATCH RESULT ---")
            print("Tip: To score a BYE, enter the winning player's ID, and '0' for the loser.")
            for p in players:
                print(f"[{p.id}] {p.name}")
                
            try:
                p1_id = int(input("\nEnter winning player's ID: "))
                p2_id = int(input("Enter losing player's ID (or 0 for BYE): "))
                
                # Handling the Bye
                if p2_id == 0:
                    p1 = next((p for p in players if p.id == p1_id), None)
                    if p1:
                        p1.add_bye()
                        save_players(players)
                        print(f"✅ BYE scored: {p1.name} receives +1 Win and +50 Spread.")
                    else:
                        print("❌ Invalid player ID.")
                    continue # Skip the rest of the loop and go back to menu
                
                # Handling a normal match
                spread = int(input("Enter the positive spread (e.g., 50): "))
                
                p1 = next((p for p in players if p.id == p1_id), None)
                p2 = next((p for p in players if p.id == p2_id), None)
                
                if p1 and p2:
                    p1.add_result(opponent_id=p2.id, opponent_name=p2.name, is_win=True, is_draw=False, spread=spread)
                    p2.add_result(opponent_id=p1.id, opponent_name=p1.name, is_win=False, is_draw=False, spread=-spread)
                    save_players(players)
                    print(f"✅ Result saved: {p1.name} beat {p2.name} by {spread} points.")
                else:
                    print("❌ Invalid player IDs.")
            except ValueError:
                print("❌ Invalid input. Please enter numbers only.")

        elif choice == '3':
            if not players:
                print("No players to generate stats for.")
                continue
                
            try:
                round_input = input("Which round are you generating pairings for? ")
                round_num = int(round_input)
                
                # Build local files
                build_static_site(players, round_num)
                
                # Ask to deploy
                deploy = input("\nDo you want to push these updates live to AWS S3? (y/n): ").lower()
                if deploy == 'y':
                    deploy_to_s3()
                else:
                    print("Skipped deployment. Files saved locally only.")
            except ValueError:
                print("❌ Invalid round number.")
            
        elif choice == '4':
            confirm = input("⚠️ ARE YOU SURE? This will delete all players and match history. (y/n): ").lower()
            if confirm == 'y':
                clear_players()
                players = [] # Reset the list in memory
                
                # Optionally clear the output folder too
                if os.path.exists('output'):
                    for f in os.listdir('output'):
                        if f.endswith('.html'):
                            os.remove(os.path.join('output', f))
                            
                print("✅ Tournament data has been completely wiped. Ready for a new event!")
            else:
                print("Reset cancelled.")
                
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()