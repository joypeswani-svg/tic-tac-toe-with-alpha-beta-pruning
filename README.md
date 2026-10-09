# 🎮 Tic-Tac-Toe: Minimax & Alpha-Beta Pruning (AI Educational Web App)

A full-featured, interactive, two-pane web application built for a college project in **Foundations of Artificial Intelligence (Adversarial Search)**. The application allows a human to play against an unbeatable AI while learning how the **Minimax** algorithm and **Alpha-Beta Pruning** work under the hood through real-time performance analytics and decision tree visualization.

---

## 📸 Application Screenshot

```
+------------------------------------+---+------------------------------------+
| LEFT PANE: PLAYABLE TIC-TAC-TOE    | | | RIGHT PANE: ALGORITHM ANALYSIS     |
|                                    | | |                                    |
| [🏆 SCORE BOARD: Human / AI / Draw]| | | [📊 Performance Comparison Table]  |
|                                    | | | - Nodes Explored: 549,946 vs 20,866|
| [3x3 Board with #3d1515 UI]        | | | - Search Efficiency: 96.2% fewer   |
| - Interactive click to move (X)    | | |                                    |
| - Turn indicator & Status updates  | | | [🌳 Live Decision Tree (SVG)]      |
| - Algorithm selector (Minimax / AB)| | | - Solid circles: Evaluated nodes   |
| - Difficulty (Hard / Med / Easy)   | | | - Dashed circles: Pruned nodes     |
| - First move toggle (Human / AI)   | | | - Hover nodes for name, score & α/β|
| - "New Game" & "Reset Scores"      | | | - ⛶ Fullscreen & Back to Normal    |
|                                    | | | [🎯 Candidate Move Scores & Map]   |
|                                    | | | [📈 Nodes Explored Bar Chart]      |
|                                    | | | [📖 Educational How-It-Works Box]  |
+------------------------------------+---+------------------------------------+
                   <-- Draggable Resizable Divider -->
```
*(Placeholder: Replace with screenshot of `http://localhost:5000` after running the application)*

---

## 🚀 How to Run

### 1. Requirements
- Python 3.8 or newer
- Modern web browser (Chrome, Safari, Firefox, Edge)

### 2. Setup Virtual Environment & Install Dependencies
```bash
# Navigate to the project root directory
cd "Tic Tac Toe"

# Create a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (Flask & pytest)
pip install -r requirements.txt
```

### 3. Start the Web Server
```bash
python app.py
```

### 4. Open the App in Your Browser
Visit: **[http://localhost:5001](http://localhost:5001)** (or **[http://localhost:5000](http://localhost:5000)**)

> **💡 macOS Tip (HTTP 403 on Port 5000):**  
> On macOS Monterey and later, Apple's **AirPlay Receiver** (`ControlCenter`) listens on port 5000 by default and returns an HTTP 403 Forbidden error. `app.py` automatically detects this and starts on **port 5001** (`http://localhost:5001`). Alternatively, you can disable AirPlay Receiver in **System Settings > General > AirDrop & AirPlay > AirPlay Receiver (toggle OFF)**.


---

## 🧪 Running the Automated Test Suite

Run the full pytest suite (17 tests verifying win/draw logic, minimax equivalence, alpha-beta efficiency, exhaustive proof of non-loss, API routes, and presentation PDF delivery):

```bash
pytest -v
```

All 17 tests pass deterministically in under 2 seconds:
- `test_win_detection`: Verifies all 8 winning rows, columns, and diagonals.
- `test_draw_detection`: Verifies terminal draw state when the board fills with no winner.
- `test_valid_moves`: Verifies legal bounds and cell occupancy protection.
- `test_minimax_alphabeta_equivalence_random_positions`: Proves Minimax and Alpha-Beta produce identical scores across 30 arbitrary game states, with Alpha-Beta exploring fewer or equal nodes.
- `test_alphabeta_prunes_empty_board`: Verifies exact measured node counts from an empty board.
- `test_ai_never_loses_exhaustive_human_first`: Exhaustively simulates all 569 complete game paths when human plays first—proving **0 AI losses**.
- `test_ai_never_loses_exhaustive_ai_first`: Exhaustively simulates all 73 complete game paths when AI plays first—proving **0 AI losses**.
- `test_decision_tree_structure`: Verifies node attributes, alpha/beta bounds, and cutoff tracking.
- `test_app.py` suite: Verifies all Flask endpoints (`/`, `/api/move`, `/api/reset`, `/presentation.pdf`), illegal move handling, AI opening moves, and difficulty parameters.

---

## 📊 Empty-Board Node Counts & Algorithm Comparison

> **For Presentation Quoting:**  
> When analyzing an empty $3 \times 3$ Tic-Tac-Toe board from scratch (depth 0), pure **Minimax** performs an exhaustive depth-first search exploring exactly **549,946 game states (nodes)**. In contrast, **Alpha-Beta Pruning** evaluates the identical game tree and identifies the exact same optimal value ($0$, guaranteeing at least a draw) while exploring only **20,866 nodes** and executing **7,692 branch cutoffs**. This represents an **elimination of 529,080 redundant states (a 96.2% reduction in search space)**, reducing initial compute latency from $\sim 800\text{ ms}$ down to $\sim 25\text{ ms}$ ($\approx 32\times$ speedup) without discarding any candidate paths that could affect the optimal minimax decision.

### Measured Comparison Summary Table

| Metric | Minimax (No Pruning) | Minimax + Alpha-Beta Pruning | Impact / Speedup |
| :--- | :---: | :---: | :---: |
| **Nodes Explored (Empty Board)** | **549,946** | **20,866** | **96.2% fewer nodes** |
| **Pruned Branches** | 0 | **7,692** | 7,692 subtrees skipped |
| **Execution Time (Empty Board)** | $\sim 800\text{ ms}$ | $\sim 25\text{ ms}$ | **$32\times$ faster** |
| **Decision Optimality** | Optimal ($0$) | Optimal ($0$) | **Identical outcome** |
| **Total Possible Games** | 255,168 | 255,168 | Identical game space |
| **AI Losses (Exhaustive)** | **0** | **0** | **Mathematically Unbeatable** |

---

## 🧠 Algorithmic Concepts (How It Works)

### 1. Minimax Principle
The game tree consists of alternating decision layers:
- **MAX Nodes (AI Turn):** Maximizes the utility score:
  $$\text{Score}(\text{AI Win}) = +10 - \text{depth}, \quad \text{Score}(\text{Draw}) = 0$$
- **MIN Nodes (Human Turn):** Minimizes the utility score:
  $$\text{Score}(\text{Human Win}) = \text{depth} - 10$$

Incorporating depth ensures the AI prefers **faster wins** (smaller depth $\implies$ larger positive score) and **delayed losses** (larger depth $\implies$ less negative score).

### 2. Alpha-Beta Bounds
- $\alpha$ (**Alpha**): The highest score guaranteed to the MAX player along the path from root. Initialized to $-\infty$.
- $\beta$ (**Beta**): The lowest score guaranteed to the MIN player along the path from root. Initialized to $+\infty$.

### 3. The Pruning Condition: $\beta \le \alpha$
During depth-first traversal:
- Whenever a child node produces a value such that $\beta \le \alpha$, the parent already possesses an alternative branch that guarantees a better (or equal) payoff.
- Therefore, the remaining sibling branches from this node can never influence the root's decision and are safely **pruned** (a cutoff occurs).

---

## 🖥️ Screen Layout & Features

### Left Pane: Playable Game
- **Score Board Card:** Green card displaying cumulative counts of Human wins, AI wins, Draws, and a "Reset Scores" button (stored in `localStorage`).
- **Main Tic-Tac-Toe Board:** 3x3 grid with animated markers (`X` in deep navy, `O` in coral), winning cell pulse animation, and status banner.
- **Algorithm Selector:** Choose between `Minimax + Alpha-Beta` and `Minimax (No Pruning)`.
- **Difficulty Selector:**
  - *Hard (Full Depth):* Unbeatable, full search lookahead.
  - *Medium (Depth-Limited: 3):* Searches ahead 3 plies; blocks immediate threats but susceptible to subtle forks.
  - *Easy:* Incorporates deliberate random mistakes (40% probability).
- **First Move Selector:** Toggle between Human ($X$) and AI ($O$). When AI is set to start, it immediately executes its opening move on the empty board.
- **New Game Button:** Resets the board and initiates a fresh game session.

### Draggable Resizable Divider
- Interactive vertical divider between the two panes with left and right arrow handles (`◂` and `▸`).
- Allows smooth mouse/touch dragging to expand or collapse the right analysis window without breaking responsiveness.

### Right Pane: Educational AI Analysis
- **Performance Comparison Table:** Live side-by-side comparison of *Nodes Explored*, *Execution Time (ms)*, *Pruned Branches*, and *Search Efficiency (% fewer nodes)* for both the current move and cumulative across the game.
- **Decision Tree Visualizer (SVG):**
  - Renders root MAX node and child MIN nodes.
  - **Solid Circles:** Evaluated states.
  - **Dashed Circles:** Pruned states (cutoffs).
  - Annotations show $\alpha$ and $\beta$ bounds at each node.
  - Click any depth-1 candidate node to zoom into its specific lookahead subtree!
  - Click "View Root" to restore the top-level tree.
- **Candidate Move Scores & Mini-Board:** Heatmap display showing candidate values ($+8, 0, -8$, etc.) on each empty cell and highlighting the chosen move.
- **Nodes Explored History Chart:** Responsive SVG bar chart comparing search volume (Minimax vs Alpha-Beta) per move.
- **"How It Works" Box:** Student-friendly reference explaining adversarial search and pruning rules.

---

## 📁 Project Structure

```
Tic Tac Toe/
├── app.py              # Flask server routes (/ and /api/move, /api/reset)
├── game.py             # Board state, win/draw checks, winning combinations
├── ai.py               # Minimax & Alpha-Beta implementations, instrumentation, tree builder
├── pytest.ini          # Pytest configuration (pythonpath = .)
├── requirements.txt    # Flask and pytest dependencies
├── README.md           # Documentation, run instructions, and theory
├── templates/
│   └── index.html      # Two-pane HTML5 layout and semantic markup
├── static/
│   ├── style.css       # Emerald theme styling, animations, responsive divider
│   └── script.js       # Game loop, fetch API, SVG tree visualizer, bar chart
└── tests/
    ├── test_ai.py      # Algorithmic tests, equivalence check, exhaustive proof
    └── test_app.py     # Integration tests for Flask endpoints and API contracts
```

---

## 🎓 Academic Presentation Notes
- **Why are Alpha-Beta and Minimax scores identical?**  
  Alpha-Beta pruning is mathematically guaranteed to prune only subtrees that are strictly inferior to an already discovered path. It never discards an optimal path.
- **Why are empty-board counts so large in Minimax?**  
  Tic-Tac-Toe has $9! = 362,880$ permutations of move sequences, plus early terminal wins. Without pruning, Minimax evaluates all 549,946 internal and leaf states.
- **Why can the AI never lose?**  
  In a finite, zero-sum, perfect-information game with optimal play by both sides, Tic-Tac-Toe is a theoretical draw. Because Minimax searches every terminal path, it selects minimax-optimal moves that ensure a human opponent can never reach a winning configuration.
