import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

EXP_df = pd.read_csv("level.csv")

def exp_calc(from_level, to_level, residual=0):
	if residual == 0:
		exp = EXP_df.iloc[from_level:to_level, 1].sum()
	else:
		exp = EXP_df.iloc[from_level+1:to_level, 1].sum() + residual
	return exp

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(children=[
    
    html.H1(children='FGO EXP Calculator'),
    
    html.Div(children='From level:'),

    dcc.Input(id='from-level', value=1, type='number', min=1, max=100),

    html.Div(children='To level:'),

    dcc.Input(id='to-level', value=50, type='number', min=1, max=100),

    html.Div(children='Residual EXP:'),

    dcc.Input(id='residual-exp', value=0, type='number', min=1, max=100),

    html.Div(id='exp-needed')
], className="container"
)

@app.callback(
    dash.dependencies.Output('exp-needed', 'children'),
    [dash.dependencies.Input('from-level', 'value'),
     dash.dependencies.Input('to-level', 'value'),
     dash.dependencies.Input('residual-exp', 'value')])
def update_exp_text(from_level, to_level, residual_exp):
    if from_level > to_level:
        return "From level can\'t be higher than to level."
    else:
        exp_needed = exp_calc(from_level, to_level, residual_exp)
        return html.Div([
            html.P("EXP Needed: {:,}".format(exp_needed)),
            html.P("1/2 EXP: {:,.0f}".format(exp_needed/2)),
            html.P("1/3 EXP: {:,.0f}".format(exp_needed/3))
        ])

if __name__ == '__main__':
    app.run_server(debug=True)
