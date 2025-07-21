"""
Created on : 2025-07-07
Author   : Erwan Tchaleu
Email    : erwan.tchale@gmail.com

"""

from pymonik import task, MultiResultHandle

import numpy as np
from typing import List, Tuple, Optional
from . import TaskEnv

onArmoniK = False

### NTask

@task(active=onArmoniK)
def nTask(delta : list, n : int, config :TaskEnv.Config, me, Recurse = True, Result: Optional[bool] = None):
    
    ### PrintGraph ###
    gPrint = (me != None)
    if gPrint:
        from controllers import Graph
        me.setType(f"{n}Task")
    ### Ecriture des logs en mémoire
    id = "PRGOUT : {}TASK : ".format(n) + delta.__str__()

    # Si le resultat est déjà connu on ne teste pas
    test = None
    if Result == None:
        test = config.Test(delta)
    else:
        test = Result


    if test: # Test le delta passé en param

        ### PrintGraph ###
        if gPrint:
            me.sout(me, [None, True])
        return None, True
    
    if Recurse == False: # Si pas de récusivité
        ### PrintGraph ###
        if gPrint:
            me.sout(me, ["Input", False])
        return "Input", False

    # Si le test fail

    # Si |Delta| = 1 on a fini
    if len(delta) == 1:

        ### PrintGraph ###
        if gPrint:
            me.sout(me, [[delta], False])
        return [delta], False
    

    #Sinon on split en n (= granularity)
    subdiv = TaskEnv.split(delta, n)
    subdivArg = [(delta, 2, config, Graph() if gPrint else None) for delta in subdiv] #Mise en forme pour le passage en paramètre
    GrOut = None

    ### PrintGraph ###
    if gPrint:
        GrOut = Graph()
    result = nTask.map_invoke(subdivArg) #type: ignore

    ### PrintGraph ###
    if gPrint:
        for i in subdivArg:
            me.down(i[3], i[0])
            out = i[3].out[0]
            while out != out.out[0]:
                out = out.out[0]
            GrOut.sup(*out.out)
        me.sout(GrOut, None)

    return nAGG.invoke(subdiv, result, n, config,  GrOut, delegate = True)#type: ignore




#########################################################################################################
### NAGG
#########################################################################################################

@task(active=onArmoniK)
def nAGG(subdiv : List[list], answers : List[Tuple[List[list] | None, bool]], n : int, config :TaskEnv.Config, me):

    ### PrintGraph ###
    gPrint = (me != None)
    if gPrint:
        from controllers import Graph
        me.setType(f"{n}AGG")
    ### Ecriture des logs en mémoire
    id = "PRGOUT : {}AGG : ".format(n) + subdiv.__str__()
     
      


    test = False
    for a in answers:
        if not a[1]:
            test = True
            break

    def merge(tabofrep): # Merge sans doublon
        dic = {}
        res = []
        for rep in tabofrep:
            if rep[0] == None:
                continue
            for val in rep[0]:
                key = val.__str__()
                if key not in dic:
                    dic[key] = val
                    res.append(val)
        return res

            

    if test: # Si l'un des sets à fail, on retourne directe l'union des set de subset
        rep = merge(answers)

        ### PrintGraph ###
        if gPrint:
            me.sout(me, [rep, False])
        return rep, False
    

    if n == 2: # Si la granularité vaut 2, on ne test pas les complémentaires et on augmente directement la granularité
        omega = sum(subdiv, [])
        if len(omega) <= n:

            ### PrintGraph ###
            if gPrint:
                me.sout(me, [[omega], False])
            return [omega], False
        
        newdivision = [] # Pour le 2nAGG
        newdivisionArg = [] # Pour les nTask

        k = min(2*n, len(omega))
        for delta in subdiv: # Mise en forme des lis
            if len(delta) >= 2:
                temp = TaskEnv.split(delta, 2)
                newdivisionArg.append((temp[0], 2, config, Graph() if gPrint else None))
                newdivisionArg.append((temp[1], 2, config, Graph() if gPrint else None))
                newdivision.append(temp[0])
                newdivision.append(temp[1])
            else :
                newdivisionArg.append((delta, 2, config, Graph() if gPrint else None))
                newdivision.append(delta)
            
        result = nTask.map_invoke(newdivisionArg)#type: ignore
        GrOut = None

        ### PrintGraph ###
        if gPrint:
            GrOut = Graph()
            for i in newdivisionArg:
                me.down(i[3], i[0])
                GrOut.sup(*i[3].out)
            me.sout(GrOut, None)

        return nAGG.invoke(newdivision, result, k, config, GrOut, delegate = True)#type: ignore
    
    

    next = nAGG2
    recursion = True
    #Sinon on teste les complémentaires
    if config.mode == "Analyse":

        ### PrintGraph ###
        if gPrint:
            me.setType(f"{n}Analyser - Up")

        # Changement du type d'execution si mode Analyser
        recursion = False
        next = nAnalyser
        
        
    omega = sum(subdiv, [])
    k = max(2, n-1)
    nablas = [(TaskEnv.listminus(omega, delta), k, config, Graph() if gPrint else None, recursion) for delta in subdiv]
    result = nTask.map_invoke(nablas)#type: ignore
    GrOut = None

    ### PrintGraph ###
    if gPrint:
        GrOut = Graph()
        for i in nablas:
            me.down(i[3], i[0])
            GrOut.sup(*i[3].out)
        me.sout(GrOut, None)
    
    return next.invoke(subdiv, result, n, config, GrOut, delegate = True)#type: ignore






#########################################################################################################
### NAGG2
#########################################################################################################

@task(active=onArmoniK)
def nAGG2(subdiv : List[list], answers : List[Tuple[List[list] | None, bool]], n : int, config : TaskEnv.Config, me):

    ### PrintGraph ###
    gPrint = (me != None)
    if gPrint:
        from controllers import Graph
        me.setType(f"{n}AGG2")

    ### Ecriture des logs en mémoire
    id = "PRGOUT : {}AGG2 : ".format(n) + subdiv.__str__()


    test = False
    for a in answers:
        if not a[1]:
            test = True
            break
    
    def merge(tabofrep): # Merge sans doublon
        dic = {}
        res = []
        for rep in tabofrep:
            if rep[0] == None:
                continue
            for val in rep[0]:
                key = val.__str__()
                if key not in dic:
                    dic[key] = val
                    res.append(val)
        return res

            

    if test: # Si l'un des complémentaire à fail, on retourne directe l'union des set de subset
        rep = merge(answers)

        ### PrintGraph ###
        if gPrint: 
            me.sout(me, [rep, False])
        return rep, False

    # Sinon on augmente la granularité

    omega = sum(subdiv, [])
    if len(omega) <= n: # Si granularité max on retourne le delta courant (omega)

        ### PrintGraph ###
        if gPrint:
            me.sout(me, [[omega], False])
        return [omega], False
    
    newdivision = [] # Pour le 2nAGG
    newdivisionArg = [] # Pour les nTask

    k = min(2*n, len(omega))
    for delta in subdiv: # Mise en forme des lis
        if len(delta) >= 2:
            temp = TaskEnv.split(delta, 2)
            newdivisionArg.append((temp[0], 2, config, Graph() if gPrint else None))
            newdivisionArg.append((temp[1], 2, config, Graph() if gPrint else None))
            newdivision.append(temp[0])
            newdivision.append(temp[1])
        else :
            newdivisionArg.append((delta, 2, config, Graph() if gPrint else None))
            newdivision.append(delta)
    result = nTask.map_invoke(newdivisionArg)#type: ignore
    GrOut = None

    ### PrintGraph ###
    if gPrint:
        GrOut = Graph()
        for i in newdivisionArg:
            me.down(i[3], i[0])
            GrOut.sup(*i[3].out)
        me.sout(GrOut, None)

    return nAGG.invoke(newdivision, result, k, config, GrOut, delegate = True) # type: ignore




#########################################################################################################
### NAnalyser
#########################################################################################################

@task(active=onArmoniK)
def nAnalyser(subdiv : List[list], answers : List[Tuple[List[list] | None, bool]], n : int, config : TaskEnv.Config, me):

    ### PrintGraph ###
    gPrint = (me != None)
    if gPrint:
        from controllers import Graph
        me.setType(f"{n}Analyser - Down")
    ### Ecriture des logs en mémoire
    id = "PRGOUT : {}Analyser - Down : ".format(n) + subdiv.__str__()


    test = False
    idxs = []
    idx = 0
    for a in answers:
        if not a[1]:
            test = True
            idxs.append(idx)
        idx += 1

            
    omega = sum(subdiv, []) # Utile pour faire tous les complémentaires etc


    if test: ##### Si l'un des complémentaire a fail, on analyse
            
                
        # Est-on au niveau de découpage le plus fin
        granularityMax = (len(omega) == n) 
        if granularityMax and (len(idxs) == 1): #TODO: cf. preuve 
            rep = [TaskEnv.listminus(omega, subdiv[idxs[0]])]
            ### PrintGraph ###
            if gPrint:
                me.addLabel("One fail")
                me.addLabel("Granularity Max !")
                me.sout(me, [rep, False])
            return rep, False
        

        if len(idxs) == 1: # Si un seul fail on recurse dessus
            #On prépare les arguments
            idx = idxs[0]
            nabla = TaskEnv.listminus(omega, subdiv[idx])

            GrOut = None
            ### PrintGraph ### 
            if gPrint:
                me.addLabel("One fail")
                GrOut = Graph(emphas= "orange")
                me.down(GrOut, nabla)
                me.sout(GrOut, None)

            k = min(2*(n-1), len(nabla))
            return nTask.invoke(nabla, k, config, GrOut, True, False, delegate=True)
            

        Achanger = True #TODO: Activation de l'analyse ou pas à retirer
        if Achanger: 


            ### PrintGraph ###
            if gPrint:
                me.setType(f"{n}Analyser - Middle")
            
            # On prépare les arguments pour chaque nabla qui bug, avec le nabla associé, la subdiv adaptée et on a déjà le resultat
            Args = []
            vals = [True for i in range(n)]
            for idx in idxs:
                vals[idx] = False

            #Création des Arguments pour tester les intersections
            # TODO: Adapter pour que si le split en deux n'etait pas possible on le sache
            bis = n // 2
            for i in range(bis):
                idx = 2*i
                if vals[idx] == False:
                    for j in range(idx+2, n):
                        if vals[j] == False:
                            intersection = TaskEnv.listminus(omega, subdiv[idx])
                            intersection = TaskEnv.listminus(intersection, subdiv[j])
                            Args.append((intersection, 2, config, Graph() if gPrint else None, False))

                idx = 2*i + 1
                if vals[idx] == False:
                    for j in range(idx+1, n):
                        if vals[j] == False:
                            intersection = TaskEnv.listminus(omega, subdiv[idx])
                            intersection = TaskEnv.listminus(intersection, subdiv[j])
                            Args.append((intersection, 2, config, Graph() if gPrint else None, False))
            
            #Building the conjugated tab
            conjugate = [None for _ in range(n)]
            for i in range(bis):
                if vals[2*i] == False and vals[2*i+1] == False:
                    conjugate[2*i] = 2*i + 1 # type: ignore
                    conjugate[2*i+1] = 2*i # type: ignore
                else:
                    conjugate[2*i] = 2*i if not vals[2*i] else None # type: ignore
                    conjugate[2*i + 1] = 2*i + 1 if not vals[2*i + 1] else None # type: ignore
                    
            
            
            answers = nTask.map_invoke(Args)
            GrOut = None

            ### PrintGraph ###
            if gPrint:
                GrOut = Graph()
                for arg in Args:
                    me.down(arg[3], arg[0])
                    GrOut.sup(*arg[3].out)
                me.sout(GrOut, None)

            return nAnalyserDown.invoke(subdiv, answers, conjugate, n, config, GrOut, delegate = True)
        

        else: # Pas de traitement

            ### PrintGraph ###
            if gPrint:
                me.addLabel(f"No Opti")
            
            # On prépare les arguments pour chaque nabla qui bug, avec le nabla associé, la subdiv adaptée et on a déjà le resultat
            Args = []
            vals = [True for i in range(n)]
            
            for idx in idxs:
                k = min(n-1, len(omega) - len(subdiv[idx]))
                Args.append((TaskEnv.listminus(omega, subdiv[idx]), k, config, Graph(emphas = "orange") if gPrint else None, True, False))
            answers = nTask.map_invoke(Args)

            GrOut = None

            ### PrintGraph ###
            if gPrint:
                GrOut = Graph()
                for arg in Args:
                    me.down(arg[3], arg[0])
                    GrOut.sup(*arg[3].out)
                me.sout(GrOut, None)

            return nAGG2.invoke(subdiv, answers, len(idxs), config, GrOut, delegate = True)#type: ignore



    
    # Sinon on augmente la granularité

    if len(omega) <= n: # Si granularité max on retourne le delta courant (omega)

        ### PrintGraph ###
        if gPrint:
            me.addLabel("Granularity Max !")
            me.sout(me, [[omega], False])
        return [omega], False

    ### PrintGraph ###
    if gPrint:
        me.addLabel("granularity up")
    
    newdivision = [] # Pour le 2nAGG
    newdivisionArg = [] # Pour les nTask

    k = min(2*n, len(omega))
    for delta in subdiv: # Mise en forme des lis
        if len(delta) >= 2:
            temp = TaskEnv.split(delta, 2)
            newdivisionArg.append((temp[0], 2, config, Graph() if gPrint else None))
            newdivisionArg.append((temp[1], 2, config, Graph() if gPrint else None))
            newdivision.append(temp[0])
            newdivision.append(temp[1])
        else :
            newdivisionArg.append((delta, 2, config, Graph() if gPrint else None))
            newdivision.append(delta)
    result = nTask.map_invoke(newdivisionArg)#type: ignore
    GrOut = None

    ### PrintGraph ###
    if gPrint:
        GrOut = Graph()
        for i in newdivisionArg:
            me.down(i[3], i[0])
            GrOut.sup(*i[3].out)
        me.sout(GrOut, None)

    return nAGG.invoke(newdivision, result, k, config, GrOut, delegate = True) # type: ignore

#########################################################################################################
### NAnalyser
#########################################################################################################

@task(active=onArmoniK)
def nAnalyserDown(subdiv : List[list], answers : List[Tuple[List[list] | None, bool]], conj : List[Optional[int]], n : int, config : TaskEnv.Config, me):

    ### PrintGraph ###
    gPrint = (me != None)
    if gPrint:
        from controllers import Graph
        me.setType(f"{n}Analyser - Down")

    ### Transform answers into matrix
    lst = [i for (i, x) in enumerate(conj) if not (x is None)]
    nb = len(lst)


    matrix =[[True]*n for _ in range(n)]
    for i in range(nb):
        matrix[lst[i]][lst[i]] = False
    
    idx1 = 0
    idx2 = 1
    for anwser in answers: # On parcours les réponses comme si on parcourait une matrice triangulaire supérieur ligne par ligne (sans la diagonale)
        if conj[lst[idx1]] == lst[idx2]: # On saute les conjugués
            idx2 += 1

        if not anwser[1]:
            matrix[lst[idx1]][lst[idx2]] = False
            matrix[lst[idx2]][lst[idx1]] = False

        idx2 += 1
        if idx2 >= nb: # Si on est arrivés au bout on recommance ligne suivante
            idx1 += 1
            idx2 = idx1 + 1
    
    """import copy
    pri = copy.deepcopy(matrix)
    for i in range(n):
        for j in range(n):
            if pri[i][j]:
                pri[i][j] = 0
            else:
                pri[i][j] = 'X'
    for col in pri:
        print(col)"""
            
    ### Analysis of the matrix
    def extractMatrix(tab): # extract the square matrix with the indexes given by tab
        size = len(tab)
        rep = [[True]*size for _ in range(size)]
        for i in range(size):
            for j in range(size):
                rep[i][j] = matrix[tab[i]][tab[j]]
        return rep
    
    def isnull(mat): # Checks if a matrix is null
        for col in mat:
            for elt in col:
                if elt:
                    return False
        return True
    
    omega = sum(subdiv, [])



    ### If only one failing subset (deg = 1) #########################################################################
    if isnull(extractMatrix(lst)):

        # Launching calculus on the full intersection
        newDelta = omega
        for idx in lst:
            newDelta = TaskEnv.listminus(newDelta, subdiv[idx])
        
        GrOut = None

        ### PrintGraph ###
        if gPrint:
            me.addLabel(f"One subset")
            GrOut = Graph()
            me.down(GrOut, newDelta)
            me.sout(GrOut, None)
                
        return nTask.invoke(newDelta, n-nb, config, GrOut, True, False, delegate=True)
    

    
    ### Sinon on simule une execution classique ######################################################################
    else:


        #TODO: On peut faire bien mieux
        results = []
        fakesons = []
        for idx in range(n): #Correspond à une n-1 Task
            nabla = TaskEnv.listminus(omega, subdiv[idx])
            if not idx in lst: # Si c'est un tache qui ne fail pas, on la génère simplement
                results.append(nTask.invoke(nabla, n-1, config, Graph(emphas="orange"), False, True))
                continue
            
                
            subdivArg = []
            newSubdiv = []
            graphs = []
            for i in range(n):
                if i == idx:
                    continue
                nablaPrime = TaskEnv.listminus(nabla, subdiv[i])
                newSubdiv.append(subdiv[i])
                rep = matrix[idx][i]
                ### PrintGraph ###
                if gPrint:
                    graphs.append(Graph(emphas="orange"))
                subdivArg.append((nablaPrime, n-2, config, graphs[-1] if gPrint else None, True, rep)) #Mise en forme pour le passage en paramètre
            
            result = nTask.map_invoke(subdivArg) #type: ignore

            fakeMother = None

            ### PrintGraph ###
            if gPrint:
                fakeMother = Graph(emphas="orange")
                fakeMother.setType(f"{n-1}Task")
                me.down(fakeMother, nabla)
                fakesons.append(fakeMother)


            GrOut1 = None

            ### PrintGraph ###
            if gPrint:
                GrOut1 = Graph()
                
                for i in subdivArg:
                    fakeMother.down(i[3], i[0])
                    out = i[3].out[0]
                    while out != out.out[0]:
                        out = out.out[0]
                    GrOut1.sup(*out.out)
                fakeMother.sout(GrOut1, None)

            results.append(nAGG.invoke(newSubdiv, result, n, config, GrOut1))
        


        ## On a récupéré les données des n-1 task et on lance donc un n aggregateur pour sortir la réponse
        GrOut = None

        ### PrintGraph ###
        if gPrint:
            GrOut = Graph()
            
            for i in fakesons:
                out = i.out[0]
                while out != out.out[0]:
                    out = out.out[0]
                GrOut.sup(*out.out)
            me.sout(GrOut, None)
        results = MultiResultHandle(results)
        return nAGG.invoke(subdiv, results, n, config, GrOut)