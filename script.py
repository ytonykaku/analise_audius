import requests
import json
import os

# Define o nome do aplicativo para as requisições
APP_NAME = "MARS_STUDY"

# Lista de URLs da API
BASE_URLS = [
    "https://discoveryprovider.audius.co",
    "https://audius-discovery-5.cultur3stake.com",
    "https://blockdaemon-audius-discovery-03.bdnodes.net"
]


def fetch_data(url, params=None):
    """Realiza uma requisição GET e retorna os dados se a resposta for bem-sucedida."""
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.RequestException as e:
        print(f"Erro ao conectar com {url}: {e}")
        return []


def get_trending_tracks(time="month", limit=100):
    """Obtém as faixas em alta e retorna uma lista com um limite máximo de resultados."""
    for base_url in BASE_URLS:
        url = f"{base_url}/v1/tracks/trending"
        params = {"time": time, "app_name": APP_NAME}
        tracks = fetch_data(url, params)
        if tracks:
            print(f"Trending tracks obtidas com sucesso de: {base_url}")
            return tracks[:limit]
    print("Não foi possível obter dados de nenhum endpoint.")
    return []


def get_artist_ids_from_tracks(tracks):
    """Extrai os IDs únicos dos artistas a partir das faixas."""
    return list({track.get("user", {}).get("id") for track in tracks if track.get("user")})


def get_followers(artist_id, limit=50):
    """Obtém seguidores de um artista específico."""
    for base_url in BASE_URLS:
        url = f"{base_url}/v1/users/{artist_id}/followers"
        params = {"limit": limit, "app_name": APP_NAME}
        followers = fetch_data(url, params)
        if followers:
            print(f"Followers obtidos para o artista {artist_id}.")
            return followers
    return []


def save_to_file(data, filename):
    """Salva os dados em um arquivo JSON."""
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)
    print(f"Dados salvos em '{filename}'")


def load_from_file(filename):
    """Carrega dados de um arquivo JSON se ele existir."""
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return json.load(file)
    return None


def main():
    """Fluxo principal de execução."""
    tracks_file = "trending_tracks.json"
    artists_file = "trending_artists.json"
    followers_file = "followers.json"

    # Obtém e salva as trending tracks
    tracks = load_from_file(tracks_file)
    if tracks is None:
        print("Arquivo de trending tracks não encontrado. Obtendo dados...")
        tracks = get_trending_tracks()
        save_to_file(tracks, tracks_file)
    else:
        print("Trending tracks carregadas do arquivo.")

    # Obtém e salva os artistas
    artist_ids = load_from_file(artists_file)
    if artist_ids is None:
        print("Arquivo de artistas não encontrado. Extraindo dados das tracks...")
        artist_ids = get_artist_ids_from_tracks(tracks)
        save_to_file(artist_ids, artists_file)
    else:
        print("IDs dos artistas carregados do arquivo.")

    # Obtém e salva os seguidores dos artistas
    followers_data = load_from_file(followers_file)
    if followers_data is None:
        print("Arquivo de seguidores não encontrado. Obtendo seguidores dos artistas...")
        followers_data = {}
        for artist_id in artist_ids:
            followers = get_followers(artist_id, limit=50)
            if followers:
                followers_data[artist_id] = followers
            else:
                print(f"Nenhum seguidor encontrado para o artista {artist_id}.")
        save_to_file(followers_data, followers_file)
    else:
        print("Dados de seguidores carregados do arquivo.")


if __name__ == "__main__":
    main()
