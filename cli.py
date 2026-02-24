from core.state import load_players, save_players
from core.models import Player
from build import build_static_site
from core.deploy import deploy_to_s3

def main():
    players = load_players()
    current_round = 1 

    while True:
        print("\n=== SCRABBLE TOURNAMENT MANAGER ===")
        print("1. Add a Player")
        print("2. Enter Match Result")
        print("3. Generate HTML & Deploy to Web")
        print("4. Exit")
        
        choice = input("Select an option: ")
        
        # ... (keep choice 1 and 2 exactly the same as before) ...

        elif choice == '3':
            round_input = input("Which round are you generating pairings for? ")
            
            # 1. Build the local files first
            build_static_site(players, int(round_input))
            
            # 2. Ask to deploy
            deploy = input("\nDo you want to push these updates live to AWS S3? (y/n): ").lower()
            if deploy == 'y':
                deploy_to_s3()
            else:
                print("Skipped deployment. Files saved locally only.")
            
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()