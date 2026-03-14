# 🏆 ATU Scrabble Tournament Engine

A robust, fully-featured Scrabble Tournament Management System built for the Accra Technical University (ATU) Scrabble Club. This engine handles everything from live score entry and dynamic Elo rating calculations to automated pairing generation and one-click deployment to AWS.

Built by **George Kobby Osae (Kobby Flex)**.

## ✨ Core Features

### 🛠️ TD Web Dashboard (Flask)
A modern, intuitive web-based Control Center for Tournament Directors to manage events in real-time.
* **Standard Score Entry:** Rapidly append match results as they come in.
* **Insert Missing Matches:** Securely wedge forgotten matches back into their correct historical round.
* **Surgical Match Editing:** Fix mismatches, edit scores, or delete corrupted records without breaking the tournament timeline.
* **Automated Math Syncing:** The engine dynamically recalculates Wins, Spread, SOS (Sum of Opponents' Scores), and Elo Ratings (Base 1200) from scratch to prevent "Ghost Points."

### 🎲 Advanced Pairing Algorithms
Generate the next round of pairings with a single click based on your preferred format:
* **Swiss System:** Rank-based pairings that actively prevent repeat matchups.
* **Round Robin:** Perfect rotational pairings for smaller groups.
* **King of the Hill (KOTH):** Strict 1v2, 3v4 pairings for high-stakes final rounds.

### 🌐 Automated Static Site Generation & Deployment
The engine automatically compiles the tournament data into a beautiful, mobile-responsive static website and pushes it live to AWS S3/CloudFront. The generated site includes:
* **Master Portal:** A lobby linking to all active/past tournaments.
* **Live Standings:** Real-time leaderboard with Wins, Spread, SOS, and Elo ratings.
* **Round Pairings:** Clean, easy-to-read board assignments.
* **Tournament Wallchart:** A professional grid showing everyone's round-by-round trajectory.
* **Player Profiles:** Clickable, individual stat cards showing a player's exact match history and opponent breakdown.
* **Team Standings:** Aggregated scores based on club/university affiliation.

## 🚀 Getting Started

### Prerequisites
* Python 3.8+
* AWS CLI configured with your S3 credentials
* Required Python packages: `flask`, `jinja2`, `boto3`

### Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/KobbyFlex00/atu-scrabble-engine.git](https://github.com/KobbyFlex00/atu-scrabble-engine.git)
   cd atu-scrabble-engine

Install the required dependencies:

Bash
pip install -r requirements.txt

Usage
Start the local Tournament Director Web Dashboard:

Bash
python app.py

Then, open your web browser and navigate to http://127.0.0.1:5000 to access the Control Center.

(Note: The original CLI version is still available by running python cli.py if a terminal environment is preferred).

📂 Project Structure
app.py: The Flask web server and routing logic for the TD Dashboard.

core/models.py: The fundamental data structures (Players, Matches) and surgical math logic.

core/standings.py: Calculates Elo ratings and sorts the leaderboards.

core/pairing.py: The algorithms for Swiss, Round Robin, and KOTH pairings.

core/state.py: Handles JSON database loading/saving.

build.py: Jinja2 static HTML site compiler.

core/deploy.py: Boto3 script for syncing the output/ folder to AWS S3.

templates/: HTML/CSS templates for both the live site and the TD Dashboard.

data/: Local JSON database storage for tournaments.

👨‍💻 Author
George Kobby Osae, General Secretary (2025/26), ATU Scrabble Club
```