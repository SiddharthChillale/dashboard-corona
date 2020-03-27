import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import os
from datetime import datetime

import live_data
print("\n:: Outside in the main now ::")

app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.LUX])
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
        html.H1('New Cases in the World',
                className='navbar-brand '),
        html.Div(id='timer',
                 children= 0, 
                 className='nav-item'),
        html.Div([
            html.A('Github', href='https://github.com/SiddharthChillale/dashboard-corona', className='text-info')
        ], className='nav-item'),
        html.Div([
            html.A('Data-Source', href='https://github.com/CSSEGISandData/COVID-19', className='text-info')
        ], className='nav-item'),
        dcc.Interval(
            id='timer-updater',
            interval = 43200*1000,
            n_intervals=0
        )

    ], className='navbar navbar-expand-lg navbar-dark bg-primary'),

    html.Div(
        id='world-statistics',
        children = 0,
        className='p-1'
    ),


    html.Div([
        html.H2("Compare here", className='card-header  '),
        dcc.Dropdown(
            id='product-dropdown',
            options=dict_products,
            optionHeight=50,
            multi=True,
            value = initial_val,
            persistence=True,
            placeholder="Select countries to compare",
            className=" card-body text-primary "
        )
    ], className='form-group card border-success', style={'margin-top':'20px'}),
    html.Div([
        html.Div([
            html.H3('Proportional Graph'),
            dcc.Graph(id='pie-graph')
        ], style={'float':'left', 'width':'100%'}),

        html.Div([
            html.H3('Cases in 24hrs'),
            html.Table(id='my-table',
                       className='table table-hover')
        ])
        ]),

    html.Div([
        html.H3('Total Confirmed Cases over 3 weeks',
                className='card-header'),
        html.Div([
            dcc.Graph(id='confirmed-trend-graph')
        ],className='card-body')
        
    ], className="card border-primary mb-3"),
              

    html.Div([
        html.H3('Death counts over 3 weeks', className = 'card-header'),
        html.Div([

        dcc.Graph(id='confirmed-death-graph'),
        ],className='card-body')

    ], className="card border-danger mb-3"),
    html.Div([
        html.H3('How much Confirmed cases increase daily ?', className = 'card-header'),
        html.Div([
        dcc.Graph(id='increment-trend-graph')
        ],className='card-body')

    ], className="card border-info text-white bg-primary mb-3")
    ], className="p-3")


@app.callback(Output('confirmed-trend-graph', 'figure'),
             [Input('product-dropdown', 'value')])
def generate_confirm_graph(selected_dropdown_value):
    print("\n::For confirm-graph")
    clean_data = CLEAN_DATA.copy()
    confirmed_filter = clean_data[0][selected_dropdown_value]

    data = timeline_confirmed(confirmed_filter, selected_dropdown_value)

    layout = dict(title = 'Confirmed Cases Timeline',
                  paper_bgcolor = 'rgba(0,0,0,0)',
                  plot_bgcolor='rgba(0,0,0,0)',
                  font= {
                    'color': '#000000'
                },
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
                  paper_bgcolor = 'rgba(0,0,0,0)',
                  plot_bgcolor='rgba(0,0,0,0)',
                  font= {
                    'color': '#000000'
                },
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

def timeline_increment(timeline_data, selected_dropdown_value):
    trace_list = []
    for value in selected_dropdown_value:
        timeline = timeline_data[value]

        trace = go.Scatter(
                y=timeline.tail(21),
                x=timeline.tail(21).index,
                name=value,
                mode='lines+markers',
                line=dict(
                    width=5
                )
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
                fill='tozerox',
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

    data = timeline_increment(confirmed_delta_filter, selected_dropdown_value)

    layout = dict(title = 'Confirmed Cases Increment Timeline',
                  paper_bgcolor = 'rgba(0,0,0,0)',
                  plot_bgcolor='rgba(0,0,0,0)',
                  font= {
                    'color': '#ffffff'
                },
                  xaxis = dict(title='Days',
                               showgrid=False
                                ),
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
    layout = dict(title = 'Pie Chart for proportions',
                  paper_bgcolor = 'rgba(0,0,0,0)',
                  plot_bgcolor='rgba(0,0,0,0)',
                  font= {
                    'color': '#000000'
                },)
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
    return [html.Tr([html.Th(col) for col in new_cases_filter.columns], className='table-info')] + [html.Tr([
        html.Td(new_cases_filter.iloc[i][col]) for col in new_cases_filter.columns
    ], className='table-secondary') for i in range(min(len(new_cases_filter), max_rows))]





@app.callback(Output('world-statistics', 'children'), 
              [Input('timer-updater', 'n_intervals')])
def get_world_stat(n):
    
    total_data = CLEAN_DATA.copy()
    affected_total = total_data[0].sum().sum() 
    deaths_total = total_data[1].sum().sum()
    percent = (deaths_total / affected_total ) *100
    return [
        html.Div([
            html.H3('Total Confirmed Cases Worldwide :' + str(affected_total)  ,className='badge badge-info p-2'),
            html.H3('Total Deaths Cases Worldwide :' + str(deaths_total) ,className='badge badge-danger p-2 '),
            html.Div([
                html.Div(className='progress-bar bg-danger', style={"width":percent}),
                html.Div(className='progress-bar bg-info', style={"width":'75%'})                
            ], className='progress')
            ])
        ]




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
            html.H6('Last updated : ' + now.strftime("%d/%m/%Y %H:%M:%S"),className='text-success'),
            html.H6('Updates every 12 hours',className='text-info')
            ])
        ]

if __name__ == '__main__':
    app.run_server()
