def print_draft(draft):
    """
    Stampa la situazione corrente della draft.
    """

    print("\n\n==============================")
    print("         DRAFT CAMBIATA")
    print("==============================")


    # ==================================================
    # TU
    # ==================================================

    print("\n--- TU ---")

    local_player = draft["local_player"]

    if local_player is not None:
        print(
            f"ID {local_player['champion_id']} "
            f"-> {local_player['name']} [TU]"
        )


    # ==================================================
    # ALLEATI
    # ==================================================

    print("\n--- MIO TEAM ---")

    for champion in draft["allies"]:
        print(
            f"ID {champion['champion_id']} "
            f"-> {champion['name']}"
        )


    # ==================================================
    # NEMICI
    # ==================================================

    print("\n--- TEAM NEMICO ---")

    for champion in draft["enemies"]:
        print(
            f"ID {champion['champion_id']} "
            f"-> {champion['name']}"
        )

def print_team_profile(
    physical_damage,
    magic_damage,
    crowd_control,
    durability,
    engage
):
    """
    Stampa il profilo generale del team.
    """

    print("\n--- PROFILO TEAM ---")

    print("Fisico:", physical_damage)
    print("Magico:", magic_damage)
    print("CC:", crowd_control)
    print("Durabilità:", durability)
    print("Engage:", engage)

def print_champion_engage(
    profiles,
    calculate_champion_engage
):
    """
    Stampa l'engage calcolato per ogni alleato.

    Questa è ancora una stampa di debug:
    più avanti probabilmente la elimineremo.
    """

    print("\n--- ENGAGE PER CAMPIONE ---")

    for champion in profiles:

        champion_name = champion.get(
            "name",
            "Sconosciuto"
        )

        engage = calculate_champion_engage(
            champion
        )

        print(
            f"{champion_name}: {engage}"
        )

def print_playstyle(profiles):
    """
    Stampa i dati playstyle originali Riot.

    Anche questa è una stampa temporanea di debug.
    """

    print("\n--- DATI PLAYSTYLE ALLEATI ---")

    for champion in profiles:

        champion_name = champion.get(
            "name",
            "Sconosciuto"
        )

        playstyle = champion.get(
            "playstyleInfo",
            {}
        )

        print(
            champion_name,
            "->",
            playstyle
        )

def print_ranking(ranking):
    """
    Stampa la classifica dei jungler consigliati.
    """

    print("\n--- CONSIGLI JUNGLE ---")

    for position, (jungler, score) in enumerate(
        ranking,
        start=1
    ):
        print(
            f"{position}. {jungler}: {score}"
        )

    print("==============================")

def print_score_breakdown(
    ranking,
    my_team_profiles,
    enemy_team_profiles,
    calculate_score_breakdown
):
    """
    Stampa il dettaglio del punteggio
    assegnato a ogni jungler.

    Usata solo durante lo sviluppo.
    """

    print("\n--- DETTAGLIO PUNTEGGI ---")


    for jungler, total_score in ranking:

        breakdown = calculate_score_breakdown(
            my_team_profiles,
            enemy_team_profiles,
            jungler
        )

        if breakdown is None:
            continue


        print(
            f"\n{jungler} -> {total_score}"
        )


        for metric, value in breakdown.items():

            if metric != "base" and value == 0:
                continue


            sign = ""

            if metric != "base" and value > 0:
                sign = "+"


            print(
                f"  {metric}: {sign}{value}"
            )

def print_live_result(draft, ranking):
    """
    Output compatto pensato per l'uso reale
    durante la Champion Select.
    """

    allies = [
        champion["name"]
        for champion in draft["allies"]
        if champion["champion_id"] != 0
    ]

    enemies = [
        champion["name"]
        for champion in draft["enemies"]
        if champion["champion_id"] != 0
    ]


    print("\n\n========================================")
    print("           JUNGLE ASSISTANT")
    print("========================================")

    print(
        "ALLY:  "
        + " | ".join(allies)
    )

    print(
        "ENEMY: "
        + " | ".join(enemies)
    )

    print("\n--- CONSIGLIO ---")

    for position, (jungler, score) in enumerate(
        ranking,
        start=1
    ):
        print(
            f"{position}. {jungler:<12} {score}"
        )

    print("========================================")