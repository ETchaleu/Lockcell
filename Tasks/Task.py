# -*- coding: utf-8 -*-
"""
Created on Mon Jun 30 14:18:03 2025

@author: etchaleungankeu
"""
from pymonik import task

import numpy as np
from typing import List, Tuple
from . import TaskEnv


@task
def nTask(delta : list, n : int, config :TaskEnv.Config):

    ### Ecriture des logs en mémoire
    id = "PRGOUT : {}TASK : ".format(n) + delta.__str__()
    if config.Test(delta): # Test le delta passé en param
        return None, True
    
    # Si le test fail

    # Si |Delta| = 1 on a fini
    if len(delta) == 1:
        return [delta], False
    

    #Sinon on split en n (= granularity)
    subdiv = TaskEnv.split(delta, n)
    subdivArg = [(delta, 2, config) for delta in subdiv] #Mise en forme pour le passage en paramètre

    result = nTask.map_invoke(subdivArg) #type: ignore

    return nAGG.invoke(subdiv, result, n, config, delegate = True)#type: ignore

#########################################################################################################
#########################################################################################################

@task
def nAGG(subdiv : list, answers : List[Tuple[List[list] | None, bool]], n : int, config :TaskEnv.Config):

    ### Ecriture des logs en mémoire
    id = "PRGOUT : {}AGG : ".format(n) + subdiv.__str__()
     
      


    test = False
    for a in answers:
        if not a[1]:
            test = True
            break

    if test: # Si un des subset a fail on a fini et on renvoie le résultat
        rep = []
        for answer in answers:
            if answer[0] != None:
                rep.extend(answer[0])
        return rep, False
    

    if n == 2: # Si la granularité vaut 2, on ne test pas les complémentaires et on augmente directement la granularité
        omega = sum(subdiv, [])
        if len(omega) <= n:
            return [omega], False
        
        newdivision = [] # Pour le 2nAGG
        newdivisionArg = [] # Pour les nTask

        for delta in subdiv: # Mise en forme des lis
            temp = TaskEnv.split(delta, 2)
            newdivisionArg.append((temp[0], 2, config))
            newdivisionArg.append((temp[1], 2, config))
            newdivision.append(temp[0])
            newdivision.append(temp[1])
        result = nTask.map_invoke(newdivisionArg)#type: ignore

        k = min(2*n, len(omega))
        return nAGG.invoke(newdivision, result, k, delegate = True)#type: ignore
    
    #Sinon on teste les complémentaires
    
    omega = sum(subdiv, [])
    k = max(2, n-1)
    nablas = [(TaskEnv.listminus(omega, delta), k, config) for delta in subdiv]
    result = nTask.map_invoke(nablas)#type: ignore
    return nAGG2.invoke(subdiv, result, n, config, delegate = True)#type: ignore


#########################################################################################################
#########################################################################################################

@task
def nAGG2(subdiv : list, answers : List[Tuple[List[list] | None, bool]], n : int, config : TaskEnv.Config):

    ### Ecriture des logs en mémoire
    id = "PRGOUT : {}AGG2 : ".format(n) + subdiv.__str__()


    test = False
    for a in answers:
        if not a[1]:
            test = True
            break
    
    if test: # Si l'un des complémentaire à fail, on retourne directe l'union des set de subset
        rep = []
        for answer in answers:
            if answer[0] != None:
                rep.extend(answer[0])
        return rep, False

    # Sinon on augmente la granularité

    omega = sum(subdiv, [])
    if len(omega) <= n: # Si granularité max on retourne le delta courant (omega)
        return [omega], False
    
    newdivision = [] # Pour le 2nAGG
    newdivisionArg = [] # Pour les nTask

    for delta in subdiv: # Mise en forme des lis
        temp = TaskEnv.split(delta, 2)
        newdivisionArg.append((temp[0], 2, config))
        newdivisionArg.append((temp[1], 2, config))
        newdivision.append(temp[0])
        newdivision.append(temp[1])
    result = nTask.map_invoke(newdivisionArg)#type: ignore

    k = min(2*n, len(omega))
    return nAGG.invoke(newdivision, result, k, config, delegate = True) # type: ignore
