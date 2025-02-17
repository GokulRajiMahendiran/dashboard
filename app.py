import yfinance as yf
import pandas as pd
from dash import Dash, html, dash_table, dcc, Input, Output, callback
from datetime import datetime
import plotly.graph_objects as go

# Portfolio Data
bro_portfolio = [
    {"Stock": "ARCHIES.NS", "Invested Value": 1978.95, "Avg Buy Price": 26.39, "Quantity": 75},
    {"Stock": "BAJAJFINSV.NS", "Invested Value": 9047.70, "Avg Buy Price": 1809.54, "Quantity": 5},
    {"Stock": "GEMSI.BO", "Invested Value": 20740.00, "Avg Buy Price": 2.07, "Quantity": 10000},
    {"Stock": "GTLINFRA.NS", "Invested Value": 17865.00, "Avg Buy Price": 2.38, "Quantity": 7500},
    {"Stock": "IDFCFIRSTB.NS", "Invested Value": 9256.20, "Avg Buy Price": 92.56, "Quantity": 100},
    {"Stock": "INVENTURE.NS", "Invested Value": 2056.80, "Avg Buy Price": 6.86, "Quantity": 300},
    {"Stock": "JPPOWER.NS", "Invested Value": 1914.50, "Avg Buy Price": 7.66, "Quantity": 250},
    {"Stock": "JMFINANCIL.NS", "Invested Value": 8414.22, "Avg Buy Price": 112.19, "Quantity": 75},
    {"Stock": "NECLIFE.NS", "Invested Value": 9804.00, "Avg Buy Price": 32.68, "Quantity": 300},
]

yuva_portfolio = [
    {"Stock": "CANBK.NS", "Quantity": 692, "Avg Price": 89.50, "Invested Value": 61934.00},
    {"Stock": "GAIL.NS", "Quantity": 750, "Avg Price": 92.33, "Invested Value": 69250.00},
    {"Stock": "IDFCFIRSTB.NS", "Quantity": 182, "Avg Price": 65.80, "Invested Value": 11975.60},
    {"Stock": "YESBANK.BO", "Quantity": 1000, "Avg Price": 20.53, "Invested Value": 20530.00},
]


# Function to fetch live stock prices (LTP)
def get_ltp(stock_symbol):
    try:
        stock = yf.Ticker(stock_symbol)
        ltp = stock.history(period="1d")['Close'].iloc[-1]
        return round(ltp, 2)
    except:
        return 0.0  # Fallback if API fails

# Function to calculate portfolio metrics
def calculate_portfolio_metrics(portfolio):
    for stock in portfolio:
        stock["LTP"] = get_ltp(stock["Stock"])
        stock["Current Value"] = round(stock["Quantity"] * stock["LTP"], 2)
        stock["PnL"] = round(stock["Current Value"] - stock["Invested Value"], 2)

    df = pd.DataFrame(portfolio)
    total_investment = round(df["Invested Value"].sum(), 2)
    total_pnl = round(df["PnL"].sum(), 2)
    return df, total_investment, total_pnl

# Initialize Dash app
app = Dash(__name__)

# Define layout
app.layout = html.Div([
    html.H1("Portfolio Dashboard", style={"textAlign": "center", "color": "#2c3e50"}),

    dcc.Interval(id="interval-component", interval=5*1000, n_intervals=0),
    html.Div(id="last-updated", style={"textAlign": "center", "margin": "10px"}),

    html.Div([
        # Bro's Portfolio
        html.Div([
            html.H2("Bro's Portfolio", style={"textAlign": "center", "color": "#1e8449"}),
            dash_table.DataTable(
                id="bro-portfolio-table",
                style_data_conditional=[
                    {
                        "if": {"filter_query": "{PnL} > 0", "column_id": "PnL"},
                        "backgroundColor": "#d4efdf",
                        "color": "#186a3b"
                    },
                    {
                        "if": {"filter_query": "{PnL} < 0", "column_id": "PnL"},
                        "backgroundColor": "#fadbd8",
                        "color": "#943126"
                    }
                ],
                style_table={"overflowX": "auto"},
                style_cell={"textAlign": "center", "padding": "5px"},
                style_header={"fontWeight": "bold"},
                style_data={"height": "30px", "whiteSpace": "normal"},
            ),
            html.Div(id="bro-portfolio-metrics", style={"marginTop": "10px", "textAlign": "center"})
        ], style={"width": "45%", "display": "inline-block", "verticalAlign": "top"}),

        # Yuva's Portfolio
        html.Div([
            html.H2("Yuva's Portfolio", style={"textAlign": "center", "color": "#1e8449"}),
            dash_table.DataTable(
                id="yuva-portfolio-table",
                style_data_conditional=[
                    {
                        "if": {"filter_query": "{PnL} > 0", "column_id": "PnL"},
                        "backgroundColor": "#d4efdf",
                        "color": "#186a3b"
                    },
                    {
                        "if": {"filter_query": "{PnL} < 0", "column_id": "PnL"},
                        "backgroundColor": "#fadbd8",
                        "color": "#943126"
                    }
                ],
                style_table={"overflowX": "auto"},
                style_cell={"textAlign": "center", "padding": "5px"},
                style_header={"fontWeight": "bold"},
                style_data={"height": "30px", "whiteSpace": "normal"},
            ),
            html.Div(id="yuva-portfolio-metrics", style={"marginTop": "10px", "textAlign": "center"})
        ], style={"width": "45%", "display": "inline-block", "verticalAlign": "top"}),
    ], style={"width": "100%", "display": "flex", "justifyContent": "space-between"}),

    # Change Graph
    html.Div([
        html.H2("PnL Change Over Time", style={"textAlign": "center", "color": "#2c3e50"}),
        dcc.Graph(id="pnl-change-graph", style={"height": "400px"})
    ])
])

# Callback to update tables, metrics, and graph
@callback(
    [Output("bro-portfolio-table", "columns"),
     Output("bro-portfolio-table", "data"),
     Output("bro-portfolio-metrics", "children"),
     Output("yuva-portfolio-table", "columns"),
     Output("yuva-portfolio-table", "data"),
     Output("yuva-portfolio-metrics", "children"),
     Output("pnl-change-graph", "figure"),
     Output("last-updated", "children")],
    [Input("interval-component", "n_intervals")]
)
def update_dashboard(n):
    # Calculate metrics for Bro's Portfolio
    bro_df, bro_total_investment, bro_total_pnl = calculate_portfolio_metrics(bro_portfolio)

    # Calculate metrics for Yuva's Portfolio
    yuva_df, yuva_total_investment, yuva_total_pnl = calculate_portfolio_metrics(yuva_portfolio)

    # PnL Change Graph
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=bro_df["Stock"], y=bro_df["PnL"],
        name="Bro's Portfolio",
        marker_color="green" if bro_total_pnl > 0 else "red"
    ))
    fig.add_trace(go.Bar(
        x=yuva_df["Stock"], y=yuva_df["PnL"],
        name="Yuva's Portfolio",
        marker_color="blue"
    ))
    fig.update_layout(title="PnL Change Over Time", xaxis_title="Stock", yaxis_title="PnL")

    # Timestamp
    timestamp = datetime.now().strftime("Last Updated: %Y-%m-%d %H:%M:%S")

    return (
        [{"name": i, "id": i} for i in bro_df.columns],
        bro_df.to_dict("records"),
        [
            html.P(f"Total Investment: ₹{bro_total_investment:.2f}", style={"fontWeight": "bold"}),
            html.P(f"Total PnL: ₹{bro_total_pnl:.2f}", style={"color": "#186a3b" if bro_total_pnl >= 0 else "#943126"}),
        ],
        [{"name": i, "id": i} for i in yuva_df.columns],
        yuva_df.to_dict("records"),
        [
            html.P(f"Total Investment: ₹{yuva_total_investment:.2f}", style={"fontWeight": "bold"}),
            html.P(f"Total PnL: ₹{yuva_total_pnl:.2f}", style={"color": "#186a3b" if yuva_total_pnl >= 0 else "#943126"}),
        ],
        fig,
        timestamp
    )
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=True, host="0.0.0.0", port=port)
