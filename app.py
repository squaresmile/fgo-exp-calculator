import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from flask_caching import Cache
import numpy as np

EXP_df = pd.read_csv("level.csv")
TABLE = [["Full EXP", 0, 0, 0], ["1/2 EXP", 0, 0, 0], ["1/3 EXP", 0, 0, 0]]
OUTPUT_df = pd.DataFrame(
    TABLE, columns=["How much", "EXP", "Class Embers", "Non-class Embers"]
)
CLASS_EXP = 32400
NON_CLASS_EXP = 27000


def exp_calc(from_level, to_level, residual=0):
    if from_level == to_level:
        return 0
    else:
        if residual == 0:
            exp = EXP_df.iloc[from_level:to_level, 1].sum()
        else:
            exp = EXP_df.iloc[from_level + 1 : to_level, 1].sum() + residual
        return exp


def generate_table(dataframe):
    return html.Table(
        # Header
        [
            html.Tr(
                [
                    html.Th(col, style={"textAlign": "center"})
                    for col in dataframe.columns
                ]
            )
        ]
        +
        # Body
        [
            html.Tr(
                [col_align(dataframe.iloc[i][col], col) for col in dataframe.columns]
            )
            for i in range(len(dataframe))
        ]
    )


def col_align(text, col):
    if col == "EXP":
        return html.Td(text, style={"textAlign": "right"})
    elif col in ["Class Embers", "Non-class Embers"]:
        return html.Td(text, style={"textAlign": "center"})
    else:
        return html.Td(text)


app = dash.Dash(
    __name__,
    url_base_pathname="/exp-calculator/",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
cache = Cache(
    app.server,
    config={"CACHE_TYPE": "redis", "CACHE_REDIS_URL": "redis://localhost:6379"},
)
app.config.suppress_callback_exceptions = True
timeout = 86400
server = app.server

app.layout = html.Div(
    children=[
        html.H2(children="FGO EXP Calculator"),
        html.Div(children="From level:"),
        dcc.Input(id="from-level", value=1, type="number", min=0, max=100),
        html.Div(children="To level:"),
        dcc.Input(id="to-level", value=50, type="number", min=0, max=100),
        html.Div(children="Residual EXP:"),
        dcc.Input(id="residual-exp", value=0, type="number", min=0, max=1456500),
        html.Div(id="exp-needed"),
    ],
    className="container",
)


@app.callback(
    dash.dependencies.Output("exp-needed", "children"),
    [
        dash.dependencies.Input("from-level", "value"),
        dash.dependencies.Input("to-level", "value"),
        dash.dependencies.Input("residual-exp", "value"),
    ],
)
@cache.memoize(timeout=timeout)
def update_exp_text(from_level, to_level, residual_exp):
    if from_level > to_level:
        return "From level can't be higher than to level."
    else:
        exp_needed = exp_calc(from_level, to_level, residual_exp)
        exp = np.array([exp_needed, exp_needed / 2, exp_needed / 3])
        OUTPUT_df["EXP"] = exp
        OUTPUT_df["Class Embers"] = np.ceil(exp / CLASS_EXP)
        OUTPUT_df["Non-class Embers"] = np.ceil(exp / NON_CLASS_EXP)
        OUTPUT_df["EXP"] = OUTPUT_df["EXP"].apply(lambda x: "{:,.0f}".format(x))
        return generate_table(OUTPUT_df)


if __name__ == "__main__":
    app.run_server(debug=True)
