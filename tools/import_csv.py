import csv
import sqlite3


# ==================================================
# CONFIGURAZIONE
# ==================================================

from app.config import DATABASE_PATH, CSV_PATH

# Le statistiche strategiche che devono essere
# presenti per considerare un campione completo.
METRICS = [
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

def import_csv():
    """
    Legge champion_strategy.csv e aggiorna SQLite.

    Regole:
    - riga completamente vuota -> ignorata
    - riga parzialmente compilata -> segnalata
    - valori fuori da 0-5 -> segnalati
    - riga completa e valida -> importata
    """

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    imported_count = 0
    skipped_count = 0
    error_count = 0


    # ==================================================
    # LETTURA CSV
    # ==================================================

    with open(
        CSV_PATH,
        "r",
        encoding="utf-8",
        newline=""
    ) as file:

        reader = csv.DictReader(file)


        for row in reader:

            riot_id = int(row["riot_id"])
            champion_name = row["name"]


            # Recuperiamo i valori delle 9 statistiche.
            values = [
                row[metric].strip()
                for metric in METRICS
            ]


            # ==================================================
            # RIGA VUOTA
            # ==================================================
            #
            # Se tutte le statistiche sono vuote,
            # significa che il campione non è ancora
            # stato classificato.
            if all(value == "" for value in values):

                skipped_count += 1
                continue


            # ==================================================
            # RIGA PARZIALMENTE COMPILATA
            # ==================================================
            #
            # Se alcune statistiche sono compilate
            # e altre no, non importiamo il campione.
            if any(value == "" for value in values):

                print(
                    f"ERRORE: {champion_name} "
                    f"ha statistiche mancanti."
                )

                error_count += 1
                continue


            # ==================================================
            # CONVERSIONE IN NUMERI
            # ==================================================

            try:

                scores = {
                    metric: int(row[metric])
                    for metric in METRICS
                }

            except ValueError:

                print(
                    f"ERRORE: {champion_name} "
                    f"contiene un valore non numerico."
                )

                error_count += 1
                continue


            # ==================================================
            # CONTROLLO SCALA 0-5
            # ==================================================

            invalid_score = False

            for metric, score in scores.items():

                if score < 0 or score > 5:

                    print(
                        f"ERRORE: {champion_name} - "
                        f"{metric} = {score} "
                        f"(deve essere tra 0 e 5)"
                    )

                    invalid_score = True


            if invalid_score:

                error_count += 1
                continue


            # ==================================================
            # AGGIORNAMENTO DATABASE
            # ==================================================

            cursor.execute(
                """
                UPDATE champion_strategy

                SET
                    engage = ?,
                    frontline = ?,
                    peel = ?,
                    disengage = ?,
                    pick_potential = ?,
                    poke = ?,
                    dps = ?,
                    burst = ?,
                    objective_control = ?

                WHERE riot_id = ?
                """,
                (
                    scores["engage"],
                    scores["frontline"],
                    scores["peel"],
                    scores["disengage"],
                    scores["pick_potential"],
                    scores["poke"],
                    scores["dps"],
                    scores["burst"],
                    scores["objective_control"],

                    riot_id
                )
            )


            # rowcount = 1 significa che SQLite
            # ha trovato e aggiornato il campione.
            if cursor.rowcount == 1:

                imported_count += 1

            else:

                print(
                    f"ERRORE: {champion_name} "
                    f"non trovato nel database."
                )

                error_count += 1


    # ==================================================
    # SALVATAGGIO
    # ==================================================

    connection.commit()
    connection.close()


    print("\nImport completato.")
    print("Campioni aggiornati:", imported_count)
    print("Campioni ancora vuoti:", skipped_count)
    print("Errori:", error_count)

# ==================================================
# AVVIO SCRIPT
# ==================================================

if __name__ == "__main__":
    import_csv()