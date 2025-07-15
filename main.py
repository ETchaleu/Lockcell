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


N = 2**2
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
    print("\n" + "-"*80 +"\n" + "-"*80  + "\n" + "Recursions : " + i.__str__() + " | Total results : " + res.__str__()  +"\n" + "-"*80  +"\n" + "-"*80, end ="\n\n")

# Problème d'implémentation de la stochasticité, en effet les 1 minimaux d'un période ne failent pas forcément à la suivanten il faut un cache ou alors transmette le fait que ce truc ne marche pas
graph = controllers.Graph()
config = controllers.TestConfig()
config.GenProb(N, (2, 1, 0, 0.3))#, (2, 2, 2, 0.5), (1, 3, 4, 0.5)) # (combien, taille, écart type)
nbRunTab = [1, 4, 6]
print(config.Pb)
input("press to continue...")
#res = controllers.SRDDMIN(searchspace, nbRunTab, say2, config)
res = controllers.RDDMIN(searchspace, say, finalSay, config, graph)
print(res)
print(config.Pb)
