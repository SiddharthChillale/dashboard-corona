import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import os
from datetime import datetime

import live_data
print("\n:: Outside in the main now ::")

app = dash.Dash(__name__)
server = app.server
# app.title = 'COVID-19 Visualization'


def get_clean_data():
    now = datetime.now()

    print("\n:: Getting clean data ...", now.strftime("%d/%m/%Y %H:%M:%S"))
    # datasets = ['./dataset/time_series_19-covid-Confirmed.csv', './dataset/time_series_19-covid-Deaths.csv', './dataset/time_series_19-covid-Recovered.csv']

    datasets = ["./dataset/time_series_covid19_confirmed_global.csv",
         "./dataset/time_series_covid19_deaths_global.csv"]

    data = []
    for i in datasets:
        # data.append(pd.read_csv('./COVID-19/csse_covid_19_data/csse_covid_19_time_series/'+i))
        data.append(pd.read_csv(i))


    # Grouping the data according to the Country/Region
    def transform_pipeline(dataset): # implement arbitrary arugument list in this function for giving dropping columns option
        ds = dataset.drop(columns=['Lat', 'Long', 'Province/State'])
        sum_data = (ds.groupby('Country/Region').sum().reset_index()).T
        cleaned_data = sum_data.rename(columns=sum_data.iloc[0]).drop(sum_data.index[0])
        return cleaned_data.apply(pd.to_numeric)

    clean_data = []
    for dataset_item in data:
        clean_data.append(transform_pipeline(dataset_item))

    return clean_data



def get_new_cases():
    now = datetime.now()

    
    print(":: Getting new cases ...", now.strftime("%d/%m/%Y %H:%M:%S"))
    clean_data = get_clean_data() ## get clean_data dataframe here
    new_cases = pd.DataFrame({"Confirmed": clean_data[0].iloc[-1]  - clean_data[0].iloc[-2],
                "Deaths": clean_data[1].iloc[-1]  - clean_data[1].iloc[-2]})

    return new_cases

def create_dict_list_of_product():
    dictlist = []
    new_cases = get_new_cases() ## get new cases here
    unique_list = new_cases.index.unique()
    for product_title in unique_list:
        dictlist.append({'value': product_title, 'label': product_title})
    return dictlist


CLEAN_DATA = get_clean_data()
NEW_CASES = get_new_cases()
dict_products = create_dict_list_of_product()
initial_val = NEW_CASES.sort_values(by="Confirmed", ascending=False).head(5).index


app.layout = html.Div([
    html.Div([
        html.H1('New Cases in the World'),
        html.H2('Choose a country'),
        html.Div(id='timer',
                 children= 0),
        dcc.Dropdown(
            id='product-dropdown',
            options=dict_products,
            multi=True,
            value = initial_val
        ),
        dcc.Interval(
            id='timer-updater',
            interval = 43200*1000,
            n_intervals=0
        )

    ], style={'width': '50%',
              'display': 'inline-block',
              "padding":'20px',
              'border-top':'1px dashed grey'}),

    html.Div([
        html.Div([
            html.H3('Proportional Graph'),
            dcc.Graph(id='pie-graph')
        ], style={'width': '50%','float':'left', 'display': 'inline'}),
        html.Div([
            html.H3('Cases in 24hrs'),
            html.Table(id='my-table'),
            html.P('')
        ], style={'width': '50%','margin':'20px', 'display': 'inline'})
        ],style={'width': '100%',
              'display': 'inline-block',
              'border-top':'1px dashed grey'}),

    html.Div([
        html.H3('Total Confirmed Cases over 3 weeks'),
        dcc.Graph(id='confirmed-trend-graph'),
        html.P('')
    ], style={'width': '100%',
              'display': 'inline-block',
              'border-top':'1px dashed grey'}),
              
    html.Div([
        html.H3('How much Confirmed cases increase daily ?'),
        dcc.Graph(id='increment-trend-graph'),
        html.P('')
    ], style={'width': '100%',
              'display': 'inline-block',
              'border-top':'1px dashed grey'}),
              
    html.Div([
        html.H3('Death counts over 3 weeks'),
        dcc.Graph(id='confirmed-death-graph'),
        html.P('')
    ], style={'width': '100%',
              'display': 'inline-block',
              'border-top':'1px dashed grey'})
    ])


@app.callback(Output('confirmed-trend-graph', 'figure'),
             [Input('product-dropdown', 'value')])
def generate_confirm_graph(selected_dropdown_value):
    print("\n::For confirm-graph")
    clean_data = CLEAN_DATA.copy()
    confirmed_filter = clean_data[0][selected_dropdown_value]

    data = timeline_confirmed(confirmed_filter, selected_dropdown_value)

    layout = dict(title = 'Confirmed Cases Timeline',
                  xaxis = dict(title='Days'),
                  yaxis = dict(title='Number of Confirmed cases'))

    figure = dict(data=data, layout=layout)
    return figure

@app.callback(Output('confirmed-death-graph', 'figure'),
             [Input('product-dropdown', 'value')])
def generate_confirm_graph(selected_dropdown_value):
    print("\n::For confirm-graph")
    clean_data = CLEAN_DATA.copy()
    death_filter = clean_data[1][selected_dropdown_value]

    data = timeline_death(death_filter, selected_dropdown_value)

    layout = dict(title = 'Confirmed Cases Timeline',
                  xaxis = dict(title='Days'),
                  yaxis = dict(title='Number of Confirmed cases'))

    figure = dict(data=data, layout=layout)
    return figure



def timeline_confirmed(timeline_data, selected_dropdown_value):
    trace_list = []
    for value in selected_dropdown_value:
        timeline = timeline_data[value]

        trace = go.Scatter(
                y=timeline.tail(21),
                x=timeline.tail(21).index,
                name=value,
                mode='lines+markers'
        )
        trace_list.append(trace)
    return trace_list



def timeline_death(timeline_data, selected_dropdown_value):
    trace_list = []
    for value in selected_dropdown_value:
        timeline = timeline_data[value]

        trace = go.Scatter(
                y=timeline.tail(21),
                x=timeline.tail(21).index,
                fill='tonexty',
                name=value,
                mode='lines+markers'
        )
        trace_list.append(trace)
    return trace_list


@app.callback(Output('increment-trend-graph', 'figure'),
             [Input('product-dropdown', 'value')])
def generate_increment_graph(selected_dropdown_value):
    print("\n:: For increment-trend-graph")

    clean_confirm_data = CLEAN_DATA.copy()
    confirmed_delta = clean_confirm_data[0].diff()
    confirmed_delta.iloc[0] = 0
    confirmed_delta_filter = confirmed_delta[selected_dropdown_value]

    data = timeline_confirmed(confirmed_delta_filter, selected_dropdown_value)

    layout = dict(title = 'Confirmed Cases Increment Timeline',
                  xaxis = dict(title='Days'),
                  yaxis = dict(title='Number of New Confirm cases'))

    figure = dict(data=data, layout=layout)
    return figure




@app.callback(Output('pie-graph', 'figure'), [Input('product-dropdown', 'value')])
def generate_pie_graph(selected_dropdown_value):
    print("#################################################")

    print("\n:: For pie-graph")

    clean_data = CLEAN_DATA.copy()
    selected_countries_filter = clean_data[0][selected_dropdown_value].iloc[-1]

    data = pie_confirmed(selected_countries_filter, selected_dropdown_value)
    layout = dict(title = 'Pie Chart for proportions')
    figure = dict(data=data, layout=layout)

    return figure


def pie_confirmed(selected_countries_filter, selected_dropdown_value):
    pie = go.Pie(labels=selected_dropdown_value,
                 values=selected_countries_filter,
                 textinfo='label+percent',
                 insidetextorientation='radial',
                 hole=0.3 )
    return [pie]


@app.callback(Output('my-table', 'children'), [Input('product-dropdown', 'value')])
def generate_table(selected_dropdown_value, max_rows=20):
    new_cases = NEW_CASES.copy()
    new_cases_ff = new_cases.reset_index().set_index('index', drop=False)
    new_cases_filter = new_cases_ff.loc[selected_dropdown_value]
    new_cases_filter = new_cases_filter.sort_values(by='Confirmed', ascending=False)
    # print(new_cases_filter)
    return [html.Tr([html.Th(col) for col in new_cases_filter.columns])] + [html.Tr([
        html.Td(new_cases_filter.iloc[i][col]) for col in new_cases_filter.columns
    ]) for i in range(min(len(new_cases_filter), max_rows))]


@app.callback(Output('timer', 'children'), 
              [Input('timer-updater', 'n_intervals')])
def data_changer(n):
    now = datetime.now()
  
    print("\n:: Downloading ...") 
    
    # print("\nData Changing for ", n, " times")
    os.system("python live_data.py")

    print("\n:: Reading from datafiles ...", now.strftime("%d/%m/%Y %H:%M:%S"), "::")

    CLEAN_DATA = get_clean_data()
    NEW_CASES = get_new_cases()

    return [
        html.Div([
            html.H2('Last updated : ' + now.strftime("%d/%m/%Y %H:%M:%S")),
            html.H3('Updates every 12 hours')
            ])
        ]

if __name__ == '__main__':
    app.run_server(debug=True)
