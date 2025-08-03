import dash
from dash import html, dcc, Input, Output, State, ALL
from typing import Dict, List

from flowfunc import Flowfunc
from flowfunc.config import Config
from flowfunc.jobrunner import JobRunner
from flowfunc.models import OutNode
import math
import random

# --- App Initialization ---
app = dash.Dash(__name__, assets_folder='assets', suppress_callback_exceptions=True)
app.title = "Qflow"

# --- 1. Define Node Functions ---
def add(a: float, b: float) -> float:
    """Adds two numbers (a + b)."""
    return a + b
def subtract(a: float, b: float) -> float:
    """Subtracts two numbers (a - b)."""
    return a - b
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers (a * b)."""
    return a * b
def divide(a: float, b: float) -> float:
    """Divides two numbers (a / b). Returns 0 if b is zero."""
    return a / b if b != 0 else 0
def power(base: float, exponent: float) -> float:
    """Calculates base to the power of exponent."""
    return math.pow(base, exponent)
def string_join(a: str, b: str, separator: str = " ") -> str:
    """Joins two strings with a separator."""
    return f"{a}{separator}{b}"
def to_uppercase(text: str) -> str:
    """Converts a string to uppercase."""
    return text.upper()
def hadamard_gate(qubit_state: str = "|0>") -> str:
    """Simulates a Hadamard gate. |0> -> |+> or |1> -> |->"""
    if qubit_state == "|0>": return "|+>"
    elif qubit_state == "|1>": return "|->"
    return "Invalid state"
def measure_qubit(state: str = "|+>") -> int:
    """Simulates measuring a qubit with a 50/50 chance."""
    if state in ["|+>", "|->"]: return random.choice([0, 1])
    return 0

# --- 2. Create and Configure Node Library ---
all_nodes = [add, subtract, multiply, divide, power, string_join, to_uppercase, hadamard_gate, measure_qubit]
nodeeditor_config = Config.from_function_list(all_nodes)
config_dict = nodeeditor_config.dict()
runner = JobRunner(nodeeditor_config)

# --- 3. Page Layouts ---
landing_page_layout = html.Div(className="container", children=[
    html.Header(className="header", children=[
        html.Div("Qflow", className="logo"),
        html.Nav(className="main-nav", children=[html.A("Features", href="#features"),html.A("Pricing", href="#pricing"),html.A("Contact", href="#contact"),]),
        dcc.Link("Launch App", href="/editor", className="button-primary"),
    ]),
    html.Section(className="hero", children=[
        html.H1("Where Quantum Meets Workflow", className="hero-title"),
        html.P("Qflow is a revolutionary visual development environment that simplifies quantum computing.", className="hero-subtitle"),
        html.Div(className="hero-cta", children=[dcc.Link("Get Started for Free", href="/editor", className="button-accent"),html.A("Learn More", href="#features", className="button-secondary"),]),
        html.Div(className="hero-image", children=[html.Img(src="https://i.imgur.com/eB3Z6g6.png", alt="Qflow Node Editor Screenshot")])
    ]),
])

def build_node_legend(conf: dict) -> List[html.Div]:
    legend_items = []
    for node_info in conf["nodeTypes"]:
        card = html.Div(className="node-info-card", children=[
            html.H3(node_info["type"]),
            html.P(node_info["description"])
        ])
        legend_items.append(card)
    return legend_items

editor_layout = html.Div(className="editor-page-container", children=[
    html.Aside(className="editor-sidebar", children=[
        html.Div(className="sidebar-header", children=[
            html.H2("Node Legend"),
            html.P("Right-click on the canvas to add nodes.")
        ]),
        html.Div(className="node-legend", children=build_node_legend(config_dict))
    ]),
    
    html.Div(className="editor-main-area", children=[
        html.Div(style={'padding': '10px', 'background-color': '#111827', 'color': 'white', 'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'height': '60px', 'borderBottom': '1px solid #4B5563'}, children=[
            dcc.Link("← Back to Home", href="/", style={'color': '#A0AEC0', 'textDecoration': 'none'}),
            html.Button(id="btn_run", children="Run Workflow", style={'backgroundColor': '#38BDF8', 'border': 'none', 'color': '#111827', 'padding': '10px 20px', 'borderRadius': '5px', 'cursor': 'pointer', 'fontWeight': 'bold'}),
        ]),
        
        html.Div(style={'position': 'relative', 'flex': '1'}, children=[
             Flowfunc(
                id="nodeeditor",
                config=config_dict,
                style={'height': '100%', 'width': '100%'}
            )
        ]),

        html.Div(id="output", style={'padding': '10px', 'backgroundColor': '#111827', 'color': 'white', 'height': '80px', 'overflowY': 'auto', 'borderTop': '1px solid #4B5563', 'fontSize': '0.875rem'}),
    ])
])

# --- 4. Main App & Callbacks ---
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/editor':
        return editor_layout
    else:
        return landing_page_layout

@app.callback(
    Output("output", "children"),
    Input("btn_run", "n_clicks"),
    State("nodeeditor", "nodes"),
)
def run_nodes(nclicks, nodes):
    if not nclicks:
        return "Click 'Run Workflow' to see the results."
    result = runner.run(nodes)
    output_divs = []
    for node_id, node_result in result.items():
        output_divs.append(
            html.Div([
                html.Span(f"Node '{node_id}': ", style={'fontWeight': 'bold', 'color': 'white'}),
                html.Span(f"{node_result}", style={'color': '#A78BFA', 'fontFamily': 'monospace'})
            ])
        )
    return output_divs

if __name__ == "__main__":
    app.run(debug=True)