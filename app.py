"""
Flask application for Tic-Tac-Toe with Minimax & Alpha-Beta Pruning.
"""

from flask import Flask, render_template, request, jsonify
import game
import ai

app = Flask(__name__)


@app.route("/")
def index():
    """Render main game interface."""
    return render_template("index.html")


@app.route("/presentation.pdf")
@app.route("/presentation")
def get_presentation():
    """Serve the project presentation PDF."""
    from flask import send_from_directory
    return send_from_directory("static", "presentation.pdf", mimetype="application/pdf")


@app.route("/api/move", methods=["POST"])
def make_move():
    """
    Handle a game move.
    Payload:
      board: List[str] of length 9
      human_move: Optional[int] (0-8) or None if AI is making first move
      algorithm: "alphabeta" | "minimax"
      difficulty: "hard" | "medium" | "easy"
      ai_first: bool
    """
    data = request.get_json() or {}
    raw_board = data.get("board", game.create_empty_board())
    board = game.normalize_board(raw_board)
    human_move = data.get("human_move")
    algorithm = data.get("algorithm", "alphabeta")
    difficulty = data.get("difficulty", "hard")
    ai_first = data.get("ai_first", False)

    ai_player = game.PLAYER_O
    human_player = game.PLAYER_X

    # If human made a move, validate and apply it
    if human_move is not None:
        if not game.is_valid_move(board, human_move):
            return jsonify({"error": f"Invalid move: cell {human_move} is occupied or out of bounds"}), 400

        board = game.make_move(board, human_move, human_player)

        # Check if human won or drew
        state_after_human = game.get_game_state(board, human_player, ai_player)
        if state_after_human["is_game_over"]:
            return jsonify({
                "board": board,
                "ai_move": None,
                "game_status": state_after_human["status"],
                "winning_line": state_after_human["winning_line"],
                "is_game_over": True,
                "minimax_stats": None,
                "alphabeta_stats": None,
                "efficiency": None,
                "candidate_moves": [],
                "decision_tree": None,
            })



    # If game is already over before AI plays
    if game.is_game_over(board):
        state = game.get_game_state(board, human_player, ai_player)
        return jsonify({
            "board": board,
            "ai_move": None,
            "game_status": state["status"],
            "winning_line": state["winning_line"],
            "is_game_over": True,
            "minimax_stats": None,
            "alphabeta_stats": None,
            "efficiency": None,
            "candidate_moves": [],
            "decision_tree": None,
        })

    # AI Turn
    ai_result = ai.get_ai_move(
        board,
        ai_player=ai_player,
        human_player=human_player,
        algorithm=algorithm,
        difficulty=difficulty,
    )

    ai_move = ai_result["move"]
    if ai_move is not None:
        board = game.make_move(board, ai_move, ai_player)

    state_after_ai = game.get_game_state(board, human_player, ai_player)

    return jsonify({
        "board": board,
        "ai_move": ai_move,
        "game_status": state_after_ai["status"],
        "winning_line": state_after_ai["winning_line"],
        "is_game_over": state_after_ai["is_game_over"],
        "minimax_stats": ai_result["minimax_stats"],
        "alphabeta_stats": ai_result["alphabeta_stats"],
        "efficiency": ai_result["efficiency"],
        "candidate_moves": ai_result["candidate_moves"],
        "decision_tree": ai_result["decision_tree"],
    })


@app.route("/api/reset", methods=["POST"])
def reset_game():
    """Reset board state."""
    return jsonify({
        "board": game.create_empty_board(),
        "game_status": "in_progress",
        "winning_line": None,
        "is_game_over": False,
    })


def get_server_port():
    import os
    import socket

    env_port = os.environ.get("PORT")
    if env_port:
        return int(env_port)

    # Check if port 5000 is available
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("0.0.0.0", 5000))
            return 5000
        except OSError:
            # Port 5000 is occupied (commonly macOS AirPlay Receiver)
            return 5001


if __name__ == "__main__":
    port = get_server_port()
    print("=" * 65)
    if port == 5001:
        print(" Note: Port 5000 is in use by macOS AirPlay Receiver (ControlCenter).")
        print(" Automatically running Tic-Tac-Toe on PORT 5001!")
    print(f" Web app running at: http://localhost:{port}")
    print("=" * 65)
    app.run(host="0.0.0.0", port=port, debug=True)

