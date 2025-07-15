"""
Created on : 2025-07-07
Author   : Erwan Tchaleu
Email    : erwan.tchale@gmail.com

"""

from pymonik import task

import numpy as np
from typing import List, Tuple
from . import TaskEnv

onArmoniK = True

@task(active=onArmoniK)
def nTask(delta : list, n : int, config :TaskEnv.Config, me):
    ############# PrintGraph
    if me != None:
        from controllers import Graph
        me.setType(f"{n}Task")
    ### Ecriture des logs en mémoire
    id = "PRGOUT : {}TASK : ".format(n) + delta.__str__()
    if config.Test(delta): # Test le delta passé en param

        ############# PrintGraph
        if me != None:
            me.sout(me, [None, True])
        return None, True, config
    
    # Si le test fail

    # Si |Delta| = 1 on a fini
    if len(delta) == 1:

        ############# PrintGraph
        if me != None:
            me.sout(me, [[delta], False])
        return [delta], False, config
    

    #Sinon on split en n (= granularity)
    subdiv = TaskEnv.split(delta, n)
    subdivArg = [(delta, 2, config, Graph() if me != None else None) for delta in subdiv] #Mise en forme pour le passage en paramètre
    GrOut = None

    ############# PrintGraph
    if me != None:
        GrOut = Graph()
    result = nTask.map_invoke(subdivArg) #type: ignore

    ############# PrintGraph
    if me != None:
        for i in subdivArg:
            me.down(i[3], i[0])
            out = i[3].out[0]
            while out != out.out[0]:
                out = out.out[0]
            GrOut.sup(*out.out)
        me.sout(GrOut, None)

    return nAGG.invoke(subdiv, result, n, config,  GrOut, delegate = True)#type: ignore

#########################################################################################################
#########################################################################################################

@task(active=onArmoniK)
def nAGG(subdiv : list, answers : List[Tuple[List[list] | None, bool]], n : int, config :TaskEnv.Config, me):

    ############# PrintGraph
    if me != None:
        from controllers import Graph
        me.setType(f"{n}AGG")
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

        ############# PrintGraph
        if me != None:
            me.sout(me, [rep, False])
        return rep, False, config
    

    if n == 2: # Si la granularité vaut 2, on ne test pas les complémentaires et on augmente directement la granularité
        omega = sum(subdiv, [])
        if len(omega) <= n:

            ############# PrintGraph
            if me != None:
                me.sout(me, [[omega], False])
            return [omega], False, config
        
        newdivision = [] # Pour le 2nAGG
        newdivisionArg = [] # Pour les nTask

        k = min(2*n, len(omega))
        for delta in subdiv: # Mise en forme des lis
            if len(delta) >= 2:
                temp = TaskEnv.split(delta, 2)
                newdivisionArg.append((temp[0], 2, config, Graph() if me != None else None))
                newdivisionArg.append((temp[1], 2, config, Graph() if me != None else None))
                newdivision.append(temp[0])
                newdivision.append(temp[1])
            else :
                newdivisionArg.append((delta, 2, config, Graph() if me != None else None))
                newdivision.append(delta)
            
        result = nTask.map_invoke(newdivisionArg)#type: ignore
        GrOut = None

        ############# PrintGraph
        if me != None:
            GrOut = Graph()
            for i in newdivisionArg:
                me.down(i[3], i[0])
                GrOut.sup(*i[3].out)
            me.sout(GrOut, None)

        return nAGG.invoke(newdivision, result, k, config, GrOut, delegate = True)#type: ignore
    
    #Sinon on teste les complémentaires
    
    omega = sum(subdiv, [])
    k = max(2, n-1)
    nablas = [(TaskEnv.listminus(omega, delta), k, config, Graph() if me != None else None) for delta in subdiv]
    result = nTask.map_invoke(nablas)#type: ignore
    GrOut = None

    ############# PrintGraph
    if me != None:
        GrOut = Graph()
        for i in nablas:
            me.down(i[3], i[0])
            GrOut.sup(*i[3].out)
        me.sout(GrOut, None)
    return nAGG2.invoke(subdiv, result, n, config, GrOut, delegate = True)#type: ignore


#########################################################################################################
#########################################################################################################

@task(active=onArmoniK)
def nAGG2(subdiv : list, answers : List[Tuple[List[list] | None, bool]], n : int, config : TaskEnv.Config, me):

    ############# PrintGraph
    if me != None:
        from controllers import Graph
        me.setType(f"{n}AGG2")
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

        ############# PrintGraph
        if me != None: 
            me.sout(me, [rep, False])
        return rep, False, config

    # Sinon on augmente la granularité

    omega = sum(subdiv, [])
    if len(omega) <= n: # Si granularité max on retourne le delta courant (omega)

        ############# PrintGraph
        if me != None:
            me.sout(me, [[omega], False])
        return [omega], False, config
    
    newdivision = [] # Pour le 2nAGG
    newdivisionArg = [] # Pour les nTask

    k = min(2*n, len(omega))
    for delta in subdiv: # Mise en forme des lis
        if len(delta) >= 2:
            temp = TaskEnv.split(delta, 2)
            newdivisionArg.append((temp[0], 2, config, Graph() if me != None else None))
            newdivisionArg.append((temp[1], 2, config, Graph() if me != None else None))
            newdivision.append(temp[0])
            newdivision.append(temp[1])
        else :
            newdivisionArg.append((delta, 2, config, Graph() if me != None else None))
            newdivision.append(delta)
    result = nTask.map_invoke(newdivisionArg)#type: ignore
    GrOut = None

    ############# PrintGraph
    if me != None:
        GrOut = Graph()
        for i in newdivisionArg:
            me.down(i[3], i[0])
            GrOut.sup(*i[3].out)
        me.sout(GrOut, None)

    return nAGG.invoke(newdivision, result, k, config, GrOut, delegate = True) # type: ignore
