import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go

app = dash.Dash(__name__)
server = app.server


datasets = ['./dataset/time_series_19-covid-Confirmed.csv', './dataset/time_series_19-covid-Deaths.csv', './dataset/time_series_19-covid-Recovered.csv']

data = []
for i in datasets:
#     data.append(pd.read_csv('./COVID-19/csse_covid_19_data/csse_covid_19_time_series/'+i))
    data.append(pd.read_csv('./' + i))



# Grouping the data according to the Country/Region
def transform_pipeline(dataset): # implement arbitrary arugument list in this function for giving dropping columns option
    ds = dataset.drop(columns=['Lat', 'Long', 'Province/State'])
    sum_data = (ds.groupby('Country/Region').sum().reset_index()).T
    cleaned_data = sum_data.rename(columns=sum_data.iloc[0]).drop(sum_data.index[0])
    return cleaned_data.apply(pd.to_numeric)

clean_data = []
for dataset_item in data:
    clean_data.append(transform_pipeline(dataset_item))



dict_of_changes = {"China":"Mainland China", "Korea, South":"Republic of Korea", "Vietnam":"Viet Nam", 'Iran':'Iran (Islamic Republic of)'
                  , 'United Kingdom':"UK"}

for key, val in dict_of_changes.items():
    for idx in range(3):
        clean_data[idx][key] = clean_data[idx][val] + clean_data[idx][key]
        clean_data[idx].drop(columns=val, inplace=True)

new_cases = pd.DataFrame({"Confirmed": clean_data[0].iloc[-1]  - clean_data[0].iloc[-2],
               "Deaths": clean_data[1].iloc[-1]  - clean_data[1].iloc[-2],
              "Recovered": clean_data[2].iloc[-1]  - clean_data[2].iloc[-2]})


def create_dict_list_of_product():
    dictlist = []
    unique_list = new_cases.index.unique()
    for product_title in unique_list:
        dictlist.append({'value': product_title, 'label': product_title})
    return dictlist


dict_products = create_dict_list_of_product()
# print("New cases in World : (past 24 hours)")
# print(new_cases.sort_values(by="Confirmed", ascending=False).head(15))
# print("New cases in India : (past 24 hours)")
# print(new_cases.loc['India'])

initial_val = new_cases.sort_values(by="Confirmed", ascending=False).head(5).index
app.layout = html.Div([
    html.Div([
        html.H1('New Cases in the World'),
        html.H2('Choose a country'),
        dcc.Dropdown(
            id='product-dropdown',
            options=dict_products,
            multi=True,
            value = initial_val
        ),

    ], style={'width': '40%','float':'left','padding':'20px',
              'display': 'inline-block','padding-right':'20px'}),
    html.Div([
        html.H3('Cases in 24hrs'),
        html.Table(id='my-table'),
        html.P('')
    ], style={'width': '20%','margin':'auto','padding-left':'20px', 'display': 'inline-block'}),
    html.Div([
        html.H3('Pie Chart?'),
        dcc.Graph(id='pie-graph')
    ], style={'width': '30%','float':'right', 'display': 'inline-block'}),
    html.Div([
        html.H3('Total Confirmed Cases '),
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
              'border-top':'1px dashed grey'})
    ])


@app.callback(Output('confirmed-trend-graph', 'figure'), [Input('product-dropdown', 'value')])
def generate_confirm_graph(selected_dropdown_value):
    confirmed_filter = clean_data[0][selected_dropdown_value]

    data = timeline_confirmed(confirmed_filter, selected_dropdown_value)

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
                y=timeline,
                x=timeline.index,
                name=value
        )
        trace_list.append(trace)
    return trace_list

@app.callback(Output('increment-trend-graph', 'figure'), [Input('product-dropdown', 'value')])
def generate_increment_graph(selected_dropdown_value):
    confirmed_delta = clean_data[0].diff()
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


    selected_countries_filter = clean_data[0][selected_dropdown_value].iloc[-1]
    
    data = pie_confirmed(selected_countries_filter, selected_dropdown_value)
    layout = dict(title = 'Pie Chart')
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
    new_cases_ff = new_cases.reset_index().set_index('index', drop=False)
    new_cases_filter = new_cases_ff.loc[selected_dropdown_value]
    new_cases_filter = new_cases_filter.sort_values(by='Confirmed', ascending=False)
    # print(new_cases_filter)
    return [html.Tr([html.Th(col) for col in new_cases_filter.columns])] + [html.Tr([
        html.Td(new_cases_filter.iloc[i][col]) for col in new_cases_filter.columns
    ]) for i in range(min(len(new_cases_filter), max_rows))]


if __name__ == '__main__':
    app.run_server(debug=True)
