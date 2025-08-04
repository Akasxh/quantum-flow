**Flowfunc’s** architecture—how a plain Python function becomes a draggable node in the browser, how graphs are stored, validated, and executed, and how the same engine can run locally or on a Redis / RQ cluster.

---

## 1. Building the catalogue of **Nodes** and **Ports**

| Step                                     | Key class / file                                 | What happens                                                                                                                                                                                                                                                                                           |
| ---------------------------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Introspect the user’s functions** | `flowfunc/config.py → Config.from_function_list` | The helper loops over every function you pass (e.g. `add`, `mul`, `trig_function`).  For each function it calls `process_node`, which uses **`inspect.signature()`** to read • positional/keyword args • type annotations • default values.                                                            |
| **Create `Node` definitions**       | `flowfunc/models.py`                             | A `Node` dataclass holds: `id`, `type` (function name), `inputs`, `outputs`, `ui` metadata, etc.  Each argument becomes an **input `Port`**; the return annotation becomes an **output `Port`**.                                                                                                       |
| **Register unique port types**      | `PortDef` inside `Config`                        | If you annotate an argument with `Annotated[int, {"label": "First number"}]`, the label and any extra JSON are stored so the front end can render widgets (sliders, dropdowns, etc.).  A catch-all `"object"` port is appended so **any** two ports can be connected when no strict typing is desired. |
| **Serialize as JSON**               | `Config.dict()`                                  | The resulting dict contains: `nodes`, `ports`, and editor UI defaults.  This is what you pass to the React component via `Flowfunc(id="nodeeditor", config=cfg.dict())`.                                                                                                                               |

---

## 2. Front-end React (Flume) component

* Resides in `flowfunc/frontend`.
* Takes that JSON config and renders a Flume-based canvas.
* Each **Port** definition becomes a socket; each **Node** becomes a draggable card with auto-generated controls.
* When you click “Run”, Dash sends the **current graph** (array of nodes + links) back to the server via the `nodes` prop.

---

## 3. Validating and running the graph – `JobRunner`

### 3.1 Dependency resolution

1. **Convert raw JSON → `OutNode` objects** (`flowfunc/models.py`).
2. Build a **directed acyclic graph**: for every connection Flowfunc records which output port feeds which input port.
3. Topologically sort nodes so parents always execute before children (`dependent_nodes` utility).

### 3.2 Execution modes (selectable via `JobRunner.__init__`)

| Mode                    | Trigger                | How it works                                                           |
| ----------------------- | ---------------------- | ---------------------------------------------------------------------- |
| **sync** (default)      | `JobRunner.run(nodes)` | Uses plain Python calls in the main thread.                            |
| **async**               | `run_async=True`       | Uses `asyncio`; each node runs as a coroutine (`evaluate_node_async`). |

Trying for queue in a similar flow:

1. Waits for input nodes (via `asyncio.Event`).
2. Uses **Pydantic validation** to coerce/validate inputs.
3. Executes the original Python callable (awaits if coroutine).
4. Maps the returned value(s) back to output port names.
5. Marks the node status (`success`, `error`, etc.) and fires events so dependents can proceed.


## 4. Reporting status back to the UI

In your Dash callback you returned two things:

```python
return output_html, nodes_status   # ({node.id: "success"|"error"|...})
```

* Dash passes `nodes_status` back into the React component.
* The React side highlights nodes in green/red or shows spinners based on that dict.
* Your custom HTML list (`output_html`) shows results or error messages in the Results card.

---

## 5. Where things live in the repo

```
flowfunc/
├─ __init__.py
├─ config.py        # Config.from_function_list, PortDef logic
├─ models.py        # Node, OutNode, Port dataclasses (+ pydantic)
├─ jobrunner.py     # JobRunner, evaluate_node_async
├─ jobqueue.py      # NodeQueue wrapper 
├─ frontend/        # React (Flume) bundle compiled to JS/CSS
└─ utils/           # topo-sort, validators, misc helpers
```
---

### TL;DR

Flowfunc turns *ordinary* Python functions → **Node definitions → JSON → React canvas**.
At run-time the **JobRunner** topologically orders the user-drawn graph, validates inputs with **Pydantic**, then executes each function synchronously, asynchronously.
