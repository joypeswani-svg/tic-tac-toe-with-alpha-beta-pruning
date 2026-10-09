"""
AI logic for Tic-Tac-Toe: Minimax and Alpha-Beta Pruning.
Includes performance instrumentation and decision-tree generation.
"""

import time
import random
import copy
from typing import List, Optional, Tuple, Dict, Any
import game

INFINITY = 1000  # Used for alpha-beta bounds representing +/- infinity


def evaluate_terminal(board: List[str], depth: int, ai_player: str, human_player: str) -> Optional[int]:
    """
    Scoring:
      AI win = +10 - depth (faster win preferred)
      Human win = depth - 10 (slower loss preferred)
      Draw = 0
    Returns score int if terminal, else None.
    """
    winner, _ = game.check_winner(board)
    if winner == ai_player:
        return 10 - depth
    if winner == human_player:
        return depth - 10
    if game.is_board_full(board):
        return 0
    return None


def minimax(
    board: List[str],
    depth: int,
    maximizing: bool,
    ai_player: str = game.PLAYER_O,
    human_player: str = game.PLAYER_X,
    stats: Optional[Dict[str, Any]] = None,
    max_depth: Optional[int] = None,
) -> Tuple[int, Optional[int]]:
    """
    Pure Minimax algorithm with NO pruning.
    Returns (best_score, best_move).
    """
    if stats is not None:
        stats["nodes_explored"] += 1

    terminal_score = evaluate_terminal(board, depth, ai_player, human_player)
    if terminal_score is not None:
        return terminal_score, None

    if max_depth is not None and depth >= max_depth:
        return 0, None

    available_moves = game.get_available_moves(board)

    if maximizing:
        best_score = -INFINITY
        best_move = None
        for move in available_moves:
            next_board = game.make_move(board, move, ai_player)
            score, _ = minimax(
                next_board,
                depth + 1,
                False,
                ai_player=ai_player,
                human_player=human_player,
                stats=stats,
                max_depth=max_depth,
            )
            if score > best_score:
                best_score = score
                best_move = move
        return best_score, best_move
    else:
        best_score = INFINITY
        best_move = None
        for move in available_moves:
            next_board = game.make_move(board, move, human_player)
            score, _ = minimax(
                next_board,
                depth + 1,
                True,
                ai_player=ai_player,
                human_player=human_player,
                stats=stats,
                max_depth=max_depth,
            )
            if score < best_score:
                best_score = score
                best_move = move
        return best_score, best_move


def alphabeta(
    board: List[str],
    depth: int,
    alpha: float,
    beta: float,
    maximizing: bool,
    ai_player: str = game.PLAYER_O,
    human_player: str = game.PLAYER_X,
    stats: Optional[Dict[str, Any]] = None,
    max_depth: Optional[int] = None,
) -> Tuple[int, Optional[int]]:
    """
    Alpha-Beta Pruning algorithm.
    Pruning condition: if beta <= alpha: break.
    Returns (best_score, best_move).
    """
    if stats is not None:
        stats["nodes_explored"] += 1

    terminal_score = evaluate_terminal(board, depth, ai_player, human_player)
    if terminal_score is not None:
        return terminal_score, None

    if max_depth is not None and depth >= max_depth:
        return 0, None

    available_moves = game.get_available_moves(board)

    if maximizing:
        best_score = -INFINITY
        best_move = None
        for move in available_moves:
            next_board = game.make_move(board, move, ai_player)
            score, _ = alphabeta(
                next_board,
                depth + 1,
                alpha,
                beta,
                False,
                ai_player=ai_player,
                human_player=human_player,
                stats=stats,
                max_depth=max_depth,
            )
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score)
            if beta <= alpha:
                if stats is not None:
                    stats["branches_pruned"] += 1
                break
        return best_score, best_move
    else:
        best_score = INFINITY
        best_move = None
        for move in available_moves:
            next_board = game.make_move(board, move, human_player)
            score, _ = alphabeta(
                next_board,
                depth + 1,
                alpha,
                beta,
                True,
                ai_player=ai_player,
                human_player=human_player,
                stats=stats,
                max_depth=max_depth,
            )
            if score < best_score:
                best_score = score
                best_move = move
            beta = min(beta, best_score)
            if beta <= alpha:
                if stats is not None:
                    stats["branches_pruned"] += 1
                break
        return best_score, best_move


def format_bound(val: float) -> str:
    """Format alpha or beta for display (e.g. -inf, +inf, or int)."""
    if val <= -INFINITY:
        return "-∞"
    if val >= INFINITY:
        return "+∞"
    return str(int(val))


def build_decision_tree(
    board: List[str],
    depth: int = 0,
    max_tree_depth: int = 2,
    alpha: float = -INFINITY,
    beta: float = INFINITY,
    maximizing: bool = True,
    ai_player: str = game.PLAYER_O,
    human_player: str = game.PLAYER_X,
    move_played: Optional[int] = None,
    node_id: str = "root",
    enable_pruning: bool = True,
) -> Dict[str, Any]:
    """
    Build a decision tree up to max_tree_depth that explicitly records:
    - Node type (MAX or MIN)
    - Alpha and Beta bounds (if enable_pruning is True)
    - Evaluated score
    - Pruned nodes (dashed circles in visualization, only when enable_pruning is True)
    - Board snapshot
    """
    player_turn = ai_player if maximizing else human_player
    node_type = "MAX" if maximizing else "MIN"

    node = {
        "id": node_id,
        "type": node_type,
        "player": player_turn,
        "depth": depth,
        "move": move_played,
        "alpha": format_bound(alpha) if enable_pruning else "N/A",
        "beta": format_bound(beta) if enable_pruning else "N/A",
        "score": None,
        "pruned": False,
        "board": list(board),
        "children": [],
        "chosen": False,
    }

    terminal_score = evaluate_terminal(board, depth, ai_player, human_player)
    if terminal_score is not None:
        node["score"] = terminal_score
        node["is_terminal"] = True
        return node

    if depth >= max_tree_depth:
        # At tree depth limit, compute the node's true score
        if enable_pruning:
            score, _ = alphabeta(
                board,
                depth,
                alpha,
                beta,
                maximizing,
                ai_player=ai_player,
                human_player=human_player,
            )
        else:
            score, _ = minimax(
                board,
                depth,
                maximizing,
                ai_player=ai_player,
                human_player=human_player,
            )
        node["score"] = score
        return node

    available_moves = game.get_available_moves(board)
    current_alpha = alpha
    current_beta = beta

    if maximizing:
        best_score = -INFINITY
        best_child_idx = None
        pruned_from_idx = None

        for idx, move in enumerate(available_moves):
            child_id = f"{node_id}_m{move}"
            next_board = game.make_move(board, move, ai_player)

            child_node = build_decision_tree(
                next_board,
                depth=depth + 1,
                max_tree_depth=max_tree_depth,
                alpha=current_alpha,
                beta=current_beta,
                maximizing=False,
                ai_player=ai_player,
                human_player=human_player,
                move_played=move,
                node_id=child_id,
                enable_pruning=enable_pruning,
            )

            child_score = child_node["score"] if child_node["score"] is not None else 0
            if child_score > best_score:
                best_score = child_score
                best_child_idx = idx

            current_alpha = max(current_alpha, child_score)
            node["children"].append(child_node)

            if enable_pruning and current_beta <= current_alpha:
                # Alpha-beta pruning triggered!
                pruned_from_idx = idx + 1
                break

        # If pruning occurred, add the remaining candidate moves as pruned nodes
        if enable_pruning and pruned_from_idx is not None and pruned_from_idx < len(available_moves):
            for move in available_moves[pruned_from_idx:]:
                child_id = f"{node_id}_m{move}_pruned"
                pruned_board = game.make_move(board, move, ai_player)
                node["children"].append({
                    "id": child_id,
                    "type": "MIN",
                    "player": human_player,
                    "depth": depth + 1,
                    "move": move,
                    "alpha": format_bound(current_alpha),
                    "beta": format_bound(current_beta),
                    "score": None,
                    "pruned": True,
                    "board": pruned_board,
                    "children": [],
                    "chosen": False,
                })

        if best_child_idx is not None and best_child_idx < len(node["children"]):
            node["children"][best_child_idx]["chosen"] = True

        node["score"] = best_score
        node["alpha"] = format_bound(current_alpha) if enable_pruning else "N/A"
        node["beta"] = format_bound(current_beta) if enable_pruning else "N/A"
        return node

    else:
        best_score = INFINITY
        best_child_idx = None
        pruned_from_idx = None

        for idx, move in enumerate(available_moves):
            child_id = f"{node_id}_m{move}"
            next_board = game.make_move(board, move, human_player)

            child_node = build_decision_tree(
                next_board,
                depth=depth + 1,
                max_tree_depth=max_tree_depth,
                alpha=current_alpha,
                beta=current_beta,
                maximizing=True,
                ai_player=ai_player,
                human_player=human_player,
                move_played=move,
                node_id=child_id,
                enable_pruning=enable_pruning,
            )

            child_score = child_node["score"] if child_node["score"] is not None else 0
            if child_score < best_score:
                best_score = child_score
                best_child_idx = idx

            current_beta = min(current_beta, child_score)
            node["children"].append(child_node)

            if enable_pruning and current_beta <= current_alpha:
                # Pruning triggered!
                pruned_from_idx = idx + 1
                break

        if enable_pruning and pruned_from_idx is not None and pruned_from_idx < len(available_moves):
            for move in available_moves[pruned_from_idx:]:
                child_id = f"{node_id}_m{move}_pruned"
                pruned_board = game.make_move(board, move, human_player)
                node["children"].append({
                    "id": child_id,
                    "type": "MAX",
                    "player": ai_player,
                    "depth": depth + 1,
                    "move": move,
                    "alpha": format_bound(current_alpha),
                    "beta": format_bound(current_beta),
                    "score": None,
                    "pruned": True,
                    "board": pruned_board,
                    "children": [],
                    "chosen": False,
                })

        if best_child_idx is not None and best_child_idx < len(node["children"]):
            node["children"][best_child_idx]["chosen"] = True

        node["score"] = best_score
        node["alpha"] = format_bound(current_alpha) if enable_pruning else "N/A"
        node["beta"] = format_bound(current_beta) if enable_pruning else "N/A"
        return node


def analyze_candidate_moves(
    board: List[str],
    ai_player: str = game.PLAYER_O,
    human_player: str = game.PLAYER_X,
    max_depth: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Evaluate every available legal move from the current board state
    and return scores and rankings.
    """
    available_moves = game.get_available_moves(board)
    candidate_moves = []

    for move in available_moves:
        next_board = game.make_move(board, move, ai_player)
        # Use full alphabeta to evaluate the candidate move
        score, _ = alphabeta(
            next_board,
            depth=1,
            alpha=-INFINITY,
            beta=INFINITY,
            maximizing=False,
            ai_player=ai_player,
            human_player=human_player,
            max_depth=max_depth,
        )
        candidate_moves.append({
            "move": move,
            "score": score,
            "row": move // 3,
            "col": move % 3,
            "chosen": False,
        })

    return candidate_moves


def get_ai_move(
    board: List[str],
    ai_player: str = game.PLAYER_O,
    human_player: str = game.PLAYER_X,
    algorithm: str = "alphabeta",
    difficulty: str = "hard",
) -> Dict[str, Any]:
    """
    Execute AI turn analysis:
    1. Runs Minimax on board (measures nodes explored, execution time ms).
    2. Runs Alpha-Beta on board (measures nodes explored, pruned branches, execution time ms).
    3. Analyzes all candidate moves.
    4. Builds decision tree for visualization.
    5. Picks AI move according to algorithm and difficulty.
    """
    available_moves = game.get_available_moves(board)
    if not available_moves:
        return {
            "move": None,
            "minimax_stats": {"nodes_explored": 0, "execution_time_ms": 0.0, "branches_pruned": 0},
            "alphabeta_stats": {"nodes_explored": 0, "execution_time_ms": 0.0, "branches_pruned": 0},
            "efficiency": {"percent_fewer_nodes": 0.0, "nodes_saved": 0},
            "candidate_moves": [],
            "decision_tree": None,
        }

    # Determine depth limit based on difficulty
    max_depth = None
    if difficulty == "medium":
        max_depth = 3  # Depth-limited search (looks ahead 3 plies)

    # 1. Run Minimax
    mm_stats = {"nodes_explored": 0}
    t0_mm = time.perf_counter()
    mm_score, mm_move = minimax(
        board,
        depth=0,
        maximizing=True,
        ai_player=ai_player,
        human_player=human_player,
        stats=mm_stats,
        max_depth=max_depth,
    )
    t1_mm = time.perf_counter()
    mm_time_ms = round((t1_mm - t0_mm) * 1000, 3)

    # 2. Run Alpha-Beta
    ab_stats = {"nodes_explored": 0, "branches_pruned": 0}
    t0_ab = time.perf_counter()
    ab_score, ab_move = alphabeta(
        board,
        depth=0,
        alpha=-INFINITY,
        beta=INFINITY,
        maximizing=True,
        ai_player=ai_player,
        human_player=human_player,
        stats=ab_stats,
        max_depth=max_depth,
    )
    t1_ab = time.perf_counter()
    ab_time_ms = round((t1_ab - t0_ab) * 1000, 3)

    # 3. Calculate Efficiency (% fewer nodes explored)
    mm_nodes = mm_stats["nodes_explored"]
    ab_nodes = ab_stats["nodes_explored"]
    nodes_saved = max(0, mm_nodes - ab_nodes)
    if mm_nodes > 0:
        pct_fewer = round(((mm_nodes - ab_nodes) / mm_nodes) * 100, 1)
    else:
        pct_fewer = 0.0

    # 4. Candidate moves analysis
    candidate_moves = analyze_candidate_moves(
        board,
        ai_player=ai_player,
        human_player=human_player,
        max_depth=max_depth,
    )

    # 5. Decide chosen move
    if difficulty == "easy" and random.random() < 0.4 and len(available_moves) > 1:
        # Easy mode: 40% chance of making a random move
        chosen_move = random.choice(available_moves)
    else:
        # Hard mode or optimal move from selected algorithm
        chosen_move = ab_move if algorithm == "alphabeta" else mm_move

    # Mark chosen move in candidate moves list
    for cand in candidate_moves:
        if cand["move"] == chosen_move:
            cand["chosen"] = True

    # 6. Build decision tree for visualization (respects selected algorithm)
    enable_pruning = (algorithm == "alphabeta")
    decision_tree = build_decision_tree(
        board,
        depth=0,
        max_tree_depth=2,
        alpha=-INFINITY if enable_pruning else -INFINITY,
        beta=INFINITY if enable_pruning else INFINITY,
        maximizing=True,
        ai_player=ai_player,
        human_player=human_player,
        move_played=None,
        node_id="root",
        enable_pruning=enable_pruning,
    )

    # Ensure the chosen child in the tree matches chosen_move
    if decision_tree and "children" in decision_tree:
        for child in decision_tree["children"]:
            child["chosen"] = (child.get("move") == chosen_move)

    return {
        "move": chosen_move,
        "score": ab_score if algorithm == "alphabeta" else mm_score,
        "minimax_stats": {
            "nodes_explored": mm_nodes,
            "execution_time_ms": mm_time_ms,
            "branches_pruned": 0,
        },
        "alphabeta_stats": {
            "nodes_explored": ab_nodes,
            "execution_time_ms": ab_time_ms,
            "branches_pruned": ab_stats["branches_pruned"],
        },
        "efficiency": {
            "percent_fewer_nodes": pct_fewer,
            "nodes_saved": nodes_saved,
        },
        "candidate_moves": candidate_moves,
        "decision_tree": decision_tree,
    }
