import sqlite3

from app.config import DATABASE_PATH

from app.lcu import (
    find_league_client,
    load_champions,
    get_champion_details
)


def create_database():
    """
    Crea la tabella champion_strategy se non esiste.

    Se il database esiste già ma manca damage_type,
    aggiorna automaticamente lo schema.
    """

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS champion_strategy (

            riot_id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,

            damage_type TEXT,

            engage INTEGER,
            frontline INTEGER,
            peel INTEGER,
            disengage INTEGER,
            pick_potential INTEGER,
            poke INTEGER,
            dps INTEGER,
            burst INTEGER,
            objective_control INTEGER
        )
        """
    )


    # ==================================================
    # MIGRAZIONE DEL VECCHIO DATABASE
    # ==================================================

    # CREATE TABLE IF NOT EXISTS non aggiunge nuove colonne
    # a una tabella già esistente.
    #
    # Quindi controlliamo esplicitamente
    # se damage_type esiste già.
    cursor.execute(
        """
        PRAGMA table_info(champion_strategy)
        """
    )

    columns = {
        row[1]
        for row in cursor.fetchall()
    }

    if "damage_type" not in columns:

        cursor.execute(
            """
            ALTER TABLE champion_strategy
            ADD COLUMN damage_type TEXT
            """
        )

        print("Colonna damage_type aggiunta al database.")


    connection.commit()
    connection.close()


def import_champions():
    """
    Sincronizza i metadati dei campioni con League.

    Importiamo automaticamente:

    - Riot ID
    - nome
    - damage_type

    Le nostre statistiche strategiche 0-5
    NON vengono modificate.
    """

    port, token = find_league_client()

    if not port or not token:
        print("League Client NON trovato.")
        return


    champions = load_champions(
        port,
        token
    )


    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()


    # Eliminiamo eventuali vecchie voci tecniche.
    cursor.execute(
        """
        DELETE FROM champion_strategy
        WHERE riot_id <= 0 OR name = 'None'
        """
    )


    updated = 0
    missing_damage_type = 0


    for riot_id, champion_name in champions.items():

        if riot_id <= 0 or champion_name == "None":
            continue


        # ==============================================
        # RECUPERIAMO IL TIPO DI DANNO DA RIOT
        # ==============================================

        details = get_champion_details(
            port,
            token,
            riot_id
        )

        damage_type = None

        if details is not None:

            tactical_info = details.get(
                "tacticalInfo",
                {}
            )

            damage_type = tactical_info.get(
                "damageType"
            )


        if damage_type is None:
            missing_damage_type += 1


        # ==============================================
        # INSERIMENTO DEL CAMPIONE
        # ==============================================

        # Se il campione è nuovo lo inseriamo.
        cursor.execute(
            """
            INSERT OR IGNORE INTO champion_strategy (
                riot_id,
                name,
                damage_type
            )
            VALUES (?, ?, ?)
            """,
            (
                riot_id,
                champion_name,
                damage_type
            )
        )


        # Se esiste già aggiorniamo SOLO
        # i metadati Riot.
        #
        # Engage, frontline, peel ecc.
        # restano completamente intatti.
        cursor.execute(
            """
            UPDATE champion_strategy

            SET
                name = ?,
                damage_type = ?

            WHERE riot_id = ?
            """,
            (
                champion_name,
                damage_type,
                riot_id
            )
        )

        # Incrementiamo il contatore solo se
        # è stata realmente trovata una riga nel database.
        if cursor.rowcount > 0:
            updated += 1


    connection.commit()


    cursor.execute(
        """
        SELECT COUNT(*)
        FROM champion_strategy
        """
    )

    champion_count = cursor.fetchone()[0]


    connection.close()


    print()
    print("Sincronizzazione completata.")
    print("Campioni presenti:", champion_count)
    print("Metadati aggiornati:", updated)
    print("Damage type mancanti:", missing_damage_type)


if __name__ == "__main__":

    create_database()
    import_champions()