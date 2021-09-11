# Crawling And Multi-Level Clustering For A High Quantity Of News Articles

This project has been a part of the course "Key Competencies of Computer Science" at the University of Wuppertal to annotate a Crossdocument Coreference Resolution Model and was supervised by Anastasia Zhukova & Prof. Dr. Bela Gipp. 

>📋  Optional: include a graphic explaining your approach/main result, bibtex entry, link to demos, blog posts and tutorials

## Requirements

To install requirements:

```setup
pip install -r requirements.txt
```
This project consists of two parts: The crawler and the clustering algorithm. The crawler works as a usual python script. The clustering is performed within a jupyter notebook to allow easier adjusting of hyperparameters and visualisations. 

- You can download a sample dataset which has been crawled with this project by clicking [here](https://drive.google.com/drive/u/0/folders/1hXE7dH-QrgaeUjD9fOlfpDlApA8XBPTP).
- You can download an already clustered dataset by clicking here.

The dataset consists of ~250.000 American news articles from 03/2016 to 07/2021. The websites chosen are based on the [POLUSA](https://arxiv.org/abs/2005.14024) dataset to ensure a diverse political spectrum.

## Crawling & Clustering

To crawl a dataset for news articles from [CommonCrawl](https://commoncrawl.org/) type:

```crawl
python crawl.py
```

After Crawling you may cluster the dataset on one or multiple levels. 
1) **Latent Dirichlet Allocation (LDA):** First start by running the `LDA_clustering.ipynb` jupyter notebook. 
2) **K-Means & Timed Events:** For the second and third layer you may run `KMeans_clustering.ipynb`.  

### Output Directories
- Crawler: `./crawl_json`
- LDA Clustering: `./LDA_clustered_json`
- Three-Level Clustering: `./clustered_json`

>📋  Describe how to train the models, with example commands on how to train the models in your paper, including the full training procedure and appropriate hyperparameters.

## Evaluation

To evaluate my model on ImageNet, run:

```eval
python eval.py --model-file mymodel.pth --benchmark imagenet
```

>📋  Describe how to evaluate the trained models on benchmarks reported in the paper, give commands that produce the results (section below).

## Pre-trained Models

You can download pretrained models here:

- [My awesome model](https://drive.google.com/mymodel.pth) trained on ImageNet using parameters x,y,z. 

>📋  Give a link to where/how the pretrained models can be downloaded and how they were trained (if applicable).  Alternatively you can have an additional column in your results table with a link to the models.

## Results

Our model achieves the following performance on :

### [Image Classification on ImageNet](https://paperswithcode.com/sota/image-classification-on-imagenet)

| Model name         | Top 1 Accuracy  | Top 5 Accuracy |
| ------------------ |---------------- | -------------- |
| My awesome model   |     85%         |      95%       |

>📋  Include a table of results from your paper, and link back to the leaderboard for clarity and context. If your main result is a figure, include that figure and link to the command or notebook to reproduce it. 


## Contributing

>📋  Pick a licence and describe how to contribute to your code repository. 

