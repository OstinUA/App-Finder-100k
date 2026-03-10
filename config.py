DB_PATH = "seen_apps.db"

SEARCH_LOCALES = [
    ("ru", "ru"),
    ("en", "us"),
    ("en", "gb"),
    ("de", "de"),
    ("fr", "fr"),
    ("uk", "ua"),
    ("pl", "pl"),
    ("tr", "tr"),
]

GAME_KEYWORDS = [
    "action", "adventure", "arcade", "puzzle", "racing",
    "role playing", "simulation", "sports", "strategy", "trivia",
    "word", "horror", "survival", "shooter", "tower defense",
    "roguelike", "dungeon", "visual novel", "platformer", "escape room",
    "chess", "mahjong", "card game", "board game", "fighting",
    "idle game", "clicker", "match 3", "runner", "driving",
    "open world", "crafting", "building", "farming", "city builder",
    "quiz", "crossword", "sudoku", "solitaire", "slots",
    "music game", "rhythm", "dance", "karaoke",
]

NICHE_KEYWORDS = [
    "turn based tactics", "soulslike", "deckbuilder", "tactical rpg",
    "incremental game", "metroidvania", "immersive sim",
    "survival horror indie", "point and click adventure", "narrative puzzle",
    "asymmetric multiplayer", "hidden gems", "minimalist puzzle",
    "retro pixel rpg", "party game local", "walking simulator",
    "interactive fiction", "text adventure", "rogue lite",
    "auto battler", "autochess", "moba", "battle royale",
    "extraction shooter", "base building", "colony sim",
    "4x strategy", "grand strategy", "wargame", "hex tactics",
]

UTILITY_KEYWORDS = [
    "productivity", "notes", "todo list", "habit tracker",
    "meditation", "sleep sounds", "focus timer", "pomodoro",
    "language learning", "flashcards", "drawing", "pixel art editor",
    "music maker", "beat maker", "dj app", "guitar tuner",
    "astronomy", "star map", "weather", "fitness tracker",
    "workout", "yoga", "running tracker", "cycling",
    "recipe", "cooking", "nutrition", "calorie counter",
    "finance tracker", "budget", "expense tracker",
    "photo editor", "video editor", "collage maker",
    "barcode scanner", "qr code", "file manager", "calculator",
]

ALL_KEYWORDS = NICHE_KEYWORDS * 3 + GAME_KEYWORDS * 2 + UTILITY_KEYWORDS

DEFAULT_MIN_INSTALLS = 10_000
DEFAULT_MAX_INSTALLS = 0
DEFAULT_RESULTS_LIMIT = 30
DEFAULT_SEARCH_DEPTH = 140
DEFAULT_QUERIES_PER_RUN = 6
DEFAULT_WORKERS = 20

NICHE_GENRES = {
    "Word", "Trivia", "Music", "Board", "Card", "Educational",
    "Adventure", "Simulation", "Strategy", "Role Playing",
    "Puzzle", "Racing", "Sports", "Casual",
}

CACHE_TTL_SEARCH = 60 * 60 * 6
CACHE_TTL_DETAILS = 60 * 60 * 12
