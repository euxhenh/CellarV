import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from controller.methods import (clu_list, dim_list, lbt_list, ssclu_list,
                                vis_list)

from .method_settings.dim_settings import dim_settings
from .method_settings.clu_settings import clu_settings
from .method_settings.vis_settings import vis_settings
from .method_settings.ssclu_settings import ssclu_settings
from .method_settings.lbt_settings import lbt_settings


def get_cog_btn(id, display='none'):
    return dbc.Button(
        html.I(className="fas fa-cog"),
        id=id,
        color='primary',
        outline=True,
        style={'display': display}
    )


dataset_shape = dbc.Row(
    [
        dbc.Col(
            [
                dbc.InputGroup(
                    [
                        dbc.InputGroupAddon(
                            "No. Samples", addon_type="prepend"),
                        dbc.InputGroupText(
                            "N/A", className="shape-text", id="no-samples"),
                    ]
                )
            ]
        ),
        dbc.Col(
            [
                dbc.InputGroup(
                    [
                        dbc.InputGroupAddon(
                            "No. Features", addon_type="prepend"),
                        dbc.InputGroupText(
                            "N/A", className="shape-text", id="no-features"),
                    ]
                )
            ]
        )
    ],
    no_gutters=True,
    justify='between',
    className="panel mb-2"
)

dim_block = dbc.Card(
    [
        dbc.Button(
            dbc.Row(
                [
                    html.Span("Dimensionality Reduction"),
                    html.Span(style={'width': '5px'}),
                    html.I(className="fas fa-chevron-down"),
                ],
                align='baseline',
                justify='center',
                no_gutters=True
            ),
            id="dim-reduce-collapse-btn",
            color='light',
            outline=False
        ),
        dbc.Collapse(
            [
                dbc.CardBody(
                    [
                        dbc.FormGroup(
                            [
                                dbc.Label("Obtain Embeddings via"),
                                dbc.InputGroup(
                                    [
                                        dbc.Select(
                                            options=[
                                                {
                                                    'label': m['label'],
                                                    'value': m['value']
                                                } for m in dim_list],
                                            required=True,
                                            id="dim-methods-select",
                                            value=dim_list[0]['value']
                                        ),
                                        dbc.InputGroupAddon(
                                            [
                                                get_cog_btn(
                                                    i['value'] + '-btn')
                                                for i in dim_list
                                            ],
                                            addon_type="append"
                                        ),
                                        *dim_settings
                                    ]
                                )
                            ]
                        ),
                        dbc.FormGroup(
                            [
                                dbc.Label("Obtain 2D Embeddings via"),
                                dbc.InputGroup(
                                    [
                                        dbc.Select(
                                            options=[
                                                {
                                                    'label': m['label'],
                                                    'value': m['value']
                                                } for m in vis_list],
                                            required=True,
                                            id="vis-methods-select",
                                            value=vis_list[0]['value']
                                        ),
                                        dbc.InputGroupAddon(
                                            [
                                                get_cog_btn(
                                                    i['value'] + '-btn')
                                                for i in vis_list
                                            ],
                                            addon_type="append"
                                        ),
                                        *vis_settings
                                    ]
                                )
                            ]
                        ),
                        dbc.Button(
                            "Run",
                            block=True,
                            id="dim-run-btn",
                            color='primary',
                            outline=False
                        ),
                    ]
                )
            ],
            is_open=True,
            id="dim-reduce-collapse"
        )
    ],
    className="shadow-sm panel mb-2"
)

clu_block = dbc.Card(
    [
        dbc.CardBody(
            [
                dbc.FormGroup(
                    [
                        dbc.Label("Obtain Labels via"),
                        dbc.InputGroup(
                            [
                                dbc.Select(
                                    options=[
                                        {
                                            'label': m['label'],
                                            'value': m['value']
                                        } for m in clu_list],
                                    required=True,
                                    id="clu-methods-select",
                                    value=clu_list[0]['value']
                                ),
                                dbc.InputGroupAddon(
                                    [
                                        get_cog_btn(i['value'] + '-btn')
                                        for i in clu_list
                                    ],
                                    addon_type="append"
                                ),
                                *clu_settings
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

ssclu_block = dbc.Card(
    [
        dbc.CardBody(
            [
                dbc.FormGroup(
                    [
                        dbc.Label("Obtain Labels via"),
                        dbc.InputGroup(
                            [
                                dbc.Select(
                                    options=[
                                        {
                                            'label': m['label'],
                                            'value': m['value']
                                        } for m in ssclu_list],
                                    required=True,
                                    id="ssclu-methods-select",
                                    value=ssclu_list[0]['value']
                                ),
                                dbc.InputGroupAddon(
                                    [
                                        get_cog_btn(i['value'] + '-btn')
                                        for i in ssclu_list
                                    ],
                                    addon_type="append"
                                ),
                                *ssclu_settings
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

lbt_block = dbc.Card(
    [
        dbc.CardBody(
            [
                dbc.FormGroup(
                    [
                        dbc.Label("Obtain Labels via"),
                        dbc.InputGroup(
                            [
                                dbc.Select(
                                    options=[
                                        {
                                            'label': m['label'],
                                            'value': m['value']
                                        } for m in lbt_list],
                                    required=True,
                                    id="lbt-methods-select",
                                    value=lbt_list[0]['value']
                                ),
                                dbc.InputGroupAddon(
                                    [
                                        get_cog_btn(i['value'] + '-btn')
                                        for i in lbt_list
                                    ],
                                    addon_type="append"
                                ),
                                *lbt_settings
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

label_tabs = dbc.Tabs(
    [
        dbc.Tab(clu_block, label="Unsupervised", tab_id="clu"),
        dbc.Tab(ssclu_block, label="Semi-Supervised", tab_id="ssclu"),
        dbc.Tab(lbt_block, label="Label Transfer", tab_id="lbt"),
    ],
    id="label-tabs"
)

label_block = dbc.Card(
    [
        dbc.Button(
            dbc.Row(
                [
                    html.Span("Clustering"),
                    html.Span(style={'width': '5px'}),
                    html.I(className="fas fa-chevron-down"),
                ],
                align='baseline',
                justify='center',
                no_gutters=True
            ),
            id="clustering-collapse-btn",
            color='light',
            outline=False
        ),
        dbc.Collapse(
            [
                dbc.CardBody(
                    [
                        label_tabs,
                        dbc.Button(
                            "Run",
                            block=True,
                            id="label-run-btn",
                            color='primary',
                            outline=False
                        )
                    ],
                    className="mt-2"
                )
            ],
            is_open=True,
            id="clustering-collapse"
        )
    ],
    className="shadow-sm panel mb-2",
)

annotations_block = dbc.Card(
    [
        dbc.Button(
            dbc.Row(
                [
                    html.Span("Annotations"),
                    html.Span(style={'width': '5px'}),
                    html.I(className="fas fa-chevron-down"),
                ],
                align='baseline',
                justify='center',
                no_gutters=True
            ),
            id="annotation-collapse-btn",
            color='light',
            outline=False
        ),
        dbc.Collapse(
            [
                dbc.CardBody(
                    dbc.Col(
                        [
                            dbc.Row(
                                dbc.InputGroup(
                                    [
                                        dbc.InputGroupAddon(
                                            dbc.Select(
                                                options=[],
                                                id="main-annotation-select"
                                            ),
                                            id="main-annotation-addon",
                                            addon_type='prepend'
                                        ),
                                        dbc.InputGroupAddon(
                                            dbc.Select(
                                                options=[],
                                                id="side-annotation-select"
                                            ),
                                            id="side-annotation-addon",
                                            className="no-display",
                                            addon_type='prepend'
                                        ),
                                        dbc.Input(
                                            value="",
                                            placeholder="Annotation",
                                            type="text",
                                            id="annotation-input"
                                        ),
                                        dbc.InputGroupAddon(
                                            [
                                                dbc.Button(
                                                    "Store",
                                                    id="annotation-store-btn",
                                                    color='primary'
                                                )
                                            ],
                                            addon_type='append'
                                        )
                                    ]
                                ),
                                className="mb-2",
                                no_gutters=True
                            ),
                            dbc.Row(
                                dbc.Col(
                                    dash_table.DataTable(
                                        id="main-annotation-table",
                                        page_size=10,
                                        export_format='none',
                                        style_table={
                                            'overflowY': 'auto'
                                        },
                                        data=[
                                            {
                                                "cluster_id": "N/A",
                                                "annotation": "N/A"
                                            }
                                        ],
                                        columns=[
                                            {"name": "ID", "id": "cluster_id"},
                                            {"name": "Annotation",
                                                "id": "annotation"}
                                        ]
                                    )
                                ),
                                justify='center',
                                id="main-annotation-table-row",
                                no_gutters=True,
                                className="mb-2"
                            ),
                            dbc.Row(
                                dbc.Col(
                                    dash_table.DataTable(
                                        id="side-annotation-table",
                                        page_size=10,
                                        export_format='none',
                                        style_table={
                                            'overflowY': 'auto'
                                        },
                                        data=[
                                            {
                                                "cluster_id": "N/A",
                                                "annotation": "N/A"
                                            }
                                        ],
                                        columns=[
                                            {"name": "ID", "id": "cluster_id"},
                                            {"name": "Annotation",
                                                "id": "annotation"}
                                        ]
                                    )
                                ),
                                justify='center',
                                id="side-annotation-table-row",
                                no_gutters=True,
                                className="no-display mb-2"
                            ),
                            dbc.Row(
                                [
                                    dbc.InputGroup(
                                        [
                                            dbc.Input(
                                                value="",
                                                placeholder="Subset Name",
                                                type="text",
                                                id="subset-name-input"
                                            ),
                                            dbc.InputGroupAddon(
                                                dbc.Button(
                                                    "Store",
                                                    id="subset-name-store-btn",
                                                    color='primary'
                                                ),
                                                addon_type='append'
                                            )
                                        ]
                                    )
                                ],
                                className="mb-2",
                                no_gutters=True
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dcc.Loading(
                                            dbc.InputGroup([
                                                dbc.Select(
                                                    options=[],
                                                    placeholder="Merge subset",
                                                    id="main-subset-select"
                                                ),
                                                dbc.Select(
                                                    options=[],
                                                    placeholder="Merge subset",
                                                    className="no-display",
                                                    id="side-subset-select"
                                                ),
                                                dbc.InputGroupAddon(
                                                    dbc.Button(
                                                        "Merge",
                                                        id="merge-subset-btn",
                                                        color='primary'
                                                    ),
                                                    addon_type='append'
                                                )
                                            ])
                                        )
                                    )
                                ],
                                no_gutters=True
                            )
                        ]
                    )
                )
            ],
            is_open=True,
            id="annotation-collapse"
        )
    ],
    className="shadow-sm panel mb-2",
)

session_block = dbc.Card(
    [
        dbc.Button(
            dbc.Row(
                [
                    html.Span("Session"),
                    html.Span(style={'width': '5px'}),
                    html.I(className="fas fa-chevron-down"),
                ],
                align='baseline',
                justify='center',
                no_gutters=True
            ),
            id="session-collapse-btn",
            color='light',
            outline=False
        ),
        dbc.Collapse(
            [
                dbc.CardBody(
                    [
                        dbc.Button(
                            "Export Session",
                            id='export-session-btn',
                            block=True,
                            color='primary',
                            outline=False
                        ),
                        dbc.Button(
                            "Export Annotations",
                            id='export-annotations-btn',
                            block=True,
                            color='primary',
                            outline=False
                        ),
                        dcc.Loading(
                            dcc.Download("export-session-d"),
                            fullscreen=True
                        ),
                        dcc.Loading(
                            dcc.Download("export-annotations-d"),
                            fullscreen=True
                        )
                    ]
                )
            ],
            is_open=True,
            id="session-collapse"
        )
    ],
    className="shadow-sm panel mb-2",
)


sidebar = [
    dataset_shape,
    dim_block,
    label_block,
    annotations_block,
    session_block
]
