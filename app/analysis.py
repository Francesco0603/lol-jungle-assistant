# ==================================================
# ANALISI DEI CAMPIONI E DEL TEAM
# ==================================================

from .lcu import get_champion_details
from .database import get_champion_strategy

def get_champion_profiles(champions, port, token):
    """
    Recupera i dati Riot e strategici
    di una lista di campioni della draft.
    """

    profiles = []

    for champion in champions:

        champion_id = champion["champion_id"]

        # ID 0 = campione non ancora selezionato.
        if champion_id == 0:
            continue

        # Dati Riot.
        details = get_champion_details(
            port,
            token,
            champion_id
        )

        if details is None:
            continue

        # Nostri dati strategici.
        strategy = get_champion_strategy(
            champion_id
        )

        details["strategy"] = strategy

        profiles.append(details)

    return profiles

def get_ally_profiles(draft, port, token):
    """
    Restituisce i profili dei quattro alleati.
    """

    return get_champion_profiles(
        draft["allies"],
        port,
        token
    )

def get_enemy_profiles(draft, port, token):
    """
    Restituisce i profili dei campioni nemici.
    """

    return get_champion_profiles(
        draft["enemies"],
        port,
        token
    )

def calculate_team_damage(my_team_profiles):
    """
    Calcola quanto peso di danno fisico e magico
    è già presente nella nostra squadra.

    Per ora continuiamo a usare i dati Riot
    per questa informazione.
    """

    physical_damage = 0
    magic_damage = 0

    for champion in my_team_profiles:

        damage_type = champion["tacticalInfo"]["damageType"]
        damage_value = champion["playstyleInfo"]["damage"]

        if damage_type == "kPhysical":
            physical_damage += damage_value

        elif damage_type == "kMagic":
            magic_damage += damage_value

        elif damage_type == "kMixed":
            physical_damage += damage_value / 2
            magic_damage += damage_value / 2

    return physical_damage, magic_damage

def calculate_team_utility(my_team_profiles):
    """
    Calcola per ora:

    - crowd control
    - durability

    utilizzando i dati Riot.
    """

    crowd_control = 0
    durability = 0

    for champion in my_team_profiles:

        playstyle = champion.get(
            "playstyleInfo",
            {}
        )

        crowd_control += playstyle.get(
            "crowdControl",
            0
        )

        durability += playstyle.get(
            "durability",
            0
        )

    return crowd_control, durability

def calculate_champion_engage(champion):
    """
    Restituisce l'engage strategico del campione
    leggendo il valore dal nostro database SQLite.
    """

    strategy = champion.get(
        "strategy"
    )

    # Caso di sicurezza:
    # se per qualche motivo il database non ha restituito
    # il profilo del campione, consideriamo engage 0.
    if strategy is None:
        return 0

    return strategy["engage"]

def calculate_team_engage(my_team_profiles):
    """
    Restituisce il miglior engage presente nel team.
    """

    return get_best_team_strategy(
        my_team_profiles,
        "engage"
    )

def get_team_strategy_values(my_team_profiles, metric):
    """
    Restituisce i valori di una determinata metrica
    strategica per tutti gli alleati selezionati.

    Esempio:

        get_team_strategy_values(
            my_team_profiles,
            "frontline"
        )

    potrebbe restituire:

        [4, 0, 4, 0]
    """

    values = []

    for champion in my_team_profiles:

        strategy = champion.get(
            "strategy"
        )

        # Se per qualche motivo il campione
        # non ha dati strategici, lo ignoriamo.
        if strategy is None:
            continue

        value = strategy.get(
            metric,
            0
        )

        values.append(
            value
        )

    return values

def get_best_team_strategy(my_team_profiles, metric):
    """
    Restituisce il valore più alto presente nel team
    per una determinata metrica.

    Utile per caratteristiche dove ci interessa sapere
    se almeno un campione è molto forte in quell'aspetto.
    """

    values = get_team_strategy_values(
        my_team_profiles,
        metric
    )

    if not values:
        return 0

    return max(values)

def get_team_strategy_summary(my_team_profiles):
    """
    Costruisce un riepilogo completo delle metriche
    strategiche degli alleati.

    Per ogni metrica conserva i valori dei singoli campioni.
    """

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

    summary = {}

    for metric in metrics:

        values = get_team_strategy_values(
            my_team_profiles,
            metric
        )

        # Ordiniamo dal valore più alto al più basso.
        values.sort(
            reverse=True
        )

        summary[metric] = values

    return summary