from TestSuite.TestSuite import TestSuite
import json
import plotly.graph_objects as go


def run_changing_probabilities(node=True, heuristics=None, graph_name=None, parameters=None):
    with open(parameters, 'r') as f:
        data = json.load(f)
        data["Observable"]["Problem"] = "Partial"
    for i in range(1, 10):
        data["Heuristics"] = heuristics
        data["Observable"]["Sample"]["NProbability" if node else "EProbability"] = i/10
        TestSuite(params_dict=data)

def run_all_heuristics(graph_name=None, parameters=None):
    with open(parameters, 'r') as f:
        data = json.load(f)
    for i in ["Random", "Degree", "SingleDiscount", "TIM"]:
        data["Heuristics"] = i
        TestSuite(params_dict=data, graph_name=graph_name)

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
    print(results)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=[x / 10 for x in range(1, 10)], mode="lines", name="x=y"))
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

def make_graph_partial_ratio2(model, generation, heuristic, partial, partial_method, seedsetsize = None):
    observable_name = model + "_" + generation + "_" + heuristic + "_Observable.json"
    partial_name = model + "_" + generation + "_" + heuristic + "_" + partial + "-" + partial_method + "-"
    partial_end = ".json"
    x = list(range(1, 51))
    # make a trace for each seedsetsize
    # make an average and trace it
    results = []
    for i in range(1, 10):
        results.append(get_json(partial_name + "0." + str(i) + partial_end))
    # results.append(get_json(observable_name))
    result = get_json(observable_name)

    fig = go.Figure()
    # fig.add_trace(go.Scatter(x=x, y=list(range(1, 51)), mode="lines", name="x=y"))

    for index, i in enumerate(results):
        fig.add_trace(go.Scatter(x=x, y=[j/result[index] for index, j in enumerate(i)], mode="lines", name=str(index+1)))
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
# TestSuite()
# make_graph_partial_ratio2("IC", "SF", "Degree", "Sample-Nodes", "R", list(range(1, 51)))

TestSuite(params="parameters_.json")

# All on IC 0.01
run_all_heuristics(graph_name="graph.xml.gz", parameters="parameters.json")

run_changing_probabilities(graph_name="graph.xml.gz", heuristics="Random", parameters="parameters.json")
run_changing_probabilities(graph_name="graph.xml.gz", heuristics="Degree", parameters="parameters.json")
run_changing_probabilities(graph_name="graph.xml.gz", heuristics="SingleDiscount", parameters="parameters.json")
run_changing_probabilities(graph_name="graph.xml.gz", heuristics="TIM", parameters="parameters.json")

# All on IC degree based
run_all_heuristics(graph_name="graph.xml.gz", parameters="parameters0.json")

run_changing_probabilities(graph_name="graph.xml.gz", heuristics="Random", parameters="parameters0.json")
run_changing_probabilities(graph_name="graph.xml.gz", heuristics="Degree", parameters="parameters0.json")
run_changing_probabilities(graph_name="graph.xml.gz", heuristics="SingleDiscount", parameters="parameters0.json")
run_changing_probabilities(graph_name="graph.xml.gz", heuristics="TIM", parameters="parameters0.json")



