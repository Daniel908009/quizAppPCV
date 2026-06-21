from pathlib import Path

APP_TITLE = "Guessing Game"
TIMER_SECONDS = 120
SECRET_KEY = "quiz-app-secret-v1"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

CATEGORY_FILES = {
    "Famous IT People": "famous_people.json",
    "IT Companies": "it_companies.json",
}
