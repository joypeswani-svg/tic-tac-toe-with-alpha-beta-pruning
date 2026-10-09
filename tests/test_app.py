"""
Integration tests for Flask application routes and API endpoints.
"""

import pytest
import app
import game


@pytest.fixture
def client():
    app.app.config["TESTING"] = True
    with app.app.test_client() as client:
        yield client


def test_index_route(client):
    """GET / renders HTML page."""
    res = client.get("/")
    assert res.status_code == 200
    assert b"Tic-Tac-Toe" in res.data
    assert b"Minimax" in res.data


def test_api_reset(client):
    """POST /api/reset resets the board."""
    res = client.post("/api/reset")
    assert res.status_code == 200
    data = res.get_json()
    assert data["board"] == [""] * 9
    assert data["game_status"] == "in_progress"
    assert data["is_game_over"] is False


def test_api_move_human_and_ai(client):
    """POST /api/move handles human move and returns AI countermove with stats."""
    payload = {
        "board": [""] * 9,
        "human_move": 4,  # Human plays center
        "algorithm": "alphabeta",
        "difficulty": "hard",
    }
    res = client.post("/api/move", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["board"][4] == "X"
    assert data["ai_move"] is not None
    assert data["ai_move"] != 4
    assert data["board"][data["ai_move"]] == "O"
    assert data["is_game_over"] is False
    assert data["minimax_stats"]["nodes_explored"] > 0
    assert data["alphabeta_stats"]["nodes_explored"] > 0
    assert data["alphabeta_stats"]["nodes_explored"] <= data["minimax_stats"]["nodes_explored"]
    assert "percent_fewer_nodes" in data["efficiency"]
    assert len(data["candidate_moves"]) == 8
    assert data["decision_tree"] is not None
    assert data["decision_tree"]["type"] == "MAX"


def test_api_ai_first(client):
    """POST /api/move supports AI opening move from empty board."""
    payload = {
        "board": [""] * 9,
        "human_move": None,
        "algorithm": "alphabeta",
        "difficulty": "hard",
        "ai_first": True,
    }
    res = client.post("/api/move", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["ai_move"] is not None
    assert data["board"][data["ai_move"]] == "O"
    assert data["minimax_stats"]["nodes_explored"] == 549946
    assert data["alphabeta_stats"]["nodes_explored"] == 20866


def test_api_invalid_move(client):
    """POST /api/move rejects illegal moves."""
    payload = {
        "board": ["X", "", "", "", "", "", "", "", ""],
        "human_move": 0,
        "algorithm": "alphabeta",
    }
    res = client.post("/api/move", json=payload)
    assert res.status_code == 400
    assert "Invalid move" in res.get_json()["error"]


def test_api_human_winning_move(client):
    """POST /api/move returns game_status='human_win' when human completes a line."""
    # Board where X has 0 and 1, O has 3 and 4; X plays 2 to win
    board = ["X", "X", "", "O", "O", "", "", "", ""]
    payload = {
        "board": board,
        "human_move": 2,
        "algorithm": "alphabeta",
        "difficulty": "hard",
    }
    res = client.post("/api/move", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["game_status"] == "human_win"
    assert data["is_game_over"] is True
    assert data["winning_line"] == [0, 1, 2]
    assert data["ai_move"] is None


def test_api_draw_move(client):
    """POST /api/move returns game_status='draw' when human move fills board with no winner."""
    # 8 cells filled, cell 8 empty:
    # X O X
    # X O O
    # O X (cell 8)
    board = ["X", "O", "X", "X", "O", "O", "O", "X", ""]
    payload = {
        "board": board,
        "human_move": 8,
        "algorithm": "alphabeta",
        "difficulty": "hard",
    }
    res = client.post("/api/move", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["game_status"] == "draw"
    assert data["is_game_over"] is True
    assert data["winning_line"] is None


def test_api_difficulties_and_minimax_toggle(client):
    """POST /api/move supports minimax algorithm and easy/medium difficulties."""
    # Test minimax algorithm toggle
    res_mm = client.post("/api/move", json={
        "board": ["X", "", "", "", "", "", "", "", ""],
        "human_move": 4,
        "algorithm": "minimax",
        "difficulty": "medium",
    })
    assert res_mm.status_code == 200
    data_mm = res_mm.get_json()
    assert data_mm["ai_move"] is not None

    # Test easy difficulty
    res_easy = client.post("/api/move", json={
        "board": ["X", "", "", "", "", "", "", "", ""],
        "human_move": 4,
        "algorithm": "alphabeta",
        "difficulty": "easy",
    })
    assert res_easy.status_code == 200
    data_easy = res_easy.get_json()
    assert data_easy["ai_move"] is not None


def test_presentation_route(client):
    """GET /presentation.pdf returns valid PDF file."""
    res = client.get("/presentation.pdf")
    assert res.status_code == 200
    assert res.content_type == "application/pdf"
    assert res.data.startswith(b"%PDF")
    assert len(res.data) > 100000
