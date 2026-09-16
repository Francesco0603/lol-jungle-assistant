# ==================================================
# SCORING DEI JUNGLER
# ==================================================

from .analysis import (
    calculate_team_damage,
    get_team_strategy_values
)

from .database import get_champion_strategy


# ==================================================
# POOL DI JUNGLER
# ==================================================

JUNGLERS = {
    "Lee Sin": 64,
    "Amumu": 32,
    "Jarvan IV": 59,
    "Graves": 104,
    "Evelynn": 28,
    "Fiddlesticks": 9
}

# ==================================================
# CURVA DELLE METRICHE "PICCO MAX"
# ==================================================

# Il salto più importante è 3 -> 4.
#
# 4 significa che il bisogno è realmente coperto.
# 5 significa che abbiamo uno specialista eccellente.
PEAK_UTILITY = {
    0: 0,
    1: 0,
    2: 1,
    3: 4,
    4: 8,
    5: 10
}


PEAK_METRICS = [
    "engage",
    "dps",
    "peel",
    "disengage",
    "burst"
]


# ==================================================
# TARGET DI MASSA CRITICA
# ==================================================

FRONTLINE_TARGET = 9
OBJECTIVE_TARGET = 15


# ==================================================
# FUNZIONI BASE
# ==================================================

def get_best_value(
    team_profiles,
    metric
):
    """
    Restituisce il valore più alto del team
    per una determinata metrica.
    """

    values = get_team_strategy_values(
        team_profiles,
        metric
    )

    if not values:
        return 0

    return max(values)


# ==================================================
# PICCO MAX
# ==================================================

def calculate_peak_gain(
    my_team_profiles,
    jungler_strategy,
    metric
):
    """
    Calcola quanto il jungler migliora una metrica
    che dipende soprattutto dal miglior specialista
    presente nel team.
    """

    before = get_best_value(
        my_team_profiles,
        metric
    )

    jungler_value = jungler_strategy[
        metric
    ]

    after = max(
        before,
        jungler_value
    )

    return (
        PEAK_UTILITY[after]
        - PEAK_UTILITY[before]
    )


# ==================================================
# MASSA CRITICA
# ==================================================

def calculate_mass_gain(
    my_team_profiles,
    jungler_strategy,
    metric,
    target
):
    """
    Calcola quanto il jungler contribuisce
    a una metrica basata sulla somma.

    Superato il target, ulteriori punti
    non vengono premiati.
    """

    values = get_team_strategy_values(
        my_team_profiles,
        metric
    )

    before = sum(values)

    after = (
        before
        + jungler_strategy[metric]
    )

    before_capped = min(
        before,
        target
    )

    after_capped = min(
        after,
        target
    )

    return (
        after_capped
        - before_capped
    )


# ==================================================
# FRONTLINE
# ==================================================

def has_good_frontline_structure(values):
    """
    Una frontline è strutturalmente valida se:

    - abbiamo almeno un vero frontline con valore >= 4

    oppure

    - abbiamo almeno due campioni con valore >= 3
    """

    if not values:
        return False

    if max(values) >= 4:
        return True

    strong_frontliners = 0

    for value in values:

        if value >= 3:
            strong_frontliners += 1

    return strong_frontliners >= 2


def calculate_frontline_gain(
    my_team_profiles,
    jungler_strategy
):
    """
    Valuta sia la massa totale della frontline
    sia la sua struttura.
    """

    values = get_team_strategy_values(
        my_team_profiles,
        "frontline"
    )


    # ----------------------------------------------
    # MASSA CRITICA
    # ----------------------------------------------

    before_sum = sum(values)

    after_values = (
        values
        + [jungler_strategy["frontline"]]
    )

    after_sum = sum(
        after_values
    )

    mass_gain = (
        min(after_sum, FRONTLINE_TARGET)
        - min(before_sum, FRONTLINE_TARGET)
    )


    # ----------------------------------------------
    # STRUTTURA
    # ----------------------------------------------

    before_structure = has_good_frontline_structure(
        values
    )

    after_structure = has_good_frontline_structure(
        after_values
    )

    structure_gain = 0

    if (
        not before_structure
        and after_structure
    ):
        structure_gain = 3


    return (
        mass_gain
        + structure_gain
    )


# ==================================================
# SINERGIA PICK + BURST
# ==================================================

def calculate_pick_burst_gain(
    my_team_profiles,
    jungler_strategy
):
    """
    Pick e Burst lavorano insieme.

    La forza della coppia è limitata
    dalla caratteristica più debole.
    """

    before_pick = get_best_value(
        my_team_profiles,
        "pick_potential"
    )

    before_burst = get_best_value(
        my_team_profiles,
        "burst"
    )

    before_synergy = min(
        before_pick,
        before_burst
    )


    after_pick = max(
        before_pick,
        jungler_strategy["pick_potential"]
    )

    after_burst = max(
        before_burst,
        jungler_strategy["burst"]
    )

    after_synergy = min(
        after_pick,
        after_burst
    )


    return (
        PEAK_UTILITY[after_synergy]
        - PEAK_UTILITY[before_synergy]
    )

# ==================================================
# SINERGIA POKE + DISENGAGE
# ==================================================

# Questa sinergia deve pesare meno delle metriche principali.
#
# Un team con buon poke ma senza disengage
# rischia di essere semplicemente ingaggiato.
SYNERGY_UTILITY = {
    0: 0,
    1: 0,
    2: 0,
    3: 1,
    4: 2,
    5: 3
}


def calculate_poke_disengage_gain(
    my_team_profiles,
    jungler_strategy
):
    """
    Valuta la coerenza tra Poke e Disengage.

    Non vogliamo costruire necessariamente
    una composizione poke.

    Premiamo solamente il jungler se migliora
    una sinergia che il team possiede già
    o sta quasi completando.
    """

    before_poke = get_best_value(
        my_team_profiles,
        "poke"
    )

    before_disengage = get_best_value(
        my_team_profiles,
        "disengage"
    )

    # La sinergia è limitata dal lato più debole.
    before_synergy = min(
        before_poke,
        before_disengage
    )


    after_poke = max(
        before_poke,
        jungler_strategy["poke"]
    )

    after_disengage = max(
        before_disengage,
        jungler_strategy["disengage"]
    )

    after_synergy = min(
        after_poke,
        after_disengage
    )


    return (
        SYNERGY_UTILITY[after_synergy]
        - SYNERGY_UTILITY[before_synergy]
    )


# ==================================================
# BILANCIAMENTO AD / AP
# ==================================================

def calculate_damage_balance_bonus(
    my_team_profiles,
    jungler_damage_type
):
    """
    Premia leggermente il jungler che corregge
    un forte sbilanciamento AD/AP.
    """

    physical_damage, magic_damage = calculate_team_damage(
        my_team_profiles
    )


    # Team troppo magico.
    if magic_damage > physical_damage + 2:

        if jungler_damage_type == "kPhysical":
            return 5

        if jungler_damage_type == "kMagic":
            return -2


    # Team troppo fisico.
    elif physical_damage > magic_damage + 2:

        if jungler_damage_type == "kMagic":
            return 5

        if jungler_damage_type == "kPhysical":
            return -2


    return 0


# ==================================================
# ANALISI DEL TEAM NEMICO
# ==================================================

def calculate_enemy_frontline_level(
    enemy_team_profiles
):
    """
    Valuta quanta frontline possiede il team nemico.

    0 = poca
    1 = significativa
    2 = molto alta
    """

    values = get_team_strategy_values(
        enemy_team_profiles,
        "frontline"
    )

    if not values:
        return 0


    total_frontline = sum(values)

    strong_frontliners = sum(
        1
        for value in values
        if value >= 4
    )


    # Due vere frontline oppure
    # tanta massa complessiva.
    if (
        strong_frontliners >= 2
        or total_frontline >= 10
    ):
        return 2


    # Una frontline seria oppure
    # una quantità discreta complessiva.
    if (
        strong_frontliners >= 1
        or total_frontline >= 6
    ):
        return 1


    return 0


def calculate_enemy_engage_level(
    enemy_team_profiles
):
    """
    Valuta quanto è pericoloso l'engage nemico.

    0 = basso
    1 = importante
    2 = molto forte
    """

    values = get_team_strategy_values(
        enemy_team_profiles,
        "engage"
    )

    if not values:
        return 0


    best_engage = max(values)

    strong_engagers = sum(
        1
        for value in values
        if value >= 4
    )


    # Un engage eccezionale oppure
    # più fonti forti di engage.
    if (
        best_engage >= 5
        or strong_engagers >= 2
    ):
        return 2


    if best_engage >= 4:
        return 1


    return 0


def calculate_enemy_fragility_level(
    enemy_team_profiles
):
    """
    Cerca di capire se il team nemico
    presenta molti bersagli fragili.

    Per questa prima versione consideriamo
    molto fragili i campioni con frontline <= 1.
    """

    values = get_team_strategy_values(
        enemy_team_profiles,
        "frontline"
    )

    if not values:
        return 0


    squishy_count = sum(
        1
        for value in values
        if value <= 1
    )


    if squishy_count >= 4:
        return 2

    if squishy_count >= 3:
        return 1

    return 0


# ==================================================
# CONTROMISURA: FRONTLINE NEMICA
# ==================================================

def calculate_vs_frontline_bonus(
    enemy_team_profiles,
    jungler_strategy
):
    """
    Se il nemico ha molta frontline,
    premiamo il DPS sostenuto.
    """

    pressure = calculate_enemy_frontline_level(
        enemy_team_profiles
    )

    if pressure == 0:
        return 0


    dps = jungler_strategy["dps"]


    dps_value = {
        0: 0,
        1: 0,
        2: 0,
        3: 1,
        4: 2,
        5: 3
    }[dps]


    return (
        dps_value
        * pressure
    )


# ==================================================
# CONTROMISURA: ENGAGE NEMICO
# ==================================================

def calculate_anti_engage_rating(
    jungler_strategy
):
    """
    Misura quanto il jungler può aiutare
    contro un team che entra aggressivamente.

    Peel e Disengage sono le caratteristiche
    principali.

    Una vera frontline aggiunge un piccolo bonus.
    """

    rating = max(
        jungler_strategy["peel"],
        jungler_strategy["disengage"]
    )


    if jungler_strategy["frontline"] >= 4:
        rating += 1


    return min(
        rating,
        5
    )


def calculate_vs_engage_bonus(
    enemy_team_profiles,
    jungler_strategy
):
    """
    Premia i jungler capaci di reggere,
    proteggere o interrompere un engage nemico.
    """

    pressure = calculate_enemy_engage_level(
        enemy_team_profiles
    )

    if pressure == 0:
        return 0


    rating = calculate_anti_engage_rating(
        jungler_strategy
    )


    base_bonus = {
        0: 0,
        1: 0,
        2: 1,
        3: 2,
        4: 3,
        5: 4
    }[rating]


    # Engage nemico importante.
    if pressure == 1:
        return base_bonus


    # Engage nemico molto forte.
    #
    # Aumentiamo il peso, ma mettiamo un tetto
    # perché il team nemico deve restare
    # un fattore secondario rispetto ai nostri bisogni.
    return min(
        base_bonus + 2,
        6
    )


# ==================================================
# CONTROMISURA: TEAM NEMICO FRAGILE
# ==================================================

def calculate_vs_squishy_bonus(
    enemy_team_profiles,
    jungler_strategy
):
    """
    Contro molti bersagli fragili aumentano di valore
    i jungler capaci di trovare un target e burstarlo.
    """

    fragility = calculate_enemy_fragility_level(
        enemy_team_profiles
    )

    if fragility == 0:
        return 0


    assassination_power = min(
        jungler_strategy["pick_potential"],
        jungler_strategy["burst"]
    )


    base_bonus = {
        0: 0,
        1: 0,
        2: 1,
        3: 2,
        4: 3,
        5: 4
    }[assassination_power]


    if fragility == 1:
        return base_bonus


    return min(
        base_bonus + 1,
        5
    )


# ==================================================
# SCORING PRINCIPALE
# ==================================================

def calculate_scores(
    my_team_profiles,
    enemy_team_profiles
):
    """
    Valuta ogni jungler in due fasi:

    1. Quanto completa il nostro team.
    2. Quanto è adatto contro il team nemico.

    Il primo fattore rimane il più importante.
    """

    scores = {}


    for jungler_name, riot_id in JUNGLERS.items():

        score = 50


        # ==============================================
        # DATI DEL JUNGLER
        # ==============================================

        jungler_strategy = get_champion_strategy(
            riot_id
        )

        if jungler_strategy is None:

            scores[jungler_name] = score
            continue


        # ==============================================
        # A. COMPLETAMENTO DEL NOSTRO TEAM
        # ==============================================

        # Picchi.
        for metric in PEAK_METRICS:

            score += calculate_peak_gain(
                my_team_profiles,
                jungler_strategy,
                metric
            )


        # Frontline.
        score += calculate_frontline_gain(
            my_team_profiles,
            jungler_strategy
        )


        # Objective Control.
        score += calculate_mass_gain(
            my_team_profiles,
            jungler_strategy,
            "objective_control",
            OBJECTIVE_TARGET
        )


        # Pick + Burst.
        score += calculate_pick_burst_gain(
            my_team_profiles,
            jungler_strategy
        )

        # Poke + Disengage.
        score += calculate_poke_disengage_gain(
            my_team_profiles,
            jungler_strategy
        )


        # AD / AP.
        score += calculate_damage_balance_bonus(
            my_team_profiles,
            jungler_strategy["damage_type"]
        )


        # ==============================================
        # B. ADATTAMENTO AL TEAM NEMICO
        # ==============================================

        # Molta frontline nemica -> DPS.
        score += calculate_vs_frontline_bonus(
            enemy_team_profiles,
            jungler_strategy
        )


        # Molto engage nemico -> difesa / peel / disengage.
        score += calculate_vs_engage_bonus(
            enemy_team_profiles,
            jungler_strategy
        )


        # Molti squishy -> Pick + Burst.
        score += calculate_vs_squishy_bonus(
            enemy_team_profiles,
            jungler_strategy
        )


        scores[jungler_name] = score


    return scores


# ==================================================
# BREAKDOWN DEL PUNTEGGIO
# ==================================================

def calculate_score_breakdown(
    my_team_profiles,
    enemy_team_profiles,
    jungler_name
):
    """
    Restituisce la spiegazione completa
    del punteggio di un jungler.

    Viene utilizzata solamente in DEBUG_MODE.
    """

    riot_id = JUNGLERS[
        jungler_name
    ]

    jungler_strategy = get_champion_strategy(
        riot_id
    )

    if jungler_strategy is None:
        return None


    breakdown = {
        "base": 50
    }


    # ==============================================
    # NOSTRO TEAM
    # ==============================================

    for metric in PEAK_METRICS:

        breakdown[metric] = calculate_peak_gain(
            my_team_profiles,
            jungler_strategy,
            metric
        )


    breakdown["frontline"] = calculate_frontline_gain(
        my_team_profiles,
        jungler_strategy
    )


    breakdown["objective_control"] = calculate_mass_gain(
        my_team_profiles,
        jungler_strategy,
        "objective_control",
        OBJECTIVE_TARGET
    )


    breakdown["pick_burst"] = calculate_pick_burst_gain(
        my_team_profiles,
        jungler_strategy
    )

    breakdown["poke_disengage"] = calculate_poke_disengage_gain(
        my_team_profiles,
        jungler_strategy
    )

    breakdown["damage_balance"] = calculate_damage_balance_bonus(
        my_team_profiles,
        jungler_strategy["damage_type"]
    )


    # ==============================================
    # TEAM NEMICO
    # ==============================================

    breakdown["vs_enemy_frontline"] = calculate_vs_frontline_bonus(
        enemy_team_profiles,
        jungler_strategy
    )


    breakdown["vs_enemy_engage"] = calculate_vs_engage_bonus(
        enemy_team_profiles,
        jungler_strategy
    )


    breakdown["vs_enemy_squishy"] = calculate_vs_squishy_bonus(
        enemy_team_profiles,
        jungler_strategy
    )


    return breakdown


# ==================================================
# ORDINAMENTO
# ==================================================

def sort_scores(scores):
    """
    Ordina i jungler dal punteggio più alto
    al più basso.
    """

    return sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True
    )