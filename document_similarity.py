from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import euclidean_distances
import pandas as pd

PATH = 'crawl_csv\crawl_0_0.csv'

def load_data_from_csv():
    df = pd.read_csv(PATH)
    print(df.head(1))
    print('\n')
    return df

def get_title_list(df):
    title_list = df['title'].tolist()
    return title_list

def get_features(title_list):
    vectorizer = CountVectorizer()
    features = vectorizer.fit_transform(title_list).todense()
    print(vectorizer.vocabulary_)
    print('\n')
    return features

def main():
    df = load_data_from_csv()
    title_list = get_title_list(df)
    features = get_features(title_list)
    for i, f in enumerate(features):
        print(f'Index: {i} distance: {euclidean_distances(features[2], f)}')
         
if __name__ == '__main__':
    main()