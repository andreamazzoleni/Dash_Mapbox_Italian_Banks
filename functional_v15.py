# Housekeeping

import dash
import dash_core_components as dcc
import dash_html_components as html
import os
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import json
import numpy as np
from fuzzywuzzy import fuzz, process
from matplotlib.colors import Normalize
from matplotlib import cm
from itertools import product
import copy
import matplotlib.pyplot as plt

mapbox_apikey = "pk.eyJ1IjoiYW5kcmVhbWF6em9sZW5pIiwiYSI6ImNqemQ2dWUwczAzbWMzZHBlb3h0b2RxNGoifQ.iN9TK8p2JFjQTZ8Ed9DrEA"

directory = "/Users/andreamazzoleni/Desktop"
os.chdir(directory)

# Set up databases

## coordinates
main = pd.read_excel('main_v2.xlsx')
all = main.Gruppo.drop_duplicates().tolist()
all.sort()
all = ['BBPM','BNP','BPB','BPER','BPS','CARIGE','CASA','CREDEM','CREVAL','DB','INTESA','MEDIOBANCA','MPS','SELLA','UBI','UNICREDIT']

## dropdown options
#opt = []
#for i in all:
#    opt.append({'label': f"{i}", 'value': f'{i}'})

opt =   [{'label': 'Banco BPM', 'value': 'BBPM'},
         {'label': 'BNP', 'value': 'BNP'},
         {'label': 'Banca Popolare di Bari', 'value': 'BPB'},
         {'label': 'BPER', 'value': 'BPER'},
         {'label': 'Banco Popolare di Sondrio', 'value': 'BPS'},
         {'label': 'Carige', 'value': 'CARIGE'},
         {'label': 'CASA', 'value': 'CASA'},
         {'label': 'Credem', 'value': 'CREDEM'},
         {'label': 'Credito Valtellinese', 'value': 'CREVAL'},
         {'label': 'Deutsche Bank', 'value': 'DB'},
         {'label': 'Intesa Sanpaolo', 'value': 'INTESA'},
         {'label': 'Mediobanca', 'value': 'MEDIOBANCA'},
         {'label': 'Monte dei Paschi', 'value': 'MPS'},
         {'label': 'Banca Sella', 'value': 'SELLA'},
         {'label': 'Unione Banche Italiane', 'value': 'UBI'},
         {'label': 'Unicredit', 'value': 'UNICREDIT'}]


## colors
colors = ['rgb(128,128,128)','rgb(0,128,128)','rgb(0,0,128)','rgb(0,255,0)','rgb(255,165,0)','rgb(255,255,0)']

## number of banks for histogram
count = []

for i in all:
    df1 = main[main['Gruppo'] == f'{i}']
    count.append(len(df1))

## Choropleth DB

os.chdir("/users/andreamazzoleni/desktop")

df = pd.read_excel("loans.xlsx",header=0)
df = df.set_index('Provincia')
df = pd.Series(df["Value"])
df['Milano'] =0
df['Roma'] =0

# Choropleth Map

with open('province_2019.geojson') as f:
     geojson = json.load(f)

n_provinces = len(geojson['features'])
provinces_names = []
for i in range(n_provinces):
    provinces_names.append( geojson['features'][i]['properties']['prov_name'] )

def get_centers():
    lon, lat =[], []

    for k in range(n_provinces):
        geometry = geojson['features'][k]['geometry']

        if geometry['type'] == 'Polygon':
            coords=np.array(geometry['coordinates'][0])
        elif geometry['type'] == 'MultiPolygon':
            coords=np.array(geometry['coordinates'][0][0])              # I am not sure why he takes two coords for MultiPolygon and one for Polygon, to check

        lon.append(sum(coords[:,0]) / len(coords[:,0]))
        lat.append(sum(coords[:,1]) / len(coords[:,1]))

    return lon, lat

def scalarmappable(cmap, cmin, cmax):
        colormap = cm.get_cmap(cmap)
        norm = Normalize(vmin=cmin, vmax=cmax)
        return cm.ScalarMappable(norm=norm, cmap=colormap)

def get_scatter_colors(sm, df):
    grey = 'rgba(128,128,128,1)'
    return ['rgba' + str(sm.to_rgba(m, bytes = True, alpha = 1)) if not np.isnan(m) else grey for m in df]

def get_colorscale(sm, df, cmin, cmax):
    xrange = np.linspace(0, 1, len(df))
    values = np.linspace(cmin, cmax, len(df))

    return [[i, 'rgba' + str(sm.to_rgba(v, bytes = True))] for i,v in zip(xrange, values) ]

def get_hover_text(df) :
    text_value = (df).round(2).astype(str) + "mln"
    with_data = '<b>{}</b> <br> {}'
    no_data = '<b>{}</b> <br> no data'

    return [with_data.format(p,v) if v != 'nan%' else no_data.format(p) for p,v in zip(df.index, text_value)]

# Run all the functions


# App Starts

external_stylesheets = [ 'https://codepen.io/amyoshino/pen/jzXypZ.css' ]

app = dash.Dash( __name__ , external_stylesheets=external_stylesheets )

app.title = "Bank Branches: Italy"


app.layout = html.Div(children = [

        # Heading
        html.Div(children = [
                html.H1(children = 'Bank Branches: Italy',
                        )
        ],className = 'row'),

        html.Div(children = [

            # Dropdown1
            html.Div(children =[
                html.P('Choose banks (max 2):'),
                dcc.Dropdown(
                        id = 'dropdown1',
                        options = opt,
                        multi = True,
                        value = [],
                        placeholder="Select a bank"
                        )
                    ],className='seven columns'),

            # Choropletic_checklist
            html.Div(children=[
                html.P('Choose economic indicator:'),
                dcc.Dropdown(
                        id = 'dropdown2',
                        options = [
                                    {'label' : 'Loans oustanding (excl. bad loans)', 'value' : 'loans' },
                                    {'label' : "Clients' assets under management/custody", 'value': 'AUM' }
                                    ],
                        value = 'loans',
                        multi = False
                        )
            ],className='five columns')

        ],className='row'),

        html.Div(children = [

            # Map
            html.Div(children=[
                dcc.Graph(
                        id = 'map',
                        )
                ],className='seven columns'),

            # Choropleth Map
            html.Div(children=[
                dcc.Graph(
                            id='choropleth-map'
                            )

            ],className='five columns')

        ],className = 'row'),

        html.Div(children=[

            # Histogram
            dcc.Graph(
                    id = 'bar-chart'
                    )

        ],className='row')

        ], className='ten columns offset-by-one')


@app.callback([
        Output('map','figure'),
        Output('bar-chart','figure')],
        [Input('dropdown1','value')]
        )

def multi_output(value):

    # Map

    append_data = []

    if value == []:
        add = go.Scattermapbox(
                                        lat = [45.472296],
                                        lon = [9.196582],
                                        mode = "markers",
                                        name = "UBS Italia",
                                        marker = go.scattermapbox.Marker(
                                            size = 6,
                                            color=colors[0]
                                            )
                                        )
        append_data.append(add)

    else:
        for i in range(len(value)):
            add = go.Scattermapbox(
                                        lat = list(main['lat'][main['Gruppo'] == value[i]]),
                                        lon = list(main['lon'][main['Gruppo'] == value[i]]),
                                        mode = "markers",
                                        name = value[i],
                                        marker = go.scattermapbox.Marker(
                                            size = 6,
                                            color=colors[i]
                                        )
                                    )
            append_data.append(add)


    figure1 = go.Figure(
                        data = append_data,
                        layout = go.Layout(
                                    autosize=True,
                                    mapbox= dict(
                                                accesstoken=mapbox_apikey,
                                                bearing=0,
                                                pitch=0,
                                                zoom=5,
                                                center= dict(   lat=45.464180,
                                                                lon=9.190299),
                                                style="open-street-map"),
                                    height=600
                            )
                        )

    # Map 2

    order = pd.DataFrame([all,count]).transpose().sort_values(1,ascending=False)

    figure2 = go.Figure()

    if len(value)>1:
        total = []

        for i in value:
            val = order.loc[ order[0] == i , 1].tolist()
            total.append(val[0])

        figure2.add_trace(
                go.Histogram(
                        histfunc="sum",
                        y=[sum(total)],
                        x=['combo'],
                        name = "Combo",
                        marker_color='#330C73',
                        opacity=0.75
                        ),
                )

    figure2.add_trace(
            go.Histogram(
                    histfunc="sum",
                    y=order[1],
                    x=order[0],
                    name = "Historical",
                    marker_color='#70db70',
                    opacity=0.75
                    )
            )

    # Choropletic Map

    return figure1, figure2

@app.callback(
            Output('choropleth-map','figure'),
            [Input('dropdown2','value')]
            )

def update_choropleth(value):

    var = value

    df = pd.read_excel(f"{var}.xlsx").set_index('Provincia')
    df = pd.Series(df['Value'])

    df_reindexed = df.reindex(index = provinces_names)   # give the same index order as the geojson

    colormap = 'Blues'
    cmin = df_reindexed.min()
    cmax = df_reindexed.max()

    lons, lats = get_centers()

    sm = scalarmappable(colormap, cmin, cmax)
    scatter_colors = get_scatter_colors(sm, df_reindexed)
    colorscale = get_colorscale(sm, df_reindexed, cmin, cmax)
    hover_text = get_hover_text(df_reindexed)

    tickformat = "#,###.0" #.0%

    layers=([  dict(sourcetype = 'geojson',
                    source = geojson['features'][k],
                    below  = "",
                    type   = 'fill',
                    line   = dict(width = 1),
                    color  = scatter_colors[k],
                    opacity = 0.8
                                            ) for k in range(n_provinces)
                                            ]
            )

    figure = go.Figure(
                go.Scattermapbox(
                    lat=lats,
                    lon=lons,
                    mode='markers',
                    text=hover_text,
                    marker = go.scattermapbox.Marker(
                               size = 1,
                                color = scatter_colors,
                                showscale = True,
                                cmin = df_reindexed.min(),
                                cmax = df_reindexed.max(),
                                colorscale = colorscale,
                                colorbar = dict(tickformat = tickformat )
                                ),
                    showlegend=False,
                    hoverinfo='text'
                            ),
                layout = dict(#title="Choropletic Map",
                      autosize=True,
#                     width=700,
                      height=600,
                      hovermode='closest',
                      hoverdistance = 30,
                      mapbox=dict(accesstoken=mapbox_apikey,
                                  layers=layers,
                                  bearing=0,
                                  center=dict(
                                  lat = 45.472296,
                                  lon = 9.196582),
                                  pitch=0,
                                  zoom=4.5,
                                  style = 'open-street-map'
                            )
                      )
                )

    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
