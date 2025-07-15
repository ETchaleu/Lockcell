"""
Created on : 2025-07-07
Author   : Erwan Tchaleu
Email    : erwan.tchale@gmail.com

"""

import controllers
from Tasks import TaskEnv

import cloudpickle # Install cloudpickle
cloudpickle.register_pickle_by_value(TaskEnv) # Pour les modules de ton code tu fait du sort que ca soit pickler par value
cloudpickle.register_pickle_by_value(controllers) # Pour les modules de ton code tu fait du sort que ca soit pickler par value


printgraph = True
N = 2**8
searchspace = [i for i in range(N)]

def counter(n : int):
    if n <0:
        return "Number Err"
    if n <= 3:
        if n == 1:
            return "First"
        if n == 2:
            return "Second"
        if n == 3:
            return "Third"
    return n.__str__() + "th"

def say(res, i):
    print(counter(i) + " results : " + res.__str__() + "\n" +"-"*80)

def say2(res):
    print("Found : " + res.__str__() + "\n" +"-"*80)

def finalSay(res, i):
    print("\n" + "-"*80 +"\n" + "-"*80  + "\n" + "Recursions : " + i.__str__() + " | Total results : " + res.__str__()  +"\n" + "-"*80  +"\n" + "-"*80)

# Problème d'implémentation de la stochasticité, en effet les 1 minimaux d'un période ne failent pas forcément à la suivanten il faut un cache ou alors transmette le fait que ce truc ne marche pas
graph = controllers.Graph()
if not printgraph:
    graph = None
config = controllers.TestConfig()
config.GenProb(N, (2, 1, 0, 0.3), (2, 2, 2, 0.5), (1, 3, 4, 0.5)) # (combien, taille, écart type)
nbRunTab = [1, 4, 6]
print(config.Pb)
input("press to continue...")
#res = controllers.SRDDMIN(searchspace, nbRunTab, say2, config)
res = controllers.RDDMIN(searchspace, say, finalSay, config, graph)
print(res)
print(config.Pb)

from graphviz import Digraph

Gr = Digraph()

def findOut(g : controllers.Graph) -> controllers.Graph:
    out = g.out[0]
    while out != out.out[0]:
        out = out.out[0]
    return out

def TrueFalse(val):
    return "green" if val else "black"

def print1(g: controllers.Graph):
    if g.up:
        for _in in g.up:
            out = findOut(_in[0])
            dataId = "d_" + out.id
            Gr.edge(dataId, g.id)
    if g.son:
        for _son in g.son:
            son = _son[0]
            data = _son[1]
            Gr.node(son.id, son.type)
            dataId = "i_" + son.id
            Gr.node(dataId, data.__str__(), shape="box")
            Gr.edge(g.id, dataId)
            Gr.edge(dataId, son.id)
            print1(son)
    if g.out[1] == None:
        Gr.node(g.out[0].id, g.out[0].type)
        print1(g.out[0])
    else:
        data = g.out[1]
        color = TrueFalse(data[1])
        data = data[0]
        Gr.node("d_" + g.id, data.__str__(), shape="box", fontcolor=color)
        Gr.edge(g.id, "d_" + g.id)
if printgraph:
    Gr.node(graph.id, graph.type)
    print1(graph)
    Gr.render("graph", format="pdf", view=True)