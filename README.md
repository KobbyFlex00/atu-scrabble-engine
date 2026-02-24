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
