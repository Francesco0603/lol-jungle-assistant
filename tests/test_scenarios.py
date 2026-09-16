from app.lcu import (
    find_league_client,
    get_champion_details
)

from app.database import get_champion_strategy

from app.scoring import (
    calculate_scores,
    calculate_score_breakdown,
    sort_scores
)


# ==================================================
# CONFIGURAZIONE TEST
# ==================================================

# True  -> stampa anche tutti i dettagli dei punteggi
# False -> stampa solo il ranking
SHOW_BREAKDOWN = False


# ==================================================
# COSTRUZIONE PROFILI
# ==================================================

def build_profile(port, token, champion_id):
    """
    Costruisce un profilo identico a quello
    utilizzato durante una Champion Select reale.

    Contiene:
    - dati Riot
    - dati strategici del nostro database
    """

    details = get_champion_details(
        port,
        token,
        champion_id
    )

    if details is None:
        return None

    details["strategy"] = get_champion_strategy(
        champion_id
    )

    return details


def build_team(port, token, champion_ids):
    """
    Costruisce una squadra partendo
    da una lista di Riot ID.
    """

    profiles = []

    for champion_id in champion_ids:

        profile = build_profile(
            port,
            token,
            champion_id
        )

        if profile is not None:
            profiles.append(profile)

    return profiles


# ==================================================
# SCENARI
# ==================================================

SCENARIOS = {

    # --------------------------------------------------
    # A. TEAM SENZA VERO ENGAGE
    # --------------------------------------------------
    #
    # Lucian / Akali / Garen / Milio
    #
    # Ci aspettiamo che Amumu, Jarvan e Fiddle
    # ricevano parecchio valore.
    "A - Team senza engage": {

        "allies": [
            236,   # Lucian
            84,    # Akali
            86,    # Garen
            902    # Milio
        ],

        "enemies": [
            254,   # Vi
            106,   # Volibear
            53,    # Blitzcrank
            145,   # Kai'Sa
            99     # Lux
        ]
    },


    # --------------------------------------------------
    # B. TEAM MOLTO AD
    # --------------------------------------------------
    #
    # Darius / Yasuo / Jinx / Pyke
    #
    # Dovrebbero aumentare di valore
    # i jungler magici.
    "B - Team molto AD": {

        "allies": [
            122,   # Darius
            157,   # Yasuo
            222,   # Jinx
            555    # Pyke
        ],

        "enemies": [
            54,    # Malphite
            64,    # Lee Sin
            103,   # Ahri
            51,    # Caitlyn
            40     # Janna
        ]
    },


    # --------------------------------------------------
    # C. TEAM MOLTO AP
    # --------------------------------------------------
    #
    # Galio / Akali / Viktor / Lux
    #
    # Dovrebbero aumentare di valore
    # Graves, Lee Sin e Jarvan.
    "C - Team molto AP": {

        "allies": [
            3,     # Galio
            84,    # Akali
            112,   # Viktor
            99     # Lux
        ],

        "enemies": [
            58,    # Renekton
            19,    # Warwick
            238,   # Zed
            222,   # Jinx
            117    # Lulu
        ]
    },


    # --------------------------------------------------
    # D. NEMICI MOLTO TANKY
    # --------------------------------------------------
    #
    # Il nostro team è abbastanza equilibrato,
    # ma dall'altra parte ci sono diverse frontline.
    #
    # Ci aspettiamo che DPS alto
    # diventi particolarmente prezioso.
    "D - Nemici molto tanky": {

        "allies": [
            127,   # Lissandra
            18,    # Tristana
            43,    # Karma
            86     # Garen
        ],

        "enemies": [
            516,   # Ornn
            33,    # Rammus
            54,    # Malphite
            201,   # Braum
            145    # Kai'Sa
        ]
    },


    # --------------------------------------------------
    # E. NEMICI MOLTO SQUISHY
    # --------------------------------------------------
    #
    # Quasi nessuna frontline avversaria.
    #
    # Pick + Burst dovrebbero acquisire valore.
    "E - Nemici molto squishy": {

        "allies": [
            14,    # Sion
            61,    # Orianna
            222,   # Jinx
            201    # Braum
        ],

        "enemies": [
            7,     # LeBlanc
            81,    # Ezreal
            101,   # Xerath
            350,   # Yuumi
            238    # Zed
        ]
    }
}


# ==================================================
# CONNESSIONE A LEAGUE
# ==================================================

port, token = find_league_client()

if not port or not token:
    print("League Client NON trovato.")
    exit()


# ==================================================
# ESECUZIONE DI TUTTI GLI SCENARI
# ==================================================

for scenario_name, scenario in SCENARIOS.items():

    my_team_profiles = build_team(
        port,
        token,
        scenario["allies"]
    )

    enemy_team_profiles = build_team(
        port,
        token,
        scenario["enemies"]
    )


    scores = calculate_scores(
        my_team_profiles,
        enemy_team_profiles
    )

    ranking = sort_scores(
        scores
    )


    # ==================================================
    # OUTPUT
    # ==================================================

    print("\n")
    print("=" * 55)
    print(scenario_name)
    print("=" * 55)

    print("\nRANKING:")

    for position, (jungler, score) in enumerate(
        ranking,
        start=1
    ):

        print(
            f"{position}. {jungler:<12} {score}"
        )


    # ==================================================
    # BREAKDOWN OPZIONALE
    # ==================================================

    if SHOW_BREAKDOWN:

        print("\nBREAKDOWN:")

        for jungler, score in ranking:

            breakdown = calculate_score_breakdown(
                my_team_profiles,
                enemy_team_profiles,
                jungler
            )

            print(
                f"\n{jungler} -> {score}"
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


print("\n")
print("=" * 55)
print("TEST COMPLETATI")
print("=" * 55)