"""
Created on : 2025-07-07
Author   : Erwan Tchaleu
Email    : erwan.tchale@gmail.com

"""

import controllers
from Tasks import TaskEnv
from graphViz import MultiViz

import cloudpickle # Install cloudpickle
cloudpickle.register_pickle_by_value(TaskEnv) # Pour les modules de ton code tu fait du sort que ca soit pickler par value
cloudpickle.register_pickle_by_value(controllers) # Pour les modules de ton code tu fait du sort que ca soit pickler par value


printgraph = True
N = 2**6
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

# Problème d'implémentation de la stochasticité, en effet les 1 minimaux d'un période ne failent pas forcément à la suivante il faut un cache ou alors transmette le fait que ce truc ne marche pas
Viz = MultiViz(active=printgraph)
### config = controllers.TestConfig([[[56], 0.3], [[94], 0.3], [[42, 40], 0.5], [[118, 114, 115], 0.5], [[76, 80, 82], 0.5]]) EXCELLENT EXEMPLE avec N = 2**7
config = controllers.TestConfig([([51], 0.3), ([1], 0.3), ([12, 11], 0.5), ([4, 2, 0], 0.5), ([63, 62, 61], 0.5), ([15, 10, 6], 0.5), ([20, 17, 16], 0.5), ([46, 40, 35], 0.5)])
config.setMode("Analyse")
#config.GenProb(N, (2, 1, 0, 0.3), (1, 2, 2, 0.5), (5, 3, 4, 0.5)) # (combien, taille, écart type)
nbRunTab = [1, 4, 6]
print(config.Pb)
input("press to continue...")
#res = controllers.SRDDMIN(searchspace, nbRunTab, say2, config)
res = controllers.RDDMIN(searchspace, say, finalSay, config, Viz)
print(res)
print(config.Pb)

if printgraph:
    Viz.aff_all()


