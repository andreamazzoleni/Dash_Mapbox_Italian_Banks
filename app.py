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
import matplotlib.pyplot as plt
import urllib.request as request
from urllib.request import urlopen
import csv
mapbox_apikey = "pk.eyJ1IjoiYW5kcmVhbWF6em9sZW5pIiwiYSI6ImNqemQ2dWUwczAzbWMzZHBlb3h0b2RxNGoifQ.iN9TK8p2JFjQTZ8Ed9DrEA"

# Set up databases

## coordinates
main = pd.read_csv("https://raw.githubusercontent.com/andreamazzoleni/Dash_Mapbox_Italian_Banks/master/main_v2.csv")
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


# App Starts

external_stylesheets = [ 'https://codepen.io/amyoshino/pen/jzXypZ.css' ]

app = dash.Dash( __name__ , external_stylesheets=external_stylesheets )

server = app.server

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
                    ],className='twelve columns'),

        ],className='row'),

        html.Div(children = [

            # Map
            html.Div(children=[
                dcc.Graph(
                        id = 'map',
                        )
                ],className='twelve columns'),
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

    return figure1, figure2


if __name__ == '__main__':
    app.run_server(debug=True)
