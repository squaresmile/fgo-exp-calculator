import json
from math import ceil
from typing import Dict, List, TypedDict, Union

import dash
import dash_core_components as dcc
import dash_html_components as html


with open("level_exp.json", "r", encoding="utf-8") as f:
    EXP_LEVEL: Dict[str, int] = json.load(f)
ROWS = ["Full EXP", "1/2 EXP", "1/3 EXP"]
CLASS_EXP = 32400
NON_CLASS_EXP = 27000


class output_column(TypedDict):
    name: str
    values: List[str]


def exp_calc(from_level: int, to_level: int, residual: int = 0) -> int:
    if from_level == to_level:
        return 0
    else:
        if residual == 0:
            exp = EXP_LEVEL[str(to_level)] - EXP_LEVEL[str(from_level)]
        else:
            exp = EXP_LEVEL[str(to_level)] - EXP_LEVEL[str(from_level + 1)] + residual
        return exp


def generate_table(dataframe: List[output_column]) -> html.Table:
    return html.Table(
        # Header
        [
            html.Tr(
                [
                    html.Th(col["name"], style={"textAlign": "center"})
                    for col in dataframe
                ]
            )
        ]
        +
        # Body
        [
            html.Tr([col_align(col["values"][i], col["name"]) for col in dataframe])
            for i in range(len(ROWS))
        ]
    )


def col_align(text: str, col: str) -> html.Td:
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
server = app.server

app.layout = html.Div(
    children=[
        html.H2(children="FGO EXP Calculator"),
        html.Div(children="From level:"),
        dcc.Input(id="from-level", value=1, type="number", min=0, max=100, step=1),
        html.Div(children="To level:"),
        dcc.Input(id="to-level", value=50, type="number", min=0, max=100, step=1),
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
def update_exp_text(
    from_level: int, to_level: int, residual_exp: int
) -> Union[str, html.Table]:
    if from_level is None or to_level is None:
        return "Plese enter an integer not bigger than 100."
    elif from_level > to_level:
        return "From level can't be higher than to level."
    else:
        if residual_exp is None:
            residual_exp = 0
        output_table: List[output_column] = []
        exp_needed = exp_calc(from_level, to_level, residual_exp)
        exp_list = (exp_needed, exp_needed / 2, exp_needed / 3)
        output_table.append({"name": "How much", "values": ROWS})
        output_table.append(
            {"name": "EXP", "values": [f"{exp:,.0f}" for exp in exp_list]}
        )
        output_table.append(
            {
                "name": "Class Embers",
                "values": [f"{ceil(exp / CLASS_EXP)}" for exp in exp_list],
            }
        )
        output_table.append(
            {
                "name": "Non-class Embers",
                "values": [f"{ceil(exp / CLASS_EXP)}" for exp in exp_list],
            }
        )
        return generate_table(output_table)


if __name__ == "__main__":
    app.run_server(debug=True)
