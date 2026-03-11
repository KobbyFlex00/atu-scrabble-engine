import os
from core.state import load_players, save_players, clear_players, DATA_DIR
from core.models import Player
from build import build_static_site, build_master_portal
from core.deploy import deploy_to_s3, deploy_master_portal

def list_tournaments():
    if not os.path.exists(DATA_DIR):
        return []
    files = os.listdir(DATA_DIR)
    return [f.replace('.json', '').replace('_', ' ').title() for f in files if f.endswith('.json')]

def crud_menu(players, tournament_name):
    while True:
        print(f"\n--- 🛠️ MANAGE DATA (CRUD) - {tournament_name} ---")
        print("1. Edit Player Details (Name, Club, Rating)")
        print("2. Undo/Delete a Match Result")
        print("3. Delete a Player entirely")
        print("4. Back to Main Menu")
        
        choice = input("Select: ")
        
        if choice == '1':
            for p in players: print(f"[{p.id}] {p.name} ({p.club})")
            p_id = int(input("\nEnter Player ID to edit: "))
            player = next((p for p in players if p.id == p_id), None)
            if player:
                print("Leave blank to keep current value.")
                new_name = input(f"New Name [{player.name}]: ")
                new_club = input(f"New Club [{player.club}]: ")
                new_rating = input(f"New Rating [{player.rating}]: ")
                
                if new_name: player.name = new_name
                if new_club: player.club = new_club
                if new_rating: player.rating = int(new_rating)
                save_players(players, tournament_name)
                print("✅ Player updated.")
            else:
                print("❌ Player not found.")
                
        elif choice == '2':
            for p in players: print(f"[{p.id}] {p.name}")
            p1_id = int(input("\nEnter Player ID to modify: "))
            player1 = next((p for p in players if p.id == p1_id), None)
            
            if player1:
                print(f"\nHistory for {player1.name}:")
                for m in player1.history:
                    print(f"- Played: {m['opp_name']} (ID: {m['opp_id']}) | Result: {m['result']} {m['spread']}")
                
                opp_id = int(input("\nEnter the Opponent ID of the match to delete: "))
                
                if player1.remove_result(opp_id):
                    if opp_id != 0:
                        player2 = next((p for p in players if p.id == opp_id), None)
                        if player2: player2.remove_result(player1.id)
                        
                    save_players(players, tournament_name)
                    print("✅ Match deleted and stats reverted.")
                else:
                    print("❌ Match not found in history.")
            
        elif choice == '3':
            for p in players: print(f"[{p.id}] {p.name}")
            p_id = int(input("\nEnter Player ID to DELETE: "))
            player = next((p for p in players if p.id == p_id), None)
            if player:
                confirm = input(f"Are you sure you want to delete {player.name}? (y/n): ")
                if confirm.lower() == 'y':
                    players.remove(player)
                    save_players(players, tournament_name)
                    print("✅ Player deleted.")
            
        elif choice == '4':
            break

def tournament_menu(tournament_name):
    players = load_players(tournament_name)

    while True:
        print(f"\n=== 🏆 {tournament_name.upper()} MENU ===")
        print("1. Add a Player")
        print("2. Enter Match Result")
        print("3. Manage Data (Edit / Delete / Undo)")
        print("4. Generate HTML & Deploy to Web")
        print("5. Exit to Tournament Selector")
        
        choice = input("Select an option: ")
        
        if choice == '1':
            p_id = len(players) + 1 if players else 1
            while any(p.id == p_id for p in players): p_id += 1 
            
            name = input("Player Name: ")
            club = input("Club/University: ")
            rating = int(input("Rating (e.g., 1200): "))
            players.append(Player(id=p_id, name=name, club=club, rating=rating))
            save_players(players, tournament_name)
            print(f"✅ Added {name} successfully!")

        elif choice == '2':
            if not players:
                print("No players yet.")
                continue
            print("\nTip: Enter '0' for losing ID to score a BYE.")
            for p in players: print(f"[{p.id}] {p.name}")
            
            try:
                p1_id = int(input("\nWinning player ID: "))
                p2_id = int(input("Losing player ID: "))
                
                if p2_id == 0:
                    p1 = next((p for p in players if p.id == p1_id), None)
                    if p1:
                        p1.add_bye()
                        save_players(players, tournament_name)
                        print(f"✅ BYE scored for {p1.name}.")
                    continue
                
                spread = int(input("Positive spread (e.g., 50): "))
                p1 = next((p for p in players if p.id == p1_id), None)
                p2 = next((p for p in players if p.id == p2_id), None)
                
                if p1 and p2:
                    p1.add_result(p2.id, p2.name, True, False, spread)
                    p2.add_result(p1.id, p1.name, False, False, -spread)
                    save_players(players, tournament_name)
                    print(f"✅ {p1.name} beat {p2.name} by {spread}.")
            except ValueError:
                print("❌ Numbers only.")

        elif choice == '3':
            crud_menu(players, tournament_name)

        elif choice == '4':
            if not players: continue
            round_num = int(input("Generating pairings for round #: "))
            build_static_site(players, round_num, tournament_name)
            
            deploy = input("\nDeploy to AWS S3? (y/n): ").lower()
            if deploy == 'y':
                deploy_to_s3(tournament_name)
                
        elif choice == '5':
            break

def main():
    while True:
        print("\n=== ATU SCRABBLE ENGINE ===")
        print("Select or Create a Tournament:")
        
        existing = list_tournaments()
        if existing:
            for i, name in enumerate(existing):
                print(f"{i+1}. {name}")
            print(f"{len(existing) + 1}. Create New Tournament")
        else:
            print("1. Create New Tournament")
            
        print("--------------------------------")
        print("P. Update & Deploy Master Portal")
        print("0. Exit Engine")
        
        choice = input("\nSelect: ").upper()
        
        if choice == '0':
            print("Shutting down...")
            break
            
        if choice == 'P':
            build_master_portal(existing)
            deploy = input("Do you want to push the Master Portal live to AWS S3? (y/n): ").lower()
            if deploy == 'y':
                deploy_master_portal()
            continue
            
        try:
            choice_idx = int(choice)
            if existing and 1 <= choice_idx <= len(existing):
                tournament_menu(existing[choice_idx - 1])
            elif choice_idx == len(existing) + 1 or (not existing and choice_idx == 1):
                new_name = input("\nEnter new tournament name (e.g., 'Division 1'): ")
                if new_name:
                    tournament_menu(new_name)
        except ValueError:
            pass

if __name__ == "__main__":
    main()