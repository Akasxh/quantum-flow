import dash
from dash import html, dcc, Input, Output, State, ALL, ctx
from typing import Dict, List, Any

from flowfunc import Flowfunc
from flowfunc.config import Config
from flowfunc.jobrunner import JobRunner
from flowfunc.models import OutNode
import math
import random
import datetime

# --- App Initialization ---
app = dash.Dash(__name__, assets_folder='assets', suppress_callback_exceptions=True)
app.title = "Qflow"

# --- 1. Define Node Functions ---
# (This section is unchanged)
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
def compare_values(a: str, b: str, operation: str = "==") -> bool:
    """Compares two values (a, b) based on the operation (==, !=, >, <, >=, <=)."""
    try:
        num_a, num_b = float(a), float(b)
        if operation == "==": return num_a == num_b
        if operation == "!=": return num_a != num_b
        if operation == ">": return num_a > num_b
        if operation == "<": return num_a < num_b
        if operation == ">=": return num_a >= num_b
        if operation == "<=": return num_a <= num_b
    except (ValueError, TypeError):
        if operation == "==": return a == b
        if operation == "!=": return a != b
    return False
def conditional_switch(condition: bool, value_if_true: str, value_if_false: str) -> str:
    """Outputs one of two string values based on a boolean condition."""
    return value_if_true if condition else value_if_false
def create_list(item1: str = "", item2: str = "", item3: str = "") -> List[str]:
    """Creates a list from up to 3 string items."""
    return [item for item in [item1, item2, item3] if item]
def get_list_item(data_list: List[Any], index: int = 0) -> Any:
    """Retrieves an item from a list by its index."""
    try:
        return data_list[index]
    except (IndexError, TypeError):
        return None
def log_message(message: str, prefix: str = "LOG") -> str:
    """A simple node to format a log message. Useful for debugging workflows."""
    log_entry = f"[{prefix}] - {message}"
    print(log_entry)
    return log_entry
def get_current_time(format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Gets the current date and time, formatted as a string."""
    return datetime.datetime.now().strftime(format_string)

# --- 2. Create and Configure Node Library ---
all_nodes = [
    add, subtract, multiply, divide, power, string_join, to_uppercase,
    hadamard_gate, measure_qubit, compare_values, conditional_switch,
    create_list, get_list_item, log_message, get_current_time
]
nodeeditor_config = Config.from_function_list(all_nodes)
config_dict = nodeeditor_config.dict()
runner = JobRunner(nodeeditor_config)

# --- 3. Page Layouts ---
landing_page_layout = html.Div(className="container", children=[
    html.Header(className="header", children=[
        html.Div("Qflow", className="logo"),
        html.Nav(className="main-nav", children=[html.A("Features", href="#features"),html.A("Pricing", href="#pricing"),html.A("Contact", href="#contact"),]),
        dcc.Link("Launch App", href="/workflows", className="button-primary"),
    ]),
    html.Section(className="hero", children=[
        html.H1("Where Quantum Meets Workflow", className="hero-title"),
        html.P("Qflow is a revolutionary visual development environment that simplifies quantum computing.", className="hero-subtitle"),
        html.Div(className="hero-cta", children=[dcc.Link("Get Started for Free", href="/workflows", className="button-accent"),html.A("Learn More", href="#features", className="button-secondary"),]),
        html.Div(className="hero-image", children=[html.Img(src="https://i.imgur.com/eB3Z6g6.png", alt="Qflow Node Editor Screenshot")])
    ]),
])

workflows_layout = html.Div(className="dashboard-container", children=[
    html.Div(className="dashboard-header", children=[
        html.H1("My Workflows"),
        dcc.Link("＋ Create New Workflow", href="/editor", className="button-accent")
    ]),
    html.Div(id="workflows-grid-container", className="workflows-grid")
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
            dcc.Link("← Back to Workflows", href="/workflows", style={'color': '#A0AEC0', 'textDecoration': 'none'}),
            dcc.Input(id='workflow-title-input', placeholder='Untitled Workflow', style={'backgroundColor': '#374151', 'border': '1px solid #4B5563', 'color': 'white', 'padding': '8px', 'borderRadius': '5px'}),
            html.Div([
                html.Button(id="btn_save", children="Save", style={'backgroundColor': '#3B82F6', 'border': 'none', 'color': 'white', 'padding': '10px 20px', 'borderRadius': '5px', 'cursor': 'pointer', 'fontWeight': 'bold', 'marginRight': '10px'}),
                html.Button(id="btn_run", children="Run Workflow", style={'backgroundColor': '#38BDF8', 'border': 'none', 'color': '#111827', 'padding': '10px 20px', 'borderRadius': '5px', 'cursor': 'pointer', 'fontWeight': 'bold'}),
            ])
        ]),
        
        html.Div(style={'position': 'relative', 'flex': '1'}, children=[
             Flowfunc(
                id="nodeeditor",
                config=config_dict,
                nodes={},
                style={'height': '100%', 'width': '100%'}
            )
        ]),

        html.Div(id="output", style={'padding': '10px', 'backgroundColor': '#111827', 'color': 'white', 'height': '80px', 'overflowY': 'auto', 'borderTop': '1px solid #4B5563', 'fontSize': '0.875rem'}),
    ]),
])

# --- 4. Main App Layout & Callbacks ---
app.layout = html.Div([
    dcc.Store(id='workflow-storage', storage_type='local'),
    dcc.Store(id='save-notification-trigger'),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/editor':
        return editor_layout
    elif pathname == '/workflows':
        return workflows_layout
    else:
        return landing_page_layout

@app.callback(
    Output('workflows-grid-container', 'children'),
    Input('workflow-storage', 'data')
)
def update_workflow_dashboard(stored_data):
    if not stored_data:
        return html.P("No saved workflows yet. Create one in the editor!", style={'color': 'white', 'textAlign': 'center'})

    cards = []
    sorted_workflows = sorted(stored_data.items(), key=lambda item: item[0], reverse=True)
    
    for wf_id, wf_data in sorted_workflows:
        card = html.Div(className="workflow-card", children=[
            html.H3(wf_data.get('title', 'Untitled Workflow')),
            html.P(wf_data.get('description', 'No description.'), className="workflow-description"),
            html.Div(className="workflow-footer", children=[
                html.Span(f"Last modified: {wf_data.get('last_modified', 'N/A')}", className="workflow-date"),
                html.Div([
                    html.Button("Delete", id={'type': 'delete-workflow-btn', 'index': wf_id}, n_clicks=0, className="workflow-button delete"),
                    dcc.Link("Edit ➔", href=f"/editor?id={wf_id}", className="workflow-button edit")
                ])
            ])
        ])
        cards.append(card)
    return cards

@app.callback(
    Output('workflow-storage', 'data', allow_duplicate=True),
    Input({'type': 'delete-workflow-btn', 'index': ALL}, 'n_clicks'),
    State('workflow-storage', 'data'),
    prevent_initial_call=True
)
def delete_workflow(delete_clicks, stored_data):
    stored_data = stored_data or {}
    triggered_id = ctx.triggered_id
    
    if not any(n_clicks and n_clicks > 0 for n_clicks in delete_clicks):
        return dash.no_update

    if triggered_id:
        wf_id_to_delete = triggered_id['index']
        if wf_id_to_delete in stored_data:
            del stored_data[wf_id_to_delete]

    return stored_data

@app.callback(
    Output('workflow-storage', 'data'),
    Output('save-notification-trigger', 'data'),
    Input('btn_save', 'n_clicks'),
    State('workflow-storage', 'data'),
    State('nodeeditor', 'nodes'),
    State('url', 'search'),
    State('workflow-title-input', 'value'),
    prevent_initial_call=True
)
def save_workflow(n_clicks, stored_data, nodes, search, title):
    stored_data = stored_data or {}
    
    query_params = dict(param.split("=") for param in search.strip("?").split("&") if "=" in param)
    wf_id = query_params.get('id')

    if not wf_id:
        wf_id = 'wf_' + str(int(datetime.datetime.now().timestamp()))
    
    stored_data[wf_id] = {
        'id': wf_id,
        'title': title or 'Untitled Workflow',
        'description': 'Workflow saved from the editor.',
        'last_modified': datetime.datetime.now().strftime("%Y-%m-%d"),
        'nodes': nodes
    }
    
    return stored_data, datetime.datetime.now().timestamp()

@app.callback(
    Output('nodeeditor', 'nodes'),
    Output('workflow-title-input', 'value'),
    Input('url', 'href'),
    State('workflow-storage', 'data')
)
def load_workflow_into_editor(href, stored_data):
    if not href or 'editor' not in href.split('?')[0]:
        return dash.no_update

    search = href.split('?', 1)[-1] if '?' in href else ''
    query_params = dict(param.split("=") for param in search.strip("?").split("&") if "=" in param)
    wf_id = query_params.get('id')

    if wf_id and stored_data and wf_id in stored_data:
        workflow_to_load = stored_data[wf_id]
        return workflow_to_load.get('nodes', {}), workflow_to_load.get('title', 'Untitled Workflow')
    
    return {}, 'Untitled Workflow'


@app.callback(
    Output("output", "children"),
    Input("btn_run", "n_clicks"),
    State("nodeeditor", "nodes"),
)
def run_nodes(nclicks, nodes):
    if not nclicks:
        return "▶ Click 'Run Workflow' to see the results."
    results_dict = runner.run(nodes)
    if not results_dict:
        return "▶ Workflow ran, but no final results were produced."
    output_log = []
    for node_id, result_object in results_dict.items():
        node_type = nodes.get(node_id, {}).get("type", "Unknown")
        final_value = result_object.result
        log_entry = html.Div([
            html.Span("✅ ", style={'color': '#10B981', 'fontWeight': 'bold'}),
            html.Span(f"Node '{node_type}' finished with output: "),
            html.Span(f"{final_value}", style={'color': '#A78BFA', 'fontFamily': 'monospace', 'fontWeight': 'bold'})
        ])
        output_log.append(log_entry)
    return output_log

# This clientside callback shows the "Saved!" notification
app.clientside_callback(
    """
    function(trigger) {
        if (trigger) {
            alert('Workflow Saved! ✅');
        }
        return '';
    }
    """,
    Output('save-notification-trigger', 'data', allow_duplicate=True),
    Input('save-notification-trigger', 'data'),
    prevent_initial_call=True
)


if __name__ == "__main__":
    app.run(debug=True)