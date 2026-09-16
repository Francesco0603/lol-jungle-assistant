import sqlite3

from .config import DATABASE_PATH


def get_champion_strategy(riot_id):
    """
    Restituisce il profilo completo di un campione
    cercandolo tramite Riot ID.

    Comprende:

    - metadati Riot
    - metriche strategiche 0-5
    """

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT
            riot_id,
            name,
            damage_type,
            engage,
            frontline,
            peel,
            disengage,
            pick_potential,
            poke,
            dps,
            burst,
            objective_control

        FROM champion_strategy

        WHERE riot_id = ?
        """,
        (riot_id,)
    )


    row = cursor.fetchone()

    connection.close()


    if row is None:
        return None


    return dict(row)

def validate_database():
    """
    Controlla che il database necessario all'app
    esista e contenga tutti i dati richiesti.

    Restituisce:
        (True, messaggio)  se tutto è corretto
        (False, messaggio) se esiste un problema
    """

    # ==================================================
    # FILE DATABASE
    # ==================================================

    if not DATABASE_PATH.exists():
        return (
            False,
            f"Database non trovato: {DATABASE_PATH}"
        )


    try:

        connection = sqlite3.connect(
            DATABASE_PATH
        )

        cursor = connection.cursor()


        # ==================================================
        # TABELLA
        # ==================================================

        cursor.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'champion_strategy'
            """
        )

        if cursor.fetchone() is None:

            connection.close()

            return (
                False,
                "Tabella champion_strategy non trovata."
            )


        # ==================================================
        # NUMERO CAMPIONI
        # ==================================================

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM champion_strategy
            """
        )

        champion_count = cursor.fetchone()[0]


        if champion_count == 0:

            connection.close()

            return (
                False,
                "Il database non contiene campioni."
            )


        # ==================================================
        # DATI MANCANTI
        # ==================================================

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM champion_strategy

            WHERE
                damage_type IS NULL
                OR engage IS NULL
                OR frontline IS NULL
                OR peel IS NULL
                OR disengage IS NULL
                OR pick_potential IS NULL
                OR poke IS NULL
                OR dps IS NULL
                OR burst IS NULL
                OR objective_control IS NULL
            """
        )

        incomplete_count = cursor.fetchone()[0]

        connection.close()


        if incomplete_count > 0:

            return (
                False,
                (
                    f"{incomplete_count} campioni "
                    "hanno dati strategici incompleti."
                )
            )


        return (
            True,
            (
                f"Database valido: "
                f"{champion_count} campioni."
            )
        )


    except sqlite3.Error as error:

        return (
            False,
            f"Errore SQLite: {error}"
        )