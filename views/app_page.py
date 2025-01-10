import os
import io
import logging
import diskcache
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback_context as ctx
from dash.dependencies import Input, Output, State
from sqlalchemy import create_engine
from dotenv import load_dotenv
from locales import load_locale
from dash import DiskcacheManager
import dash_loading_spinners as dls
import dash_bootstrap_components as dbc
from utils import store_query, count_queries_daily, count_queries_monthly, get_user_role, count_queries_for_user_org, get_user_org_query_limit, get_user_query_limit

import base64


load_dotenv()
page_name = "app_page"
localization  = load_locale(page_name)

logger = logging.getLogger(__name__)

FREE_DAILY_QUERY_LIMIT = 2
UPGRADE_DAILY_QUERY_LIMIT = 4

# Database Integration (unchanged for now)
print(os.getenv("DATABASE_URL"))
engine = create_engine(os.getenv("DB_URL"))


cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)

# User Input Handling Section
user_input_section = html.Div(
    id="user-input-container",
    style={"padding": "20px", "backgroundColor": "#f9f9f9"},
    children=[
        html.H3("Lesson Plan Filters", className="mb-4"),
        dbc.Form([
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(
                        id="subject-category",
                        options=[
                            {"label": "Humanities", "value": "Humanities"},
                            {"label": "Natural Sciences", "value": "Natural Sciences"},
                            {"label": "Others", "value": "Others"},
                        ],
                        placeholder="Select Subject Category",
                    ),
                    width=6,
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="subject",
                        options=[],  # Will be dynamically populated based on category
                        placeholder="Select Subject",
                    ),
                    width=6,
                ),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col(
                    dcc.Input(
                        id="min-age",
                        type="number",
                        placeholder="Min Age",
                        className="form-control",
                    ),
                    width=3,
                ),
                dbc.Col(
                    dcc.Input(
                        id="max-age",
                        type="number",
                        placeholder="Max Age",
                        className="form-control",
                    ),
                    width=3,
                ),
                dbc.Col(
                    dcc.Input(
                        id="duration",
                        type="number",
                        placeholder="Max Duration (minutes)",
                        className="form-control",
                    ),
                    width=6,
                ),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col(
                    dbc.Button(
                        localization["submit-button"],
                        id="submit-user-input",
                        color="primary",
                        className="btn-block",
                    ),
                    width=12,
                ),
            ]),
        ]),
    ],
)

# Dynamic Collapsible Sections for Lesson Methods
collapsible_sections = html.Div(
    id="collapsible-sections-container",
    className="container mt-5",
    children=[
        html.H3(localization["section-heading"], className="mb-4"),
        html.Div(id="lesson-methods-container"),  # Will be dynamically populated
    ],
)

# Layout


app_page_layout = html.Div(
    children=[
        dcc.Store(id="thread-store", data=""), 
        dcc.Store(id="conversation-store", data=""),    
        collapsible_sections,

        # Hlavní kontejner pro vstupy a výstupy
        html.Div(
            className="container-fluid mt-5",
            children=[
                # Jediný řádek s jedním sloupcem, který obsahuje všechny prvky
                dbc.Row(
                    children=[
                        dbc.Col(
                            [
                                # Karta s výstupy a vstupy
                                dbc.Card(
                                    [
                                        # Zobrazení zbývajících dotazů
                                        html.Div(
                                            id='remaining-queries-output',
                                            className='mb-3',
                                            style={
                                                "backgroundColor": "#FFFFFF",
                                                "borderColor": "#DE3873",
                                                "borderWidth": "2px",
                                                "borderStyle": "solid",
                                                "color": "#686868",
                                                "width": "100%",
                                                "padding": "10px",
                                                "textAlign": "center",
                                                "overflow": "hidden",
                                                "textOverflow": "ellipsis",
                                                "whiteSpace": "normal",
                                            }
                                        ),
                                        dbc.Spinner(html.Div(id="loading-component")),
                                        html.Div(
                                            dls.GridFade(
                                                [
                                                    html.Div(
                                                        collapsible_sections,
                                                        className="mb-5", 
                                                        style={
                                                            "width": "100%",
                                                            "textAlign": "justify",
                                                        },
                                                    ),
                                                ],
                                                color="#9F77B5",
                                            ),
                                            style={"width": "100%", "padding": "0", "margin": "0"},
                                        ),
                                        # Textarea Input
                                        dbc.Textarea(
                                            id="user-input",
                                            className="form-control mb-3",
                                            placeholder=localization["user-input-placeholder"],
                                            style={"height": "320px", "width": "100%"},
                                        ),
                                        # Tlačítko pro odeslání
                                        html.Button(
                                            localization["submit-button"],
                                            id="submit-user-input",
                                            className="btn btn-primary w-100 mb-3",
                                            style={"backgroundColor": "#3884DE", "border": "none"},
                                        ),
                                        dbc.Row([
                                            dbc.Col(
                                                html.Button(
                                                    localization["download-pdf-chat-button"],
                                                    id="pdf-download-button",
                                                    className="btn btn-primary w-100",
                                                    style={"backgroundColor": "#DE3873", "border": "none"},
                                                ),
                                                width=6
                                            ),
                                            dbc.Col(
                                                html.Button(
                                                    localization["new-thread-button"],
                                                    id="new-thread-button",
                                                    className="btn btn-primary w-100",
                                                    style={"backgroundColor": "#DE3873", "border": "none"},
                                                ),
                                                width=6
                                            )
                                        ], className="mb-3"),
                                        dcc.Download(id='pdf-download'),
                                    ],
                                    className="mb-3",
                                    style={"max-width": "1800px", "width": "100%"},
                                ),
                            ],
                            width=12,
                        )
                    ],
                )
            ],
        ),
    ]
)

def register_app_page_callbacks(app):

    # Callbacks
    @app.callback(
        Output("subject", "options"),
        [Input("subject-category", "value")],
    )
    def update_subject_dropdown(category):
        # Mock subjects based on category (replace with backend API call)
        subjects_map = {
            "Humanities": ["Art", "History", "Philosophy"],
            "Natural Sciences": ["Biology", "Chemistry", "Physics"],
            "Others": ["Logic", "General Studies"],
        }
        return [{"label": subj, "value": subj} for subj in subjects_map.get(category, [])]

    @app.callback(
        Output("lesson-methods-container", "children"),
        [Input("submit-user-input", "n_clicks")],
        [State("subject-category", "value"), State("subject", "value"), State("min-age", "value"), State("max-age", "value"), State("duration", "value")],
    )
    def generate_lesson_methods(n_clicks, category, subject, min_age, max_age, duration):
        if not n_clicks:
            return []

        # Mock backend response (replace with FastAPI call)
        mock_methods = [
            {
                "name": "Introduction to Art",
                "description": "Learn basic art techniques.",
                "duration": 30,
            },
            {
                "name": "Basics of Chemistry",
                "description": "Explore fundamental chemical reactions.",
                "duration": 45,
            },
        ]

        # Dynamically create collapsible sections based on methods
        collapsible_children = []
        for i, method in enumerate(mock_methods, start=1):
            collapsible_children.append(
                dbc.Collapse(
                    id=f"lesson-method-{i}",
                    is_open=True,  # Default to open; adjust as needed
                    children=html.Div([
                        html.H5(f"{method['name']}", className="mb-2"),
                        html.P(f"Description: {method['description']}", className="mb-1"),
                        html.P(f"Duration: {method['duration']} minutes"),
                    ]),
                )
            )

        return collapsible_children