def build_draft(session, champion_names):
    """
    Trasforma i dati grezzi della Champion Select
    in una struttura più semplice da usare.

    Restituisce:
        - il nostro giocatore
        - i 4 alleati
        - i nemici
    """

    local_player_cell_id = session["localPlayerCellId"]

    draft = {
        "local_player": None,
        "allies": [],
        "enemies": []
    }


    # ==================================================
    # NOSTRO TEAM
    # ==================================================

    for player in session["myTeam"]:

        champion_id = player["championId"]
        cell_id = player["cellId"]

        champion = {
            "cell_id": cell_id,
            "champion_id": champion_id,
            "name": get_champion_name(
                champion_id,
                champion_names
            )
        }

        # Il giocatore locale viene tenuto separato
        # dagli altri quattro alleati.
        if cell_id == local_player_cell_id:
            draft["local_player"] = champion
        else:
            draft["allies"].append(champion)


    # ==================================================
    # TEAM NEMICO
    # ==================================================

    for player in session["theirTeam"]:

        champion_id = player["championId"]

        champion = {
            "cell_id": player["cellId"],
            "champion_id": champion_id,
            "name": get_champion_name(
                champion_id,
                champion_names
            )
        }

        draft["enemies"].append(champion)


    return draft


def get_champion_name(champion_id, champion_names):
    """
    Converte un Riot ID nel nome del campione.

    champion_id == 0 significa che il giocatore
    non ha ancora selezionato un campione.
    """

    if champion_id == 0:
        return "Non selezionato"

    return champion_names.get(
        champion_id,
        f"ID sconosciuto: {champion_id}"
    )


def get_draft_signature(session):
    """
    Crea una rappresentazione compatta della draft.

    Serve per capire se qualcuno ha cambiato pick
    senza dover ristampare continuamente gli stessi dati.
    """

    my_team_ids = tuple(
        player["championId"]
        for player in session["myTeam"]
    )

    enemy_team_ids = tuple(
        player["championId"]
        for player in session["theirTeam"]
    )

    return (
        my_team_ids,
        enemy_team_ids
    )