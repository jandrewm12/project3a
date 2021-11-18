'''
This web service extends the Alphavantage api by creating a visualization module, 
converting json query results retuned from the api into charts and other graphics. 

This is where you should add your code to function query the api
'''
import requests
from datetime import datetime
from datetime import date
import pygal
import json


#Helper function for converting date
def convert_date(str_date):
    return datetime.strptime(str_date, '%Y-%m-%d').date()

# Modified convert_date() function to include time -- neccessary for intraday time series
def convert_datetime(str_datetime):
    return datetime.strptime(str_datetime, '%Y-%m-%d %H:%M:%S').date()

# converts choice to API-friendly text
def time_series_to_api_text(time_series_choice):
    if time_series_choice == "1": return "TIME_SERIES_INTRADAY"
    elif time_series_choice == "2": return "TIME_SERIES_DAILY"
    elif time_series_choice == "3": return "TIME_SERIES_WEEKLY"
    elif time_series_choice == "4": return "TIME_SERIES_MONTHLY"

# converts time series text to json-friendly text for querying
def time_series_to_json_text(time_series_text):
    if time_series_text == "TIME_SERIES_INTRADAY":
        new_time_series_text = "Time Series (5min)"
    elif time_series_text == "TIME_SERIES_DAILY":
        new_time_series_text = "Time Series (Daily)"
    elif time_series_text == "TIME_SERIES_WEEKLY": 
        new_time_series_text = "Weekly Time Series"
    elif time_series_text == "TIME_SERIES_MONTHLY":
        new_time_series_text = "Monthly Time Series"
    return new_time_series_text

# makes url for querying alphavantage API
def make_url(symbol, time_series):
    return "https://www.alphavantage.co/query?function=" + time_series_to_api_text(time_series) + "&symbol=" + symbol + "&interval=5min&outputsize=full&apikey=LIE8L1SQATAK0ZTM"

# gets json from url
def get_json(url):
    r = requests.get(url)
    return r.json()

# parses json
def parse_json(data):
    string_dictionary = json.dumps(data)
    parsed_json = json.loads(string_dictionary)
    return parsed_json

# selects graph type based on selection
def choose_graph(chart_type):
    if chart_type == '1': line_chart = pygal.Bar(x_label_rotation=40)
    elif chart_type == '2': line_chart = pygal.Line(x_label_rotation=40)
    return line_chart

# makes chart using user selected data
def make_chart(symbol, chart_type, time_series, start_date, end_date):

    url = make_url(symbol, time_series)
    json_data = get_json(url)
    parsed_json = parse_json(json_data)

    ts = time_series_to_json_text(time_series_to_api_text(time_series))
    print(ts)

    open_list = []
    high_list = []
    low_list = []
    close_list = []
    date_list = []

    for date in parsed_json[ts]:
        if ts == "Time Series (5min)":
            if start_date <= convert_datetime(date) and convert_datetime(date) <= end_date:
                date_list.append(date)
                open_list.append(float(parsed_json[ts][date]["1. open"]))
                high_list.append(float(parsed_json[ts][date]["2. high"]))
                low_list.append(float(parsed_json[ts][date]["3. low"]))
                close_list.append(float(parsed_json[ts][date]["4. close"]))
            else: continue
        else:

            if start_date <= convert_date(date) and convert_date(date) <= end_date:
                date_list.append(date)
                open_list.append(float(parsed_json[ts][date]["1. open"]))
                high_list.append(float(parsed_json[ts][date]["2. high"]))
                low_list.append(float(parsed_json[ts][date]["3. low"]))
                close_list.append(float(parsed_json[ts][date]["4. close"]))
            else: continue

    date_list.reverse()
    open_list.reverse()
    high_list.reverse()
    low_list.reverse()
    close_list.reverse()

    title = "Stock Data for " + symbol + ": " + str(start_date) + " to " + str(end_date)

    chart = choose_graph(chart_type)
    chart.title = title
    chart.x_labels = map(str, date_list)
    chart.add('Open', open_list)
    chart.add('High', high_list)
    chart.add('Low', low_list)
    chart.add('Close', close_list)

    chart = chart.render_data_uri()
    return chart

# gets symbols for populating symbol choice field.
def get_symbols():
    f = open("symbols.json", "r")
    data = json.load(f)
    parsed_symbols = parse_json(data)
    f.close()

    symbol_list = []

    for company in parsed_symbols:
        symbol_list.append(company['ACT Symbol'])

    list_of_symbol_tuples = []
    for symbol in symbol_list:
        symbol_tuple = (symbol, symbol)
        list_of_symbol_tuples.append(symbol_tuple)

    return list_of_symbol_tuples