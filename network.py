import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json
import pandas as pd
from collections import Counter
import numpy as np

# Carrega os dados dos arquivos JSON
def load_data():
    with open("trending_artists_allTime.json", "r") as file:
        artists = json.load(file)
    with open("followers_allTime.json", "r") as file:
        followers = json.load(file)
    with open("trending_tracks_allTime.json", "r") as file:
        tracks = json.load(file)
    return artists, followers, tracks

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

# Calcula estatísticas da rede
def compute_network_statistics(G):
    num_vertices = G.number_of_nodes()
    num_arestas = G.number_of_edges()
    coef_clustering = nx.average_clustering(G)
    
    print(f"📊 Número de vértices: {num_vertices}")
    print(f"🔗 Número de arestas: {num_arestas}")
    print(f"🔄 Coeficiente de clustering médio: {coef_clustering:.4f}")
    
    return num_vertices, num_arestas, coef_clustering

# Calcula distribuição de graus
def plot_degree_distribution(G):
    degrees = [G.degree(n) for n in G.nodes()]
    plt.figure(figsize=(10, 5))
    plt.hist(degrees, bins=30, alpha=0.7, color='blue', edgecolor='black')
    plt.xlabel("Grau")
    plt.ylabel("Frequência")
    plt.title("Distribuição de Graus da Rede")
    plt.show()

# Calcula centralidade dos vértices
def compute_centralities(G):
    degree_centrality = nx.degree_centrality(G)
    eigenvector_centrality = nx.eigenvector_centrality(G, max_iter=1000)
    
    return degree_centrality, eigenvector_centrality

# Plota a rede com centralidade proporcional
def plot_artist_graph_with_legend(G, legend_info, degree_centrality, eigenvector_centrality):
    labels = {artist_id: info["artist_name"] for artist_id, info in legend_info.items()}
    
    node_sizes = [5000 * eigenvector_centrality.get(node, 0) if node in labels else 50 for node in G.nodes]
    node_colors = ["orange" if node in labels else "lightblue" for node in G.nodes]
    
    plt.figure(figsize=(15, 10))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(
        G,
        pos,
        with_labels=True,
        labels=labels,
        node_size=node_sizes,
        node_color=node_colors,
        edge_color="gray",
        font_size=10,
    )
    
    legend_handles = [
        mpatches.Patch(
            color="orange", 
            label=f"{info['artist_name']} - {info['title']} ({info['genre']})"
        )
        for artist_id, info in legend_info.items()
    ]
    plt.legend(handles=legend_handles, loc="upper left", title="Artistas, Músicas e Gêneros")
    
    plt.title("Rede de Artistas e Seguidores (Nome do Artista, Música e Gênero)")
    plt.show()

if __name__ == "__main__":
    # Carrega os dados
    artists, followers, tracks = load_data()

    # Monta o grafo
    G = build_network(artists, followers)
    
    # Calcula estatísticas da rede
    compute_network_statistics(G)
    
    # Plota distribuição de graus
    plot_degree_distribution(G)
    
    # Calcula centralidades
    degree_centrality, eigenvector_centrality = compute_centralities(G)
    
    # Prepara os dados para a legenda
    legend_info = {track["user"]["id"]: {"artist_name": track["user"]["name"], "title": track["title"], "genre": track["genre"]} for track in tracks}
    
    # Plota a rede ajustada
    plot_artist_graph_with_legend(G, legend_info, degree_centrality, eigenvector_centrality)
    
    print("✅ Análise concluída com sucesso!")
