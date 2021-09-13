# Crawling And Multi-Level Clustering For A High Quantity Of News Articles :newspaper:

This project has been a part of the course "Key Competencies in Computer Science" at the University of Wuppertal to annotate a Crossdocument Coreference Resolution Model and was supervised by Anastasia Zhukova.

## Table of Contents
  - [Requirements](#requirements)
  - [Crawling & Clustering](#crawling--clustering)
    - [Pipelines](#pipelines)
    - [Output Directories](#output-directories)
  - [Methodology](#methodology)
  - [Archieve The Best Possible Result](#archieve-the-best-possible-result)
    - [Crawler](#crawler)
    - [Clustering](#clustering)
  - [Contributing](#contributing)

## Requirements

To install requirements:

```setup
pip install -r requirements.txt
```
This project consists of two parts: The crawler and the clustering algorithms. The crawler works as a usual python script. The clustering is performed within two jupyter notebooks to allow easier adjusting of hyperparameters and visualisations. 

- You can download a sample dataset which has been crawled with this project by clicking [here](https://drive.google.com/drive/u/0/folders/1hXE7dH-QrgaeUjD9fOlfpDlApA8XBPTP).
- You can download the already clustered dataset by clicking here.

The dataset consists of ~250.000 American news articles from 03/2016 to 07/2021. The websites chosen are based on the [POLUSA](https://arxiv.org/abs/2005.14024) dataset to ensure a diverse political spectrum.

## Crawling

To crawl a dataset of news articles from [CommonCrawl](https://commoncrawl.org/), type:

```crawl
python crawl.py
```

### Pipeline
The Crawler is gathering WARC data from CommonCrawl and processing it into a json layout. This json data can later be used for clustering.


<img src="https://github.com/snakeeye98/automated-crawling-and-multi-level-clustering-of-news-articles/blob/main/repo_images/crawl_pipeline.png" width="800">

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

To archieve the best results you may change some parameters in the code. The following parameters have a significant influence on the quality of the produced dataset.

### Crawler

| Parameter          | Description                          |
| ------------------ |--------------------------------------|
| `TARGET_WEBSITES`  | Websites you want to keep crawled data|
| `TEST_TARGETS`| URLs to request WARC-files from CommonCrawl|
|`INDEXES`| Indexes from CommonCrawl|
|`MAX_ARCHIVE_FILES_PER_URL`| Maximum amount of archive files per item of `TEST_TARGETS`|
|`MINIMUM_MAINTEXT_LENGTH`| Shorter articles will be discarded|
|`MAX_CONNECTION_RETRIES`| Maximum retries while downloading|
|`START_NUMERATION_AT`| Change if you want to extend dataset|
|`DESIRED_LANGUAGE`| Select desired language, for example `en`|   

Define Indexes (which represent the release dates of news articles) by choosing them from the [CommonCrawl Index List](https://index.commoncrawl.org/).

### Clustering

#### LDA Clustering
These parameters can be adjusted within the `LDA_clustering.ipynb` (first level).

| Parameter          | Description                          |
| ------------------ |--------------------------------------|
|`topic_amount_start`| Minimum amount of clusters|
|`topic_amount_end`| Maximum amount of clusters|
|`iteration_interval`| Default Interval is 1|
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
|`min_df`|
|`max_df`|

## Results

>📋  Describe how to evaluate the trained models on benchmarks reported in the paper, give commands that produce the results (section below).

Our model achieves the following performance on :

### [Image Classification on ImageNet](https://paperswithcode.com/sota/image-classification-on-imagenet)

| Model name         | Top 1 Accuracy  | Top 5 Accuracy |
| ------------------ |---------------- | -------------- |
| My awesome model   |     85%         |      95%       |

>📋  Include a table of results from your paper, and link back to the leaderboard for clarity and context. If your main result is a figure, include that figure and link to the command or notebook to reproduce it. 


## Contributing

>📋  Pick a licence and describe how to contribute to your code repository. 

