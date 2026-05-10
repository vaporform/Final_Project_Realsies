# Devil's Gambit

## Project Description

- **Project by:** Siraphob Phonphakdee
- **Game Genre:** Strategy, Puzzle, Card Game, Turn-Based

Devil's Gambit is a turn-based strategic card game featuring player versus demon gameplay on a 4×4 grid. Players flip cards to score points and compete against increasingly challenging demon opponents, each with unique AI strategies. The game also includes a comprehensive statistics dashboard for analyzing gameplay performance across multiple sessions.

---

## Installation

### Clone the Repository
```sh
git clone https://github.com/vaporform/Final_Project_Realsies.git
cd Final_Project_Realsies
```

### Create and Activate Python Virtual Environment

**Windows:**
```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Mac:**
```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Required Dependencies
- pygame-ce==2.5.7
- matplotlib==3.10.8
- pandas==3.0.2
- **NOTE:** YOU MUST USE PYTHON VERSION 3.14.0 OR HIGHER!
### Dependencies Error
If you found compatibility issues, you can replace the requirements.txt as
- pygame-ce
- matplotlib
- pandas
---

## Running the Game

After activating the Python virtual environment, you can start the game by running:

**Windows:**
```bat
python main.py
```

**Mac:**
```sh
python3 main.py
```

The game will launch with a title screen. Use arrow keys to move the cursor and space bar to select.

---

## Tutorial / Usage

### Game Controls
- **Arrow Keys**: Move the cursor on the grid (up/down/left/right)
- **Space**: Select or flip a card from the grid.
- **Right Arrow (at edge)**: Enter your helper card hand.
- **Left Arrow (in hand)**: Return to grid from helper hands.
- **Space (in hand)**: Select and use the helper card.

### How to Play
At the start, a 4×4 grid of face-down cards with each assigned random value from each player's deck. The player can choose do following:
1. **Select a Card**: Selecting a card flips it, scoring its value toward your side of the scale. Any color is counted. However, if you flipped a white card, you get a random Helper Card. (Unless you've previously used a helper card earlier)

2. **Use Helper Cards**: Special ability cards that modify gameplay rules. Select helper cards by moving right from the grid edge. Each card has it's own unique quirks and skills!

Your goal is to tip your scale all the way towards you. Break the threshold!

**Tips:**
- **Combos:** Complete a full row, column, or diagonal for bonus points! When a combo is completed, the matched line refills with new cards from player's deck (Shown at the corner leftside of the scale.).
- **Read Hints:** Each demon has their own unique quirks. Descriptions might give you a hint about their strategy.
- **Plan Ahead:** Plan how you pick your cards, stock up your helper cards, and think about your opponent's next move!

---

## Game Features

- **Turn-Based Grid Combat:** Strategic card selection on a 4×4 grid.
- **Multiple Demon Opponents:** Four unique demons, each with distinct AI personalities and strategies.
- **Combo System:** Match complete rows, columns, or diagonals for bonus points and grid refills.
- **Scale Mechanics:** Visual scale showing real-time score differential between player and demon.
- **Helper Cards:** Special ability cards that modify gameplay rules with diverse abilities! Each with special quirks and combos.
- **Tutorial:** A basic comprehensive guided introduction to all game mechanics.
- **Progressive Difficulty:** Four levels with increasing opponent complexity.
- **Rich Visuals:** Sprite-based graphics with animated board states and scale visualization.
- **Story Elements:** Dialogue scenes introducing each demon opponent with themed descriptions.
- **Automatic Statistics Logging:** Game data persists to CSV files for each demon
- **Interactive Dashboard:** Tkinter-based statistics viewer with multiple chart types
- **Performance Analysis:** Track win rates, helper card effectiveness, and scoring patterns
- **Multi-Game Aggregation:** Analyze trends across multiple gameplay sessions

---

## Known Bugs

No bugs were known as of this README.md

---

## Unfinished Works

Currently the game is designed to be played in one sitting, so there are no pause or return menus.

---

## External Sources

### Libraries & Frameworks Used
- **Pygame-CE**: Game engine, sprite rendering, input handling, and display

- **Matplotlib**: Creating statistical charts and graphs in the data dashboard

- **Pandas**: Loading, filtering, and processing CSV game statistics

- **Tkinter**: Building the statistics visualization GUI

### Assets
- **Fonts**: Tiny5-Regular by The Tiny5 Project, AlmendraSC-Regular by Ana Sanfelippo, Felipa-Regular by Fontstage, and Jacquard24-Regular by The Soft Type Project.
- **Music**: All music used in the game were made by NotJam on Itch.io
- **Sound Effects**: Some sounds were made by NotJam on Itch.io, and generated from jsfxr by Eric Fredricksen (with contributions from Chris McCormick).
