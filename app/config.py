from pathlib import Path


# ==================================================
# PERCORSI DEL PROGETTO
# ==================================================

# __file__ punta a:
#
# PythonProject/app/config.py
#
# .parent        -> PythonProject/app
# .parent.parent -> PythonProject
BASE_DIR = Path(__file__).resolve().parent.parent


# Cartella dei dati.
DATA_DIR = BASE_DIR / "data"


# Database SQLite.
DATABASE_PATH = DATA_DIR / "lol_draft.db"


# CSV con i valori strategici.
CSV_PATH = DATA_DIR / "champion_strategy.csv"