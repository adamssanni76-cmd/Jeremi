from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import uuid, copy, sys, os, random

sys.path.insert(0, os.path.dirname(__file__))
from jeremi import (
    all_tiles, build_bag, create_board, deal_tiles,
    validate_word, calculate_score, get_word_tiles,
    get_all_new_words, detect_processes,
    replenish_hand, withdraw_tiles,
    VOWELS, VALID_DIACRITIC_COMBOS, validate_diacritic,
    determine_first_player
)
import unicodedata

app = Flask(__name__)
app.secret_key = 'jeremi-2025'
socketio = SocketIO(app, cors_allowed_origins="*")
rooms = {}

def serialize_board(board):
    result = []
    for row in board:
        r = []
        for cell in row:
            if cell is None:
                r.append(None)
            elif isinstance(cell, dict):
                r.append(cell)
            else:
                r.append({"bonus": cell})
        result.append(r)
    return result

def broadcast_state(room_id):
    room = rooms[room_id]
    _, bs = create_board()
    bonus_map = {f"{r},{c}": v for (r,c),v in bs.items()}
    socketio.emit("game_state", {
        "board":        serialize_board(room["board"]),
        "players":      [{"name":p["name"],"score":p["score"],"tiles":len(p["hand"])} for p in room["players"]],
        "current_turn": room["current_turn"],
        "bag_count":    len(room["bag"]),
        "turn_number":  room["turn_number"],
        "bonus_squares":bonus_map,
    }, room=room_id)

def send_hand(room_id, idx):
    room = rooms[room_id]
    player = room["players"][idx]
    sid = room["sids"][idx]
    hand = [{"symbol": t.get("symbol") or "BLANK", "points": t["points"], "type": t["type"]} for t in player["hand"]]
    print(f"[DEBUG] Sending {len(hand)} tiles to {player['name']} (idx={idx}, sid={sid[:8]}...)")
    # Send to specific socket and also broadcast with player_index so client filters
    socketio.emit("your_hand", {"hand": hand, "player_index": idx}, to=sid)
    # Fallback: also broadcast to room so client can match by player_index
    socketio.emit("your_hand", {"hand": hand, "player_index": idx}, room=room_id)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/sw.js")
def service_worker():
    from flask import send_from_directory
    return send_from_directory('static', 'sw.js', mimetype='application/javascript')

@socketio.on("request_hand")
def on_request_hand(data):
    room_id = data.get("room_id")
    pi = data.get("player_index")
    print(f"[DEBUG] request_hand from player {pi} in room {room_id}")
    if room_id not in rooms:
        emit("error", {"msg": "Room not found"}); return
    room = rooms[room_id]
    if pi is None or pi >= len(room["players"]):
        emit("error", {"msg": "Invalid player index"}); return
    send_hand(room_id, pi)

@socketio.on("create_room")
def on_create(data):
    room_id = str(uuid.uuid4())[:6].upper()
    board, bs = create_board()
    rooms[room_id] = {
        "board": board, "bonus_squares": bs, "bag": build_bag(),
        "players": [], "sids": [], "current_turn": 0,
        "turn_number": 1, "consecutive_passes": 0,
        "started": False, "placed_this_turn": [], "history": []
    }
    join_room(room_id)
    rooms[room_id]["players"].append({"name": data["name"], "score": 0, "hand": [], "skip_next": False})
    rooms[room_id]["sids"].append(request.sid)
    emit("room_created", {"room_id": room_id, "player_index": 0})
    socketio.emit("room_update", {"players": [p["name"] for p in rooms[room_id]["players"]]}, room=room_id)

@socketio.on("join_room_game")
def on_join(data):
    room_id = data["room_id"].upper()
    if room_id not in rooms:
        emit("error", {"msg": f"Room {room_id} not found."}); return
    room = rooms[room_id]
    if room["started"]:
        emit("error", {"msg": "Game already started."}); return
    if len(room["players"]) >= 4:
        emit("error", {"msg": "Room is full."}); return
    join_room(room_id)
    idx = len(room["players"])
    room["players"].append({"name": data["name"], "score": 0, "hand": [], "skip_next": False})
    room["sids"].append(request.sid)
    emit("room_joined", {"room_id": room_id, "player_index": idx})
    socketio.emit("room_update", {"players": [p["name"] for p in room["players"]]}, room=room_id)

@socketio.on("start_game")
def on_start(data):
    room_id = data["room_id"]
    room = rooms.get(room_id)
    if not room or len(room["players"]) < 2:
        emit("error", {"msg": "Need at least 2 players."}); return
    first = determine_first_player(room["players"], room["bag"])
    fi = next(i for i,p in enumerate(room["players"]) if p["name"] == first["name"])
    room["players"] = room["players"][fi:] + room["players"][:fi]
    room["sids"]    = room["sids"][fi:]    + room["sids"][:fi]
    for p in room["players"]:
        random.shuffle(room["bag"])
        p["hand"] = deal_tiles(room["bag"], 9)
    room["started"] = True
    socketio.emit("game_started", {"players": [p["name"] for p in room["players"]], "first": room["players"][0]["name"]}, room=room_id)
    broadcast_state(room_id)
    for i in range(len(room["players"])): send_hand(room_id, i)
    # Notify first player it's their turn
    first_sid = room["sids"][0]
    socketio.emit("your_turn", {"player": room["players"][0]["name"], "player_index": 0}, to=first_sid)

@socketio.on("place_tile")
def on_place(data):
    room_id, pi, ti, row, col = data["room_id"], data["player_index"], data["tile_index"], data["row"], data["col"]
    room = rooms.get(room_id)
    if not room or room["current_turn"] != pi: emit("error", {"msg": "Not your turn!"}); return
    player = room["players"][pi]
    board = room["board"]
    if ti < 0 or ti >= len(player["hand"]): emit("error", {"msg": "Invalid tile."}); return
    cell = board[row][col]
    tile = copy.deepcopy(player["hand"][ti])
    if tile["type"] == "diacritic":
        if not isinstance(cell, dict) or "symbol" not in cell:
            emit("error", {"msg": "Diacritic must go on an existing tile!"}); return
        valid, reason = validate_diacritic(tile["symbol"], cell["symbol"], cell["type"], row, col, board)
        if not valid: emit("error", {"msg": reason}); return
        cell["symbol"] = unicodedata.normalize("NFC", cell["symbol"] + tile["symbol"])
        cell["diacritic"] = tile["symbol"]
        cell["points"] += tile["points"]
        player["hand"].pop(ti)
        room["placed_this_turn"].append({"tile": cell, "row": row, "col": col, "bonus": room["bonus_squares"].get((row,col))})
    else:
        if isinstance(cell, dict) and "symbol" in cell:
            emit("error", {"msg": "Square already occupied!"}); return
        board[row][col] = tile
        player["hand"].pop(ti)
        room["placed_this_turn"].append({"tile": tile, "row": row, "col": col, "bonus": room["bonus_squares"].get((row,col))})
    broadcast_state(room_id)
    send_hand(room_id, pi)

@socketio.on("undo_tile")
def on_undo(data):
    room_id, pi = data["room_id"], data["player_index"]
    room = rooms.get(room_id)
    if not room or room["current_turn"] != pi: return
    placed = room["placed_this_turn"]
    if not placed: emit("error", {"msg": "Nothing to undo!"}); return
    last = placed.pop()
    bonus = room["bonus_squares"].get((last["row"], last["col"]))
    room["board"][last["row"]][last["col"]] = bonus if bonus else None
    if last["tile"].get("type") != "boundary":
        room["players"][pi]["hand"].append(last["tile"])
    broadcast_state(room_id)
    send_hand(room_id, pi)

@socketio.on("submit_word")
def on_submit(data):
    room_id, pi = data["room_id"], data["player_index"]
    room = rooms.get(room_id)
    if not room or room["current_turn"] != pi: return
    placed = room["placed_this_turn"]
    if not placed: emit("error", {"msg": "No tiles placed!"}); return
    board, bs, player = room["board"], room["bonus_squares"], room["players"][pi]
    all_words = get_all_new_words(placed, board, bs)
    for wt in all_words:
        valid, reason = validate_word(wt, board)
        if not valid:
            emit("error", {"msg": f"Invalid: {reason}"})
            withdraw_tiles(placed, board, bs)
            for pt in placed:
                if pt["tile"].get("type") != "boundary": player["hand"].append(pt["tile"])
            room["placed_this_turn"] = []
            broadcast_state(room_id); send_hand(room_id, pi); return
    score = calculate_score(placed, board, bs)
    if len(placed) == 9: score += 30
    player["score"] += score
    replenish_hand(player, room["bag"])
    word_str = "".join(pt["tile"]["symbol"] for pt in placed if pt["tile"].get("type") != "boundary")
    procs = []
    for wt in all_words: procs.extend(detect_processes(wt, board))
    room["placed_this_turn"] = []
    room["consecutive_passes"] = 0
    room["history"].append({"turn": room["turn_number"], "player": player["name"], "word": f"/{word_str}/", "score": score})
    socketio.emit("word_played", {"player": player["name"], "word": f"/{word_str}/", "score": score, "processes": ", ".join(sorted(set(procs))).replace("_"," ")}, room=room_id)
    _next_turn(room_id)

@socketio.on("pass_turn")
def on_pass(data):
    room_id, pi = data["room_id"], data["player_index"]
    room = rooms.get(room_id)
    if not room or room["current_turn"] != pi: return
    player = room["players"][pi]
    for pt in room["placed_this_turn"]:
        bonus = room["bonus_squares"].get((pt["row"], pt["col"]))
        room["board"][pt["row"]][pt["col"]] = bonus if bonus else None
        if pt["tile"].get("type") != "boundary": player["hand"].append(pt["tile"])
    room["placed_this_turn"] = []
    room["consecutive_passes"] += 1
    socketio.emit("player_passed", {"player": player["name"]}, room=room_id)
    _next_turn(room_id)

@socketio.on("replace_tiles")
def on_replace(data):
    room_id, pi, indices = data["room_id"], data["player_index"], data.get("indices", [])
    room = rooms.get(room_id)
    if not room or room["current_turn"] != pi: return
    player = room["players"][pi]
    valid = [i for i in indices if 0 <= i < len(player["hand"])]
    returned = [player["hand"].pop(i) for i in sorted(valid, reverse=True)]
    player["hand"].extend(deal_tiles(room["bag"], len(returned)))
    room["bag"].extend(returned); random.shuffle(room["bag"])
    room["consecutive_passes"] += 1
    socketio.emit("tiles_replaced", {"player": player["name"], "count": len(returned)}, room=room_id)
    send_hand(room_id, pi)
    _next_turn(room_id)

def _next_turn(room_id):
    room = rooms[room_id]
    n = len(room["players"])
    if room["consecutive_passes"] >= n * 2:
        _end_game(room_id, "all_passed"); return
    if not room["bag"]:
        for p in room["players"]:
            if not p["hand"]: _end_game(room_id, p["name"]); return
    room["current_turn"] = (room["current_turn"] + 1) % n
    room["turn_number"] += 1
    np = room["players"][room["current_turn"]]
    if np.get("skip_next"):
        np["skip_next"] = False
        socketio.emit("turn_skipped", {"player": np["name"]}, room=room_id)
        _next_turn(room_id); return
    broadcast_state(room_id)
    next_sid = room["sids"][room["current_turn"]]
    socketio.emit("your_turn", {"player": np["name"], "player_index": room["current_turn"]}, to=next_sid)

def _end_game(room_id, reason):
    room = rooms[room_id]
    finisher = next((p for p in room["players"] if p["name"] == reason), None)
    total = 0
    deductions = []
    for p in room["players"]:
        if p["hand"]:
            left = sum(t["points"] for t in p["hand"])
            p["score"] -= left; total += left
            deductions.append({"name": p["name"], "deduction": left})
    if finisher: finisher["score"] += total
    scores = sorted([{"name": p["name"], "score": p["score"]} for p in room["players"]], key=lambda x: -x["score"])
    socketio.emit("game_over", {"reason": reason, "final_scores": scores, "winner": scores[0]["name"], "deductions": deductions}, room=room_id)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"JEREMI server starting at http://localhost:{port}")
    socketio.run(app, debug=False, host="0.0.0.0", port=port)
