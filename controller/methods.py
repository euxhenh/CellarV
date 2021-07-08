from .cellar.core import (cl_Agglomerative, cl_Ingest, cl_KMeans, cl_KMedoids,
                          cl_kPCA, cl_Leiden, cl_MDS, cl_PCA,
                          cl_SpectralClustering, cl_ssLeiden, cl_TruncatedSVD,
                          cl_UMAP, cl_uncertainty)

dim_list = [
    {'label': 'PCA', 'value': 'dim-PCA', 'func': cl_PCA},
    {'label': 'Truncated SVD', 'value': 'dim-Truncated-SVD',
     'func': cl_TruncatedSVD},
    {'label': 'Kernel PCA', 'value': 'dim-Kernel-PCA', 'func': cl_kPCA},
    {'label': 'MDS', 'value': 'dim-MDS', 'func': cl_MDS},
    {'label': 'UMAP', 'value': 'dim-UMAP', 'func': cl_UMAP},
]


vis_list = [
    {'label': 'UMAP', 'value': 'vis-UMAP', 'func': cl_UMAP},
    {'label': 'PCA', 'value': 'vis-PCA', 'func': cl_PCA},
    {'label': 'MDS', 'value': 'vis-MDS', 'func': cl_MDS},
    # {'label': 'Truncated SVD', 'value': 'vis-Truncated-SVD',
    #  'func': cl_TruncatedSVD},
    {'label': 'Kernel PCA', 'value': 'vis-Kernel-PCA', 'func': cl_kPCA}
]

clu_list = [
    {'label': 'Leiden', 'value': 'clu-Leiden', 'func': cl_Leiden},
    {'label': 'KMeans', 'value': 'clu-KMeans', 'func': cl_KMeans},
    {'label': 'KMedoids', 'value': 'clu-KMedoids', 'func': cl_KMedoids},
    {'label': 'Spectral Clustering', 'value': 'clu-Spectral-Clustering',
     'func': cl_SpectralClustering},
    {'label': 'Agglomerative Clustering',
     'value': 'clu-Agglomerative', 'func': cl_Agglomerative}
    # {'label': 'Cluster Ensemble', 'value': 'clu-Cluster-Ensemble','func':},
]


ssclu_list = [
    {'label': 'Constrained Leiden',
        'value': 'ssclu-Constrained-Leiden', 'func': cl_ssLeiden},
    {'label': 'Uncertainty Clustering',
        'value': 'ssclu-Uncertainty-Clustering', 'func': cl_uncertainty}
    # {'label': 'Constrained KMeans', 'value': 'ssclu-Constrained-KMeans'},
    # {'label': 'Seeded KMeans', 'value': 'ssclu-Seeded-KMeans'},
    # {'label': 'KNN Filter', 'value': 'ssclu-KNN-Filter'}
]


lbt_list = [
    {'label': 'Scanpy Ingest',
        'value': 'lbt-Scanpy-Ingest', 'func': cl_Ingest},
    # {'label': 'SingleR', 'value': 'lbt-SingleR'}
]


def find_method(cat_list, method_value):
    for c in cat_list:
        if c['value'] == method_value:
            return c
