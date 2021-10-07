"""
Main file for the dash server
"""
# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import yfinance as yf

# An example of how to apply style sheets
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# line plot object that is dynamically loaded
ticker = yf.Ticker("AAPL")
# reset the indeex so that it is no longer a multi-level df
data = ticker.history(period="max").reset_index()
ticker_fig = px.line(data, x="Date", y="Close", title="Stock Ticker Close $$")

# TODO: This should be in a different file
# app layout
app.layout = html.Div(children=[

    html.Div(
        id="input_ticker_div",
        children=[
            "Ticker ",
            dcc.Input(
                id="ticker_input",
                value="AAPL",
                )
        ]
    ),

    # The 'Graph' object
    dcc.Graph(
        id="ticker_graph",
        figure=ticker_fig,
    )

])


# Wrap the update function in an 'app' callback
# set output and then input
# can be multiple to multiple?
# update happens on every value change
@app.callback(
Output(component_id="ticker_graph", component_property="figure"),
Input(component_id="ticker_input", component_property="value")
)
def update_ticker_fig(ticker: str):
    """
    args:
    -----
    ticker: string passed to the input component from callback
    """
    data = None
    try:
        ticker = yf.Ticker(ticker)
        data = ticker.history(period="max").reset_index()
        # [x] process ticker data
        # Data looks like
        #      Open High Low Close Volume Dividends Stock Splits
        # Date              
    except:
        pass

    # only act when data is not none
    if data is not None:
        return px.line(data, x="Date", y="Close", 
        title="Stock Ticker Close $$")
    


if __name__ == '__main__':
    app.run_server(debug=True)