import random
import unicodedata
import os
import json
import copy
from itertools import permutations

# =============================================================
# TILE DATA
# count = number of tiles in the bag
# points = score value of the tile
# =============================================================

all_tiles = {
    # NASALS
    "m":   {"count": 2,  "points": 4,  "type": "base_consonant"},
    "ɱ":   {"count": 8,  "points": 1,  "type": "base_consonant"},
    "n":   {"count": 2,  "points": 4,  "type": "base_consonant"},
    "ɲ":   {"count": 6,  "points": 2,  "type": "base_consonant"},
    "ŋ":   {"count": 4,  "points": 3,  "type": "base_consonant"},
    "ɴ":   {"count": 8,  "points": 1,  "type": "base_consonant"},
    "ŋm":  {"count": 8,  "points": 1,  "type": "base_consonant"},
    # PLOSIVES
    "p":   {"count": 2,  "points": 4,  "type": "base_consonant"},
    "b":   {"count": 2,  "points": 4,  "type": "base_consonant"},
    "t":   {"count": 2,  "points": 4,  "type": "base_consonant"},
    "d":   {"count": 2,  "points": 4,  "type": "base_consonant"},
    "c":   {"count": 8,  "points": 1,  "type": "base_consonant"},
    "ɟ":   {"count": 8,  "points": 1,  "type": "base_consonant"},
    "k":   {"count": 2,  "points": 4,  "type": "base_consonant"},
    "g":   {"count": 2,  "points": 4,  "type": "base_consonant"},
    "q":   {"count": 8,  "points": 1,  "type": "base_consonant"},
    "ɢ":   {"count": 8,  "points": 1,  "type": "base_consonant"},
    "ʔ":   {"count": 8,  "points": 1,  "type": "base_consonant"},
    "kp":  {"count": 2,  "points": 4,  "type": "base_consonant"},
    "gb":  {"count": 4,  "points": 3,  "type": "base_consonant"},
    # EJECTIVES
    "pʼ":  {"count": 8,  "points": 1,  "type": "base_consonant"},
    "tʼ":  {"count": 8,  "points": 1,  "type": "base_consonant"},
    "cʼ":  {"count": 8,  "points": 1,  "type": "base_consonant"},
    "kʼ":  {"count": 8,  "points": 1,  "type": "base_consonant"},
    "qʼ":  {"count": 8,  "points": 1,  "type": "base_consonant"},
    # CLICKS
    "ʘ":   {"count": 8,  "points": 1,  "type": "base_consonant"},
    "[":   {"count": 8,  "points": 1,  "type": "base_consonant"},
    "ǃ":   {"count": 8,  "points": 1,  "type": "base_consonant"},
    "ǂ":   {"count": 8,  "points": 1,  "type": "base_consonant"},
    # AFFRICATES
    "pɸ":  {"count": 8,  "points": 1,  "type": "base_consonant"},
    "bβ":  {"count": 8,  "points": 1,  "type": "base_consonant"},
    "ts":  {"count": 8,  "points": 1,  "type": "base_consonant"},
    "dz":  {"count": 8,  "points": 1,  "type": "base_consonant"},
    "tʃ":  {"count": 8,  "points": 1,  "type": "base_consonant"},
    "dʒ":  {"count": 8,  "points": 1,  "type": "base_consonant"},
    "kx":  {"count": 8,  "points": 1,  "type": "base_consonant"},
    "gɣ":  {"count": 8,  "points": 1,  "type": "base_consonant"},
    # FRICATIVES
    "ɸ":   {"count": 8,  "points": 1,  "type": "base_consonant"},
    "β":   {"count": 8,  "points": 1,  "type": "base_consonant"},
    "f":   {"count": 4,  "points": 3,  "type": "base_consonant"},
    "v":   {"count": 6,  "points": 2,  "type": "base_consonant"},
    "s":   {"count": 2,  "points": 4,  "type": "base_consonant"},
    "z":   {"count": 6,  "points": 2,  "type": "base_consonant"},
    "ʃ":   {"count": 6,  "points": 2,  "type": "base_consonant"},
    "ʒ":   {"count": 8,  "points": 1,  "type": "base_consonant"},
    "ç":   {"count": 8,  "points": 1,  "type": "base_consonant"},
    "ʝ":   {"count": 8,  "points": 1,  "type": "base_consonant"},
    "x":   {"count": 8,  "points": 1,  "type": "base_consonant"},
    "ɣ":   {"count": 8,  "points": 1,  "type": "base_consonant"},
    "χ":   {"count": 8,  "points": 1,  "type": "base_consonant"},
    "ʁ":   {"count": 8,  "points": 1,  "type": "base_consonant"},
    "ħ":   {"count": 8,  "points": 1,  "type": "base_consonant"},
    "ʕ":   {"count": 8,  "points": 1,  "type": "base_consonant"},
    "h":   {"count": 8,  "points": 1,  "type": "base_consonant"},
    "ʋ":   {"count": 8,  "points": 1,  "type": "base_consonant"},
    # APPROXIMANTS
    "r":   {"count": 4,  "points": 3,  "type": "base_consonant"},
    "j":   {"count": 2,  "points": 4,  "type": "base_consonant"},
    "w":   {"count": 2,  "points": 4,  "type": "base_consonant"},
    "l":   {"count": 2,  "points": 4,  "type": "base_consonant"},
    # VOWELS — points = count (both equal, from physical game)
    "i":   {"count": 1, "points": 20, "type": "base_vowel"},
    "e":   {"count": 3, "points": 13, "type": "base_vowel"},
    "ɛ":   {"count": 5,  "points": 8,  "type": "base_vowel"},
    "a":   {"count": 1, "points": 20, "type": "base_vowel"},
    "ɔ":   {"count": 1, "points": 16, "type": "base_vowel"},
    "o":   {"count": 3, "points": 11, "type": "base_vowel"},
    "u":   {"count": 3, "points": 14, "type": "base_vowel"},
    "ɪ":   {"count": 8,  "points": 2,  "type": "base_vowel"},
    "ʊ":   {"count": 8,  "points": 3,  "type": "base_vowel"},
    # DIACRITICS — count=actual tiles, points=score
    "̃":    {"count": 4,  "points": 14, "type": "diacritic"},  # Nasalisation
    "ʷ":   {"count": 12, "points": 2,  "type": "diacritic"},  # Labialisation
    "ʲ":   {"count": 12, "points": 1,  "type": "diacritic"},  # Palatalisation
    "ˬ":   {"count": 6,  "points": 8,  "type": "diacritic"},  # Voicing
    "ː":   {"count": 8,  "points": 7,  "type": "diacritic"},  # Comp. lengthening
    "ˀ":   {"count": 4,  "points": 10, "type": "diacritic"},  # Glottalisation
    "ˠ":   {"count": 4,  "points": 10, "type": "diacritic"},  # Velarization
    "ˤ":   {"count": 12, "points": 1,  "type": "diacritic"},  # Pharyngealisation
    "ø":   {"count": 4,  "points": 12, "type": "diacritic"},  # Elision
    "̩":    {"count": 12, "points": 2,  "type": "diacritic"},  # Syllabicity
}

# =============================================================
# PHONOLOGICAL CONSTANTS
# =============================================================

VOWELS            = {"i", "e", "ɛ", "a", "ɔ", "o", "u", "ɪ", "ʊ"}

def build_extended_vowels():
    base = {"i", "e", "ɛ", "a", "ɔ", "o", "u", "ɪ", "ʊ"}
    long_v = {"iː", "eː", "ɛː", "aː", "ɔː", "oː", "uː"}
    nasal_v = {"ĩ", "ẽ", "ɛ̃", "ã", "ɔ̃", "õ", "ũ"}
    ext = base.copy()
    for v in long_v | nasal_v:
        ext.add(unicodedata.normalize("NFC", v))
    return ext
GLIDES            = {"j", "w"}
NASALS            = {"m", "n", "ɲ", "ŋ", "ɴ", "ŋm"}
ROUNDED_VOWELS    = {"u", "o", "ɔ"}
FRONT_HIGH_VOWELS = {"i", "e"}
PHARYNGEALS       = {"ħ", "ʕ"}
EXTENDED_VOWELS   = build_extended_vowels()

_RAW_DIACRITIC_COMBOS = [
    # Process 1: Nasalisation (̃)
    "ĩ", "ẽ", "ɛ̃", "ã", "ɔ̃", "õ", "ũ", "m̃", "ñ", "ŋ̃",
    # Process 4: Labialisation (ʷ)
    "mʷ", "ŋʷ", "kʷ", "gʷ",
    # Process 5: Palatalisation (ʲ)
    "dʲ", "gʲ",
    # Process 6: Voicing (ˬ)
    "pˬ", "tˬ", "kˬ", "fˬ", "sˬ", "ʃˬ", "θˬ", "xˬ", "χˬ", "ħˬ", "hˬ",
    "tsˬ", "tʃˬ", "kxˬ", "pɸˬ", "cˬ", "qˬ",
    # Process 7: Compensatory lengthening (ː)
    "iː", "eː", "ɛː", "aː", "ɔː", "oː", "uː",
    # Process 13: Glottalisation (ˀ)
    "bˀ", "dˀ", "gˀ", "vˀ", "zˀ", "lˀ", "rˀ", "mˀ", "nˀ",
    # Process 14: Velarization (ˠ)
    "lˠ", "rˠ", "nˠ", "sˠ", "zˠ",
    # Process 15: Pharyngealisation (ˤ)
    "lˤ",
    # Process 2: Elision (ø)
    "iø", "eø", "aø", "oø", "uø", "ɛø", "ɔø",
    # Syllabicity (̩) — nasals
    "m̩", "ɱ̩", "n̩", "ɲ̩", "ŋ̩", "ŋm̩",
]
VALID_DIACRITIC_COMBOS = {unicodedata.normalize("NFC", c) for c in _RAW_DIACRITIC_COMBOS}

# =============================================================
# TILE BAG
# =============================================================

scale = {1: 10, 2: 4, 3: 4, 4: 3, 5: 2, 6: 2, 7: 1, 8: 1}
VOWEL_TILE_COUNTS = {"i":20,"e":13,"ɛ":8,"a":20,"ɔ":16,"o":11,"u":14,"ɪ":2,"ʊ":3}

def build_bag():
    bag = []
    for symbol, info in all_tiles.items():
        t = info["type"]
        if t == "diacritic":
            count = info["count"]
        elif t == "base_vowel":
            count = VOWEL_TILE_COUNTS.get(symbol, 1)
        else:
            count = scale.get(info["count"], 1)
        for _ in range(count):
            bag.append({"symbol": symbol, "points": info["points"], "type": t})
    for _ in range(6):
        bag.append({"symbol": None, "points": 0, "type": "blank"})
    random.shuffle(bag)
    return bag


def deal_tiles(bag, num_tiles=9):
    hand = []
    for _ in range(num_tiles):
        if bag:
            # Draw from a random position for true randomness
            idx = random.randint(0, len(bag) - 1)
            hand.append(bag.pop(idx))
    return hand

# =============================================================
# BOARD  — internal indices 0-14; all display/input uses 1-15
# =============================================================

def create_board():
    board = []
    for row in range(15):
        board.append([None] * 15)

    bonus_squares = {
        # TM - 5 squares (independent)
        (0, 9):   "TM",
        (2, 7):   "TM",
        (7, 7):   "TM",
        (12, 8):  "TM",
        (14, 5):  "TM",
        # Bottom-left + diagonal mirror → top-right
        (12, 0):  "DS",  (2, 14):  "DS",
        (13, 1):  "TL",  (1, 13):  "TL",
        (12, 2):  "DS",  (2, 12):  "DS",
        (11, 3):  "DL",  (3, 11):  "DL",
        (10, 4):  "DS",  (4, 10):  "DS",
        (8, 4):   "DM",  (6, 10):  "DM",
        (9, 5):   "DL",  (5, 9):   "DL",
        (10, 6):  "DS",  (4, 8):   "DS",
        # Bottom-right + diagonal mirror → top-left
        (10, 8):  "DS",  (4, 6):   "DS",
        (9, 9):   "DM",  (5, 5):   "DM",
        (8, 10):  "DM",  (6, 4):   "DM",
        (10, 10): "DS",  (4, 4):   "DS",
        (11, 11): "DL",  (3, 3):   "DL",
        (12, 12): "DM",  (2, 2):   "DM",
        (13, 13): "TL",  (1, 1):   "TL",
        (14, 12): "DM",  (0, 2):   "DM",
    }

    for (row, col), bonus in bonus_squares.items():
        board[row][col] = bonus

    board[7][0] = "START"
    return board, bonus_squares


def cell_display(symbol):
    """
    Return a fixed-width display string for a symbol.
    Combining diacritics (like ̩ ̃) are zero-width so we pad accordingly.
    """
    import unicodedata as ud
    # Count combining characters (zero display width)
    combining = sum(1 for c in symbol if ud.combining(c))
    # Pad to visual width of 2
    visual_len = len(symbol) - combining
    pad = max(0, 2 - visual_len)
    return ' ' * pad + symbol


def print_board(board):
    # Column headers: 1-15
    print("\n     " + "  ".join(f"{c:2}" for c in range(1, 16)))
    print("     " + "----" * 15)
    for row in range(15):
        row_label = f"R{row+1:2} |"
        row_display = []
        for col in range(15):
            cell = board[row][col]
            if cell is None:
                row_display.append("  .")
            elif cell == "START":
                row_display.append("  ★")
            elif isinstance(cell, dict) and cell.get('type') == 'boundary':
                row_display.append("  #")
            elif isinstance(cell, dict):
                symbol = cell['symbol'] if cell['symbol'] else "?"
                row_display.append(" " + cell_display(symbol))
            else:
                row_display.append(f" {cell:>2}")
        print(row_label + " ".join(row_display))

# =============================================================
# PLAYER SETUP
# =============================================================

def setup_players():
    print("Game modes:")
    print("  1. Human vs AI (JEREMI-AI)")
    print("  2. Human vs Human (2-4 players)")
    mode = input("Choose mode (1 or 2): ").strip()

    if mode == "1":
        name = input("Enter your name: ").strip() or "Player"
        return [
            {"name": name,        "hand": [], "score": 0, "is_ai": False},
            {"name": "JEREMI-AI", "hand": [], "score": 0, "is_ai": True},
        ]

    players = []
    while True:
        try:
            num_players = int(input("How many players? (2-4): "))
            if 2 <= num_players <= 4:
                break
            print("Please enter a number between 2 and 4.")
        except ValueError:
            print("Please enter a valid number.")
    for i in range(num_players):
        name = input(f"Enter name for Player {i+1}: ").strip() or f"Player {i+1}"
        players.append({"name": name, "hand": [], "score": 0, "is_ai": False})
    return players


def determine_first_player(players, bag):
    print("\n--- Drawing to determine first player ---")
    drawn = []
    for player in players:
        # Draw from a random position in the bag
        idx    = random.randint(0, len(bag) - 1)
        tile   = bag.pop(idx)
        symbol = tile['symbol'] if tile['symbol'] else "BLANK"
        print(f"{player['name']} draws: {symbol} ({tile['points']} pts)")
        drawn.append((player, tile))
        # Put tile back in a random position
        bag.insert(random.randint(0, len(bag)), tile)

    drawn.sort(key=lambda x: x[1]['points'], reverse=True)
    first_player = drawn[0][0]
    print(f"\n{first_player['name']} goes first!")
    return first_player

# =============================================================
# TURN ACTIONS
# =============================================================

def display_hand(player):
    print(f"\n{player['name']}'s rack:")
    for i, tile in enumerate(player['hand']):
        display_i = i  # 0-indexed for input consistency
        if tile['type'] in ('blank', 'blank_declared'):
            sym = tile.get('symbol') or 'BLANK'
            print(f"  [{display_i}] {sym} (0 pts) [BLANK]")
        else:
            print(f"  [{display_i}] {tile['symbol']} ({tile['points']} pts)")


def get_player_action(player):
    print(f"\n{player['name']}'s turn!")
    print("  1. Play tiles on board")
    print("  2. Replace tiles from rack (loses turn)")
    print("  3. Replace a tile on the board (word-final only)")
    print("  4. Pass")
    print("  5. Place word boundary [#]")
    print("  6. View game history")
    print("  7. Save game")
    while True:
        choice = input("Enter 1-7: ").strip()
        if choice in ['1', '2', '3', '4', '5', '6', '7']:
            return choice
        print("Please enter 1, 2, 3, 4, 5, 6 or 7.")


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def display_scoreboard(players):
    print("\n┌──────────────────────────────┐")
    print("│          SCOREBOARD          │")
    print("├──────────────────────────────┤")
    for player in sorted(players, key=lambda x: x['score'], reverse=True):
        ai_tag = "  "  # AI disabled
        name   = player['name'][:14]
        score  = player['score']
        print(f"│ {ai_tag} {name:<14} {score:>6} pts │")
    print("└──────────────────────────────┘")


def display_history(history):
    if not history:
        print("No moves yet.")
        return
    print("\n─── Game History ──────────────────────────────")
    for entry in history:
        turn   = entry['turn']
        name   = entry['player']
        action = entry['action']
        score  = entry.get('score', '')
        score_str = f"  (+{score} pts)" if score != '' else ''
        print(f"  Turn {turn:>2}  {name:<14}  {action}{score_str}")
    print("───────────────────────────────────────────────")


# =============================================================
# SAVE / LOAD
# =============================================================

SAVE_FILE = "jeremi_save.json"


def _board_to_json(board):
    """Serialise board: replace None with null-marker, keep strings and dicts."""
    result = []
    for row in board:
        result.append([cell if cell is not None else "__EMPTY__" for cell in row])
    return result


def _board_from_json(data):
    board = []
    for row in data:
        board.append([None if cell == "__EMPTY__" else cell for cell in row])
    return board


def save_game(board, bonus_squares, players, bag, turn_number,
              consecutive_passes, history):
    state = {
        "board":             _board_to_json(board),
        "bonus_squares":     {f"{r},{c}": v for (r, c), v in bonus_squares.items()},
        "players":           players,
        "bag":               bag,
        "turn_number":       turn_number,
        "consecutive_passes": consecutive_passes,
        "history":           history,
    }
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    print(f"✅ Game saved to '{SAVE_FILE}'.")


def load_game():
    if not os.path.exists(SAVE_FILE):
        print(f"No save file found ('{SAVE_FILE}').")
        return None
    with open(SAVE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    board        = _board_from_json(state['board'])
    bonus_squares = {tuple(int(x) for x in k.split(',')): v
                     for k, v in state['bonus_squares'].items()}
    players           = state['players']
    bag               = state['bag']
    turn_number       = state['turn_number']
    consecutive_passes = state['consecutive_passes']
    history           = state.get('history', [])
    print(f"✅ Game loaded from '{SAVE_FILE}'.")
    return board, bonus_squares, players, bag, turn_number, consecutive_passes, history



def _validate_blank_symbol(raw):
    """
    Validate a symbol declared for a blank tile.
    Returns (is_valid, normalised_symbol, tile_type).
    """
    # Try NFC normalisation first
    normalised = unicodedata.normalize("NFC", raw.strip())
    if normalised in all_tiles:
        return True, normalised, all_tiles[normalised]["type"]
    # Also check raw
    if raw.strip() in all_tiles:
        info = all_tiles[raw.strip()]
        return True, raw.strip(), info["type"]
    return False, raw, None

def board_has_tiles(board):
    for row in range(15):
        for col in range(15):
            if isinstance(board[row][col], dict):
                return True
    return False


def covers_start_square(placed_tiles):
    return any(t['row'] == 7 and t['col'] == 0 for t in placed_tiles)


def connects_to_existing(placed_tiles, board):
    for pt in placed_tiles:
        row, col = pt['row'], pt['col']
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = row+dr, col+dc
            if 0 <= nr < 15 and 0 <= nc < 15:
                cell = board[nr][nc]
                if isinstance(cell, dict):
                    existing = not any(t['row'] == nr and t['col'] == nc for t in placed_tiles)
                    if existing:
                        return True
    return False


def check_consonant_cluster(board, row, col, current_sym, direction):
    """
    Check if placing current_sym at (row,col) creates an illegal cluster.
    Returns True if ILLEGAL, False if OK.
    Valid sequences: C+V, V+C, C+G+V (CGV), syllabic_nasal+C
    """
    def get_sym(r, c):
        if 0 <= r < 15 and 0 <= c < 15:
            cell = board[r][c]
            if isinstance(cell, dict) and cell.get('type') != 'boundary':
                return cell.get('symbol')
        return None

    if direction == 'horizontal':
        left   = get_sym(row, col - 1)
        right  = get_sym(row, col + 1)
        left2  = get_sym(row, col - 2)
        right2 = get_sym(row, col + 2)
    else:
        left   = get_sym(row - 1, col)
        right  = get_sym(row + 1, col)
        left2  = get_sym(row - 2, col)
        right2 = get_sym(row + 2, col)

    sym_nfc = unicodedata.normalize("NFC", current_sym)
    is_glide = current_sym in GLIDES
    is_syllabic = sym_nfc in SYLLABIC_NASALS

    # Syllabic nasals can precede consonants — never an illegal cluster
    if is_syllabic:
        return False

    # Check left neighbor
    if left and left not in VOWELS:
        left_nfc = unicodedata.normalize("NFC", left)
        left_syllabic = left_nfc in SYLLABIC_NASALS
        if left_syllabic:
            return False  # syllabic nasal + C is valid
        if left in GLIDES:
            return True   # G + C is invalid
        # C + current: valid only if current is a glide AND right is a vowel (CGV)
        if is_glide:
            if right and right in VOWELS:
                return False  # valid CGV: C + G + V
            return True   # glide not followed by vowel
        return True  # C + C is invalid

    # Check right neighbor
    if right and right not in VOWELS:
        right_nfc = unicodedata.normalize("NFC", right)
        right_syllabic = right_nfc in SYLLABIC_NASALS
        if right_syllabic:
            return False  # C + syllabic nasal is valid
        if right in GLIDES:
            # current + glide: valid only if vowel follows glide
            after_glide = right2
            if after_glide and after_glide in VOWELS:
                return False  # valid CGV
            return True
        if is_glide:
            return True   # glide + C is invalid
        return True  # C + C is invalid

    return False


def _undo_last_tile(placed_tiles, player, board, bonus_squares):
    """Remove the most recently placed tile and return it to the player's hand."""
    if not placed_tiles:
        print("Nothing to undo.")
        return
    pt    = placed_tiles.pop()
    row, col = pt['row'], pt['col']
    tile  = pt['tile']

    # Restore the board cell
    if tile.get('diacritic'):
        # Diacritic was merged into an existing tile — reverse the merge
        cell = board[row][col]
        diac = tile['diacritic']
        cell['symbol']  = cell['symbol'].replace(diac, '')
        cell['points'] -= all_tiles.get(diac, {}).get('points', 0)
        if 'diacritic' in cell:
            del cell['diacritic']
        # Return just the diacritic tile to hand
        diac_tile = {"symbol": diac, "points": all_tiles[diac]['points'], "type": "diacritic"}
        player['hand'].append(diac_tile)
    elif tile.get('type') == 'boundary':
        board[row][col] = bonus_squares.get((row, col)) or None
        # boundary tiles don't go back to hand (they're free markers)
    else:
        board[row][col] = bonus_squares.get((row, col)) or None
        player['hand'].append(tile)

    print(f"↩ Undone: tile at R{row+1} C{col+1} returned to hand.")
    print_board(board)


def _validate_blank_symbol(symbol):
    """Return (valid, normalised_symbol, type) for a blank tile declaration."""
    symbol = symbol.strip()
    if not symbol:
        return False, None, None
    # Check directly in all_tiles
    if symbol in all_tiles:
        info = all_tiles[symbol]
        return True, symbol, info['type']
    # Also accept NFC-normalised versions (handles composed diacritic combos)
    nfc = unicodedata.normalize("NFC", symbol)
    if nfc in all_tiles:
        info = all_tiles[nfc]
        return True, nfc, info['type']
    # Check valid diacritic combos
    if nfc in VALID_DIACRITIC_COMBOS:
        return True, nfc, 'base_consonant'
    return False, None, None


def place_tiles(player, board, bonus_squares, bag):
    placed_tiles = []
    board_has_tiles_before = board_has_tiles(board)
    print_board(board)

    while True:
        display_hand(player)
        print("\nOptions:")
        print("  Enter tile index to place a tile")
        print("  '#'  — place a word/morpheme boundary marker")
        print("  'u'  — undo last placed tile")
        print("  'r'  — replace rack tiles instead (loses turn)")
        print("  'p'  — pass your turn")
        print("  'done' — finish your turn")
        choice = input("> ").strip().lower()

        # ── UNDO ──────────────────────────────────────────────────────────
        if choice == 'u':
            _undo_last_tile(placed_tiles, player, board, bonus_squares)
            continue

        # ── REPLACE RACK TILES ────────────────────────────────────────────
        if choice == 'r':
            if placed_tiles:
                print("You have already placed tiles this turn. Undo them first ('u') to replace.")
                continue
            replaced = replace_rack_tiles(player, bag)
            if replaced:
                return 'replaced'  # signal to take_turn that turn was used
            continue

        # ── PASS ──────────────────────────────────────────────────────────
        if choice == 'p':
            if placed_tiles:
                print("You have already placed tiles. Undo them first ('u') to pass.")
                continue
            return 'passed'  # signal to take_turn

        # ── DONE ──────────────────────────────────────────────────────────
        if choice == 'done':
            if len(placed_tiles) == 0:
                print("You must place at least one tile!")
                continue
            # First word must be at least 2 tiles
            real_placed = [t for t in placed_tiles if t['tile'].get('type') != 'boundary']
            if not board_has_tiles_before and len(real_placed) < 2:
                print("First word must have at least 2 symbols!")
                continue

            # Filter only non-boundary tiles to determine word direction
            real_tiles = [t for t in placed_tiles if t['tile'].get('type') != 'boundary']

            # Check no gaps (only applies to 2+ real tiles)
            if len(real_tiles) > 1:
                rows = [t['row'] for t in real_tiles]
                cols = [t['col'] for t in real_tiles]
                if len(set(rows)) == 1:           # horizontal
                    r = rows[0]
                    for c in range(min(cols), max(cols)+1):
                        if not isinstance(board[r][c], dict):
                            print("Gap detected between tiles! Fill all squares in between.")
                            for pt in placed_tiles:
                                pr, pc = pt['row'], pt['col']
                                bonus  = bonus_squares.get((pr, pc))
                                board[pr][pc] = bonus if bonus else None
                                if pt['tile'].get('type') != 'boundary':
                                    player['hand'].append(pt['tile'])
                            placed_tiles = []
                            print_board(board)
                            break
                    if not placed_tiles:
                        continue
                else:                              # vertical
                    c = cols[0]
                    for r in range(min(rows), max(rows)+1):
                        if not isinstance(board[r][c], dict):
                            print("Gap detected between tiles! Fill all squares in between.")
                            for pt in placed_tiles:
                                pr, pc = pt['row'], pt['col']
                                bonus  = bonus_squares.get((pr, pc))
                                board[pr][pc] = bonus if bonus else None
                                if pt['tile'].get('type') != 'boundary':
                                    player['hand'].append(pt['tile'])
                            placed_tiles = []
                            print_board(board)
                            break
                    if not placed_tiles:
                        continue

            # First move: must cover START square (internal R7 C0 = display R8 C1)
            if not board_has_tiles_before and not covers_start_square(placed_tiles):
                print("First word must cover the START square (R8, C1)!")
                for pt in placed_tiles:
                    row, col = pt['row'], pt['col']
                    bonus    = bonus_squares.get((row, col))
                    board[row][col] = bonus if bonus else None
                    if pt['tile'].get('type') != 'boundary':
                        player['hand'].append(pt['tile'])
                placed_tiles = []
                print_board(board)
                continue

            # Subsequent moves: must connect to existing tiles
            if board_has_tiles_before and not connects_to_existing(placed_tiles, board):
                print("Your word must connect to an existing tile on the board!")
                for pt in placed_tiles:
                    row, col = pt['row'], pt['col']
                    bonus    = bonus_squares.get((row, col))
                    board[row][col] = bonus if bonus else None
                    if pt['tile'].get('type') != 'boundary':
                        player['hand'].append(pt['tile'])
                placed_tiles = []
                print_board(board)
                continue
            break

        # ── BOUNDARY MARKER ───────────────────────────────────────────────
        if choice == '#':
            try:
                row = int(input("Place [#] at row (1-15): ")) - 1
                col = int(input("Place [#] at col (1-15): ")) - 1
            except ValueError:
                print("Please enter valid numbers.")
                continue
            if not (0 <= row <= 14 and 0 <= col <= 14):
                print("Position out of bounds!")
                continue
            if isinstance(board[row][col], dict):
                print("That square is already occupied!")
                continue
            boundary_tile = {"symbol": "#", "points": 0, "type": "boundary"}
            board[row][col] = boundary_tile
            placed_tiles.append({"tile": boundary_tile, "row": row, "col": col, "bonus": None})
            print_board(board)
            print(f"Placed [#] boundary marker at R{row+1} C{col+1}")
            continue

        # ── TILE INDEX ────────────────────────────────────────────────────
        if not choice.isdigit():
            print("Please enter a tile index (number), '#', 'u' to undo, or 'done'.")
            continue

        tile_index = int(choice)
        if tile_index < 0 or tile_index >= len(player['hand']):
            print("Invalid tile index.")
            continue

        tile = player['hand'][tile_index].copy()

        # Blank tile — validate the symbol the player declares
        # Blank tile always scores 0 regardless of declared symbol
        if tile['type'] == 'blank':
            while True:
                raw = input("Blank tile — what symbol does it represent? ").strip()
                valid_sym, sym_normalised, sym_type = _validate_blank_symbol(raw)
                if valid_sym:
                    tile['symbol'] = sym_normalised
                    tile['type']   = 'blank_declared'
                    tile['points'] = 0  # blank always scores 0
                    break
                all_syms = sorted(all_tiles.keys())
                print(f"'{raw}' is not a valid IPA symbol in this game.")
                print("Valid symbols include: " + ", ".join(all_syms[:20]) + " ...")
                print("Please enter a symbol from the tile set.")

        # Position input: player enters 1-based, converted to 0-based internally
        try:
            row = int(input(f"Place '{tile['symbol']}' at row (1-15): ")) - 1
            col = int(input(f"Place '{tile['symbol']}' at col (1-15): ")) - 1
        except ValueError:
            print("Please enter valid numbers.")
            continue

        if not (0 <= row <= 14 and 0 <= col <= 14):
            print("Position out of bounds!")
            continue

        cell = board[row][col]

        # ── DIACRITIC ─────────────────────────────────────────────────────
        if tile['type'] == 'diacritic':
            if not isinstance(cell, dict):
                print("Diacritic tiles must be placed on an existing base tile!")
                continue
            base_symbol = cell['symbol']
            base_type   = cell['type']
            valid, reason = validate_diacritic(tile['symbol'], base_symbol, base_type, row, col, board)
            if not valid:
                print(f"Invalid diacritic placement: {reason}")
                continue
            old_symbol        = cell['symbol']
            cell['symbol']    = old_symbol + tile['symbol']
            cell['diacritic'] = tile['symbol']
            cell['points']   += tile['points']
            placed_tiles.append({"tile": cell, "row": row, "col": col,
                                  "bonus": bonus_squares.get((row, col))})
            player['hand'].pop(tile_index)
            print_board(board)
            print(f"Applied '{tile['symbol']}' to '{old_symbol}' → '{cell['symbol']}' at R{row+1} C{col+1}")

        # ── BASE TILE ─────────────────────────────────────────────────────
        else:
            if isinstance(cell, dict):
                print("That square is already occupied!")
                continue

            # Note: consonant cluster validation happens at word level via validate_word
            # This allows CGV sequences to be built tile by tile (C, then G, then V)

            # First tile of the game must be on row 8 (internal row 7)
            if not board_has_tiles_before and len(placed_tiles) == 0:
                if row != 7:
                    print("First tile must be placed on row 8 (the START row)!")
                    continue

            # ── DIRECTION CONSTRAINT ──────────────────────────────────────
            # Only real (non-boundary) tiles count for straight-line enforcement.
            real_placed = [t for t in placed_tiles if t['tile'].get('type') != 'boundary']
            if len(real_placed) >= 1:
                existing_rows = [t['row'] for t in real_placed]
                existing_cols = [t['col'] for t in real_placed]

                if len(real_placed) == 1:
                    # Direction not yet fixed — new tile may share row OR column
                    existing_row = existing_rows[0]
                    existing_col = existing_cols[0]
                    if row != existing_row and col != existing_col:
                        print("All tiles must be in a straight line (same row or same column)!")
                        continue
                else:
                    # Direction is fixed by first two real tiles
                    direction_is_horizontal = len(set(existing_rows)) == 1
                    if direction_is_horizontal:
                        if row != existing_rows[0]:
                            print(f"All tiles must be on row {existing_rows[0]+1} (horizontal play)!")
                            continue
                    else:
                        if col != existing_cols[0]:
                            print(f"All tiles must be on column {existing_cols[0]+1} (vertical play)!")
                            continue

            board[row][col] = tile
            placed_tiles.append({"tile": tile, "row": row, "col": col,
                                  "bonus": bonus_squares.get((row, col))})
            player['hand'].pop(tile_index)
            print_board(board)
            print(f"Placed '{tile['symbol']}' at R{row+1} C{col+1}")

    return placed_tiles


def is_word_final(tile_index, player_hand):
    """
    A tile is word-final if it is at the end of the player's rack
    (i.e. not in the middle of a formed word on the board).
    For rack replacement purposes, any tile on the rack is eligible
    unless it's a blank that has already been declared on the board.
    """
    return True  # All rack tiles are eligible; board tiles cannot be replaced


def replace_rack_tiles(player, bag):
    """
    Rack replacement — player discards tiles from their rack face down,
    draws same number from bag, loses their turn. No score awarded.
    Player CAN see their own rack tiles before deciding.
    """
    display_hand(player)
    print("\nYou may replace any or all tiles from your rack.")
    print("  - Discard tiles face down, draw same number from bag")
    print("  - No score awarded for this action")
    print("  - Blank tiles can be replaced")
    print("\nEnter indices to replace (e.g. 0 2 4), or 'all', or 'cancel':")
    choice = input("> ").strip()

    if choice == 'cancel':
        print("Replacement cancelled.")
        return False

    if choice == 'all':
        indices = list(range(len(player['hand'])))
    else:
        try:
            indices = [int(x) for x in choice.split()]
        except ValueError:
            print("Invalid input.")
            return False

    valid_indices = [i for i in indices if 0 <= i < len(player['hand'])]
    if not valid_indices:
        print("No valid tile indices.")
        return False

    tiles_to_return = []
    for i in sorted(valid_indices, reverse=True):
        tiles_to_return.append(player['hand'].pop(i))

    new_tiles = deal_tiles(bag, len(tiles_to_return))
    player['hand'].extend(new_tiles)
    bag.extend(tiles_to_return)
    random.shuffle(bag)
    print(f"Replaced {len(tiles_to_return)} tile(s) from rack. No score awarded.")
    return True


def is_word_final_on_board(row, col, board):
    """
    Check if a tile on the board is word-final —
    it must be at the END of exactly one word formation,
    not in the middle of a word, and not shared by multiple formations.
    """
    def occupied(r, c):
        return 0 <= r < 15 and 0 <= c < 15 and isinstance(board[r][c], dict)

    left  = occupied(row, col - 1)
    right = occupied(row, col + 1)
    up    = occupied(row - 1, col)
    down  = occupied(row + 1, col)

    in_horiz_middle = left and right   # surrounded horizontally
    in_vert_middle  = up and down      # surrounded vertically
    in_horiz        = left or right
    in_vert         = up or down

    # Middle of any word — not replaceable
    if in_horiz_middle or in_vert_middle:
        return False

    # Belongs to two formations — not replaceable
    if in_horiz and in_vert:
        return False

    return True


def replace_board_tile(board, bonus_squares, bag):
    """
    In-game board replacement — replace a word-final tile already on the board.
    Rules:
    i)  Word-final tiles only (not shared by multiple formations)
    ii) Blank tiles replaced only with the symbol they represent
    iii) No score awarded
    """
    print("\nBoard tile replacement:")
    print("  - Only word-final tiles can be replaced")
    print("  - A tile shared by two formations cannot be replaced")
    print("  - Blank tiles replaced only with their declared symbol")
    print("  - No score awarded")

    try:
        row = int(input("Enter row of tile to replace (1-15): ")) - 1
        col = int(input("Enter col of tile to replace (1-15): ")) - 1
    except ValueError:
        print("Invalid input.")
        return False

    if not (0 <= row <= 14 and 0 <= col <= 14):
        print("Position out of bounds!")
        return False

    cell = board[row][col]
    if not isinstance(cell, dict):
        print("No tile at that position!")
        return False

    if not is_word_final_on_board(row, col, board):
        print("That tile belongs to more than one formation and cannot be replaced!")
        return False

    # Handle blank tile — can only be replaced with its declared symbol
    if cell.get('type') == 'blank':
        declared = cell.get('symbol')
        if declared:
            sym_info = all_tiles.get(declared)
            if sym_info:
                new_tile = {"symbol": declared, "points": sym_info['points'], "type": sym_info['type']}
                board[row][col] = new_tile
                bag.append(cell)
                random.shuffle(bag)
                print(f"Blank tile replaced with proper '{declared}' tile. No score.")
                return True
        print("Cannot replace this blank tile.")
        return False

    # Regular tile replacement
    new_sym = input(f"Replace '{cell['symbol']}' with which symbol? ").strip()
    sym_info = all_tiles.get(new_sym)
    if not sym_info:
        print(f"'{new_sym}' is not a valid tile symbol!")
        return False

    new_tile = {"symbol": new_sym, "points": sym_info['points'], "type": sym_info['type']}
    board[row][col] = new_tile
    bag.append(cell)
    random.shuffle(bag)
    print(f"Replaced '{cell['symbol']}' with '{new_sym}'. No score awarded.")
    return True


def replenish_hand(player, bag):
    tiles_needed = 9 - len(player['hand'])
    if tiles_needed > 0 and bag:
        new_tiles = deal_tiles(bag, tiles_needed)
        player['hand'].extend(new_tiles)
        print(f"{player['name']} draws {len(new_tiles)} new tile(s).")

# =============================================================
# SCORING
# =============================================================

def is_boundary(cell):
    return isinstance(cell, dict) and cell.get('type') == 'boundary'


def get_connected_tiles(board, start_row, start_col, direction):
    tiles = []
    if direction == 'horizontal':
        col = start_col
        while col > 0 and isinstance(board[start_row][col-1], dict) and not is_boundary(board[start_row][col-1]):
            col -= 1
        while col < 15 and isinstance(board[start_row][col], dict) and not is_boundary(board[start_row][col]):
            tiles.append({"tile": board[start_row][col], "row": start_row, "col": col})
            col += 1
    elif direction == 'vertical':
        row = start_row
        while row > 0 and isinstance(board[row-1][start_col], dict) and not is_boundary(board[row-1][start_col]):
            row -= 1
        while row < 15 and isinstance(board[row][start_col], dict) and not is_boundary(board[row][start_col]):
            tiles.append({"tile": board[row][start_col], "row": row, "col": start_col})
            row += 1
    return tiles


def get_word_tiles(board, placed_tiles):
    rows = [t['row'] for t in placed_tiles]
    cols = [t['col'] for t in placed_tiles]
    if len(placed_tiles) == 1:
        row, col = placed_tiles[0]['row'], placed_tiles[0]['col']
        h = get_connected_tiles(board, row, col, 'horizontal')
        v = get_connected_tiles(board, row, col, 'vertical')
        return h if len(h) >= len(v) else v
    elif len(set(rows)) == 1:
        return get_connected_tiles(board, rows[0], min(cols), 'horizontal')
    else:
        return get_connected_tiles(board, min(rows), cols[0], 'vertical')


def identify_morphemes(word_tiles):
    symbols   = [t['tile']['symbol'] for t in word_tiles]
    morphemes = []
    start     = 0
    end       = len(word_tiles)

    if symbols and symbols[0] == 'i':
        morphemes.append({"type": "prefix", "tiles": [word_tiles[0]]})
        start = 1

    has_suffix = False
    if len(symbols) >= 2 and symbols[-2] == 'n' and symbols[-1] == 'ɛ':
        has_suffix = True
        end = len(word_tiles) - 2

    morphemes.append({"type": "root", "tiles": word_tiles[start:end]})
    if has_suffix:
        morphemes.append({"type": "suffix", "tiles": word_tiles[-2:]})
    return morphemes


def score_single_word(word_tiles, placed_tiles, bonus_squares):
    """
    Score = sum of ALL tile values in the word (new + existing) + bonuses.
    Bonus squares only activate when a NEW tile is placed on them this turn.

    3-level hierarchy:
      1. DS  — doubles one individual tile's score
      2. DM/TM — doubles/triples the morpheme subtotal (after DS)
      3. DL/TL — doubles/triples the whole word total (after DM/TM)

    Rules:
      - Only one DL or TL can apply per word (the highest one wins if both hit)
      - DM/TM applies per morpheme independently
      - DS is collected separately from DM/TM/DL/TL
    """
    placed_positions = {(t['row'], t['col']) for t in placed_tiles}

    # Collect word-level multiplier from newly placed tiles
    # Only DL or TL qualifies; take the strongest one if multiple hit
    word_multiplier      = 1
    word_multiplier_name = None
    for t in word_tiles:
        pos   = (t['row'], t['col'])
        if pos not in placed_positions:
            continue
        bonus = bonus_squares.get(pos)
        if bonus == 'TL' and word_multiplier < 3:
            word_multiplier      = 3
            word_multiplier_name = 'TL'
        elif bonus == 'DL' and word_multiplier < 2:
            word_multiplier      = 2
            word_multiplier_name = 'DL'

    # Step 1: DS — double individual tile scores for newly placed tiles on DS squares
    for t in word_tiles:
        pos        = (t['row'], t['col'])
        bonus      = bonus_squares.get(pos)
        tile_score = t['tile']['points']
        if pos in placed_positions and bonus == 'DS':
            tile_score *= 2
            print(f"  DS: '{t['tile']['symbol']}' {t['tile']['points']} × 2 = {tile_score}")
        t['score'] = tile_score

    # Step 2: DM/TM — sum each morpheme, then apply its multiplier if activated
    morphemes   = identify_morphemes(word_tiles)
    total_score = 0
    for morpheme in morphemes:
        m_score      = sum(t['score'] for t in morpheme['tiles'])
        m_multiplier = 1
        m_name       = None
        # Only one DM/TM per morpheme (strongest wins)
        for t in morpheme['tiles']:
            pos   = (t['row'], t['col'])
            if pos not in placed_positions:
                continue
            bonus = bonus_squares.get(pos)
            if bonus == 'TM' and m_multiplier < 3:
                m_multiplier = 3
                m_name       = 'TM'
            elif bonus == 'DM' and m_multiplier < 2:
                m_multiplier = 2
                m_name       = 'DM'
        if m_multiplier > 1:
            old = m_score
            m_score *= m_multiplier
            print(f"  {m_name}: {morpheme['type']} morpheme {old} × {m_multiplier} = {m_score}")
        total_score += m_score

    # Step 3: DL/TL — apply the single word-level multiplier
    if word_multiplier > 1:
        old = total_score
        total_score *= word_multiplier
        print(f"  {word_multiplier_name}: word {old} × {word_multiplier} = {total_score}")

    return total_score


def calculate_score(placed_tiles, board, bonus_squares):
    all_words = get_all_new_words(placed_tiles, board, bonus_squares)
    total = 0
    for i, word_tiles in enumerate(all_words):
        word_str = ''.join(t['tile']['symbol'] for t in word_tiles
                            if t['tile'].get('type') != 'boundary')
        score = score_single_word(word_tiles, placed_tiles, bonus_squares)
        if len(all_words) > 1:
            label = "Main" if i == 0 else f"Side word {i}"
            print(f"  {label} /{word_str}/: {score} pts")
        total += score
    return total

# =============================================================
# DIACRITIC VALIDATION
# =============================================================

def get_adjacent_symbols(board, row, col):
    adjacent = []
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = row+dr, col+dc
        if 0 <= nr < 15 and 0 <= nc < 15:
            cell = board[nr][nc]
            if isinstance(cell, dict) and cell.get('symbol'):
                adjacent.append((cell['symbol'], nr, nc))
    return adjacent


def validate_diacritic(diacritic, base_symbol, base_type, row, col, board):
    combined = unicodedata.normalize("NFC", base_symbol + diacritic)
    adjacent = get_adjacent_symbols(board, row, col)
    adj_syms = [s for s, r, c in adjacent]

    if combined not in VALID_DIACRITIC_COMBOS:
        valid_bases = [c.replace(diacritic, '') for c in VALID_DIACRITIC_COMBOS
                       if c.endswith(diacritic)]
        return False, (f"'{combined}' is not a valid combination. "
                       f"'{diacritic}' can only be applied to: {', '.join(sorted(valid_bases))}")

    if diacritic == "̃":
        if not any(s in NASALS for s in adj_syms):
            return False, "Nasalisation requires an adjacent nasal sound."
    elif diacritic == "ʷ":
        if not any(s in ROUNDED_VOWELS for s in adj_syms):
            return False, "Labialisation (ʷ) requires the consonant to precede /u, o, ɔ/."
    elif diacritic == "ʲ":
        if not any(s in FRONT_HIGH_VOWELS for s in adj_syms):
            return False, "Palatalisation (ʲ) requires the consonant to precede /i/ or /e/."
    elif diacritic == "ˤ":
        if not any(s in PHARYNGEALS for s in adj_syms):
            return False, "Pharyngealisation (ˤ) requires an adjacent pharyngeal /ħ/ or /ʕ/."
    elif diacritic == "ˬ":
        # Voicing — must be between two vowels
        if not (len(adj_syms) >= 2 and
                any(s in VOWELS for s in adj_syms) and
                sum(1 for s in adj_syms if s in VOWELS) >= 1):
            return False, "Voicing (ˬ) requires the consonant to be between two vowels."
    elif diacritic == "ˀ":
        GLOTTALS = {"ʔ", "h", "ħ", "ʕ"}
        if not any(s in GLOTTALS for s in adj_syms):
            return False, "Glottalisation (ˀ) requires an adjacent glottal sound /ʔ, h, ħ, ʕ/."
    elif diacritic == "ˠ":
        VELARS = {"k", "g", "ŋ", "x", "ɣ", "kp", "gb"}
        BACK_VOWELS = {"u", "o", "ɔ", "ʊ"}
        if not any(s in VELARS or s in BACK_VOWELS for s in adj_syms):
            return False, ("Velarization (ˠ) requires an adjacent velar consonant "
                           "/k,g,ŋ,x,ɣ/ or close back vowel /u,o,ɔ/.")
    elif diacritic == "ø":
        has_boundary = any(
            isinstance(board[r][c], dict) and board[r][c].get('type') == 'boundary'
            for s, r, c in adjacent
        )
        has_adjacent_vowel = any(s in VOWELS for s in adj_syms)
        if not (has_boundary or has_adjacent_vowel):
            return False, ("Elision (ø) requires the vowel to be at a word/morpheme "
                           "boundary [#] or adjacent to another vowel.")

    return True, None

# =============================================================
# WORD & SIDE-WORD HELPERS
# =============================================================

def get_all_new_words(placed_tiles, board, bonus_squares):
    # Only use real (non-boundary) tiles for direction detection
    real_tiles = [t for t in placed_tiles if t['tile'].get('type') != 'boundary']
    if not real_tiles:
        return []

    rows = [t['row'] for t in real_tiles]
    cols = [t['col'] for t in real_tiles]

    if len(real_tiles) == 1:
        main_dir  = 'horizontal'
        cross_dir = 'vertical'
    elif len(set(rows)) == 1:
        main_dir  = 'horizontal'
        cross_dir = 'vertical'
    else:
        main_dir  = 'vertical'
        cross_dir = 'horizontal'

    new_words = []

    if main_dir == 'horizontal':
        main_word = get_connected_tiles(board, rows[0], min(cols), 'horizontal')
    else:
        main_word = get_connected_tiles(board, min(rows), cols[0], 'vertical')

    if len(main_word) > 1:
        new_words.append(main_word)

    seen = set()
    for pt in real_tiles:
        cross = get_connected_tiles(board, pt['row'], pt['col'], cross_dir)
        if len(cross) > 1:
            key = (cross[0]['row'], cross[0]['col'], cross[-1]['row'], cross[-1]['col'])
            if key not in seen:
                seen.add(key)
                new_words.append(cross)

    return new_words

# =============================================================
# WORD VALIDATION
# =============================================================

def is_consonant(symbol):
    nfc = unicodedata.normalize("NFC", symbol)
    return symbol not in VOWELS and nfc not in EXTENDED_VOWELS


def is_vowel_like(sym):
    nfc = unicodedata.normalize("NFC", sym)
    return sym in VOWELS or nfc in EXTENDED_VOWELS

def is_valid_syllable(symbols):
    n = len(symbols)
    if n == 1:
        return is_vowel_like(symbols[0])
    elif n == 2:
        return is_consonant(symbols[0]) and is_vowel_like(symbols[1])
    elif n == 3:
        return (is_consonant(symbols[0]) and symbols[1] in GLIDES and is_vowel_like(symbols[2]))
    return False


# Syllabic nasal symbols (they form their own syllable nucleus like vowels)
SYLLABIC_NASALS = {
    unicodedata.normalize("NFC", s) for s in
    ["m̩", "ɱ̩", "n̩", "ɲ̩", "ŋ̩", "ŋm̩"]
}

def is_syllabic_nucleus(sym):
    """Returns True if the symbol can be a syllable nucleus (vowel or syllabic nasal)"""
    return sym in VOWELS or unicodedata.normalize("NFC", sym) in SYLLABIC_NASALS

def split_into_syllables(symbol_list):
    syllables = []
    i = 0
    while i < len(symbol_list):
        sym = symbol_list[i]
        # Try CGV (3 symbols) — only if current is consonant
        if i + 2 < len(symbol_list) and sym not in VOWELS and sym not in SYLLABIC_NASALS:
            chunk = symbol_list[i:i+3]
            if is_valid_syllable(chunk):
                syllables.append(chunk)
                i += 3
                continue
        # Try CV (2 symbols)
        if i + 1 < len(symbol_list) and sym not in VOWELS and sym not in SYLLABIC_NASALS:
            chunk = symbol_list[i:i+2]
            if is_valid_syllable(chunk):
                syllables.append(chunk)
                i += 2
                continue
        # V alone (vowel or syllabic nasal forms its own syllable)
        if is_syllabic_nucleus(sym) or is_vowel_like(sym):
            syllables.append([sym])
            i += 1
            continue
        return None
    return syllables



# =============================================================
# PROCESS DETECTION
# Every word must demonstrate at least one phonological process
# =============================================================

TENSE_VOWELS = {"i", "e", "u", "o", "a"}
LAX_VOWELS   = {"ɪ", "ɛ", "ʊ", "ɔ"}

VOICELESS = {"p", "t", "k", "f", "s", "ʃ", "θ", "x", "χ", "ħ", "h",
             "ts", "tʃ", "kx", "pɸ", "c", "q"}
FRICATIVES = {"f", "v", "s", "z", "ʃ", "ʒ", "θ", "ð", "x", "ɣ", "χ",
              "ʁ", "ħ", "ʕ", "h", "ɦ", "ɸ", "β", "ç", "ʝ"}
APPROXIMANTS = {"j", "w", "l", "r", "ɹ", "ɻ", "ʋ", "ɥ"}
PLOSIVES = {"p", "b", "t", "d", "k", "g", "c", "ɟ", "q", "ɢ", "ʔ",
            "kp", "gb"}

def detect_processes(word_tiles, board):
    """
    Detect which phonological processes are demonstrated in a word.
    Returns list of detected process names.
    """
    processes = []
    tiles = [t for t in word_tiles if t['tile'].get('type') != 'boundary']
    symbols = [t['tile']['symbol'] for t in tiles]
    if not symbols:
        return processes

    # 1. NASALISATION — nasalised vowel tile present
    nasalised = {unicodedata.normalize("NFC", v) for v in
                 ["ĩ", "ẽ", "ɛ̃", "ã", "ɔ̃", "õ", "ũ"]}
    for t in tiles:
        if unicodedata.normalize("NFC", t['tile']['symbol']) in nasalised:
            processes.append("nasalisation")
            break

    # 2. LABIALISATION — kʷ, gʷ, mʷ, ŋʷ present
    labialised = {unicodedata.normalize("NFC", s) for s in ["mʷ","ŋʷ","kʷ","gʷ"]}
    for t in tiles:
        if unicodedata.normalize("NFC", t['tile']['symbol']) in labialised:
            processes.append("labialisation")
            break

    # 3. PALATALISATION — dʲ, gʲ present
    palatalised = {unicodedata.normalize("NFC", s) for s in ["dʲ","gʲ"]}
    for t in tiles:
        if unicodedata.normalize("NFC", t['tile']['symbol']) in palatalised:
            processes.append("palatalisation")
            break

    # 4. VOICING — tile with ˬ diacritic
    for t in tiles:
        if t['tile'].get('diacritic') == 'ˬ':
            processes.append("voicing")
            break

    # 5. COMPENSATORY LENGTHENING — long vowel tile present
    long_vowels = {unicodedata.normalize("NFC", s) for s in
                   ["iː","eː","ɛː","aː","ɔː","oː","uː"]}
    for t in tiles:
        if unicodedata.normalize("NFC", t['tile']['symbol']) in long_vowels:
            processes.append("compensatory_lengthening")
            break

    # 6. NASAL HOMORGANIC ASSIMILATION — syllabic nasal matching following consonant
    syllabic_nasals = {unicodedata.normalize("NFC", s) for s in
                       ["m̩","ɱ̩","n̩","ɲ̩","ŋ̩","ŋm̩"]}
    for i in range(len(tiles) - 1):
        s1 = unicodedata.normalize("NFC", tiles[i]['tile']['symbol'])
        s2 = tiles[i+1]['tile']['symbol']
        if s1 in syllabic_nasals and s2 not in VOWELS:
            processes.append("nasal_homorganic_assimilation")
            break

    # 7. GLIDE FORMATION — j or w before a vowel
    for i in range(len(symbols) - 1):
        if symbols[i] in GLIDES and symbols[i+1] in VOWELS:
            processes.append("glide_formation")
            break

    # 8. SPIRANTISATION — fricative between two vowels
    for i in range(1, len(symbols) - 1):
        if (symbols[i] in FRICATIVES and
                symbols[i-1] in VOWELS and
                symbols[i+1] in VOWELS):
            processes.append("spirantisation")
            break

    # 9. APPROXIMANT — approximant between two vowels (stop context)
    for i in range(1, len(symbols) - 1):
        if (symbols[i] in APPROXIMANTS and
                symbols[i-1] in VOWELS and
                symbols[i+1] in VOWELS):
            processes.append("approximant")
            break

    # 10. GLOTTALISATION — ʔ adjacent to another sound
    for i, sym in enumerate(symbols):
        if sym == 'ʔ' and len(symbols) > 1:
            processes.append("glottalisation")
            break

    # 11. VELARIZATION — lˤ present
    for t in tiles:
        if unicodedata.normalize("NFC", t['tile']['symbol']) == unicodedata.normalize("NFC","lˤ"):
            processes.append("velarization")
            break

    # 12. PHARYNGEALISATION — lˤ also covers this
    # (same tile, dual process marker)

    # 13. VOWEL HARMONY — at least 2 DIFFERENT vowels sharing tense or lax feature
    word_vowels = [s for s in symbols if s in VOWELS]
    if len(set(word_vowels)) >= 2:  # must have at least 2 distinct vowels
        all_tense = all(v in TENSE_VOWELS for v in word_vowels)
        all_lax   = all(v in LAX_VOWELS   for v in word_vowels)
        if all_tense or all_lax:
            processes.append("vowel_harmony")

    # 14. ELISION — [#] boundary with vowel absent on one side
    has_boundary = any(t['tile'].get('type') == 'boundary' for t in word_tiles)
    if has_boundary:
        processes.append("elision")

    # 15. INSERTION — vowel inserted between two consonants in borrowed word
    # Only counts if the word has more consonants than a normal JEREMI word would
    # i.e. the word structure suggests a consonant cluster was broken up
    # Detected as: C V C V C pattern (more than one VC sequence with flanking consonants)
    consonant_positions = [i for i, s in enumerate(symbols) if s not in VOWELS and s not in GLIDES]
    vowel_positions     = [i for i, s in enumerate(symbols) if s in VOWELS]
    # Insertion indicated when two consonants are separated only by a single vowel
    # AND the word has at least 3 consonants (suggesting borrowed word with clusters)
    if len(consonant_positions) >= 3:
        for i in range(1, len(symbols) - 1):
            s_prev = symbols[i-1]
            s_curr = symbols[i]
            s_next = symbols[i+1]
            if (s_prev not in VOWELS and s_prev not in GLIDES and
                    s_curr in VOWELS and
                    s_next not in VOWELS and s_next not in GLIDES):
                processes.append("insertion")
                break

    return processes

def validate_word(word_tiles, board):
    if not word_tiles:
        return False, "No tiles placed."

    symbols = [t['tile']['symbol'] for t in word_tiles
               if t['tile'].get('type') != 'boundary']

    if not symbols:
        return False, "Word contains only boundary markers."

    # Rule 1: syllable structure
    syllables = split_into_syllables(symbols)
    if syllables is None:
        return False, (f"Invalid syllable structure. Only CV, V, CGV allowed. "
                       f"Got: /{' '.join(symbols)}/")

    # Rule 2: max trisyllabic (root only)
    root_symbols = symbols[:]
    if root_symbols and root_symbols[0] == 'i' and len(root_symbols) > 1:
        root_symbols = root_symbols[1:]
    if len(root_symbols) >= 2 and root_symbols[-2] == 'n' and root_symbols[-1] == 'ɛ':
        root_symbols = root_symbols[:-2]
    root_syllables = split_into_syllables(root_symbols)
    if root_syllables and len(root_syllables) > 3:
        return False, f"Word root exceeds 3 syllables ({len(root_syllables)} found)."

    # Rule 3a: Glide formation (checked before negation)
    # /i/ or /u/ before a vowel must become /j/ or /w/
    for idx in range(len(symbols) - 1):
        s1, s2 = symbols[idx], symbols[idx+1]
        if s1 in {'i', 'u'} and s2 in VOWELS:
            glide = 'j' if s1 == 'i' else 'w'
            return False, (f"Glide formation: /{s1}/ before /{s2}/ "
                           f"must become /{glide}/. Use /{glide}{s2}/ instead.")

    # Rule 3b: verb/noun distinction
    # Verbs begin with consonants, nouns begin with vowels
    root_start_sym = symbols[1] if (symbols[0] == 'i' and len(symbols) > 1) else symbols[0]

    # Negation prefix [i] only on verbs (consonant-initial roots)
    if symbols[0] == 'i' and len(symbols) > 1:
        if symbols[1] in VOWELS:
            return False, "Negation prefix [i] can only be used on verbs (consonant-initial words)."

    # Progressive suffix [nɛ] only on verbs
    has_suffix = len(symbols) >= 2 and symbols[-2] == 'n' and symbols[-1] == 'ɛ'
    if has_suffix:
        # Strip prefix and suffix to get root
        root_start = 1 if symbols[0] == 'i' else 0
        root = symbols[root_start:-2]
        if root and root[0] in VOWELS:
            return False, "Progressive suffix [nɛ] can only be used on verbs (consonant-initial words)."

    # Rule 4: no consonant cluster except CGV
    # Syllabic nasals count as syllable nuclei (not consonants) for this check
    for i in range(len(symbols) - 1):
        s1, s2 = symbols[i], symbols[i+1]
        s1_nfc = unicodedata.normalize("NFC", s1)
        s2_nfc = unicodedata.normalize("NFC", s2)
        s1_is_cons = not is_vowel_like(s1) and s1_nfc not in SYLLABIC_NASALS
        s2_is_cons = not is_vowel_like(s2) and s2_nfc not in SYLLABIC_NASALS
        if s1_is_cons and s2_is_cons:
            if s2 in GLIDES:
                if i + 2 < len(symbols) and symbols[i+2] in VOWELS:
                    continue
                return False, f"Glide /{s2}/ must be followed by a vowel (CGV). Got /{s1}{s2}../."
            elif s1 in GLIDES:
                return False, f"Glide /{s1}/ must precede a vowel, not /{s2}/."
            else:
                return False, f"Illegal consonant cluster: /{s1}{s2}/."

    # Rule 5: diacritic combos
    for t in word_tiles:
        tile = t['tile']
        if tile.get('diacritic'):
            diac     = tile['diacritic']
            base     = tile['symbol'].replace(diac, '')
            combined = unicodedata.normalize("NFC", base + diac)
            if combined not in VALID_DIACRITIC_COMBOS:
                return False, f"Invalid diacritic combination: /{combined}/."

    # Rule 6: Nasal homorganic assimilation
    # A syllabic nasal before a consonant must match that consonant's place
    # e.g. m̩ before bilabial, ŋ̩ before velar, ɲ̩ before palatal etc.
    BILABIAL    = {"p", "b", "m", "pʼ", "ɓ", "pɸ", "bβ"}
    LABIODENTAL = {"f", "v", "ɱ"}
    VELAR       = {"k", "g", "ŋ", "kp", "gb", "kx", "gɣ", "kʼ", "ɠ"}
    PALATAL     = {"c", "ɟ", "ɲ", "cʼ", "ʄ"}
    UVULAR      = {"q", "ɢ", "ɴ", "qʼ", "ʛ"}

    # Map place → correct syllabic nasal symbol
    PLACE_NASALS = {
        "bilabial":    "m̩",
        "labiodental": "ɱ̩",
        "velar":       "ŋ̩",
        "palatal":     "ɲ̩",
        "uvular":      "ɴ",   # no syllabic uvular nasal tile
        "alveolar":    "n̩",
    }

    def get_place(sym):
        if sym in BILABIAL:    return "bilabial"
        if sym in LABIODENTAL: return "labiodental"
        if sym in VELAR:       return "velar"
        if sym in PALATAL:     return "palatal"
        if sym in UVULAR:      return "uvular"
        return "alveolar"

    # Check syllabic nasals in the word
    for idx in range(len(word_tiles) - 1):
        t1 = word_tiles[idx]['tile']
        t2 = word_tiles[idx + 1]['tile']
        sym1 = t1.get('symbol', '')
        sym2 = t2.get('symbol', '')

        # Skip boundary tiles
        if t1.get('type') == 'boundary' or t2.get('type') == 'boundary':
            continue

        # Is sym1 a syllabic nasal (has syllabicity diacritic ̩)?
        is_syllabic_nasal = (
            t1.get('diacritic') == '̩' and
            sym1.replace('̩', '') in {"m", "ɱ", "n", "ɲ", "ŋ", "ŋm"}
        )

        if is_syllabic_nasal and sym2 not in VOWELS and sym2 not in GLIDES:
            place = get_place(sym2)
            expected = PLACE_NASALS.get(place, "n̩")
            # Normalise both for comparison
            sym1_nfc = unicodedata.normalize("NFC", sym1)
            exp_nfc  = unicodedata.normalize("NFC", expected)
            if sym1_nfc != exp_nfc:
                base_nasal = sym1.replace('̩', '')
                return False, (
                    f"Nasal homorganic assimilation: syllabic /{base_nasal}/ before "
                    f"/{sym2}/ ({place}) must be /{expected}/."
                )

    return True, None

# =============================================================
# AI OPPONENT  — follows every rule the human player must follow
# =============================================================

def is_valid_word_structure(symbol_list):
    if not symbol_list:
        return False
    symbols    = list(symbol_list)
    root_start = 0
    root_end   = len(symbols)
    if symbols[0] == 'i' and len(symbols) > 1:
        root_start = 1
    if len(symbols) >= root_start + 2 and symbols[-2] == 'n' and symbols[-1] == 'ɛ':
        root_end = len(symbols) - 2
    root = symbols[root_start:root_end]
    if not root:
        return False
    syllables = split_into_syllables(root)
    if syllables is None or len(syllables) > 3:
        return False
    return True


def generate_candidate_words(hand):
    """
    Generate valid word sequences using only tiles actually in the AI's hand.
    Diacritic combos are pre-merged. Blank tiles are declared as 'a'.
    """
    base_tiles      = [t for t in hand if t['symbol'] and t['type'] != 'diacritic']
    diacritic_tiles = [t for t in hand if t['symbol'] and t['type'] == 'diacritic']
    blank_count     = sum(1 for t in hand if t['type'] == 'blank')

    symbols          = []
    used_diacritics  = set()

    for bt in base_tiles:
        base_sym = bt['symbol']
        combined = False
        for dt in diacritic_tiles:
            if dt['symbol'] in used_diacritics:
                continue
            combo = unicodedata.normalize("NFC", base_sym + dt['symbol'])
            if combo in VALID_DIACRITIC_COMBOS:
                symbols.append(combo)
                used_diacritics.add(dt['symbol'])
                combined = True
                break
        if not combined:
            symbols.append(base_sym)

    # Blanks declared as the most common vowel 'a'
    for _ in range(blank_count):
        symbols.append("a")

    candidates = set()
    for length in range(2, min(10, len(symbols) + 1)):
        for perm in permutations(symbols, length):
            word      = list(perm)
            base_word = [unicodedata.normalize("NFD", s)[0] if len(s) > 1 else s for s in word]
            if is_valid_word_structure(base_word):
                candidates.add(tuple(word))

    return [list(c) for c in candidates]


def find_anchor_positions(board):
    """
    On an empty board, only the START square is valid.
    Otherwise, return all empty cells adjacent to an existing tile.
    """
    if not board_has_tiles(board):
        return [(7, 0)]   # START square (internal 0-based)

    anchors = []
    for row in range(15):
        for col in range(15):
            if isinstance(board[row][col], dict):
                continue
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = row+dr, col+dc
                if 0 <= nr < 15 and 0 <= nc < 15:
                    if isinstance(board[nr][nc], dict):
                        anchors.append((row, col))
                        break
    return anchors


def simulate_score_ai(word_symbols, start_row, start_col, direction,
                      board, bonus_squares, hand):
    """
    Simulate placing a word and return the score.
    Enforces EVERY rule the human player must follow:
      - tiles must come from the actual hand
      - first move must cover START (internal row 7, col 0)
      - subsequent moves must connect to existing tiles
      - no consonant clusters
      - all words (main + side) must pass validate_word()
    Uses the same 3-level morpheme-aware scoring as score_single_word().
    Returns -1 if the move is invalid for any reason.
    """
    dr = 1 if direction == 'vertical'   else 0
    dc = 1 if direction == 'horizontal' else 0

    # Bounds
    end_r = start_row + dr * (len(word_symbols) - 1)
    end_c = start_col + dc * (len(word_symbols) - 1)
    if not (0 <= start_row <= 14 and 0 <= start_col <= 14):
        return -1
    if not (0 <= end_r <= 14 and 0 <= end_c <= 14):
        return -1

    board_is_empty = not board_has_tiles(board)

    # Walk through squares and match/consume hand tiles
    temp_positions = []
    hand_copy      = list(hand)
    newly_placed   = []
    r, c           = start_row, start_col

    for sym in word_symbols:
        cell = board[r][c]
        if isinstance(cell, dict) and cell.get('type') != 'boundary':
            if cell['symbol'] != sym:
                return -1
            temp_positions.append((r, c, sym, False, cell['points']))
        elif cell in [None, "START"] or (isinstance(cell, str) and cell not in ("START",)):
            tile_info = all_tiles.get(sym)
            if tile_info is None:
                return -1
            # Must find the tile in hand (or a blank)
            found = False
            for i, t in enumerate(hand_copy):
                if t['symbol'] == sym:
                    hand_copy.pop(i); found = True; break
            if not found:
                for i, t in enumerate(hand_copy):
                    if t['type'] == 'blank':
                        hand_copy.pop(i); found = True; break
            if not found:
                return -1
            temp_positions.append((r, c, sym, True, tile_info['points']))
            newly_placed.append((r, c))
        else:
            return -1
        r += dr
        c += dc

    if not newly_placed:
        return -1

    # Rule: first move must cover START
    if board_is_empty:
        if not any(nr == 7 and nc == 0 for nr, nc in newly_placed):
            return -1

    # Rule: subsequent moves must connect
    if not board_is_empty:
        connected = False
        placed_set = set(newly_placed)
        for (nr, nc) in newly_placed:
            for ddr, ddc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nnr, nnc = nr+ddr, nc+ddc
                if 0 <= nnr < 15 and 0 <= nnc < 15:
                    nb = board[nnr][nnc]
                    if isinstance(nb, dict) and (nnr, nnc) not in placed_set:
                        connected = True; break
            if connected:
                break
        if not connected:
            return -1

    # Rule: no consonant clusters
    for (nr, nc, sym, is_new, pts) in temp_positions:
        if not is_new:
            continue
        info = all_tiles.get(sym, {})
        if info.get('type') == 'base_consonant' and sym not in GLIDES:
            if check_consonant_cluster(board, nr, nc, sym, direction):
                return -1

    # Build a temporary board for word validation
    temp_board = [row[:] for row in board]
    for (nr, nc, sym, is_new, pts) in temp_positions:
        if is_new:
            info = all_tiles.get(sym, {})
            temp_board[nr][nc] = {"symbol": sym, "points": pts,
                                   "type": info.get('type', 'base_consonant')}

    # Validate main word
    if direction == 'horizontal':
        main_word = get_connected_tiles(temp_board, start_row, start_col, 'horizontal')
    else:
        main_word = get_connected_tiles(temp_board, start_row, start_col, 'vertical')

    valid, _ = validate_word(main_word, temp_board)
    if not valid:
        return -1

    # Validate all side words
    cross_dir  = 'vertical' if direction == 'horizontal' else 'horizontal'
    placed_set = set(newly_placed)
    for (nr, nc) in newly_placed:
        cross = get_connected_tiles(temp_board, nr, nc, cross_dir)
        if len(cross) > 1:
            valid, _ = validate_word(cross, temp_board)
            if not valid:
                return -1

    # --- SCORING: same 3-level system as score_single_word() ---
    def score_wtiles(wtiles):
        """Score ALL tiles in word (new + existing), bonuses only on new tiles."""
        activated = []
        for t in wtiles:
            pos        = (t['row'], t['col'])
            bonus      = bonus_squares.get(pos)
            tile_score = t['tile']['points']
            if pos in placed_set and bonus == 'DS':
                tile_score *= 2
            if pos in placed_set and bonus in ('DL', 'TL', 'DM', 'TM'):
                activated.append(bonus)
            t['score'] = tile_score
        morphemes  = identify_morphemes(wtiles)
        word_total = 0
        for morpheme in morphemes:
            # Sum ALL tiles in morpheme (not just newly placed)
            m_score = sum(t['score'] for t in morpheme['tiles'])
            for t in morpheme['tiles']:
                pos = (t['row'], t['col'])
                if pos not in placed_set:
                    continue
                bonus = bonus_squares.get(pos)
                if bonus == 'DM':
                    m_score *= 2; break
                elif bonus == 'TM':
                    m_score *= 3; break
            word_total += m_score
        for bonus in activated:
            if bonus == 'DL':
                word_total *= 2
            elif bonus == 'TL':
                word_total *= 3
        return word_total

    total_score = score_wtiles(main_word)

    seen = set()
    for (nr, nc) in newly_placed:
        cross = get_connected_tiles(temp_board, nr, nc, cross_dir)
        key   = (cross[0]['row'], cross[0]['col'], cross[-1]['row'], cross[-1]['col'])
        if len(cross) > 1 and key not in seen:
            seen.add(key)
            total_score += score_wtiles(cross)

    if len(newly_placed) == 9:
        total_score += 30

    return total_score


def ai_take_turn(ai_player, board, bonus_squares, bag, consecutive_passes):
    print(f"\n🤖 {ai_player['name']} is thinking...")

    candidates = generate_candidate_words(ai_player['hand'])
    anchors    = find_anchor_positions(board)

    best_score = -1
    best_move  = None

    for word_symbols in candidates:
        for (anchor_r, anchor_c) in anchors:
            for direction in ['horizontal', 'vertical']:
                for offset in range(len(word_symbols)):
                    if direction == 'horizontal':
                        start_r, start_c = anchor_r, anchor_c - offset
                    else:
                        start_r, start_c = anchor_r - offset, anchor_c

                    score = simulate_score_ai(
                        word_symbols, start_r, start_c,
                        direction, board, bonus_squares, ai_player['hand']
                    )
                    if score > best_score:
                        best_score = score
                        best_move  = (word_symbols, start_r, start_c, direction)

    if best_move is None or best_score <= 0:
        print(f"🤖 {ai_player['name']} passes (no valid move found).")
        return consecutive_passes + 1

    word_symbols, start_r, start_c, direction = best_move
    dr = 1 if direction == 'vertical'   else 0
    dc = 1 if direction == 'horizontal' else 0

    placed_tiles = []
    r, c         = start_r, start_c
    hand_copy    = list(ai_player['hand'])
    valid_exec   = True

    for sym in word_symbols:
        cell = board[r][c]
        if isinstance(cell, dict):
            # Existing tile — must match expected symbol
            if cell.get('symbol') != sym:
                valid_exec = False
                break
        else:
            tile = None
            for i, t in enumerate(hand_copy):
                if t['symbol'] == sym:
                    tile = hand_copy.pop(i); break
            if tile is None:
                for i, t in enumerate(hand_copy):
                    if t['type'] == 'blank':
                        tile           = hand_copy.pop(i).copy()
                        info           = all_tiles.get(sym, {})
                        tile['symbol'] = sym
                        tile['type']   = info.get('type', 'base_consonant')
                        tile['points'] = info.get('points', 0)
                        break
            if tile is None:
                valid_exec = False
                break
            board[r][c] = tile
            placed_tiles.append({"tile": tile, "row": r, "col": c,
                                  "bonus": bonus_squares.get((r, c))})
        r += dr
        c += dc

    # Safety check — validate the full word on the board
    if valid_exec and placed_tiles:
        all_words = get_all_new_words(placed_tiles, board, bonus_squares)
        for wt in all_words:
            ok, _ = validate_word(wt, board)
            if not ok:
                # Withdraw tiles
                for pt in placed_tiles:
                    pr, pc = pt['row'], pt['col']
                    bonus  = bonus_squares.get((pr, pc))
                    board[pr][pc] = bonus if bonus else None
                    hand_copy.append(pt['tile'])
                placed_tiles = []
                valid_exec = False
                break

    if not valid_exec or not placed_tiles:
        print(f"🤖 {ai_player['name']} passes (could not execute move).")
        ai_player['hand'] = hand_copy
        return consecutive_passes + 1

    ai_player['hand'] = hand_copy
    word_str = ''.join(word_symbols)
    # Display uses 1-based
    print(f"🤖 {ai_player['name']} plays: /{word_str}/ at R{start_r+1} C{start_c+1} ({direction})")
    print_board(board)

    turn_score = calculate_score(placed_tiles, board, bonus_squares)
    if len(placed_tiles) == 9:
        print("🎉 30-point bonus for playing all 9 tiles!")
        turn_score += 30

    ai_player['score'] += turn_score
    print(f"🤖 Turn score: {turn_score} | Total: {ai_player['score']}")
    replenish_hand(ai_player, bag)
    return 0

# =============================================================
# CHALLENGING
# =============================================================

def ai_should_challenge(word_tiles, board):
    valid, reason = validate_word(word_tiles, board)
    if not valid:
        return True, reason
    return False, None




def withdraw_tiles(placed_tiles, board, bonus_squares):
    """Remove placed tiles from board, restoring bonus squares."""
    for pt in placed_tiles:
        row, col = pt['row'], pt['col']
        bonus    = bonus_squares.get((row, col))
        board[row][col] = bonus if bonus else None


def challenge_word(players, current_player, placed_tiles, board, bonus_squares):
    """
    Challenge window — human players only.
    After a word is played, other players can challenge before score is added.
    - Challenger right  → current player withdraws tiles, loses points and turn
    - Challenger wrong  → challenger loses points and next turn
    """
    other_players = [p for p in players
                     if p['name'] != current_player['name']]
    word_tiles = get_word_tiles(board, placed_tiles)
    word_str   = ''.join(t['tile']['symbol'] for t in word_tiles
                         if t['tile'].get('type') != 'boundary')

    print(f"\n--- CHALLENGE WINDOW --- Word played: /{word_str}/")
    print("Queries should be about:")
    print("  i)   Syllable and word structure")
    print("  ii)  Right environment for processes")
    print("  iii) Appropriate use of diacritics")

    for challenger in other_players:
        if challenger.get('is_ai'):
            should_challenge, reason = ai_should_challenge(word_tiles, board)
            if should_challenge:
                print(f"\n🤖 {challenger['name']} CHALLENGES: {reason}")
                print(f"\nChallenge upheld! {current_player['name']} withdraws their tiles.")
                withdraw_tiles(placed_tiles, board, bonus_squares)
                for pt in placed_tiles:
                    current_player['hand'].append(pt['tile'])
                turn_score = sum(t['tile']['points'] for t in placed_tiles)
                current_player['score'] -= turn_score
                print(f"{current_player['name']} loses {turn_score} pts and their turn.")
                return False
            else:
                print(f"🤖 {challenger['name']} does not challenge.")
            continue

        response = input(f"\n{challenger['name']}: Challenge this word? (y/n): ").strip().lower()
        if response == 'y':
            # Run automatic validation to assist
            valid, auto_reason = validate_word(word_tiles, board)
            if not valid:
                print(f"\n⚠️  Automatic check found: {auto_reason}")

            verdict = input("\nAfter checking the manual — is the word VALID? (y/n): ").strip().lower()
            if verdict == 'n':
                # Challenger is RIGHT
                print(f"\nChallenge upheld! {current_player['name']} withdraws their tiles.")
                withdraw_tiles(placed_tiles, board, bonus_squares)
                # Return tiles to hand
                for pt in placed_tiles:
                    current_player['hand'].append(pt['tile'])
                turn_score = sum(t['tile']['points'] for t in placed_tiles)
                current_player['score'] -= turn_score
                print(f"{current_player['name']} loses {turn_score} pts and their turn.")
                return False
            else:
                # Challenger is WRONG
                print(f"\nChallenge failed! /{word_str}/ stands.")
                penalty = sum(t['tile']['points'] for t in placed_tiles)
                challenger['score'] -= penalty
                print(f"{challenger['name']} loses {penalty} pts and their next turn.")
                challenger['skip_next'] = True
                return True

    return True  # no challenge raised

# =============================================================
# TURN
# =============================================================

def take_turn(player, board, bonus_squares, bag, consecutive_passes,
              players=[], turn_number=1, history=None):
    if history is None:
        history = []

    clear_screen()
    print(f"\n===== Turn {turn_number} — {player['name']} =====")
    print_board(board)

    # Route AI player to AI logic
    if player.get('is_ai'):
        prev_score = player['score']
        result = ai_take_turn(player, board, bonus_squares, bag, consecutive_passes)
        turn_score = player['score'] - prev_score
        history.append({
            "turn":   turn_number,
            "player": player['name'],
            "action": "AI played",
            "score":  turn_score if turn_score > 0 else "",
        })
        display_scoreboard(players)
        return result

    while True:
        action = get_player_action(player)

        if action == '5':
            # Place word/morpheme boundary marker freely
            try:
                brow = int(input("Place [#] at row (1-15): ")) - 1
                bcol = int(input("Place [#] at col (1-15): ")) - 1
            except ValueError:
                print("Invalid input.")
                continue
            if not (0 <= brow <= 14 and 0 <= bcol <= 14):
                print("Position out of bounds!")
                continue
            if isinstance(board[brow][bcol], dict):
                print("That square is already occupied!")
                continue
            board[brow][bcol] = {"symbol": "#", "points": 0, "type": "boundary"}
            print_board(board)
            print(f"Placed [#] boundary marker at R{brow+1} C{bcol+1}")
            continue

        if action == '6':
            display_history(history)
            continue

        if action == '7':
            return 'save'

        break

    if action == '1':
        # Play tiles on board
        result = place_tiles(player, board, bonus_squares, bag)

        # Handle replace/pass chosen from within place_tiles
        if result == 'replaced':
            history.append({
                "turn":   turn_number,
                "player": player['name'],
                "action": "replaced rack tiles (lost turn)",
                "score":  "",
            })
            print(f"{player['name']} loses their turn for replacing tiles.")
            return consecutive_passes + 1

        if result == 'passed':
            print(f"{player['name']} passes.")
            history.append({
                "turn":   turn_number,
                "player": player['name'],
                "action": "passed",
                "score":  "",
            })
            return consecutive_passes + 1

        placed_tiles = result
        all_words = get_all_new_words(placed_tiles, board, bonus_squares)
        all_valid = True
        for word_tiles in all_words:
            valid, reason = validate_word(word_tiles, board)
            if not valid:
                print(f"\n❌ Invalid word: {reason}")
                withdraw_tiles(placed_tiles, board, bonus_squares)
                for pt in placed_tiles:
                    if pt['tile'].get('type') != 'boundary':
                        player['hand'].append(pt['tile'])
                all_valid = False
                break

        if not all_valid:
            return consecutive_passes

        word_valid = challenge_word(players, player, placed_tiles, board, bonus_squares)

        if word_valid:
            turn_score = calculate_score(placed_tiles, board, bonus_squares)
            if len(placed_tiles) == 9:
                print("🎉 30-point bonus for playing all 9 tiles!")
                turn_score += 30
            player['score'] += turn_score
            print(f"\nTurn score: {turn_score}")

            # Show detected processes informatively
            all_words = get_all_new_words(placed_tiles, board, bonus_squares)
            all_procs = []
            for wt in all_words:
                all_procs.extend(detect_processes(wt, board))
            if all_procs:
                proc_names = ', '.join(sorted(set(all_procs))).replace('_', ' ')
                print(f"📚 Process(es) demonstrated: {proc_names}")

            replenish_hand(player, bag)

            word_str = ''.join(
                t['tile']['symbol'] for t in placed_tiles
                if t['tile'].get('type') != 'boundary'
            )
            history.append({
                "turn":   turn_number,
                "player": player['name'],
                "action": f"played /{word_str}/",
                "score":  turn_score,
            })

        display_scoreboard(players)
        return 0

    elif action == '2':
        # Replace tiles from rack — loses turn
        replace_rack_tiles(player, bag)
        history.append({
            "turn":   turn_number,
            "player": player['name'],
            "action": "replaced rack tiles (lost turn)",
            "score":  "",
        })
        print(f"{player['name']} loses their turn for replacing tiles.")
        return consecutive_passes + 1

    elif action == '3':
        # Replace a word-final tile on the board — no score, no turn loss
        replaced = replace_board_tile(board, bonus_squares, bag)
        if replaced:
            history.append({
                "turn":   turn_number,
                "player": player['name'],
                "action": "replaced board tile",
                "score":  "",
            })
            print_board(board)
        return consecutive_passes

    elif action == '4':
        # Pass
        print(f"{player['name']} passes.")
        history.append({
            "turn":   turn_number,
            "player": player['name'],
            "action": "passed",
            "score":  "",
        })
        return consecutive_passes + 1

    return consecutive_passes

# =============================================================
# GAME OVER
# =============================================================

def check_game_over(bag, players, consecutive_passes):
    """
    Game ends when:
    1. All players pass twice in succession (each player passed at least twice
       without any play in between)
    2. Bag empty and one player has used all tiles
    """
    # Each player must have passed at least twice with no plays in between
    # consecutive_passes tracks total passes since last play
    # For N players, N*2 consecutive passes means all passed twice
    if consecutive_passes >= len(players) * 2:
        return True, "all_passed"
    if len(bag) == 0:
        for player in players:
            if len(player['hand']) == 0:
                return True, player['name']
    return False, None


def end_game(players):
    print("\n========== GAME OVER ==========")

    # Find player who used all tiles (if any)
    finisher = None
    for player in players:
        if len(player['hand']) == 0:
            finisher = player
            break

    total_leftover = 0
    print("\n--- Tile deductions ---")
    for player in players:
        if len(player['hand']) > 0:
            leftover = sum(t['points'] for t in player['hand'])
            if leftover > 0:
                player['score'] -= leftover
                total_leftover  += leftover
                tiles_str = ' '.join(
                    t['symbol'] if t.get('symbol') else 'BLANK'
                    for t in player['hand']
                )
                print(f"  {player['name']}: -{leftover} pts (unused: {tiles_str})")
        else:
            print(f"  {player['name']}: no tiles remaining")

    # Player who finished gets all leftover points from ALL other players
    if finisher and total_leftover > 0:
        finisher['score'] += total_leftover
        print(f"\n  {finisher['name']} gains +{total_leftover} pts "
              f"(sum of all opponents' unused tiles)")

    print("\n--- FINAL SCORES ---")
    players_sorted = sorted(players, key=lambda x: x['score'], reverse=True)
    for i, player in enumerate(players_sorted):
        medal = ["🥇", "🥈", "🥉"][i] if i < 3 else "  "
        print(f"  {medal} {player['name']}: {player['score']} pts")
    print(f"\n🏆 {players_sorted[0]['name']} wins!")

# =============================================================
# MAIN
# =============================================================

def main():
    clear_screen()
    print("=============================")
    print("     Welcome to JEREMÍ!      ")
    print("=============================\n")
    print("  1. New game")
    print("  2. Load saved game")
    while True:
        start = input("Choose (1 or 2): ").strip()
        if start in ('1', '2'):
            break
        print("Please enter 1 or 2.")

    history = []

    if start == '2':
        loaded = load_game()
        if loaded is None:
            print("Starting a new game instead.\n")
            start = '1'
        else:
            board, bonus_squares, players, bag, turn_number, consecutive_passes, history = loaded
            print(f"Resuming at turn {turn_number}.")
            input("Press Enter to continue...")

    if start != '2':
        board, bonus_squares = create_board()
        bag     = build_bag()
        players = setup_players()

        first_player = determine_first_player(players, bag)

        # Shuffle bag before each player draws so every hand is independently random
        for player in players:
            random.shuffle(bag)
            player['hand'] = deal_tiles(bag, 9)

        first_index = players.index(first_player)
        players     = players[first_index:] + players[:first_index]

        consecutive_passes = 0
        turn_number        = 1

    while True:
        for player in players:
            if player.get('skip_next'):
                clear_screen()
                print(f"\n===== Turn {turn_number} — {player['name']} =====")
                print(f"{player['name']}'s turn skipped (challenge penalty).")
                player['skip_next'] = False
                turn_number += 1
                continue

            result = take_turn(
                player, board, bonus_squares, bag,
                consecutive_passes, players, turn_number, history
            )

            # Player chose to save
            if result == 'save':
                save_game(board, bonus_squares, players, bag,
                          turn_number, consecutive_passes, history)
                input("Game saved. Press Enter to continue your turn...")
                result = take_turn(
                    player, board, bonus_squares, bag,
                    consecutive_passes, players, turn_number, history
                )

            consecutive_passes = result
            turn_number += 1

            game_over, reason = check_game_over(bag, players, consecutive_passes)
            if game_over:
                clear_screen()
                if reason == "all_passed":
                    print("\nAll players passed twice — game over!")
                else:
                    print(f"\n{reason} has used all tiles — game over!")
                display_history(history)
                end_game(players)
                if os.path.exists(SAVE_FILE):
                    os.remove(SAVE_FILE)
                return


if __name__ == "__main__":
    main()
