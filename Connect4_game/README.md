# Connect 4 - AI Game

## CSC 361 - Artificial Intelligence Project

A Connect 4 game implementation featuring multiple AI agents using different algorithms and strategies.

---
## overview

This project implements the classic **Connect 4** game with a graphical user interface (GUI) and multiple AI opponents:-
- **Minimax Algorithm** with Alpha-Beta Pruning
- **Adaptive/Evolving Minimax** that learns from games played (adapt for the opponent)

Players can compete against each other or against AI agents of varying difficulty levels of minimax.

---

## features

- **Full-screen GUI** built with Tkinter
- **Human vs Human** gameplay
- **Human vs AI** with selectable difficulty
- **AI vs AI** to watch agents compete
- **Three difficulty levels** for Minimax (easy,medium, hard)
- **Adaptive AI** that improves its strategy over time
---

## Structure

Connect4_game/
|-- main.py                 # runs the GUI
|-- connect4_gui.py         # GUI implementation (Tkinter)
|-- README.md               # This file
|-- src/
    |-- board.py            # game board logic (state, moves, win detection)
    |-- minimax_agent.py    # minimax AI with Alpha-Beta pruning
    |-- adaptive_minimax.py # adapting minimax that learns from games
    |-- train.py            # training script for adaptive agent
    |-- agent_weights.json  # saved weights for adaptive agent


---

## Installation

### what you need to run the program

- Python >= 3.8
- Tkinter (if not included with python)

### Setup
- (Optional) create a virtual environment:
   run these commands 
   python3 -m venv .venv
   source .venv/bin/activate  # on macOS
   # or
   .venv\Scripts\activate     # on Windows ( not sure since im a mac user... )
---

## AI agents

### 1. minimax Agent (`minimax_agent.py`)

A classic game-playing AI using the **Minimax algorithm** with **Alpha-Beta pruning**.

| Difficulty | Search Depth | Behavior |
|------------|--------------|----------|
| Easy       | 2 levels     | Makes some mistakes, beatable |
| Medium     | 4 levels     | Decent challenge |
| Hard       | 6 levels     | Very strong, rarely loses |

### 2. Adaptive/Evolving Agent (`adaptive_minimax.py`)

I have implemented this agent with a complex heuristic that i can not give it a value manually since its detailed and complex but using a complicated and advanced ``adjust_weights`` that analyze the game givin to it and the critical positions with the results as wining or losing or if draw, then its adjust the heuristic to give more points for the good moves, less for the bad moves

after each game the adaptive agent plays it call ``finalize_game`` which control the learning process

**how the learning process?**
record the game -> adjust the heuristic -> clear the recorded game

**Key Features:**
- Starts with default weights for evaluating positions
- After each game, analyzes what patterns led to win/loss
- Adjusts weights to improve future performance
- Saves learned weights to `agent_weights.json`

---

##  How the Algorithms Work

### minimax with Alpha-Beta pruning

The minimax algorithm explores the game tree to find the optimal move:

```
function MINIMAX(state, depth, maximizingPlayer):
    if depth = 0 or game over:
        return heuristic_evaluation(state)
    
    if maximizingPlayer:
        maxEval = -∞
        for each move in valid_moves:
            eval = MINIMAX(result(state, move), depth-1, FALSE)
            maxEval = max(maxEval, eval)
        return maxEval
    else:
        minEval = +∞
        for each move in valid_moves:
            eval = MINIMAX(result(state, move), depth-1, TRUE)
            minEval = min(minEval, eval)
        return minEval
```

**Alpha-Beta pruning** optimizes this by cutting off branches that won't affect the final decision:
- **Alpha**: Best value the maximizer can guarantee
- **Beta**: Best value the minimizer can guarantee
- Prune when alpha ≥ beta

### Heuristic Evaluation

The agents evaluate board positions using weighted features:

| Feature | Description | Purpose |
|---------|-------------|---------|
| `three` | 3 pieces in a row with 1 empty | Strong offensive position |
| `two` | 2 pieces in a row with 2 empty | Building potential |
| `center` | Control of center column | Strategic advantage |
| `opp_three` | Opponent has 3 in a row | Defensive urgency |
| `double_threat` | Two winning threats at once | Nearly guaranteed win |

### Adaptive Learning

After each game, the Evolving agent:

1. **analyzes** the game positions
2. **counts** patterns (threats, center control, etc.)
3. **adjusts** weights based on outcome:
   - **Win**: boost weights of patterns that appeared
   - **loss**: increase defensive weights, adjust strategy
4. **saves** updated weights for next game

---

## training the Adaptive Agent

To train the adaptive agent against the minimax agent:

run these commands
```cd Connect4_game/src```
```python3 train.py```

This will:
1. play 100 games vs easy minimax
2. play 200 games vs medium minimax
3. play 100 games vs hard minimax
4. save the learned weights to `agent_weights.json`
---

## references
- I relied heavily on the course slides and searching the internet 

---

## team member worked in this game:

**Majed AlDajani** 
