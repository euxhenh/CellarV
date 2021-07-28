import numpy as np
import dash_bio as dashbio
import plotly.graph_objects as go
import plotly.express as px

from ..utils.exceptions import InternalError, UserError
from ._tools import cl_add_gene_symbol, cl_get_expression
from ..utils.misc import is_sparse
from ..utils.colors import PALETTE, get_col_i


def get_dim_figure(adata, title):
    if 'x_emb_2d' not in adata.obsm:
        raise InternalError("x_emb_2d not found in adata.")

    indices = np.arange(adata.shape[0]).astype('str')
    names = adata.obs.index.to_numpy().astype('str')
    hover_name = [i + ": " + j for i, j in zip(indices, names)]

    fig = px.scatter(
        x=adata.obsm['x_emb_2d'][:, 0],
        y=adata.obsm['x_emb_2d'][:, 1],
        opacity=0.8,
        custom_data=[np.arange(adata.shape[0])],  # indices
        hover_name=hover_name,
        render_mode='webgl')

    fig.update_layout(
        title=title,
        showlegend=True,
        plot_bgcolor='#FFFFFF',
        dragmode='lasso',
        xaxis={'visible': False},
        yaxis={'visible': False}
    )

    return fig


def get_clu_figure(adata, title):
    if 'x_emb_2d' not in adata.obsm or 'labels' not in adata.obs:
        raise InternalError("x_emb_2d or labels not found in adata.")

    hover_data = {}

    unq_colors = np.unique(adata.obs['labels'].to_numpy())
    maxval = np.max(unq_colors)
    unq_colors = list(unq_colors.astype(str))
    pal = [px.colors.convert_colors_to_same_type(i)[0][0] for i in PALETTE]

    if 'annotations' in adata.obs:
        hover_data['Annotation'] = adata.obs['annotations'].to_numpy()

    indices = np.arange(adata.shape[0]).astype('str')
    names = adata.obs.index.to_numpy().astype('str')
    hover_name = [i + ": " + j for i, j in zip(indices, names)]

    fig = px.scatter(
        x=adata.obsm['x_emb_2d'][:, 0],
        y=adata.obsm['x_emb_2d'][:, 1],
        hover_name=hover_name,
        hover_data=hover_data,
        custom_data=[np.arange(adata.shape[0])],  # indices
        color=adata.obs['labels'].astype('str'),
        category_orders={'color': unq_colors},
        opacity=0.8,
        labels={'color': 'Cluster ID'},
        color_discrete_map={str(i): get_col_i(pal, i)
                            for i in range(maxval + 1)},
        render_mode='webgl')

    fig.update_layout(
        title=title,
        showlegend=True,
        plot_bgcolor='#FFFFFF',
        dragmode='lasso',
        xaxis={'visible': False},
        yaxis={'visible': False}
    )

    return fig


def get_reset_figure(adata, title):
    if 'labels' in adata.obs:
        return get_clu_figure(adata, title)

    return get_dim_figure(adata, title)


def get_expression_figure(adata, feature_values, feature_range):
    feature_values = np.array(feature_values, dtype='U200').flatten()
    single_feature = len(feature_values) == 1

    for feat in feature_values:
        if feat not in adata.var_names.to_numpy():
            raise InternalError(f"Feature {feat} not found in var_names.")

    if 'x_emb_2d' not in adata.obsm:
        raise InternalError("No 2d embeddings found.")

    # Construct title with gene symbols
    # If more than 3 genes were used, we append dots
    symbols = adata[:, feature_values].var['gene_symbols']
    title = symbols[0]
    for i in range(1, min(3, len(symbols))):
        title += ", " + symbols[i]
    if len(symbols) > 3:
        title += "..."

    hover_data = {}

    if 'annotations' in adata.obs:
        hover_data['Annotation'] = adata.obs['annotations'].to_numpy()
    if 'labels' in adata.obs:
        hover_data['Cluster ID'] = adata.obs['labels'].to_numpy()

    expression = cl_get_expression(adata, feature_values)

    if single_feature:
        if feature_range[0] > feature_range[1]:
            raise InternalError("Incorrect feature range found.")

        hover_data['Normalized Val.'] = expression.copy()
        new_min = np.min(expression[expression >= feature_range[0]])
        new_max = np.max(expression[expression <= feature_range[1]])
        expression[expression < feature_range[0]] = new_min
        expression[expression > feature_range[1]] = new_max

    exp_max = expression.max()

    fig = px.scatter(
        x=adata.obsm['x_emb_2d'][:, 0],
        y=adata.obsm['x_emb_2d'][:, 1],
        hover_name=adata.obs.index.to_numpy().astype('str'),
        hover_data=hover_data,
        custom_data=[np.arange(adata.shape[0])],  # indices
        color=expression,
        opacity=0.8,
        labels={
            'color': 'Clipped Val.' if single_feature else 'Normalized Val.'},
        range_color=[expression.min(), 1 if exp_max == 0 else exp_max],
        render_mode='webgl',
        color_continuous_scale=px.colors.sequential.Viridis
    )

    fig.update_layout(
        title=title,
        showlegend=True,
        plot_bgcolor='#FFFFFF',
        dragmode='lasso',
        xaxis={'visible': False},
        yaxis={'visible': False}
    )

    return fig


def get_heatmap(adata, feature_list):
    if 'labels' not in adata.obs:
        raise InternalError("No labels found in adata.")

    feature_list = np.array(feature_list).flatten()

    if not set(feature_list).issubset(set(adata.var_names.to_numpy())):
        raise UserError("Some features not found in data.")

    unq_labels = np.unique(adata.obs['labels'])
    aves = []

    for label in unq_labels:
        row = adata[:, feature_list].X[np.where(
            adata.obs['labels'] == label)]
        if is_sparse(row):
            row = np.asarray(row.todense())
        row = row.mean(axis=0)
        aves.append(row)
    aves = np.array(aves)

    if 'gene_symbols' not in adata.var:
        cl_add_gene_symbol(adata)

    cluster = 'all'
    if aves.shape[1] == 1:
        cluster = 'row'
    if aves.shape[0] == 1:
        cluster = 'col'

    fig = dashbio.Clustergram(
        data=aves,
        column_labels=list(adata[:, feature_list].var['gene_symbols']),
        row_labels=['Cluster' + str(i) for i in unq_labels],
        color_map=[
            [0.0, '#440154'],
            [0.25, '#3e4989'],
            [0.5, '#26828e'],
            [0.75, '#35b779'],
            [1.0, '#fde725']
        ],
        cluster=cluster,
        center_values=True,
        line_width=2,
        width=600
    )

    fig.update_xaxes(tickangle=-90)

    return fig


def get_violin_plot(adata, feature, plot1):
    if feature not in adata.var_names:
        raise UserError(f"Feature {feature} not found in adata.")

    vect = adata[:, feature].X
    if is_sparse(vect):
        vect = np.asarray(vect.todense())
    vect = vect.flatten()

    unq_labels = np.unique(adata.obs['labels'])
    pal = [px.colors.convert_colors_to_same_type(i)[0][0] for i in PALETTE]

    if 'gene_symbols' not in adata.var:
        cl_add_gene_symbol(adata)

    fig = go.Figure()

    for i, label in enumerate(unq_labels):
        fig.add_trace(
            go.Violin(
                y=vect[adata.obs['labels'] == label],
                name='Cluster ' + str(label),
                box_visible=True,
                meanline_visible=True,
                marker=go.violin.Marker(color=get_col_i(pal, label))
            )
        )

    title = adata[:, feature].var['gene_symbols'].item()
    title = 'PLOT 1: ' + title if plot1 else 'PLOT 2: ' + title

    fig.update_layout(
        title={'text': title},
        showlegend=False,
        plot_bgcolor='#FFFFFF',
        xaxis={'zeroline': False, 'showgrid': False},
        yaxis={'zeroline': False, 'showgrid': False},
    )

    return fig
