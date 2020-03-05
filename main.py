from TestSuite.TestSuite import TestSuite
import json
import plotly.graph_objects as go


def run_changing_probabilities(node=True, heuristics=None):
    with open('parameters.json', 'r') as f:
        data = json.load(f)
        data["Observable"]["Problem"] = "Partial"
    for i in range(1, 10):
        data["Observable"]["Sample"]["NProbability" if node else "EProbability"] = i/10
        TestSuite(params_dict=data)

def run_all_heuristics():
    with open('parameters.json', 'r') as f:
        data = json.load(f)
    for i in ["Random", "Degree", "SingleDiscount"]:
        data["Heuristics"] = i
        TestSuite(params_dict=data)

def get_json(name):
    with open(name, "r") as f:
        data = json.loads(json.load(f))
        temp = data["Data"]
    return temp

def make_graph_partial_ratio(model, generation, heuristic, partial, partial_method, seedsetsize = None):
    observable_name = model + "_" + generation + "_" + heuristic + "_Observable.json"
    partial_name = model + "_" + generation + "_" + heuristic + "_" + partial + "-" + partial_method + "-"
    partial_end = ".json"
    x = [i/10 for i in range(1, 11)]
    # make a trace for each seedsetsize
    # make an average and trace it
    results = []
    for i in range(1, 10):
        results.append(get_json(partial_name + "0." + str(i) + partial_end))
    results_observable = get_json(observable_name)
    results_ = []
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=[x / 10 for x in range(1, 11)], mode="lines", name="x=y"))
    for i in range(len(results_observable)):
        fig.add_trace(go.Scatter(x=x, y=[j[i]/results_observable[i] for j in results], mode="lines", name=seedsetsize[i]))
    fig.update_layout(
        title="Plot representing the ration of PO/O result using IC and TIM",
        xaxis_title="% Partial Observability",
        yaxis_title="Solution compared to Observable Solution",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="#7f7f7f"
        )
    )
    fig.show()


# run_changing_probabilities()
# run_all_heuristics()
TestSuite()
# make_graph_partial_ratio("IC", "SF", "Random", "Sample-Nodes", "R", [10, 20, 30, 40, 50])

# graph_draw(g, output_size=(1000, 1000), output="graph.png")

