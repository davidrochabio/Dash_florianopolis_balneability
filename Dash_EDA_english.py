import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import plotly.graph_objs as go
import plotly.figure_factory as ff


# reads the csv and parses the dateTime column
df = pd.read_csv('df_english.csv', sep=';', index_col=0, parse_dates=['dateTime'])

features_points = pd.read_excel('features_points.xlsx')

map1 = px.scatter_mapbox(
    features_points, lat='lat', lon='long', hover_data=['point', 'balneary', 'reference', 'location', 'fresh_water', 'drenage_beach', 'drenage_point'], 
    mapbox_style='carto-positron', center={"lat": -27.61587, "lon": -48.48378}, zoom=8)

years = list(df.dateTime.dt.year.unique())
years.append('All the years')
points = list(df.point.sort_values().unique())
stats_list = ['Description of the data (df.describe())', 'Stats of E. Coli per point', 
              'Balneability condition per point', 'Stats of E. Coli and amount of rain', 
              'Stats of E. Coli per beach and point that have drenages', 'Stats of E. Coli per year',
              'Stats of E. Coli per month']

#-----------------------------------------------------------------------------
### Summary Stats

describe = df.describe().reset_index()

summary_stats_point = df.groupby('point').agg({'dateTime': 'count', 'e_coli': ['mean', 'median', 'var', 'std']}).reset_index()
summary_stats_point.columns = summary_stats_point.columns.droplevel()

cross_condit = pd.crosstab(df.point, df.condition, margins=True, margins_name='Total of measures').reset_index()
cross_condit['Percentage Not Good'] = cross_condit['IMPRÓPRIA'] / cross_condit['Total of measures'] * 100
cross_condit['Percentage Good'] = cross_condit['PRÓPRIA'] / cross_condit['Total of measures'] * 100
cross_condit['Percentage Indeterminate'] = cross_condit['INDETERMINADO'] / cross_condit['Total of measures'] * 100
cross_condit

summary_stats_rain = df.groupby('rain')['e_coli'].agg(['mean', 'median', 'var', 'std']).reset_index()

summary_stats_drenage = df.groupby(['fresh_water', 'drenage_beach', 'drenage_point'])['e_coli'].agg(['mean', 'median', 'var', 'std']).reset_index()

summary_stats_year = df.groupby(df.dateTime.dt.year).agg({'dateTime': 'count', 'e_coli': ['mean', 'median', 'var', 'std']}).reset_index()
summary_stats_year.columns = summary_stats_year.columns.droplevel()

summary_stats_month = df.groupby(df.dateTime.dt.month).agg({'dateTime': 'count', 'e_coli': ['mean', 'median', 'var', 'std']}).reset_index()
summary_stats_month.columns = summary_stats_month.columns.droplevel()

#-----------------------------------------------------------------------------
### Dashboard

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets) 

app.layout = html.Div([
    html.Div([
        html.H1(
            children='Balneability Analysis | Florianópolis - SC, Brazil',
            style={
                'textAlign' : 'center',
            }
        ),
        dcc.Graph(id='map1', figure=map1)
    ]),
    
    html.Div([
        html.Div([
            dcc.Markdown('''###### Point'''), 
            dcc.Dropdown(
                id='drop_point1',
                options=[{'label': i, 'value': i} for i in points],
            ),
            dcc.Markdown('''###### Year'''),
            dcc.Dropdown(
                id='drop_years1',
                options=[{'label': i, 'value': i} for i in years],
                value='All the years'
            ),
            dcc.Graph(id='graph1'),
            dcc.Graph(id='graph3'),
            dcc.Graph(id='graph5'),
            dcc.Graph(id='graph7'),
        ], className='six columns'),
        html.Div([
            dcc.Markdown('''###### Point'''), 
            dcc.Dropdown(
                id='drop_point2',
                options=[{'label': i, 'value': i} for i in points],
            ),
            dcc.Markdown('''###### Year'''),
            dcc.Dropdown(
                id='drop_years2',
                options=[{'label': i, 'value': i} for i in years],
                value='All the years'
            ),
            dcc.Graph(id='graph2'),
            dcc.Graph(id='graph4'),
            dcc.Graph(id='graph6'),
            dcc.Graph(id='graph8'),
        ], className='six columns'),
    ]),
    
    html.Div([
        html.H4(
            children='Stats Tables',
            style={
                'textAlign' : 'center',
            }
        ),
        dcc.Dropdown(
            id='drop_stats',
            options=[{'label': i, 'value': i} for i in stats_list],
        ),
        dash_table.DataTable(
            id='table',
            page_size=10,
            data=[],
        ),
        html.H1(
            children='__________________________________________',
            style={
                'textAlign' : 'center',
            }
        ),
        html.H6(
            children='Data source: https://balneabilidade.ima.sc.gov.br/',
            style={
                'textAlign' : 'center',
            }
        ),
        html.H6(
            children='Created by: Andhros Guimarães e David Guimarães',
            style={
                'textAlign' : 'center',
            }
        ),
        html.H1(
            children='-----------------------------------------',
            style={
                'textAlign' : 'center',
            }
        ),
    ]),

])

@app.callback(
    [dash.dependencies.Output('graph1', 'figure'),
    dash.dependencies.Output('graph3', 'figure'),
    dash.dependencies.Output('graph5', 'figure'),
    dash.dependencies.Output('graph7', 'figure')],
    [dash.dependencies.Input('drop_point1', 'value'),
    dash.dependencies.Input('drop_years1', 'value')]
)

def update_graph(pointN, yearsN):
    
    if yearsN == 'All the years':
        filtered_df = df[df.point == pointN].sort_values(by='dateTime')
    
    else:
        filtered_df = df[(df.point == pointN) & (df.dateTime.dt.year == yearsN)].sort_values(by='dateTime')
        
    graph1 = px.histogram(filtered_df, x="e_coli", marginal="rug",
                          histnorm='percent', range_x=[0, 25000], nbins=25, 
                          title='Histogram - Percentage of measures x values of E. Coli')
    
    graph3 = px.violin(filtered_df, y='e_coli', title='Violin Plot - Distribution of E. Coli Values')
    
    graph5 = px.box(filtered_df, y='e_coli', title='Box plot - Distribution of E. Coli Values')
        
    graph7 = px.line(filtered_df, x='dateTime', y='e_coli', hover_data=df.columns,
                     title='Time Series - Values of E. Coli')
    
    return graph1, graph3, graph5, graph7

@app.callback(
    [dash.dependencies.Output('graph2', 'figure'),
    dash.dependencies.Output('graph4', 'figure'),
    dash.dependencies.Output('graph6', 'figure'),
    dash.dependencies.Output('graph8', 'figure')],
    [dash.dependencies.Input('drop_point2', 'value'),
    dash.dependencies.Input('drop_years2', 'value')]
)

def update_graph2(pointN2, yearsN2):
    if yearsN2 == 'All the years':
        filtered_df1 = df[df.point == pointN2].sort_values(by='dateTime')
    
    else:
        filtered_df1 = df[(df.point == pointN2) & (df.dateTime.dt.year == yearsN2)].sort_values(by='dateTime')

    graph2 = px.histogram(filtered_df1, x="e_coli", marginal="rug",
                          histnorm='percent', range_x=[0, 25000], nbins=25,
                          title='Histogram - Percentage of measures x values of E. Coli')
    
    graph4 = px.violin(filtered_df1, y='e_coli', title='Violin Plot - Distribution of E. Coli Values')
    
    graph6 = px.box(filtered_df1, y='e_coli', title='Box plot - Distribution of E. Coli Values')
    
    graph8 = px.line(filtered_df1, x='dateTime', y='e_coli', hover_data=df.columns,
                     title='Time Series - Values of E. Coli')

    return graph2, graph4, graph6, graph8


@app.callback(
    [dash.dependencies.Output('table', 'data'),
     dash.dependencies.Output('table', 'columns')],
    [dash.dependencies.Input('drop_stats', 'value')],
)

def update_stats_table(df):
    
    if df is None:
        columns = []
        data = []
    
    elif df == 'Description of the data (df.describe())':
        table = describe
        columns = [{"name": i, "id": i} for i in table.columns]
        data = table.to_dict('rows')
    
    elif df == 'Stats of E. Coli per point':
        table = summary_stats_point
        columns = [{"name": i, "id": i} for i in table.columns]
        data = table.to_dict('rows')
        
    elif df == 'Balneability condition per point':
        table = cross_condit
        columns = [{"name": i, "id": i} for i in table.columns]
        data = table.to_dict('rows')
        
    elif df == 'Stats of E. Coli and amount of rain':
        table = summary_stats_rain
        columns = [{"name": i, "id": i} for i in table.columns]
        data = table.to_dict('rows')
    
    elif df == 'Stats of E. Coli per beach and point that have drenages':
        table = summary_stats_drenage
        columns = [{"name": i, "id": i} for i in table.columns]
        data = table.to_dict('rows')
    
    elif df == 'Stats of E. Coli per year':
        table = summary_stats_year
        columns = [{"name": i, "id": i} for i in table.columns]
        data = table.to_dict('rows')
    
    elif df == 'Stats of E. Coli per month':
        table = summary_stats_month
        columns = [{"name": i, "id": i} for i in table.columns]
        data = table.to_dict('rows')
    
    return data, columns


if __name__ == '__main__':
    app.run_server(debug=True)