"""
Unit tests for Tic-Tac-Toe Game Logic and AI Algorithms.
"""

import random
import pytest
import game
import ai


def test_win_detection():
    """Verify all 8 winning lines (3 rows, 3 cols, 2 diagonals) and non-wins."""
    # Rows
    for row in range(3):
        b = game.create_empty_board()
        for col in range(3):
            b[row * 3 + col] = "X"
        winner, line = game.check_winner(b)
        assert winner == "X"
        assert line == (row * 3, row * 3 + 1, row * 3 + 2)

    # Columns
    for col in range(3):
        b = game.create_empty_board()
        for row in range(3):
            b[row * 3 + col] = "O"
        winner, line = game.check_winner(b)
        assert winner == "O"
        assert line == (col, col + 3, col + 6)

    # Diagonals
    b_diag1 = ["X", "", "", "", "X", "", "", "", "X"]
    winner, line = game.check_winner(b_diag1)
    assert winner == "X"
    assert line == (0, 4, 8)

    b_diag2 = ["", "", "O", "", "O", "", "O", "", ""]
    winner, line = game.check_winner(b_diag2)
    assert winner == "O"
    assert line == (2, 4, 6)

    # Empty board has no winner
    assert game.check_winner(game.create_empty_board()) == (None, None)


def test_draw_detection():
    """Verify draw detection when board is full and no winner."""
    # Draw board:
    # X O X
    # X O O
    # O X X
    draw_board = ["X", "O", "X", "X", "O", "O", "O", "X", "X"]
    assert game.is_board_full(draw_board)
    winner, _ = game.check_winner(draw_board)
    assert winner is None
    status = game.get_game_state(draw_board)
    assert status["status"] == "draw"
    assert status["is_game_over"] is True


def test_valid_moves():
    """Verify move validation."""
    b = game.create_empty_board()
    assert game.is_valid_move(b, 0)
    assert game.is_valid_move(b, 8)
    assert not game.is_valid_move(b, 9)
    assert not game.is_valid_move(b, -1)

    b[4] = "X"
    assert not game.is_valid_move(b, 4)
    assert len(game.get_available_moves(b)) == 8


def test_minimax_alphabeta_equivalence_random_positions():
    """
    Minimax and Alpha-Beta must always return the exact same best score
    and best move across diverse board positions.
    Also verifies Alpha-Beta explores fewer or equal nodes.
    """
    random.seed(42)

    # Test 30 random reachable positions with various move counts (1 to 7 moves)
    for _ in range(30):
        board = game.create_empty_board()
        moves_count = random.randint(1, 6)
        current_player = "X"
        for _ in range(moves_count):
            avail = game.get_available_moves(board)
            if not avail:
                break
            m = random.choice(avail)
            board[m] = current_player
            current_player = "O" if current_player == "X" else "X"
            if game.is_game_over(board):
                break

        if game.is_game_over(board):
            continue

        mm_stats = {"nodes_explored": 0}
        ab_stats = {"nodes_explored": 0, "branches_pruned": 0}

        mm_score, mm_move = ai.minimax(board, 0, True, ai_player="O", human_player="X", stats=mm_stats)
        ab_score, ab_move = ai.alphabeta(
            board, 0, -ai.INFINITY, ai.INFINITY, True, ai_player="O", human_player="X", stats=ab_stats
        )

        # Both must return the identical score
        assert mm_score == ab_score, f"Scores differed at board {board}: MM={mm_score}, AB={ab_score}"

        # If best moves differ, both moves must achieve the same optimal score
        if mm_move != ab_move:
            # Verify ab_move and mm_move both have optimal score
            board_mm = game.make_move(board, mm_move, "O")
            score_mm_test, _ = ai.alphabeta(board_mm, 1, -ai.INFINITY, ai.INFINITY, False, "O", "X")
            board_ab = game.make_move(board, ab_move, "O")
            score_ab_test, _ = ai.alphabeta(board_ab, 1, -ai.INFINITY, ai.INFINITY, False, "O", "X")
            assert score_mm_test == score_ab_test == mm_score

        # Alpha-Beta must explore fewer or equal nodes
        assert ab_stats["nodes_explored"] <= mm_stats["nodes_explored"], (
            f"Alpha-Beta explored more nodes ({ab_stats['nodes_explored']}) than Minimax ({mm_stats['nodes_explored']})"
        )


def test_alphabeta_prunes_empty_board():
    """
    Verify empty-board node counts:
    Minimax explores ~550,000 nodes (exactly 549,946).
    Alpha-Beta explores significantly fewer nodes (~20,866, >95% reduction).
    """
    board = game.create_empty_board()
    mm_stats = {"nodes_explored": 0}
    ab_stats = {"nodes_explored": 0, "branches_pruned": 0}

    mm_score, mm_move = ai.minimax(board, 0, True, ai_player="O", human_player="X", stats=mm_stats)
    ab_score, ab_move = ai.alphabeta(
        board, 0, -ai.INFINITY, ai.INFINITY, True, ai_player="O", human_player="X", stats=ab_stats
    )

    assert mm_score == ab_score == 0
    assert mm_move == ab_move
    assert mm_stats["nodes_explored"] == 549946
    assert ab_stats["nodes_explored"] == 20866
    assert ab_stats["branches_pruned"] == 7692

    reduction_pct = (mm_stats["nodes_explored"] - ab_stats["nodes_explored"]) / mm_stats["nodes_explored"] * 100
    assert reduction_pct > 95.0


def test_ai_never_loses_exhaustive_human_first():
    """
    Exhaustive search over EVERY possible sequence of human moves when human plays first.
    Proves that the AI can never lose (0 losses across all 569 terminal paths).
    """
    def play_path(board, human_turn):
        winner, _ = game.check_winner(board)
        if winner == "X":
            pytest.fail(f"AI lost on board: {board}")
        if winner == "O" or game.is_board_full(board):
            return

        if human_turn:
            for move in game.get_available_moves(board):
                next_board = game.make_move(board, move, "X")
                play_path(next_board, False)
        else:
            _, ai_move = ai.alphabeta(
                board, 0, -ai.INFINITY, ai.INFINITY, True, ai_player="O", human_player="X"
            )
            next_board = game.make_move(board, ai_move, "O")
            play_path(next_board, True)

    play_path(game.create_empty_board(), human_turn=True)


def test_ai_never_loses_exhaustive_ai_first():
    """
    Exhaustive search over EVERY possible sequence of human moves when AI plays first.
    Proves that the AI can never lose (0 losses across all 73 terminal paths).
    """
    def play_path(board, ai_turn):
        winner, _ = game.check_winner(board)
        if winner == "X":
            pytest.fail(f"AI lost on board: {board}")
        if winner == "O" or game.is_board_full(board):
            return

        if ai_turn:
            _, ai_move = ai.alphabeta(
                board, 0, -ai.INFINITY, ai.INFINITY, True, ai_player="O", human_player="X"
            )
            next_board = game.make_move(board, ai_move, "O")
            play_path(next_board, False)
        else:
            for move in game.get_available_moves(board):
                next_board = game.make_move(board, move, "X")
                play_path(next_board, True)

    play_path(game.create_empty_board(), ai_turn=True)


def test_decision_tree_structure():
    """Verify decision tree contains nodes, alpha, beta, and pruned status."""
    board = ["X", "", "", "", "O", "", "", "", ""]
    tree = ai.build_decision_tree(board, depth=0, max_tree_depth=2)
    assert tree["id"] == "root"
    assert tree["type"] == "MAX"
    assert len(tree["children"]) == 7  # 7 empty cells
    # Check that children have alpha, beta, and valid node attributes
    for child in tree["children"]:
        assert "alpha" in child
        assert "beta" in child
        assert "pruned" in child
        assert "move" in child


def test_decision_tree_minimax_no_pruning():
    """Verify that when enable_pruning=False, 0 nodes are pruned in the decision tree."""
    board = ["X", "", "", "", "O", "", "", "", ""]
    tree = ai.build_decision_tree(board, depth=0, max_tree_depth=2, enable_pruning=False)
    assert tree["id"] == "root"
    assert tree["alpha"] == "N/A"
    assert tree["beta"] == "N/A"

    def verify_no_pruned_nodes(node):
        assert node["pruned"] is False
        for c in node["children"]:
            verify_no_pruned_nodes(c)

    verify_no_pruned_nodes(tree)
