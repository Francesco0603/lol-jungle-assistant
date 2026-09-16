import time

# ==================================================
# LEAGUE CLIENT
# ==================================================

from app.lcu import (
    find_league_client,
    get_game_phase,
    get_champ_select,
    load_champions
)


# ==================================================
# DRAFT
# ==================================================

from app.draft import (
    build_draft,
    get_draft_signature
)


# ==================================================
# ANALISI
# ==================================================

from app.analysis import (
    get_ally_profiles,
    get_enemy_profiles,
    calculate_team_damage,
    calculate_team_utility,
    calculate_team_engage,
    calculate_champion_engage,
    get_best_team_strategy,
    get_team_strategy_summary
)


# ==================================================
# SCORING
# ==================================================

from app.scoring import (
    calculate_scores,
    calculate_score_breakdown,
    sort_scores
)


# ==================================================
# DATABASE
# ==================================================

from app.database import (
    validate_database
)


# ==================================================
# DISPLAY
# ==================================================

from app.display import (
    print_draft,
    print_team_profile,
    print_champion_engage,
    print_playstyle,
    print_score_breakdown,
    print_live_result
)


# ==================================================
# CONFIGURAZIONE
# ==================================================

# True:
# mostra tutti i dati utili allo sviluppo.
#
# False:
# mostra solamente l'output compatto
# pensato per l'uso durante le ranked.
DEBUG_MODE = True


# ==================================================
# PROGRAMMA PRINCIPALE
# ==================================================

def main():

    # ==================================================
    # 1. CONTROLLO DATABASE
    # ==================================================

    database_ok, database_message = validate_database()

    if not database_ok:

        print("\nERRORE DATABASE")
        print(database_message)

        print(
            "\nEsegui gli strumenti di inizializzazione "
            "e import prima di avviare Jungle Assistant."
        )

        return


    if DEBUG_MODE:
        print(database_message)


    # ==================================================
    # 2. STATO DELLA CONNESSIONE
    # ==================================================

    # League potrebbe non essere ancora aperto.
    port = None
    token = None

    # Dizionario Riot ID -> nome campione.
    champions = {}

    # Ultima draft analizzata.
    last_draft = None


    # ==================================================
    # 3. CICLO PRINCIPALE
    # ==================================================

    while True:

        # ==================================================
        # CONNESSIONE / RICONNESSIONE A LEAGUE
        # ==================================================

        if not port or not token:

            port, token = find_league_client()


            # League non è ancora aperto.
            if not port or not token:

                print(
                    "\rLeague Client non trovato - "
                    "Aspetto l'avvio di League...     ",
                    end=""
                )

                time.sleep(2)
                continue


            # Il processo esiste, ma vogliamo verificare
            # che l'API locale sia già pronta.
            champions = load_champions(
                port,
                token
            )


            if not champions:

                print(
                    "\rLeague Client in avvio...     ",
                    end=""
                )

                port = None
                token = None

                time.sleep(1)
                continue


            print("\nLeague Client trovato!")

            if DEBUG_MODE:
                print("Porta:", port)

            print("Campioni caricati.")
            print("Aspetto una Champion Select...\n")


        # ==================================================
        # 4. GAME PHASE
        # ==================================================

        phase = get_game_phase(
            port,
            token
        )


        # ==================================================
        # CONNESSIONE PERSA
        # ==================================================

        if phase is None:

            print(
                "\rConnessione con League persa - "
                "tentativo di riconnessione...     ",
                end=""
            )

            # Le vecchie credenziali potrebbero
            # non essere più valide.
            port = None
            token = None

            champions = {}
            last_draft = None

            time.sleep(1)
            continue


        # ==================================================
        # NON SIAMO IN CHAMPION SELECT
        # ==================================================

        if phase != "ChampSelect":

            # Quando inizierà una nuova draft
            # dovrà essere analizzata da zero.
            last_draft = None

            print(
                f"\rStato: {phase} - "
                "Aspetto Champion Select...     ",
                end=""
            )

            time.sleep(1)
            continue


        # ==================================================
        # 5. CHAMPION SELECT
        # ==================================================

        session = get_champ_select(
            port,
            token
        )


        # La sessione potrebbe non essere disponibile
        # per qualche istante durante le transizioni.
        if session is None:

            time.sleep(0.5)
            continue


        # ==================================================
        # 6. CONTROLLO CAMBIAMENTI DELLA DRAFT
        # ==================================================

        current_draft = get_draft_signature(
            session
        )


        # Se nessuno ha cambiato pick,
        # non serve ricalcolare tutto.
        if current_draft == last_draft:

            time.sleep(0.5)
            continue


        last_draft = current_draft


        # ==================================================
        # 7. COSTRUZIONE DELLA DRAFT
        # ==================================================

        draft = build_draft(
            session,
            champions
        )


        # ==================================================
        # 8. PROFILI DEI CAMPIONI
        # ==================================================

        my_team_profiles = get_ally_profiles(
            draft,
            port,
            token
        )

        enemy_team_profiles = get_enemy_profiles(
            draft,
            port,
            token
        )


        # ==================================================
        # 9. SCORING
        # ==================================================

        scores = calculate_scores(
            my_team_profiles,
            enemy_team_profiles
        )

        ranking = sort_scores(
            scores
        )


        # ==================================================
        # 10. DEBUG
        # ==================================================

        if DEBUG_MODE:

            print_draft(
                draft
            )


            # ----------------------------------------------
            # DATI RIOT
            # ----------------------------------------------

            physical_damage, magic_damage = calculate_team_damage(
                my_team_profiles
            )

            crowd_control, durability = calculate_team_utility(
                my_team_profiles
            )

            engage = calculate_team_engage(
                my_team_profiles
            )


            print_team_profile(
                physical_damage,
                magic_damage,
                crowd_control,
                durability,
                engage
            )


            # ----------------------------------------------
            # MIGLIOR VALORE PER METRICA
            # ----------------------------------------------

            print("\n--- PROFILO STRATEGICO ---")

            metrics = [
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


            for metric in metrics:

                value = get_best_team_strategy(
                    my_team_profiles,
                    metric
                )

                print(
                    f"{metric}: {value}"
                )


            # ----------------------------------------------
            # VALORI COMPLETI DEL TEAM
            # ----------------------------------------------

            team_strategy = get_team_strategy_summary(
                my_team_profiles
            )

            print(
                "\n--- VALORI STRATEGICI COMPLETI ---"
            )


            for metric, values in team_strategy.items():

                print(
                    f"{metric}: {values}"
                )


            # ----------------------------------------------
            # ENGAGE PER CAMPIONE
            # ----------------------------------------------

            print_champion_engage(
                my_team_profiles,
                calculate_champion_engage
            )


            # ----------------------------------------------
            # PLAYSTYLE RIOT
            # ----------------------------------------------

            print_playstyle(
                my_team_profiles
            )


            # ----------------------------------------------
            # BREAKDOWN SCORING
            # ----------------------------------------------

            print_score_breakdown(
                ranking,
                my_team_profiles,
                enemy_team_profiles,
                calculate_score_breakdown
            )


        # ==================================================
        # 11. OUTPUT DA RANKED
        # ==================================================

        print_live_result(
            draft,
            ranking
        )


        # ==================================================
        # 12. POLLING
        # ==================================================

        time.sleep(0.5)


# ==================================================
# AVVIO
# ==================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print(
            "\n\nJungle Assistant chiuso."
        )