import os
import traceback
from core.state import load_players, save_players, clear_players, rename_tournament, delete_tournament, DATA_DIR
from core.models import Player
from build import build_static_site, build_master_portal
from core.deploy import deploy_to_s3, deploy_master_portal

def list_tournaments():
    if not os.path.exists(DATA_DIR):
        return []
    files = os.listdir(DATA_DIR)
    return [f.replace('.json', '').replace('_', ' ').title() for f in files if f.endswith('.json')]

def view_and_edit_rounds(players, tournament_name):
    try:
        max_round = max((len(p.history) for p in players), default=0)
        highest_allowed = max_round + 1

        print(f"\nAvailable Rounds: 1 to {highest_allowed} (Select {highest_allowed} to manually build a new round)")
        round_num = int(input("Enter round number to view/edit: "))

        if not (1 <= round_num <= highest_allowed):
            print("❌ Invalid round number.")
            return

        round_idx = round_num - 1
        processed_ids = set()
        matches_display = []

        for p in players:
            if p.id in processed_ids:
                continue
            if len(p.history) > round_idx:
                match_data = p.history[round_idx]
                opp_id = match_data['opp_id']

                if opp_id == 0:
                    matches_display.append({'p1': p, 'p2': None, 'spread': match_data['spread'], 'p1_res': match_data['result']})
                    processed_ids.add(p.id)
                else:
                    opp = next((o for o in players if o.id == opp_id), None)
                    if opp:
                        matches_display.append({'p1': p, 'p2': opp, 'spread': match_data['spread'], 'p1_res': match_data['result']})
                        processed_ids.add(p.id)
                        processed_ids.add(opp_id)

        print(f"\n--- 📅 ROUND {round_num} MATCHES ---")
        if not matches_display:
            print("No matches recorded for this round yet.")
        else:
            for i, m in enumerate(matches_display):
                if m['p2'] is None:
                    print(f"{i+1}. {m['p1'].name} has a BYE (+{m['spread']})")
                else:
                    p1_name = m['p1'].name
                    p2_name = m['p2'].name
                    p1_res = m['p1_res']
                    p2_res = 'W' if p1_res == 'L' else ('L' if p1_res == 'W' else 'D')
                    spread = m['spread']
                    print(f"{i+1}. {p1_name} ({p1_res}) vs {p2_name} ({p2_res}) | Spread for {p1_name}: {spread}")

        print("\nOptions:")
        print("1. Edit an existing match score")
        print("2. Change players in a match (Fix wrong pairing)")
        print("3. Add a missing match to this round")
        print("4. Delete a match from this round")
        print("0. Go back")
        choice = input("Select: ")

        if choice == '1':
            if not matches_display:
                print("❌ No matches to edit.")
                return
            match_idx = int(input("\nEnter the match number to edit: ")) - 1
            if 0 <= match_idx < len(matches_display):
                selected = matches_display[match_idx]
                if selected['p2'] is None:
                    print("❌ Cannot edit a BYE from this menu. Use Option 4 to delete it.")
                    return

                p1 = selected['p1']
                p2 = selected['p2']

                print(f"\n--- ✏️ EDITING: {p1.name} vs {p2.name} ---")
                new_res = input(f"Did {p1.name} Win, Lose, or Draw? (W/L/D): ").upper()
                if new_res not in ['W', 'L', 'D']:
                    print("❌ Invalid result. Use W, L, or D.")
                    return

                new_spread = int(input(f"Enter the new spread for {p1.name} (e.g., if they lost by 20, enter -20): "))

                if p1.edit_result(p2.id, new_res, new_spread):
                    p2_res = 'W' if new_res == 'L' else ('L' if new_res == 'W' else 'D')
                    p2.edit_result(p1.id, p2_res, -new_spread)
                    save_players(players, tournament_name)
                    print("✅ Match successfully updated! (Remember to Generate & Deploy to see changes on the site)")
                else:
                    print("❌ Failed to find match in history.")
            else:
                print("❌ Invalid match number.")
                
        elif choice == '2':
            if not matches_display:
                print("❌ No matches to edit.")
                return
            match_idx = int(input("\nEnter the match number with the wrong pairing: ")) - 1
            if 0 <= match_idx < len(matches_display):
                selected = matches_display[match_idx]
                old_p1 = selected['p1']
                old_p2 = selected['p2']

                print(f"\n--- 🔄 REPLACING PAIRING: {old_p1.name} vs {'BYE' if old_p2 is None else old_p2.name} ---")
                
                if old_p2 is None:
                    old_p1.remove_result(0)
                else:
                    old_p1.remove_result(old_p2.id)
                    old_p2.remove_result(old_p1.id)

                print("\nEnter the CORRECT pairing details:")
                print("Tip: Enter '0' for losing ID to score a BYE.")
                try:
                    new_p1_id = int(input("Winning player ID: "))
                    new_p2_id = int(input("Losing player ID: "))
                    
                    if new_p2_id == 0:
                        new_p1 = next((p for p in players if p.id == new_p1_id), None)
                        if new_p1:
                            new_p1.insert_bye(round_idx)
                            save_players(players, tournament_name)
                            print(f"✅ Replaced with a BYE for {new_p1.name} in Round {round_num}.")
                        else:
                            print("❌ Player not found. (Old match was deleted, please add new match using Option 3).")
                            save_players(players, tournament_name)
                    else:
                        spread = int(input("Positive spread (e.g., 50): "))
                        new_p1 = next((p for p in players if p.id == new_p1_id), None)
                        new_p2 = next((p for p in players if p.id == new_p2_id), None)
                        
                        if new_p1 and new_p2:
                            new_p1.insert_result(round_idx, new_p2.id, new_p2.name, True, False, spread)
                            new_p2.insert_result(round_idx, new_p1.id, new_p1.name, False, False, -spread)
                            save_players(players, tournament_name)
                            print(f"✅ Pairing successfully changed to {new_p1.name} vs {new_p2.name}!")
                        else:
                            print("❌ One or both players not found. (Old match was deleted, please add new match using Option 3).")
                            save_players(players, tournament_name)
                except ValueError:
                    print("❌ Invalid input. (Old match was deleted, please add new match manually using Option 3).")
                    save_players(players, tournament_name)
            else:
                print("❌ Invalid match number.")

        elif choice == '3':
            print(f"\n--- ➕ ADD MISSING MATCH TO ROUND {round_num} ---")
            print("Tip: Enter '0' for losing ID to score a BYE.")
            try:
                p1_id = int(input("Winning player ID: "))
                p2_id = int(input("Losing player ID: "))
                
                if p2_id == 0:
                    p1 = next((p for p in players if p.id == p1_id), None)
                    if p1:
                        p1.insert_bye(round_idx)
                        save_players(players, tournament_name)
                        print(f"✅ BYE inserted into Round {round_num} for {p1.name}.")
                    else:
                        print("❌ Player not found.")
                else:
                    spread = int(input("Positive spread (e.g., 50): "))
                    p1 = next((p for p in players if p.id == p1_id), None)
                    p2 = next((p for p in players if p.id == p2_id), None)
                    
                    if p1 and p2:
                        p1.insert_result(round_idx, p2.id, p2.name, True, False, spread)
                        p2.insert_result(round_idx, p1.id, p1.name, False, False, -spread)
                        save_players(players, tournament_name)
                        print(f"✅ {p1.name} beat {p2.name} by {spread} (Inserted perfectly at Round {round_num}).")
                    else:
                        print("❌ One or both players not found.")
            except ValueError:
                print("❌ Invalid input. Use numbers.")

        elif choice == '4':
            if not matches_display:
                print("❌ No matches to delete.")
                return
            match_idx = int(input("\nEnter the match number to delete: ")) - 1
            if 0 <= match_idx < len(matches_display):
                selected = matches_display[match_idx]
                p1 = selected['p1']
                p2 = selected['p2']

                if p2 is None:
                    confirm = input(f"Are you sure you want to delete the BYE for {p1.name}? (y/n): ")
                    if confirm.lower() == 'y':
                        if p1.remove_result(0):
                            save_players(players, tournament_name)
                            print("✅ BYE successfully deleted!")
                        else:
                            print("❌ Failed to find BYE in history.")
                else:
                    confirm = input(f"Are you sure you want to completely delete the match: {p1.name} vs {p2.name}? (y/n): ")
                    if confirm.lower() == 'y':
                        if p1.remove_result(p2.id):
                            p2.remove_result(p1.id)
                            save_players(players, tournament_name)
                            print("✅ Match successfully deleted! (You can re-add it using Option 3 if needed)")
                        else:
                            print("❌ Failed to find match in history.")
            else:
                print("❌ Invalid match number.")

    except ValueError:
        print("❌ Invalid input. Please enter numbers where required.")


def crud_menu(players, tournament_name):
    while True:
        print(f"\n--- 🛠️ MANAGE DATA (CRUD) - {tournament_name} ---")
        print("1. Edit Player Details (Name, Club, Rating)")
        print("2. View & Edit Matches by Round")
        print("3. Undo/Delete a Match Result")
        print("4. Delete a Player entirely")
        print("5. Back to Tournament Menu")
        
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
            view_and_edit_rounds(players, tournament_name)

        elif choice == '3':
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
            
        elif choice == '4':
            for p in players: print(f"[{p.id}] {p.name}")
            p_id = int(input("\nEnter Player ID to DELETE: "))
            player = next((p for p in players if p.id == p_id), None)
            if player:
                confirm = input(f"Are you sure you want to delete {player.name}? (y/n): ")
                if confirm.lower() == 'y':
                    players.remove(player)
                    save_players(players, tournament_name)
                    print("✅ Player deleted.")
            
        elif choice == '5':
            break

def tournament_menu(tournament_name):
    players = load_players(tournament_name)

    while True:
        print(f"\n=== 🏆 {tournament_name.upper()} MENU ===")
        print("1. Add a Player")
        print("2. Enter Match Result")
        print("3. Manage Data & Edit Rounds")
        print("4. Generate Pairings & Deploy (Next Round)")
        print("5. 🛑 End Tournament / Re-Publish Final Results")
        print("0. Exit to Tournament Selector")
        
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
            
            try:
                round_num = int(input("Generating pairings for round #: "))
            except ValueError:
                print("❌ Invalid input. Please enter a valid round number.")
                continue
                
            print("\nSelect Pairing System:")
            print("1. Round Robin (Perfect rotation, no repeats)")
            print("2. Swiss System (Rank-based, avoids repeats)")
            print("3. King of the Hill (Strict 1v2, 3v4 - ignores repeats)")
            sys_choice = input("Choice (1/2/3): ")
            
            if sys_choice == '1':
                pairing_sys = "rr"
            elif sys_choice == '3':
                pairing_sys = "koh"
            else:
                pairing_sys = "swiss"
            
            try:
                build_static_site(players, round_num, tournament_name, pairing_system=pairing_sys)
                deploy = input("\nDeploy to AWS S3? (y/n): ").lower()
                if deploy == 'y':
                    deploy_to_s3(tournament_name)
            except Exception as e:
                print(f"\n❌ ENGINE ERROR ENCOUNTERED:")
                traceback.print_exc()
                print("-----------------------------\n")
                
        elif choice == '5':
            if not players:
                print("❌ No players in tournament.")
                continue
                
            confirm = input("\n⚠️ Are you sure you want to end the tournament and publish final results? (y/n): ")
            if confirm.lower() == 'y':
                max_round = max((len(p.history) for p in players), default=0)
                print(f"\n🏆 Wrapping up Tournament at Round {max_round}...")
                
                try:
                    build_static_site(players, max_round, tournament_name, pairing_system="final")
                    deploy_to_s3(tournament_name)
                    print("\n🎉 TOURNAMENT OFFICIALLY CONCLUDED AND PUBLISHED LIVE!")
                except Exception as e:
                    print(f"\n❌ ENGINE ERROR ENCOUNTERED:")
                    traceback.print_exc()
                    print("-----------------------------\n")
                    
        elif choice == '0':
            break

def manage_tournaments_menu(tournaments):
    while True:
        print("\n--- ⚙️ MANAGE TOURNAMENTS (RENAME/DELETE) ---")
        if not tournaments:
            print("No tournaments available to manage.")
            break
            
        for i, name in enumerate(tournaments):
            print(f"{i+1}. {name}")
        print("0. Back to Main Menu")
        
        choice = input("\nSelect a tournament to manage: ")
        
        if choice == '0':
            break
            
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(tournaments):
                target = tournaments[idx]
                print(f"\nManaging: {target}")
                print("1. Rename Tournament")
                print("2. Delete Tournament")
                print("0. Cancel")
                
                action = input("Select action: ")
                
                if action == '1':
                    new_name = input(f"Enter new name for '{target}': ")
                    if new_name and new_name.lower() != target.lower():
                        if rename_tournament(target, new_name):
                            print(f"✅ Tournament renamed to '{new_name}'.")
                            tournaments[idx] = new_name
                        else:
                            print("❌ Failed to rename tournament.")
                elif action == '2':
                    confirm = input(f"⚠️ ARE YOU SURE you want to permanently delete '{target}'? (y/n): ")
                    if confirm.lower() == 'y':
                        delete_tournament(target)
                        print(f"✅ Tournament '{target}' deleted.")
                        return 
        except ValueError:
            pass

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
        print("M. Manage Tournaments (Rename/Delete)")
        print("P. Update & Deploy Master Portal")
        print("0. Exit Engine")
        
        choice = input("\nSelect: ").upper()
        
        if choice == '0':
            print("Shutting down...")
            break
            
        if choice == 'M':
            manage_tournaments_menu(existing)
            continue
            
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