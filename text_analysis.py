import json
import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from wordcloud import WordCloud
from bertopic import BERTopic  # Modelagem de tópicos
from collections import Counter
from nltk import bigrams
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
nltk.download('vader_lexicon')

# 1. Carregar os dados
def load_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

data = load_data('trending_tracks.json')

# 2. Extrair texto relevante
def extract_text(data, field):
    documents = []
    for track in data:
        text = track.get(field, '')
        if not text:
            text = ''  # Garantir que não seja None
        if isinstance(text, list):
            text = " ".join(text)
        documents.append(text)
    return documents

titles = extract_text(data, 'title')
descriptions = extract_text(data, 'description')
tags = extract_text(data, 'tags')

# 3. Pré-processamento
def preprocess(text):
    if not isinstance(text, str):
        text = ''  # Garantir que o texto seja uma string
    text = text.lower()
    text = re.sub(r'-', ' ', text)  # Substituir hífens por espaços
    text = re.sub(r'[^a-z\s]', '', text)  # Remover caracteres especiais
    text = re.sub(r'\s+', ' ', text).strip()  # Remover espaços extras
    return text

clean_titles = [preprocess(doc) for doc in titles]
clean_descriptions = [preprocess(doc) for doc in descriptions]
clean_tags = [preprocess(doc) for doc in tags]

all_texts = clean_titles + clean_descriptions + clean_tags

# 4. Estatísticas dos textos
def text_statistics(documents, label):
    lengths = [len(doc.split()) for doc in documents]
    stats = {
        'Média': round(pd.Series(lengths).mean(), 2),
        'Mediana': round(pd.Series(lengths).median(), 2),
        'Desvio-Padrão': round(pd.Series(lengths).std(), 2),
        'Mínimo': min(lengths),
        'Máximo': max(lengths)
    }
    print(f'Estatísticas para {label}:', stats)
    return stats

text_statistics(clean_titles, "Títulos")
text_statistics(clean_descriptions, "Descrições")
text_statistics(clean_tags, "Tags")

# 5. Visualização de Distribuições
def plot_distribution(documents, label):
    lengths = [len(doc.split()) for doc in documents]
    plt.figure(figsize=(10, 5))
    sns.histplot(lengths, bins=20, kde=True)
    plt.xlabel("Número de Palavras")
    plt.ylabel("Frequência")
    plt.title(f"Distribuição do Tamanho dos Textos - {label}")
    plt.show()

plot_distribution(clean_titles, "Títulos")
plot_distribution(clean_descriptions, "Descrições")
plot_distribution(clean_tags, "Tags")

# 6. Modelagem de tópicos com BERTopic
def analyze_topics(documents, label, filename):
    model = BERTopic()
    topics, probs = model.fit_transform(documents)
    topic_info = model.get_topic_info()
    print(f"Resumo dos tópicos para {label}:")
    print(topic_info.head())
    model.save(filename)

analyze_topics(clean_titles, "Títulos", "topics_titles_model")
analyze_topics(clean_descriptions, "Descrições", "topics_descriptions_model")
analyze_topics(clean_tags, "Tags", "topics_tags_model")
analyze_topics(all_texts, "Todos", "topics_all_model")

# 7. Redução de Dimensionalidade com PCA + t-SNE
def reduce_dimensionality(documents):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(documents).toarray()
    pca = PCA(n_components=50).fit_transform(vectors)
    tsne = TSNE(n_components=2, perplexity=30, random_state=42).fit_transform(pca)
    
    plt.figure(figsize=(8, 6))
    plt.scatter(tsne[:, 0], tsne[:, 1], alpha=0.5)
    plt.title("Redução de Dimensionalidade com t-SNE")
    plt.xlabel("Componente 1")
    plt.ylabel("Componente 2")
    plt.show()

reduce_dimensionality(all_texts)

# 8. Contador de Termos (Bigramas)
def generate_bigrams(documents, label):
    all_words = " ".join(documents).split()
    bigram_counts = Counter(bigrams(all_words))
    
    print(f"Top 10 Bigramas para {label}:")
    for bigram, freq in bigram_counts.most_common(10):
        print(f"{' '.join(bigram)}: {freq}")

generate_bigrams(clean_titles, "Títulos")
generate_bigrams(clean_descriptions, "Descrições")
generate_bigrams(clean_tags, "Tags")

generate_bigrams(all_texts, "Todos")

# 9. Análise de Sentimento
def analyze_sentiment(documents, label):
    sia = SentimentIntensityAnalyzer()
    sentiments = [sia.polarity_scores(text)["compound"] for text in documents]
    
    plt.figure(figsize=(10, 5))
    sns.histplot(sentiments, bins=20, kde=True)
    plt.xlabel("Pontuação de Sentimento")
    plt.ylabel("Frequência")
    plt.title(f"Distribuição de Sentimentos - {label}")
    plt.show()
    
    print(f"Média de Sentimento para {label}: {round(pd.Series(sentiments).mean(), 2)}")

analyze_sentiment(clean_titles, "Títulos")
analyze_sentiment(clean_descriptions, "Descrições")
analyze_sentiment(clean_tags, "Tags")
analyze_sentiment(all_texts, "Todos")

# 10. Nuvem de Palavras
def generate_wordcloud(documents, label):
    all_text = " ".join(documents)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f"Nuvem de Palavras - {label}")
    plt.show()

generate_wordcloud(clean_titles, "Títulos")
generate_wordcloud(clean_descriptions, "Descrições")
generate_wordcloud(clean_tags, "Tags")
generate_wordcloud(all_texts, "Todos")
