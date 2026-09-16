import csv
import os
import sqlite3


# ==================================================
# CONFIGURAZIONE
# ==================================================

from app.config import DATABASE_PATH, CSV_PATH

# ==================================================
# COLONNE DEL NOSTRO DATASET
# ==================================================

COLUMNS = [
    "riot_id",
    "name",
    "engage",
    "frontline",
    "peel",
    "disengage",
    "pick_potential",
    "poke",
    "dps",
    "burst",
    "objective_control"
]


def export_csv():
    """
    Crea il CSV con tutti i campioni presenti
    nel database.

    riot_id e name vengono compilati automaticamente.

    Tutte le statistiche strategiche vengono invece
    lasciate vuote, perché le compileremo dopo.
    """

    # --------------------------------------------------
    # SICUREZZA
    # --------------------------------------------------
    #
    # Se il CSV esiste già NON lo sovrascriviamo.
    #
    # Questo sarà importante quando avremo passato tempo
    # a compilare i valori dei campioni.
    if os.path.exists(CSV_PATH):

        print(
            f"Il file {CSV_PATH} esiste già."
        )

        print(
            "Non è stato sovrascritto."
        )

        return


    # --------------------------------------------------
    # LETTURA DAL DATABASE
    # --------------------------------------------------

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()


    # Recuperiamo ID e nome dei campioni.
    #
    # ORDER BY name li mette in ordine alfabetico,
    # più comodo quando lavoreremo sul CSV.
    cursor.execute("""
        SELECT riot_id, name
        FROM champion_strategy
        ORDER BY name
    """)

    champions = cursor.fetchall()

    connection.close()


    # --------------------------------------------------
    # CREAZIONE CSV
    # --------------------------------------------------

    with open(
        CSV_PATH,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=COLUMNS
        )

        # Prima riga:
        #
        # riot_id,name,engage,frontline,...
        writer.writeheader()


        # Una riga per ogni campione.
        for riot_id, champion_name in champions:

            # Creiamo tutte le colonne vuote.
            row = {
                column: ""
                for column in COLUMNS
            }


            # ID e nome invece li conosciamo già.
            row["riot_id"] = riot_id
            row["name"] = champion_name


            writer.writerow(row)


    print(
        f"CSV creato correttamente: {CSV_PATH}"
    )

    print(
        f"Campioni esportati: {len(champions)}"
    )


# ==================================================
# AVVIO SCRIPT
# ==================================================

if __name__ == "__main__":
    export_csv()