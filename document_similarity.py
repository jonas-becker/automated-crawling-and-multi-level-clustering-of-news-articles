from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import euclidean_distances
import pandas as pd

PATH = '.\crawl_json\crawl_0_0.json'

def load_data_from_csv():
    df = pd.read_json(PATH, orient='index')
    #print(df.head(1))
    #print('\n')
    return df

def get_text_list(df, attribute):
    text_list = df[attribute].tolist()
    return text_list

def get_features(text_list):
    vectorizer = CountVectorizer()
    features = vectorizer.fit_transform(text_list).todense()
    print(vectorizer.vocabulary_)
    print('\n')
    return features

def main():
    df = load_data_from_csv()
    title_list = get_text_list(df, "title")
    maintext_list = get_text_list(df, "maintext")
    features_titles = get_features(title_list)
    features_maintext = get_features(maintext_list)
    print("_______________TITLE COMPARISON _____________\n")
    for i, f in enumerate(features_titles):
        print(f'EUCLIDIAN - Index: {i} distance: {euclidean_distances(features_titles[2], f)}')

    print("_______________MAINTEXT COMPARISON _____________\n")
    for i, f in enumerate(features_maintext):
        print(f'COSINE - Index: {i} distance: {cosine_similarity(features_maintext[2], f)}')


if __name__ == '__main__':
    main()