# ATU Scrabble Tournament Engine 🏆

A lightweight, blazing-fast tournament management system and static site generator designed for the ATU Scrabble Club and inter-university competitions. 

Built as a modern alternative to legacy tools like `tsh`, this engine handles player registrations, Swiss-system pairings, complex tie-breakers, and automatically deploys lightning-fast static HTML standings directly to the web via AWS S3.

## ✨ Features

* **Swiss System Pairings:** Automatically matches players with similar records while avoiding repeat matchups.
* **Smart Byes:** Elegantly handles odd numbers of players by assigning a +50 Bye to the lowest-ranked eligible player.
* **Advanced Tie-Breakers:** Uses the official Scrabble **SOS (Sum of Opponents' Scores)** to accurately rank players with identical wins and spreads.
* **Team Aggregation:** Automatically groups players by their University/Club (e.g., ATU, UG, KNUST) to generate live Team Standings.
* **Cross-Table Wallcharts:** Generates a beautiful round-by-round history view for every player.
* **Cloud-Native Deployment:** Pushes static HTML directly to an AWS S3 bucket for instant, crash-proof loading when hundreds of players refresh their phones simultaneously.

## 🛠️ Tech Stack
* **Core Logic:** Python 3
* **Templating:** Jinja2
* **Styling:** Tailwind CSS (via CDN)
* **Cloud Hosting:** Amazon S3 (`boto3`)

## 🚀 Getting Started

### 1. Prerequisites
You will need Python installed on your machine and an AWS Account with an S3 Bucket configured for Static Website Hosting.

### 2. Installation
Clone this repository and set up your virtual environment:

```bash
git clone [https://github.com/yourusername/atu-scrabble-engine.git](https://github.com/yourusername/atu-scrabble-engine.git)
cd atu-scrabble-engine
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install jinja2 boto3 python-dotenv
3. Environment Variables
Create a .env file in the root directory. Never commit this file to version control.

Code snippet
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
🎮 Running the Tournament
To start managing a tournament, run the Command Line Interface (CLI):

Bash
python cli.py
The CLI Menu:
Add a Player: Register a player's name, club/university, and initial rating.

Enter Match Result: Input the winning ID, losing ID, and point spread. (To score a BYE, enter 0 for the losing ID).

Generate HTML & Deploy: Compiles the current standings, generates the next round's pairings, builds the HTML, and optionally pushes everything live to AWS S3.

Reset Tournament: Wipes the local tournament.json state clean to prepare for a brand new event.

📁 Project Structure
/core - The brains of the operation. Contains data models, pairing algorithms, sorting logic, and deployment scripts.

/templates - Jinja2 HTML templates styled with Tailwind CSS.

/output - The locally generated static HTML files (ignored by Git).

cli.py - The interactive terminal menu for the Tournament Director.

build.py - The static-site generation script.

tournament.json - Local database tracking current tournament state (ignored by Git).

🔒 Security Note
Ensure your AWS IAM user follows the principle of least privilege, restricting access strictly to s3:PutObject for your specific tournament bucket.


To make it even easier for other developers to set this up, would you like me to help you quickly generate a `requirements.txt` file to include in the repository alongside this README?
