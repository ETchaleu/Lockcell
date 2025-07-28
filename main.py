"""
Created on : 2025-07-07
Author   : Erwan Tchaleu
Email    : erwan.tchale@gmail.com

"""

import controllers
from Tasks import TaskEnv
from graphViz import MultiViz
import VerrouConf

import cloudpickle # Install cloudpickle
cloudpickle.register_pickle_by_value(TaskEnv) # Pour les modules de ton code tu fait du sort que ca soit pickler par value
cloudpickle.register_pickle_by_value(controllers) # Pour les modules de ton code tu fait du sort que ca soit pickler par value
cloudpickle.register_pickle_by_value(VerrouConf) # Pour les modules de ton code tu fait du sort que ca soit pickler par value



printgraph = False
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


# Problème d'implémentation de la stochasticité, en effet les 1 minimaux d'un période ne failent pas forcément à la suivante il faut un cache ou alors transmette le fait que ce truc ne marche pas
Viz = MultiViz(active=printgraph)
#config = controllers.TestConfig([[[56], 0.3], [[94], 0.3], [[42, 40], 0.5], [[118, 114, 115], 0.5], [[76, 80, 78, 82], 0.5]])# EXCELLENT EXEMPLE avec N = 2**7
#config = controllers.TestConfig([[[0, 2, 4, 6], 0.5]])

import subprocess
import os

print("[INFO] Lancement du run de référence (sans perturbation)")

# Variables d’environnement pour le run de référence
env = os.environ.copy()
env["VERROU_ROUNDING_MODE"] = "nearest"
env["VERROU_FLOAT"] = "no"
env["VERROU_UNFUSED"] = "no"
env["VERROU_MCA_MODE"] = "ieee"

# Lancement de l’exécutable
ref_result = subprocess.run(
    ["./verrou/DD_RUN", "./verrou/ref"],
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)
if ref_result.returncode != 0:
    raise RuntimeError("Erreur lors de l'execution du run de référence, non perturbé")

config = VerrouConf.ConfigVerrou()
config.setInLinePath("lines")
config.setOutLinePath("Olines")
config.setDir("verrou")
config.PrepareForArmoniK()
#config = controllers.TestConfig([[[0, 2, 4, 6], 0.5]])
config.setMode("Analyse")
#config.GenProb(N, (2, 1, 0, 0.3), (1, 2, 2, 0.5), (6, 3, 4, 0.5)) # (combien, taille, écart type)
nbRunTab = [1, 4, 6]
input("press to continue...")
#res = controllers.SRDDMIN(searchspace, nbRunTab, say2, config)


def parse_line(s: str) -> str:
    """Extrait les deux premiers champs séparés par tabulation et retourne 'first:second'."""
    parts = s.strip().split('\t')
    if len(parts) < 2:
        raise ValueError("La chaîne ne contient pas au moins deux champs séparés par des tabulations.")
    return f"{parts[0]}:{parts[1]}"

def say(res, i):
    printable = []
    for r in res:
        ap = []
        for line in r:
            ap.append(parse_line(config.all_lines[line]))
        printable.append(ap)
    print(counter(i) + " results : " + printable.__str__() + "\n" +"-"*80)

def say2(res):
    print("Found : " + res.__str__() + "\n" +"-"*80)

def finalSay(res, i):
    printable = []
    for r in res:
        ap = []
        for line in r:
            ap.append(parse_line(config.all_lines[line]))
        printable.append(ap)
    print("\n" + "-"*80 +"\n" + "-"*80  + "\n" + "Recursions : " + i.__str__() + " | Total results : " + printable.__str__()  +"\n" + "-"*80  +"\n" + "-"*80)

res = controllers.RDDMIN(config.generateSearchSpace(), say, finalSay, config, Viz)
print(res)

if printgraph:
    Viz.aff_all()


