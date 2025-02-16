import json
import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from wordcloud import WordCloud
from bertopic import BERTopic  # Modelagem de tópicos
from collections import Counter
from nltk import bigrams
from nltk.sentiment import SentimentIntensityAnalyzer
from community import community_louvain
import nltk
nltk.download('vader_lexicon')

# 1. Carregar os dados

def load_data():
    with open("trending_artists_allTime.json", "r", encoding="utf-8") as file:
        artists = json.load(file)
    with open("followers_allTime.json", "r", encoding="utf-8") as file:
        followers = json.load(file)
    with open("trending_tracks_allTime.json", "r", encoding="utf-8") as file:
        tracks = json.load(file)
    return artists, followers, tracks

artists, followers, tracks = load_data()

# Criar um dicionário de referência de artistas
artist_info = {track["user"]["id"]: {"name": track["user"]["name"], "genre": track["genre"]} for track in tracks}

# 2. Construção e Análise de Comunidades na Rede
def build_graph(artists, followers):
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

G = build_graph(artists, followers)
print(f"Número de nós: {G.number_of_nodes()}")
print(f"Número de arestas: {G.number_of_edges()}")

# Detecção de Comunidades
partition = community_louvain.best_partition(G)
nx.set_node_attributes(G, partition, 'community')

# Análise de quantidade de comunidades e seus tamanhos
community_sizes = Counter(partition.values())
print("Número de comunidades detectadas:", len(community_sizes))
print("Tamanhos das comunidades:", community_sizes)

# Criar dataframe de comunidades com nome e gênero
community_data = []
for node, community in partition.items():
    artist_name = artist_info.get(node, {}).get("name", "Unknown")
    genre = artist_info.get(node, {}).get("genre", "Unknown")
    community_data.append([node, artist_name, genre, community])

community_df = pd.DataFrame(community_data, columns=['Nó', 'Nome do Artista', 'Gênero', 'Comunidade'])
community_df.to_csv("network_communities.csv", index=False)
print("Comunidades detectadas salvas em network_communities.csv")

# Visualizar Grafo
plt.figure(figsize=(10, 7))
pos = nx.spring_layout(G, seed=42)
nx.draw(G, pos, with_labels=False, node_size=30, alpha=0.7, edge_color="gray")
nx.draw_networkx_nodes(G, pos, node_color=list(partition.values()), cmap=plt.cm.jet, node_size=50)
plt.title("Detecção de Comunidades na Rede de Artistas e Seguidores")
plt.show()
