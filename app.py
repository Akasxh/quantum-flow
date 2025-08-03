from typing import Dict
import dash
from dash import html, Input, Output, State
from flowfunc import Flowfunc
from flowfunc.config import Config
from flowfunc.jobrunner import JobRunner
from flowfunc.models import OutNode

app = dash.Dash(__name__)

# Functions can be converted to nodes
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

def subtract(a: int, b: int) -> int:
    """Find difference between two numbers"""
    return a - b


# A Config object contains info about the nodes and ports available in the node editor
nodeeditor_config = Config.from_function_list([add, subtract])

# A JobRunner object helps evaluate the nodes created using the node editor
runner = JobRunner(nodeeditor_config)

app.layout = html.Div(
    [
        html.Button(id="btn_run", children="Run"),
        Flowfunc(id="nodeeditor", config=nodeeditor_config.dict()),
        html.Div(id="output"),
    ], style={"height": "600px"}
)


@app.callback(
    Output("output", "children"),
    Input("btn_run", "n_clicks"),
    State("nodeeditor", "nodes"),
)
def run_nodes(nclicks: int, output_nodes: Dict[str, OutNode]):
    """Run the node layout"""
    # The result is a dictionary of OutNode objects
    result = runner.run(output_nodes)
    output = []
    for node in result.values():
        # node.result contains the result of the node
        output.append(
            html.Div([html.H1(f"{node.type}: {node.id}"), html.P(str(node.result))])
        )
    return output

if __name__ == "__main__":
    app.run()