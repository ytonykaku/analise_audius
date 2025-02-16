import networkx as nx
import json

def load_data():
    with open("trending_artists_allTime.json", "r") as file:
        artists = json.load(file)
    with open("followers_allTime.json", "r") as file:
        followers = json.load(file)
    return artists, followers

# Monta o grafo com os dados
def build_network(artists, followers):
    G = nx.Graph()
    
    # Adiciona nós para artistas
    for artist in artists:
        G.add_node(artist, type="artist")
    
    # Adiciona arestas com base nos seguidores
    for artist, followers_list in followers.items():
        for follower in followers_list:
            follower_id = follower.get("id") if isinstance(follower, dict) else follower
            G.add_node(follower_id, type="follower")
            G.add_edge(artist, follower_id)
    
    return G

# Exporta para GEXF (compatível com Gephi)
def export_to_gephi(G, filename="network_graph.gexf"):
    nx.write_gexf(G, filename)
    print(f"✅ Arquivo salvo como {filename}, pronto para importar no Gephi!")

if __name__ == "__main__":
    # Carrega os dados
    artists, followers = load_data()
    
    # Monta o grafo
    G = build_network(artists, followers)
    
    # Exporta para Gephi
    export_to_gephi(G)
