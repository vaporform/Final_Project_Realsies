# Project Description

## 1. Project Overview

- **Project Name:** Devil's Gambit

- **Brief Description:**  
Devil's Gambit is a single-player puzzle-strategy card game where you play against demons in a game of blind card picking to win your friend's soul back. Both players share a grid of hidden cards, manipulating it in real time using special cards to gain the upper hand. Defeat each demon to progress, or lose and face the consequences. The game combines Inscryption's scale-based scoring system with the grid-based mechanics inspired by Connect 4, creating a unique experience where both players actively fight over a shared game space. 

- **Problem Statement:**  
Standard card games often feel boring, as there is nothing to lose. So, it is a wise idea to play a card game where you must win your friend's soul back! Traditional card game opponents also seems static. Thus, there are engaging AI adversaries with distinct personalities, and exploits to find. The game also provides meaningful gameplay analytics through data visualization.

- **Target Users:**
Players who enjoy games that are easy to jump into but offer a challenge for those who stick around. Or those who appreciate the retro feel, keyboard-only controls, and want a fun story-quick story without an endless amount of dialogue. Whether someone is a fan of quick luck-based rounds or calculated strategy, they will find a satisfying experience in outsmarting an opponent using nothing more than their logic and planning.

- **Key Features:**  
  - Single-player gameplay against 4 progressively challenging demons.
  - Shared 4×4 grid of hidden cards that both players actively manipulate in real time.
  - RNG system for demon decision-making based on game state and aggression values.
  - Helper card system unique abilities for board manipulation and strategy, with over a dozen possible cards!
  - Row/column/diagonal completion mechanics that trigger bonuses and grid refills.
  - Deck management with penalty cards when decks run empty.
  - In-game basic Tutorial mode with comprehensive gameplay guidance.
  - In-game visual feedback including scale visualization and board state updates.
  - Automatic gameplay statistics logging in CSV format.
  - Interactive analytics dashboard with multiple visualization types.
  - Data analysis tools showing player performance trends and helper card effectiveness.

---

## 2. Concept

### 2.1 Background
I wanted to create a game based on a simple concept: randomness. In real life, randomness is everywhere, but I wanted to explore what happens when a player can use that randomness to their advantage. That is how this game was born.

The gameplay is inspired by two seemingly opposite titles: Inscryption and Connect 4. It takes the simple goal of Connect 4 (four in a row to win) and adds the tactical depth of Inscryption. This creates a space where players can "rig" outcomes through their own wit and strategy. Unlike the turn-based placement of Connect 4, The Devil’s Gambit features a shared, contested grid where both players fight over the same space in real time.

The theme is inspired by thriller movies where a protagonist performs an ancient ritual and must pay a heavy price for it. To match this mood, the art style embraces the technical restrictions of old game consoles. By using a limited palette and a small screen, the game takes on a unique "old school" vibe that feels both nostalgic and tense.

### 2.2 Objectives
- Design a strategy card game with an easy to learn but with good strategic depth and replayability.
- Implement dynamic AI opponents that respond to player actions using weighted decision-making algorithms
- Create a contested game space where both players compete for board control and resources
- Design demons that has a reasonable learning curve for each level.
- Implement comprehensive gameplay statistics tracking and analysis for player performance insights
- Design a diverse helper card system that creates meaningful strategic decisions and dynamic combos
- Provide players with visual and audio feedback that clearly communicate game state, scoring, and momentum changes

---

## 3. UML Class Diagram

The UML Class Diagram is provided in [PDF format](./uml.pdf) showing:
- Core game classes (GameApp, GameSession, Scene hierarchy)
- Player-related classes (BasePlayer, Player, Demon, and demon subclasses)
- Game object classes (Grid, Scale, BaseCard, HelperCard)
- Helper card hierarchy with specialized implementations
- Relationships and inheritance structures

---

## 4. Object-Oriented Programming Implementation

The following classes are implemented in the project with their key roles and responsibilities:

- **BaseScene**: Serves as the base scene where it represents a part of the game (e.g., cutscene, main menu, or game round). Provides a framework for switching from one scene to another.
  - **TitleScreen**: Inherits from BaseScene. Serves as the main title screen of the game.
  - **Dialogue**: Inherits from BaseScene. Handles dialogue screens.
  - **End**: Inherits from BaseScene. shows the ending scene.
  - **GameSession**: Inherits from BaseScene. Manages the main game loop, turn order, win/lose conditions, and scene transitions.
- **Grid**: Stores and manages a 4×4 card grid. Handles card flipping, row/column completion detection, and refill logic.
- **Scale**: Tracks both players' scores. Calculates the score difference, keeps track of the current session's score, and determines when the threshold is reached.
- **Timer**: Creates a timer for checking countdown and animations. Keep track of current time in game.
- **BasePlayer**: Manages the deck and hand for each game session.
  - **Player**: Inherits from BasePlayer. Manages the player's deck, helper cards, hand, and processes player input each turn.
  - **Demon**: Inherits from BasePlayer. Uses weighted RNG and aggression values to decide between picking cards and firing passive effects.
    - **TutorialDemon**: Dummy demon providing guided gameplay with messages at each round.
    - **Imp**: Demon using random card selection strategy without strategic planning.
    - **Fafnir**: Greedy demon that prioritizes the highest-value available cards.
    - **Abigor**: Tactical demon using aggression-based logic to evaluate line completion and blocking opportunities.
    - **Baphomet**: Advanced strategic demon using complex scoring algorithms considering card values, line completions, and sabotage opportunities.

- **BaseCard**: Represents a grid card. Stores value, owner, potential effects, and face-up/face-down state.
- **HelperCard**: Base class for all helper cards. Contains methods to override by each subclass to execute its effect.
  - **Pass_On**: Pass your turn to the opponent.
  - **Peek**: Reveals selected tile of your choice.
  - **Lock**: Makes the card impossible to pick from either sides.
  - **TwoTime**: Let you choose cards twice, if you don't complete a combo.
  - **Trap**: Drain card points from opponent if picked.
  - **Blind**: Unflips a revealed tile.
  - **Oracle**: Shows the position of the highest-value unflipped tile.
  - **Inflate**: Doubles a chosen tile's value for a turn.
  - **Deflate**: Halves a chosen tile's value for a turn.
  - **Scramble**: Shuffles the values of all unflipped tiles randomly.
  - **Curse**: The opponent's next tile pick scores negative instead of positive.
  - **Bounty**: Adds 3 points to an unflipped tile.
  - **Wall**: Permanently blocks a tile from being picked.
  - **Payback**: If next turn your scale is negative, get double score of the difference.
  - **Windfall**: Draw a random helper card immediately.
  - **Fog**: Unflip all currently revealed tiles.
  - **Bleed**: Opponent loses 1 point per turn for 3 rounds.
  
- **AssetLib**: Manages sprite,font,sound loading, caching, and asset management.

- **GameApp**: The main loop of the game application.
- **Application (TkStats)**: Tkinter-based statistics dashboard for analyzing gameplay performance across multiple sessions.

---

## 5. Statistical Data
### 5.1 Data Recording Method
Each of the data features are saved in the data/DEMON_NAME/ directory. Data logging is tied to each GameSession instances with specified demon (if exists).

The logging triggers at two distinct moments in the game:
- **Player uses a Helper Card**: If the action is valid, it saves to helper_cards.csv. The data is logged as: [card.name, 1] (The name of the helper card used, followed by a 1).
- **At the End of Evaluation (Turn Resolution)**: Happens after a set of cards is picked from the grid (by either the player or the demon) and scores are calculated. The data are loged as the following:
  - **Points Gained (points_gained.csv)**: If the player was the one who made the move, it logs the points the player just scored [self.scale.player_scored].
  - **Board Control (board_cards.csv)**: Logs [self.turn_count, player_count, demon_count]. This tracks whose turn number it is overall, and how many cards on the grid belong to the player vs. the demon.
  - **Board Values (board_values.csv)**: Logs the summed value of all the cards currently on the board [board_value].
  Score Difference (points_diff.csv): Logs the current weight distribution/advantage on the scale [self.scale.get_delta_score()].
  - **Score Difference (points_diff.csv)**: Logs the current weight distribution/advantage on the scale [self.scale.get_delta_score()].

*Note that a turn counts as a single evaluation action. Since both the player and the demon trigger evaluations, the turn_count effectively represents the total number of moves made in the match so far by both entities, not individual round cycles.

### 5.2 Data Features

| Feature | Why It's Important | How It's Obtained | Where It's Collected | How It's Displayed |
|---------|-------------------|-------------------|----------------------|-------------------|
| **Points Gained per Turn** | Shows player playstyle (aggressive vs. cautious). Reveals if player prioritizes immediate scoring or setup. | Record every card pick across multiple sessions. | `player_score` from Scale class | Summary statistics (mean, SD, min, max) in table format |
| **Board Value per Turn** | Shows how the grid's total value shifts over time. Indicates if player prefers upgrading card values or acquiring helpers. | Take a snapshot of the grid's total value every turn. | Sum of all card values from Grid class | Histogram showing value range distribution |
| **Helper Card Usage Frequency** | Identifies which helper cards players rely on most. Essential for game balancing and understanding meta strategies. | Log every helper card played in each round. | `name` from HelperCard class, tracked via GameSession | Bar chart comparing frequency of each helper card |
| **Board Card Count (Player vs. Demon)** | Shows who is winning board control. Indicates momentum shifts in who owns more cards. | Record card ownership count for each turn. | `owner` attribute from BaseCard class, aggregated via Grid | Stacked bar graph showing player vs demon card distribution over time |
| **Point Difference per Turn** | Shows momentum of the game. Identifies critical swing moments and who is winning at each stage. | Calculate delta between player and demon every turn. | `get_delta_score()` from Scale class | Summary statistics (mean, SD, min, max) and line graph showing delta over time |

---

## 6. Changed Proposed Features

- Added diagonal combos for more varied choices
- Removed the "choose your rewards" part, as it disrupts the gameplay flow and player can get softlocked in extreme cases.
- Gave players more cards to start each round

---

## 7. External Sources

### Game Design Inspiration
- **Inscryption** - Scale-based scoring system, helper card mechanics, "rigging" mechanics to gain advantage
- **Connect 4** - Grid-based gameplay, row/column/diagonal completion detection.

### Libraries & Frameworks Used
- **Pygame-CE**: Game engine, sprite rendering, input handling, and display
- **Matplotlib**: Creating statistical charts and graphs in the data dashboard
- **Pandas**: Loading, filtering, and processing CSV game statistics
- **Tkinter**: Building the statistics visualization GUI

### Assets
- **Fonts**: Tiny5-Regular by The Tiny5 Project, AlmendraSC-Regular by Ana Sanfelippo, Felipa-Regular by Fontstage, and Jacquard24-Regular by The Soft Type Project. All are licensed with Open Font License.
- **Music**: All music used in the game were made by NotJam on Itch.io from NOT JAM MUSIC PACK and NOT JAM MUSIC PACK 2. License: CC0 1.0 Universal.
- **Sound Effects**: Some sounds effects were made by NotJam on Itch.io from NOT JAM MUSIC PACK 2 License: CC0 1.0, and generated from jsfxr (https://sfxr.me) by Eric Fredricksen (with contributions from Chris McCormick) License: UNILICENSE.
