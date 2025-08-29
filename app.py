import dash
from dash import dcc, html, Input, Output, callback, dash_table
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import dash_bootstrap_components as dbc
import numpy as np

# Initialize the Dash app with Bootstrap theme
app                 = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title           = "MPA data explorer"

with open ("index.html", "r") as f:
    app.index_string    = f.read()


from rimpa import site_fish, observe_fish

# Define the layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.Br(),
            html.H3("Fish Transect Explorer", className="text-center text-primary mb-5"),
            html.Hr()
        ])
    ]),
    
    # Control Panel
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Filters", className="card-title"),
                    # dbc.Row([

                    # ]),
                    dbc.Row([
                        dbc.Col([
                            html.Label("MPA/Control:"),
                            dcc.Dropdown(
                                id='mpa-control-filter',
                                options=[{'label': 'All', 'value': 'all'}] + 
                                        [{'label': val, 'value': val} for val in observe_fish['control/mpa'].unique()],
                                value='all',
                                clearable=False
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("Year:"),
                            dcc.Dropdown(
                                id='year-filter',
                                options=[{'label': 'All', 'value': 'all'}] + 
                                        [{'label': str(year), 'value': year} for year in sorted(observe_fish['year'].unique())],
                                value='all',
                                clearable=False
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("Trophic Level:"),
                            dcc.Dropdown(
                                id='trophic-filter',
                                options=[{'label': 'All', 'value': 'all'}] + 
                                        [{'label': val, 'value': val} for val in observe_fish['trophic'].unique()],
                                value='all',
                                clearable=False
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("Family:"),
                            dcc.Dropdown(
                                id='family-filter',
                                options=[{'label': 'All', 'value': 'all'}] + 
                                        [{'label': val, 'value': val} for val in observe_fish['family'].unique()],
                                value='all',
                                clearable=False
                            )
                        ], width=3)
                    ], className="mt-2")
                ])
            ])
        ])
    ], className="mb-4"),
    
    # Key Metrics Row
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="total-observations", className="text-center"),
                    html.P("Total Observations", className="text-center text-muted")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="total-species", className="text-center"),
                    html.P("Unique Species", className="text-center text-muted")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="avg-biomass", className="text-center"),
                    html.P("Avg Biomass (kg/ha)", className="text-center text-muted")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="total-sites", className="text-center"),
                    html.P("Survey Sites", className="text-center text-muted")
                ])
            ])
        ], width=3)
    ], className="mb-4"),
    
    # Main visualization row
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Biomass Distribution by MPA/Control"),
                    dcc.Graph(id="biomass-boxplot")
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Species Diversity by Trophic Level"),
                    dcc.Graph(id="trophic-diversity")
                ])
            ])
        ], width=6)
    ], className="mb-4"),
    
    # Second visualization row
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Temporal Trends"),
                    dcc.Graph(id="temporal-trends")
                ])
            ])
        ], width=7),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Size Distribution"),
                    dcc.Graph(id="size-distribution")
                ])
            ])
        ], width=5)
    ], className="mb-4"),
    
    # Site characteristics row
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Site Locations"),
                    dcc.Graph(id="site-map", config={'scrollZoom': True})
                ])
            ])
        ], width=8),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Environmental Factors"),
                    dcc.Graph(id="environmental-factors")
                ])
            ])
        ], width=4)
    ], className="mb-4"),
    
    # Data table row
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Filtered Data Summary"),
                    dash_table.DataTable(
                        id='summary-table',
                        columns=[],
                        data=[],
                        page_size=10,
                        sort_action="native",
                        filter_action="native",
                        # style_cell={'textAlign': 'left', 'fontSize': 12},
                        # style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                        style_cell={
                            'textAlign': 'left', 
                            'fontSize': 12,
                            'backgroundColor': '#374151',
                            'color': 'white',
                            'border': '1px solid #6b7280'
                        },
                        style_header={
                            'backgroundColor': '#1f2937', 
                            'fontWeight': 'bold',
                            'color': 'white',
                            'border': '1px solid #6b7280'
                        },
                        style_filter={
                            'backgroundColor': '#374151',
                            'color': 'white'
                        }


                    )
                ])
            ])
        ])
    ])
], fluid=True)

# Callback for updating all visualizations based on filters
@app.callback(
        
    [Output('total-observations', 'children'),
     Output('total-species', 'children'),
     Output('avg-biomass', 'children'),
     Output('total-sites', 'children'),
     Output('biomass-boxplot', 'figure'),
     Output('trophic-diversity', 'figure'),
     Output('temporal-trends', 'figure'),
     Output('size-distribution', 'figure'),
     Output('site-map', 'figure'),
     Output('environmental-factors', 'figure'),
     Output('summary-table', 'data'),
     Output('summary-table', 'columns')],

    [Input('mpa-control-filter', 'value'),
     Input('year-filter', 'value'),
     Input('trophic-filter', 'value'),
     Input('family-filter', 'value')]
)

def update_dashboard(mpa_control, year, trophic, family):
    # Filter the data based on selections
    filtered_data = observe_fish.copy()
    
    if mpa_control != 'all':
        filtered_data = filtered_data[filtered_data['control/mpa'] == mpa_control]
    if year != 'all':
        filtered_data = filtered_data[filtered_data['year'] == year]
    if trophic != 'all':
        filtered_data = filtered_data[filtered_data['trophic'] == trophic]
    if family != 'all':
        filtered_data = filtered_data[filtered_data['family'] == family]
    
    # Calculate metrics
    total_obs = len(filtered_data)
    unique_species = filtered_data['species'].nunique()
    avg_biomass = f"{filtered_data['biomass_(kg/ha)'].mean():.2f}"
    total_sites = filtered_data['site_name'].nunique()
    
    # Create visualizations
    
    # 1. Biomass boxplot
    biomass_fig = px.box(filtered_data, x='control/mpa', y='biomass_(kg/ha)', 
                        color='control/mpa', title="", template="plotly_dark")
    biomass_fig.update_layout(height=400, margin=dict(t=20, b=20, l=20, r=20), legend=dict(orientation="h", yanchor="bottom",y=1.05, x=-0.05))
    
    # 2. Trophic diversity
    trophic_counts = filtered_data.groupby('trophic')['species'].nunique().reset_index()
    trophic_fig = px.bar(trophic_counts, x='trophic', y='species', 
                        color='trophic', title="", template="plotly_dark")
    trophic_fig.update_layout(height=400, margin=dict(t=20, b=20, l=20, r=20))
    
    # 3. Temporal trends
    temporal_data = filtered_data.groupby(['year', 'month']).agg({
        'biomass_(kg/ha)': 'mean',
        'density_(n/ha)': 'mean'
    }).reset_index()
    temporal_data['date'] = pd.to_datetime(temporal_data[['year', 'month']].assign(day=1))
    
    temporal_fig = make_subplots(specs=[[{"secondary_y": True}]])
    temporal_fig.add_trace(
        go.Scatter(x=temporal_data['date'], y=temporal_data['biomass_(kg/ha)'], 
                  name="Biomass", line=dict(color="skyblue")),
        secondary_y=False
    )
    temporal_fig.add_trace(
        go.Scatter(x=temporal_data['date'], y=temporal_data['density_(n/ha)'], 
                  name="Density", line=dict(color="yellow")),
        secondary_y=True
    )
    temporal_fig.update_xaxes(title_text="Date")
    temporal_fig.update_yaxes(title_text="Biomass (kg/ha)", secondary_y=False)
    temporal_fig.update_yaxes(title_text="Density (n/ha)", secondary_y=True)
    temporal_fig.update_layout(height=400, margin=dict(t=20, b=20, l=20, r=20), template="plotly_dark", legend=dict(orientation="h", yanchor="bottom", y=1.05, x=-0.05))
    
    # 4. Size distribution
    size_fig = px.histogram(filtered_data, x='size_(cm)', nbins=20, 
                           color='trophic', title="")
    size_fig.update_layout(height=400, margin=dict(t=20, b=20, l=20, r=20), template="plotly_dark", legend=dict(orientation="v", yanchor="top", xanchor="left", y=0.95, x=1.06))
    
    # 5. Site map
    site_data = site_fish.merge(
        filtered_data.groupby('sea_site_id').agg({
            'biomass_(kg/ha)': 'mean',
            'density_(n/ha)': 'mean'
        }).reset_index(),
        on='sea_site_id', how='inner'
    )
    
    map_fig = px.scatter_mapbox(site_data, lat="latitude", lon="longitude",
                               size="biomass_(kg/ha)", color="mpa/control",
                               hover_data=["site_name", "mpa"],
                               mapbox_style="carto-darkmatter",
                               zoom=6)
    map_fig.update_layout(height=600, margin=dict(t=20, b=20, l=20, r=20), template="plotly_dark", legend=dict(orientation="h", yanchor="bottom", xanchor="right", y=-0.1, x=1.0))
    
    # 6. Environmental factors
    env_data = site_fish.merge(
        filtered_data.groupby('sea_site_id')['biomass_(kg/ha)'].mean().reset_index(),
        on='sea_site_id', how='inner'
    )
    env_fig = px.scatter(env_data, x='visibility', y='biomass_(kg/ha)',
                        color='bleaching', size='biomass_(kg/ha)',
                        title="")
    env_fig.update_layout(height=600, margin=dict(t=20, b=20, l=20, r=20), template="plotly_dark")
    
    # 7. Summary table
    summary_data = filtered_data.groupby(['family', 'trophic', 'control/mpa']).agg({
        'species': 'nunique',
        'biomass_(kg/ha)': 'mean',
        'density_(n/ha)': 'mean',
        'size_(cm)': 'mean'
    }).round(2).reset_index()
    
    summary_columns = [{"name": col, "id": col} for col in summary_data.columns]
    summary_data_dict = summary_data.to_dict('records')
    
    return (f"{total_obs:,}", f"{unique_species:,}", avg_biomass, f"{total_sites:,}",
            biomass_fig, trophic_fig, temporal_fig, size_fig, map_fig, env_fig,
            summary_data_dict, summary_columns)


if __name__ == '__main__':
    app.run(debug=True)
