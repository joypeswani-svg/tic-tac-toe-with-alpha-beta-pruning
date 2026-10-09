"""
Game logic for 3x3 Tic-Tac-Toe.
"""

from typing import List, Optional, Tuple, Dict, Any

PLAYER_X = "X"
PLAYER_O = "O"
EMPTY = ""

WIN_COMBINATIONS = [
    (0, 1, 2),  # Rows
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),  # Columns
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),  # Diagonals
    (2, 4, 6),
]


def create_empty_board() -> List[str]:
    """Return an empty 3x3 board."""
    return [EMPTY] * 9


def normalize_board(board: List[Any]) -> List[str]:
    """Convert nulls, spaces, or empty strings to standardized EMPTY strings."""
    normalized = []
    for cell in board:
        if cell is None or str(cell).strip() == "":
            normalized.append(EMPTY)
        elif str(cell).upper() == PLAYER_X:
            normalized.append(PLAYER_X)
        elif str(cell).upper() == PLAYER_O:
            normalized.append(PLAYER_O)
        else:
            normalized.append(EMPTY)
    return normalized


def check_winner(board: List[str]) -> Tuple[Optional[str], Optional[Tuple[int, int, int]]]:
    """
    Check if there is a winner.
    Returns (winner_symbol, winning_combination_tuple) or (None, None).
    """
    for a, b, c in WIN_COMBINATIONS:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a], (a, b, c)
    return None, None


def is_board_full(board: List[str]) -> bool:
    """Return True if all 9 cells are occupied."""
    return all(cell != EMPTY for cell in board)


def is_game_over(board: List[str]) -> bool:
    """Return True if game is won or board is full."""
    winner, _ = check_winner(board)
    return winner is not None or is_board_full(board)


def get_available_moves(board: List[str]) -> List[int]:
    """Return list of valid indices (0-8) that are empty."""
    return [i for i, cell in enumerate(board) if cell == EMPTY]


def is_valid_move(board: List[str], move: int) -> bool:
    """Validate if move is an integer 0-8 and the cell is empty."""
    if not isinstance(move, int) or move < 0 or move > 8:
        return False
    return board[move] == EMPTY


def make_move(board: List[str], move: int, player: str) -> List[str]:
    """Return a new board with the move applied."""
    new_board = list(board)
    new_board[move] = player
    return new_board


def get_game_state(board: List[str], human_player: str = PLAYER_X, ai_player: str = PLAYER_O) -> Dict[str, Any]:
    """
    Return comprehensive game status.
    status: 'in_progress' | 'human_win' | 'ai_win' | 'draw'
    """
    winner, winning_line = check_winner(board)
    full = is_board_full(board)

    if winner == human_player:
        status = "human_win"
    elif winner == ai_player:
        status = "ai_win"
    elif full:
        status = "draw"
    else:
        status = "in_progress"

    return {
        "status": status,
        "winner": winner,
        "winning_line": list(winning_line) if winning_line else None,
        "is_game_over": status != "in_progress",
        "available_moves": get_available_moves(board),
    }
