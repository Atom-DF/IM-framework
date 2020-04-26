from TestSuite.TestSuite import TestSuite
import json
import plotly.graph_objects as go
from multiprocessing import Process


def run_changing_probabilities(node=True, heuristics="Random", parameters="parameters.json"):
    with open(parameters, 'r') as f:
        data = json.load(f)
        data["Observable"]["Problem"] = "Partial"
    for i in range(1, 10):
        data["Heuristics"] = heuristics
        data["Observable"]["Sample"]["NProbability" if node else "EProbability"] = i/10
        TestSuite(params_dict=data)


def run_all_heuristics(graph_name="graph", parameters="parameters.json", heuristics=["Random", "Degree", "SingleDiscount", "DegreeDiscount", "TIM"]):
    with open(parameters, 'r') as f:
        data = json.load(f)
    for i in heuristics:
        data["Heuristics"] = i
        TestSuite(params_dict=data, graph_name=graph_name)


def get_json(name):
    with open(name, "r") as f:
        data = json.loads(json.load(f))
        temp = data["Data"]
    return temp

def get_json2(name):
    with open(name, "r") as f:
        temp = json.load(f)
    return temp

def make_graph_partial_ratio(model, degree_based, generation, heuristic, partial, partial_method, seedsetsize = None):
    observable_name = "data/"+model+degree_based + "_" + generation + "_" + heuristic + "_Observable.json"
    partial_name = "data/"+model+ degree_based + "_" + generation + "_" + heuristic + "_" + partial + "-" + partial_method + "-"
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


def make_graph_partial_ratio2(model, degree_based, generation, heuristic, partial, partial_method, seedsetsize = None):
    observable_name = "data/"+model + degree_based + "_" + generation + "_" + heuristic + "_Observable.json"
    partial_name = "data/"+model + degree_based + "_" + generation + "_" + heuristic + "_" + partial + "-" + partial_method + "-"
    partial_end = ".json"
    x = list(range(1, 51))
    # make a trace for each seedsetsize
    # make an average and trace it
    results = []
    for i in range(1, 10):
        results.append(get_json(partial_name + "0." + str(i) + partial_end))
    results.append(get_json(observable_name))
    # result = get_json(observable_name)

    fig = go.Figure()
    # fig.add_trace(go.Scatter(x=x, y=list(range(1, 51)), mode="lines", name="x=y"))
    temp = ["10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"]
    for index, i in enumerate(results):
        fig.add_trace(go.Scatter(x=x, y=[j for index, j in enumerate(i)], mode="lines", name=temp[index]))
    fig.update_layout(
        title="Plot comparing observability levels and spread spread ratio under "+model+" " + ("Degree Based" if degree_based == "True" else "Constant Based")+" using "+heuristic+" and "+partial,
        xaxis_title="Seed Set Size",
        yaxis_title="Average Spread",
        font=dict(
            family="Courier New, monospace",
            size=14,
            color="#7f7f7f"
        )
    )
    fig.show()


def make_graph_observable(model, degree_based, generation):
    observables = []
    for i in ["Random", "Degree", "SingleDiscount", "DegreeDiscount", "TIM"]:
        observables.append(get_json("data/" + model + degree_based + "_" + generation + "_" + i + "_Observable.json"))
    x = list(range(1, 51))

    fig = go.Figure()

    for index, i in enumerate(["Random", "Degree", "SingleDiscount", "TIM"]):
        fig.add_trace(go.Scatter(x=x, y=observables[index], mode="lines", name=i))
    fig.update_layout(
        title="Influence Maximization under "+model+" " + ("Degree Based" if degree_based == "True" else "Constant Based"),
        xaxis_title="Seed Set Size",
        yaxis_title="Average Spread",
        font=dict(
            family="Courier New, monospace",
            size=14,
            color="#7f7f7f"
        )
    )
    fig.show()


def test(model, degree_based, generation):
    observables = []
    for i in [1, 2, 3, 4]:
        observables.append(get_json(model + degree_based + "_" + generation + "_" + "NRun"+str(i)+"_" + "DegreeDiscount" + "_Observable.json"))
    x = [10]

    fig = go.Figure()

    for index, i in enumerate([1, 2, 3, 4]):
        fig.add_trace(go.Scatter(x=x, y=observables[index], mode="markers", name=i))
    fig.update_layout(
        title="Influence Maximization under "+model+" " + ("Degree Based" if degree_based == "True" else "Constant Based"),
        xaxis_title="Seed Set Size",
        yaxis_title="Average Spread",
        font=dict(
            family="Courier New, monospace",
            size=14,
            color="#7f7f7f"
        )
    )
    fig.show()


def experiment1():
    def run_simulation():
        TestSuite(params_dict=params, graph_name="graph")

    with open("parameters.json", "r") as fp:
        params = json.load(fp)

    params["Filename"] = "Experiment1.json"
    params["Models"]["Degree_Based"] = False

    TestSuite(graph_name="graph", save=True, params_dict=params)

    processes = []
    for i in ["Random", "Degree", "SingleDiscount", "DegreeDiscount", "TIM"]:
        params["Heuristics"] = i
        temp = Process(target=run_simulation)
        temp.start()
        processes.append(temp)

    for i in processes:
        i.join()

    params["Models"]["Degree_Based"] = True

    processes = []
    for i in ["Random", "Degree", "SingleDiscount", "DegreeDiscount", "TIM"]:
        params["Heuristics"] = i
        temp = Process(target=run_simulation)
        temp.start()
        processes.append(temp)

    for i in processes:
        i.join()

def analyse_experiment1():
    observables = []
    experiment = get_json2("Experiment1.json")

    x = experiment[0][0]["Parameters"]["SeedSetSize"]

    observables.append(("Random", experiment[0][1]["Data"]))
    observables.append(("Degree", experiment[1][1]["Data"]))
    observables.append(("TIM", experiment[2][1]["Data"]))
    observables.append(("DegreeDiscount", experiment[3][1]["Data"]))
    observables.append(("SingleDiscount", experiment[4][1]["Data"]))


    fig = go.Figure()

    for index, i in observables:
        fig.add_trace(go.Scatter(x=x, y=i, mode="lines", name=index))
    fig.update_layout(
        title="Influence Maximization under IC Constant Based",
        xaxis_title="Seed Set Size",
        yaxis_title="Average Spread",
        font=dict(
            family="Courier New, monospace",
            size=14,
            color="#7f7f7f"
        )
    )
    fig.show()

    observables = []
    experiment = get_json2("Experiment1.json")

    x = experiment[0][0]["Parameters"]["SeedSetSize"]

    observables.append(("Random", experiment[5][1]["Data"]))
    observables.append(("Degree", experiment[6][1]["Data"]))
    observables.append(("TIM", experiment[7][1]["Data"]))
    observables.append(("DegreeDiscount", experiment[8][1]["Data"]))
    observables.append(("SingleDiscount", experiment[9][1]["Data"]))

    fig = go.Figure()

    for index, i in observables:
        fig.add_trace(go.Scatter(x=x, y=i, mode="lines", name=index))
    fig.update_layout(
        title="Influence Maximization under IC Degree Based",
        xaxis_title="Seed Set Size",
        yaxis_title="Average Spread",
        font=dict(
            family="Courier New, monospace",
            size=14,
            color="#7f7f7f"
        )
    )
    fig.show()

def experiment1_():
    def run_simulation():
        TestSuite(params_dict=params, graph_name="graph")

    with open("parameters.json", "r") as fp:
        params = json.load(fp)

    params["Filename"] = "Experiment1_.json"
    params["Models"]["Degree_Based"] = False

    TestSuite(graph_name="graph", save=True, params_dict=params)

    processes = []
    for i in ["Random", "Degree", "SingleDiscount", "DegreeDiscount", "TIM"]:
        params["Heuristics"] = i
        temp = Process(target=run_simulation)
        temp.start()
        processes.append(temp)

    for i in processes:
        i.join()

    params["Models"]["Degree_Based"] = True

    processes = []
    for i in ["Random", "Degree", "SingleDiscount", "DegreeDiscount", "TIM"]:
        params["Heuristics"] = i
        temp = Process(target=run_simulation)
        temp.start()
        processes.append(temp)

    for i in processes:
        i.join()

def experiment2():
    def run_simulation():
        TestSuite(params_dict=params, graph_name="graph")

    with open("parameters.json", "r") as fp:
        params = json.load(fp)

    params["Filename"] = "Experiment2.json"
    params["Models"]["Degree_Based"] = False

    # TestSuite(graph_name="graph", save=True, params_dict=params)

    processes = []
    for i in ["Random", "Degree", "SingleDiscount", "DegreeDiscount"]:
        params["Heuristics"] = i
        temp = Process(target=run_simulation)
        temp.start()
        processes.append(temp)

    for i in processes:
        i.join()

    params["Models"]["Degree_Based"] = True

    processes = []
    for i in ["Random", "Degree", "SingleDiscount", "DegreeDiscount"]:
        params["Heuristics"] = i
        temp = Process(target=run_simulation)
        temp.start()
        processes.append(temp)

    for i in processes:
        i.join()


# 1
# TestSuite(graph_name="graph", save=True)
# analyse_experiment1()
# 2 et 3
# run_changing_probabilities(heuristics="DegreeDiscount")
# run_all_heuristics(heuristics=["Random", "Degree", "SingleDiscount", "DegreeDiscount"])
# experiment1_()

# TestSuite(save=True)
TestSuite(graph_name="graph")

# test("IC", "False", "SF") 20: 129.08999999999995 4000 seconds