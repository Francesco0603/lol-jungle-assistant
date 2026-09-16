import psutil
import requests
import urllib3


# ==================================================
# CONFIGURAZIONE HTTPS LOCALE
# ==================================================

# Il client di League utilizza HTTPS locale
# con un certificato autofirmato.
#
# Comunichiamo solamente con 127.0.0.1,
# quindi disabilitiamo questo warning specifico.
urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)


# ==================================================
# RICERCA DEL CLIENT
# ==================================================

def find_league_client():
    """
    Cerca il processo LeagueClientUx.exe
    e recupera:

    - porta locale
    - token di autenticazione

    Restituisce:
        (port, token)

    Se League non è aperto:
        (None, None)
    """

    for process in psutil.process_iter(
        ["name", "cmdline"]
    ):

        try:

            name = process.info["name"]

            if (
                name
                and name.lower() == "leagueclientux.exe"
            ):

                port = None
                token = None

                for argument in process.info["cmdline"] or []:

                    if argument.startswith(
                        "--app-port="
                    ):
                        port = argument.split(
                            "=",
                            1
                        )[1]

                    elif argument.startswith(
                        "--remoting-auth-token="
                    ):
                        token = argument.split(
                            "=",
                            1
                        )[1]

                if port and token:
                    return port, token


        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            continue


    return None, None


# ==================================================
# RICHIESTA GET GENERICA
# ==================================================

def lcu_get(port, token, endpoint):
    """
    Effettua una richiesta GET alla League Client API.

    Se il client:
    - viene chiuso
    - crasha
    - cambia porta
    - non risponde

    restituiamo None invece di far terminare
    l'intero programma.
    """

    if not port or not token:
        return None


    url = (
        f"https://127.0.0.1:"
        f"{port}"
        f"{endpoint}"
    )


    try:

        response = requests.get(
            url,
            auth=("riot", token),
            verify=False,
            timeout=2
        )

        return response


    except requests.RequestException:

        # Non stampiamo errori qui.
        #
        # Questa funzione viene chiamata molto spesso
        # e riempiremmo il terminale.
        #
        # Sarà main.py a decidere cosa fare
        # quando riceve None.
        return None


# ==================================================
# GAME PHASE
# ==================================================

def get_game_phase(port, token):
    """
    Restituisce la fase attuale del client.

    Esempi:

        Lobby
        Matchmaking
        ReadyCheck
        ChampSelect
        InProgress

    Se il client non è raggiungibile:
        None
    """

    response = lcu_get(
        port,
        token,
        "/lol-gameflow/v1/gameflow-phase"
    )


    if response is None:
        return None


    if response.status_code != 200:
        return None


    try:
        return response.json()

    except ValueError:
        return None


# ==================================================
# CHAMPION SELECT
# ==================================================

def get_champ_select(port, token):
    """
    Recupera la sessione corrente
    della Champion Select.

    Se non è disponibile:
        None
    """

    response = lcu_get(
        port,
        token,
        "/lol-champ-select/v1/session"
    )


    if response is None:
        return None


    if response.status_code != 200:
        return None


    try:
        return response.json()

    except ValueError:
        return None


# ==================================================
# LISTA CAMPIONI
# ==================================================

def load_champions(port, token):
    """
    Costruisce il dizionario:

        Riot ID -> nome campione

    Esempio:

        {
            84: "Akali",
            64: "Lee Sin",
            32: "Amumu"
        }

    Se League non risponde:
        {}
    """

    response = lcu_get(
        port,
        token,
        "/lol-game-data/assets/v1/champion-summary.json"
    )


    if response is None:
        return {}


    if response.status_code != 200:
        return {}


    try:
        data = response.json()

    except ValueError:
        return {}


    champions = {}


    for champion in data:

        champion_id = champion.get(
            "id"
        )

        champion_name = champion.get(
            "name"
        )


        # Escludiamo eventuali record tecnici
        # che non rappresentano campioni reali.
        if not champion_id:
            continue

        if champion_id <= 0:
            continue

        if not champion_name:
            continue

        if champion_name == "None":
            continue


        champions[
            champion_id
        ] = champion_name


    return champions


# ==================================================
# DETTAGLI CAMPIONE
# ==================================================

def get_champion_details(
    port,
    token,
    champion_id
):
    """
    Recupera i dati dettagliati Riot
    relativi a uno specifico campione.

    Se non sono disponibili:
        None
    """

    # ID 0 significa campione non selezionato.
    if not champion_id:
        return None


    response = lcu_get(
        port,
        token,
        (
            "/lol-game-data/assets/v1/"
            f"champions/{champion_id}.json"
        )
    )


    if response is None:
        return None


    if response.status_code != 200:
        return None


    try:
        return response.json()

    except ValueError:
        return None