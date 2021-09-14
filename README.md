# Crawling And Multi-Level Clustering Of News Articles :newspaper:
Crawling a dataset of news articles from CommonCrawl and clustering them by their topics.
## Table of Contents
  - [Motivation](#motivation)
  - [Installation](#installation)
  - [Crawling](#crawling)
    - [Pipeline](#pipeline)
  - [Clustering](#clustering)
    - [LDA Pipeline](#pipeline-lda-clustering)
    - [K-Means Pipeline](#pipeline-k-means-clustering)
  - [Output Directories](#output-directories)
  - [Methodology](#methodology)
  - [Parameters](#parameters)
    - [Crawler](#crawler)
    - [Clustering](#clustering)
  - [Contributing](#contributing)

## Motivation
Every day thousands of news articles with different political orientations are released.  
The goal of this project is to create a dataset based on a high amount of news articles, which are clustered by their topics. This will provide useful information about the focus of news media during different timeframes.  
This project has been a part of the course [Key Competencies in Computer Science](https://dke.uni-wuppertal.de/en/teaching.html) at the University of Wuppertal to annotate a Crossdocument Coreference Resolution Model and was supervised by   [Anastasia Zhukova](https://github.com/anastasia-zhukova).

## Installation

To install requirements:

```setup
pip install -r requirements.txt
```
This project consists of two parts: The crawler and the clustering algorithms. The crawler works as a usual python script. The clustering is performed within two jupyter notebooks to allow easier adjusting of hyperparameters and visualisations. 

- You can download a sample dataset which has been crawled with this project by clicking [here](https://drive.google.com/drive/u/0/folders/1hXE7dH-QrgaeUjD9fOlfpDlApA8XBPTP).
- You can download the already clustered dataset by clicking here.

The dataset consists of ~268.000 American news articles from 03/2016 to 07/2021. The websites chosen are based on the [POLUSA](https://arxiv.org/abs/2005.14024) dataset to ensure a diverse political spectrum.

## Crawling

To crawl a dataset of news articles from [CommonCrawl](https://commoncrawl.org/), type:

```crawl
python crawl.py
```

### Pipeline
The crawler is gathering WARC data from CommonCrawl and processing it into a json layout. This json data can later be used for clustering.


<img src="https://github.com/snakeeye98/automated-crawling-and-multi-level-clustering-of-news-articles/blob/main/repo_images/crawl_pipeline.png" width="800">

Running the crawler for the first time will produce a `commoncrawl_archives.json` file. This allows the crawler to be stopped and continued crawling at a later time. If there exists a file with said name, the crawler will skip the initialization of WARC paths and continue downloading immediately (while skipping already processed data). That can be used to extend an existing dataset while only changing the amount of articles crawled per timeframe.

## Clustering

After Crawling you may cluster the dataset on one or multiple levels. 
1) **Latent Dirichlet Allocation (LDA):** First start by running the jupyter notebook:
```notebook
LDA.ipynb
```  
2) **K-Means & Timed Events:** For the second and third layer you may run the jupyter notebook:
```notebook
KMeans.ipynb
```
### Pipeline LDA Clustering
The `LDA.ipynb` notebook is taking all json files within the directory `./crawl_json` and performs this pipeline on the concluded data. Each cluster will get assigned a json file representing a cluster.

<img src="https://github.com/snakeeye98/automated-crawling-and-multi-level-clustering-of-news-articles/blob/main/repo_images/lda_pipeline.png" width="800">

### Pipeline K-Means Clustering
The `KMeans.ipynb` notebook is taking all json files within the directory `./lda_clustered_json` one by one. Each level 1 cluster will then get devided into subclusters which are represented by a folder hierarchy in the output.

<img src="https://github.com/snakeeye98/automated-crawling-and-multi-level-clustering-of-news-articles/blob/main/repo_images/kMeans_pipeline.png" width="800">

## Output Directories
- Crawler: `./crawl_json`
- LDA Clustering: `./LDA_clustered_json`
  - Generate multiple json files with each one representing a cluster of different topics
- Three-Level Clustering: `./clustered_json`
  - Generate directories by clustering algorithms

All json-outputs follow the [news-please format](https://github.com/fhamborg/news-please) while adding some new variables. The added variables are:

| Variable          | Description                          |
| ------------------ |--------------------------------------|
|`LDA_ID`| ID of the articles corresponding to level 1 cluster|
| `LDA_topic_percentage`| Indicator about how well the article fits into its LDA cluster|
|`LDA_topic_keywords`| The most dominant keywords within a LDA cluster
|`kMeans_ID`| ID of the articles corresponding to level 2 cluster|
|`kMeans_topic_keywords`| The most dominant keywords within a K-Means cluster|

## Methodology

Describe how you decide which cluster amount fits etc


## Parameters

To achieve the best results you may change some parameters in the code. The following parameters have a significant influence on the quality of the produced dataset.

### Crawler

| Parameter          | Description                          |
| ------------------ |--------------------------------------|
| `TARGET_WEBSITES`  | Websites you want to keep crawled data|
| `TEST_TARGETS`| URLs to request WARC-files from CommonCrawl|
|`INDEXES`| Indexes from CommonCrawl |
|`MAX_ARCHIVE_FILES_PER_URL`| Maximum amount of archive files per item of `TEST_TARGETS`|
|`MINIMUM_MAINTEXT_LENGTH`| Shorter articles will be discarded|
|`MAX_CONNECTION_RETRIES`| Maximum retries while downloading|
|`START_NUMERATION_AT`| Change if you want to extend the dataset|
|`DESIRED_LANGUAGE`| Select desired language, for example `en`|   

Define Indexes (which represent the release dates of news articles) by choosing them from the [CommonCrawl Index List](https://index.commoncrawl.org/).

### Clustering

#### LDA Clustering
These parameters can be adjusted within the `LDA_clustering.ipynb` (first level).

| Parameter          | Description                          |
| ------------------ |--------------------------------------|
|`topic_amount_start`| Minimum amount of clusters|
|`topic_amount_end`| Maximum amount of clusters|
|`iteration_interval`| The default interval is 1|
|`desired_coherence`| Algorithm stops when value is reached|

The LDA Pipeline filters out a predefined list of stopwords extended by a json file. You can add/remove keywords by seperating them with commas in this file:
```stopwords
stopwords.json
```

#### K-Means Clustering
These parameters can be adjusted within the `KMeans_clustering.ipynb` (second & third level).

| Parameter          | Description                          |
| ------------------ |--------------------------------------|
|`max_clusters`| Maximum possible clusters|
|`min_df`| Igonore terms that appear in less articles (percent) |
|`max_df`| Igonore terms that appear in more articles (percent) |

## Results

### LDA Clustering
The optimal amount of clusters is determined by calculating the coherence score for each iteration of the algorithm. The definitive choice of clusters depends on said coherence score.  
As you can see in the data, the maximum coherence score is achieved relatively quickly. This makes LDA a good choice as a level 1 clustering algorithm as it is not too specific.

#### Data
<img align="right" src="https://github.com/snakeeye98/automated-crawling-and-multi-level-clustering-of-news-articles/blob/main/repo_images/coherence_score_curve.png" width="450">

| Amount Of Clusters | Coherence Score | 
| ------------------ |---------------- | 
| ...   |  ...  | 
| 12   |  53.79 %  | 
| 13   |  44.01 %  | 
| 14 *(best result)*  |  56.74 %  |
| 15   |  50.94 %  | 
| 16   |  52.05 %  | 
| ...   |  ...  |  
        
### K-Means Clustering
The optimal amount of clusters is determined by performing K-Means on multiple amounts of clusters. The definitive choice of clusters is made by calculating the elbow/knee of the distortion curve. The amount of level 2 clusters is calculated independently for every level 1 cluster. We chose `min_df = 0.05` and `max_df = 0.6` for this dataset.

| Amount Of Clusters | Distortion |
| ------------------ |---------------- |
| ...   |  ...  |
| 6   |  44.01 %  |
| 7 *(best result)*  |  56.74 %  |
| 8   |  50.94 %  |
| ...   |  ...  |

>📋  Describe how to evaluate the trained models on benchmarks reported in the paper, give commands that produce the results (section below).

Our model achieves the following performance on :

### [Image Classification on ImageNet](https://paperswithcode.com/sota/image-classification-on-imagenet)

| Model name         | Top 1 Accuracy  | Top 5 Accuracy |
| ------------------ |---------------- | -------------- |
| My awesome model   |     85%         |      95%       |

>📋  Include a table of results from your paper, and link back to the leaderboard for clarity and context. If your main result is a figure, include that figure and link to the command or notebook to reproduce it. 

## References

- Felix Hamborg. 2020. Newsplease Json Format. https://github.com/fhamborg/news-please/blob/master/newsplease/examples/sample.json

- Lukas Gebhard and Felix Hamborg. 2020. The POLUSA Dataset: 0.9M Political News Articles Balanced by Time and Outlet Popularity. In Proceedings of the ACM/IEEE Joint Conference on Digital Libraries in 2020 (JCDL '20). Association for Computing Machinery, New York, NY, USA, 467–468. DOI:https://doi.org/10.1145/3383583.3398567 

