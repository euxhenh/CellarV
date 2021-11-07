import io
import os
import shutil
import tarfile
from base64 import b64decode

import dash
import dash_core_components as dcc
import dash_bio as dashbio
import numpy as np
import matplotlib
import plotly.express as px
from app import app, dbroot, logger
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from .cellar.utils.tile_generator import (generate_10x_spatial,
                                          generate_tile)
from .cellar.utils.exceptions import InternalError
from .cellar.core import adjScoreProteinsCODEX, adjScoreClustersCODEX
from .cellar.core import cl_get_expression
from .multiplexer import MultiplexerOutput
from .notifications import _prep_notification
from layout.misc import empty_spatial_figure, empty_colocalization_figure


def get_parse_tar_gz_func(an):
    def _func(contents, filename, data_type):
        content_type, content_string = contents.split(',')
        decoded = b64decode(content_string)

        if data_type == 'spatial-10x':
            extract_path = f'tmp/{an}/s10x'
        elif data_type == 'spatial-codex':
            extract_path = f'tmp/{an}/codex'
        else:
            raise PreventUpdate

        if filename.endswith('tar.gz'):
            logger.info(f"Extracting tar.gz file at {extract_path}.")
            try:
                tar = tarfile.open(fileobj=io.BytesIO(decoded))
                if os.path.isdir(extract_path):
                    shutil.rmtree(extract_path)
                tar.extractall(extract_path)
                tar.close()
            except Exception as e:
                logger.error(str(e))
                error_msg = "Couldn't extract tar.gz file."
                logger.error(error_msg)
                return dash.no_update, _prep_notification(error_msg, "danger")
        else:
            return dash.no_update, _prep_notification(
                f'{filename} format not recognized.', "danger")

        return {}, _prep_notification("Finished extracting file.", "info")

    return _func


for prefix, an in zip(["main", "side"], ["a1", "a2"]):
    app.callback(
        Output(prefix + "-buf-load", "style"),
        MultiplexerOutput("push-notification", "data"),

        Input(prefix + '-upload-spatial', 'contents'),
        State(prefix + '-upload-spatial', 'filename'),
        State(prefix + "-spatial-type-dropdown", "value"),
        prevent_initial_call=True
    )(get_parse_tar_gz_func(an))


def get_generate_tile_func(an, prefix):
    def _func(n1, clean, data_type, feature_list):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        if an not in dbroot.adatas:
            raise PreventUpdate
        if 'adata' not in dbroot.adatas[an]:
            raise PreventUpdate

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id == prefix + "-data-load-clean":
            return empty_spatial_figure, dash.no_update

        adata = dbroot.adatas[an]['adata']

        colors = None
        if feature_list is None or len(feature_list) == 0:
            if 'labels' in dbroot.adatas[an]['adata'].obs:
                colors = adata.obs['labels'].to_numpy().astype(int)
        else:
            if data_type == 'spatial-10x':
                error_msg = "Protein expression view is currently " + \
                    "only supported for CODEX data."
                return dash.no_update, _prep_notification(error_msg, "info")
            feature_list = np.array(feature_list, dtype='U200').flatten()
            colors = cl_get_expression(adata, feature_list).astype(float)

        savepath = f'tmp/spatial_{an}_tile.png'
        owner = None
        if data_type == 'spatial-10x':
            # if not os.path.isdir(f'tmp/{an}/s10x'):
            #     raise PreventUpdate
            try:
                tile, owner = generate_10x_spatial(
                    f'tmp/{an}/s10x/spatial/detected_tissue_image.jpg',
                    f'tmp/{an}/s10x/spatial/tissue_positions_list.csv',
                    f'tmp/{an}/s10x/spatial/scalefactors_json.json',
                    adata=adata,
                    in_tissue=True,
                    savepath=savepath,
                    palette=dbroot.palettes[prefix])
            except Exception as e:
                logger.error(str(e))
                error_msg = "Error occurred when generating 10x spatial tile."
                logger.error(error_msg)
                return dash.no_update, _prep_notification(error_msg, "danger")
        elif data_type == 'spatial-codex':
            tile_list = os.listdir('data/codex_tile')
            fname = dbroot.adatas[an]['name']

            try:
                if fname in tile_list:
                    logger.info("Found CODEX tile locally.")

                    tile, owner = generate_tile(
                        f'data/codex_tile/{fname}/images',
                        f'data/codex_tile/{fname}/data.csv',
                        adata=adata,
                        colors=colors,
                        palette=dbroot.palettes[prefix],
                        savepath=savepath)
                else:
                    if not os.path.isdir(f'tmp/{an}/codex'):
                        raise PreventUpdate

                    tile, owner = generate_tile(
                        f'tmp/{an}/codex/images',
                        f'tmp/{an}/codex/data.csv',
                        adata=adata,
                        colors=colors,
                        palette=dbroot.palettes[prefix],
                        savepath=savepath)
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                logger.error(str(e))
                error_msg = "Error occurred when generating CODEX tile."
                logger.error(error_msg)
                return dash.no_update, _prep_notification(error_msg, "danger")
        else:
            msg = "Please select a data type."
            return dash.no_update, _prep_notification(msg, "info")

        if tile is None:
            error_msg = "No tile was generated."
            logger.error(error_msg)
            return dash.no_update, _prep_notification(error_msg, "danger")

        logger.info(f"Generated tile with shape {tile.shape}. Scaling...")

        ho, wo = tile.shape[:2]
        scaler = 1000 / max(wo, ho)
        w, h = int(scaler * wo), int(scaler * ho)

        fig = px.imshow(tile, width=w, height=h,
                        color_continuous_scale='magma')

        if owner is not None and 'labels' in dbroot.adatas[an]['adata'].obs:
            owner_cp = owner.copy()
            owner[owner < 0] = 0
            customdata = dbroot.adatas[an][
                'adata'].obs['labels'].to_numpy()[owner]
            customdata[owner_cp < 0] = -1
            fig.update(data=[{
                'customdata': customdata,
                'hovertemplate': 'Cluster ID: %{customdata}'}])
        fig.update_layout(coloraxis_showscale=False)
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)

        return fig, _prep_notification(
            f"Generated tile with shape {tile.shape[:2]}", "info")
    return _func


for prefix, an in zip(["main", "side"], ["a1", "a2"]):
    app.callback(
        Output(prefix + "-tile", "figure"),
        MultiplexerOutput("push-notification", "data"),

        Input(prefix + "-generate-tile-btn", "n_clicks"),
        Input(prefix + "-data-load-clean", "data"),
        State(prefix + "-spatial-type-dropdown", "value"),
        State(prefix + "-feature-list-spatial", "value"),
        prevent_initial_call=True
    )(get_generate_tile_func(an, prefix))


def _remap_indices(x, old, new):
    sort_idx = old.argsort()
    mapped_idx = sort_idx[
        np.searchsorted(old, x, sorter=sort_idx)]
    remapped = new[mapped_idx]
    return remapped


def get_generate_cluster_scores_func(an, prefix):
    def _func(n1, clean):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        if an not in dbroot.adatas:
            raise PreventUpdate
        if 'adata' not in dbroot.adatas[an]:
            raise PreventUpdate

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id == prefix + "-data-load-clean":
            return empty_colocalization_figure, dash.no_update

        tile_list = os.listdir('data/codex_tile')
        fname = dbroot.adatas[an]['name']

        if fname not in tile_list:
            msg = "Could not find spatial data."
            logger.warn(msg)
            return dash.no_update, _prep_notification(msg, icon="warning")

        csv_path = f'data/codex_tile/{fname}/data.csv'
        res = adjScoreClustersCODEX(dbroot.adatas[an]['adata'], csv_path)

        x_cord = res['f'].to_numpy().astype(int)
        y_cord = res['g'].to_numpy().astype(int)
        scores = res['score'].astype(float)
        unq_labels = np.unique(dbroot.adatas[an]['adata'].obs['labels'])
        n = len(unq_labels)
        x_cord = _remap_indices(x_cord, unq_labels, np.arange(n))
        y_cord = _remap_indices(y_cord, unq_labels, np.arange(n))
        heatmap = np.zeros((n, n))
        heatmap[x_cord, y_cord] = scores
        heatmap[y_cord, x_cord] = scores
        heatmap = np.log10(heatmap + 1)

        # fig = dashbio.Clustergram(
        #     data=heatmap,
        #     column_labels=list(unq_labels),
        #     row_labels=list(unq_labels),
        #     color_map=[
        #         [0.0, '#440154'],
        #         [0.25, '#3e4989'],
        #         [0.5, '#26828e'],
        #         [0.75, '#35b779'],
        #         [1.0, '#fde725']
        #     ],
        #     cluster='col',
        #     # center_values=True,
        #     line_width=2,
        #     width=600
        # )

        # fig.update_xaxes(tickangle=-90)
        # return fig, dash.no_update

        fig = px.imshow(
            heatmap,
            x=unq_labels.astype(str),
            y=unq_labels.astype(str),
            labels={
                'color': 'log10(score+1)',
                'x': 'Cluster x ID',
                'y': 'Cluster y ID'
            },
            color_continuous_scale='magma'
        )
        return fig, dash.no_update
    return _func


for prefix, an in zip(["main", "side"], ["a1", "a2"]):
    app.callback(
        Output(prefix + "-cluster-scores", "figure"),
        MultiplexerOutput("push-notification", "data"),

        Input(prefix + "-generate-cluster-scores-btn", "n_clicks"),
        Input(prefix + "-data-load-clean", "data"),
        prevent_initial_call=True
    )(get_generate_cluster_scores_func(an, prefix))


def get_generate_protein_scores_func(an, prefix):
    def _func(n1, clean):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        if an not in dbroot.adatas:
            raise PreventUpdate
        if 'adata' not in dbroot.adatas[an]:
            raise PreventUpdate

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id == prefix + "-data-load-clean":
            return empty_colocalization_figure, dash.no_update

        tile_list = os.listdir('data/codex_tile')
        fname = dbroot.adatas[an]['name']

        if fname not in tile_list:
            msg = "Could not find spatial data."
            logger.warn(msg)
            return dash.no_update, _prep_notification(msg, icon="warning")

        csv_path = f'data/codex_tile/{fname}/data.csv'
        res = adjScoreProteinsCODEX(dbroot.adatas[an]['adata'], csv_path)

        features = dbroot.adatas[an]['adata'].var['gene_symbols'].to_numpy()
        x_cord, y_cord = res['f'].astype(int), res['g'].astype(int)
        scores = res['score'].astype(float)
        n = features.shape[0]
        heatmap = np.zeros((n, n))
        heatmap[x_cord, y_cord] = scores
        heatmap[y_cord, x_cord] = scores
        heatmap = np.log10(heatmap + 1)

        fig = px.imshow(
            heatmap,
            x=features,
            y=features,
            labels={
                'color': 'log10(score+1)'
            },
            color_continuous_scale='magma'
        )
        return fig, dash.no_update
    return _func


for prefix, an in zip(["main", "side"], ["a1", "a2"]):
    app.callback(
        Output(prefix + "-protein-scores", "figure"),
        MultiplexerOutput("push-notification", "data"),

        Input(prefix + "-generate-protein-scores-btn", "n_clicks"),
        Input(prefix + "-data-load-clean", "data"),
        prevent_initial_call=True
    )(get_generate_protein_scores_func(an, prefix))


def get_download_tile_func(an):
    def _func(n1):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        if an not in dbroot.adatas:
            raise PreventUpdate

        filepath = f'tmp/spatial_{an}_tile.png'

        if not os.path.isfile(filepath):
            return dash.no_update, _prep_notification(
                "No tile image found.")

        return dcc.send_file(filepath), dash.no_update

    return _func


for prefix, an in zip(["main", "side"], ["a1", "a2"]):
    app.callback(
        Output(prefix + "-download-tile-buf", "data"),
        MultiplexerOutput("push-notification", "data"),

        Input(prefix + "-download-tile-btn", "n_clicks"),
        prevent_initial_call=True
    )(get_download_tile_func(an))
