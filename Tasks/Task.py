"""
Created on : 2025-07-07
Author   : Erwan Tchaleu
Email    : erwan.tchale@gmail.com

"""

from pymonik import task, MultiResultHandle

import numpy as np
from typing import List, Tuple, Optional, Union
from . import TaskEnv

onArmoniK = False

### NTask

@task(active=onArmoniK)
def nTask(delta : list, n : Union[int, List[list]], config :TaskEnv.Config, me, Recurse = True, Result: Optional[bool] = None):
    
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
    if isinstance(n, int):
        subdiv = TaskEnv.split(delta, n)
    else:
        subdiv = n
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
    if isinstance(n, list):
        n = len(n)
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
            print(idx, subdiv[idx])
            nabla = TaskEnv.listminus(omega, subdiv[idx])

            GrOut = None
            ### PrintGraph ### 
            if gPrint:
                me.addLabel("One fail")
                GrOut = Graph(emphas= "orange")
                me.down(GrOut, nabla)
                me.sout(GrOut, None)
            newdivision = []
            for div in subdiv:
                if div == subdiv[idx]:
                    continue
                if len(div) == 1:
                    newdivision.append(div)
                else:
                    temp = TaskEnv.split(div, 2)
                    newdivision.append(temp[0])
                    newdivision.append(temp[1])
            return nTask.invoke(nabla, newdivision, config, GrOut, True, False, delegate=True)
            

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
            if n % 2 != 0:
                conjugate[n-1] = n-1 if not vals[n-1] else None# type: ignore
            
            
            Nanswers = nTask.map_invoke(Args)
            GrOut = None

            ### PrintGraph ###
            if gPrint:
                GrOut = Graph()
                for arg in Args:
                    me.down(arg[3], arg[0])
                    GrOut.sup(*arg[3].out)
                me.sout(GrOut, None)

            return nAnalyserDown.invoke(subdiv, Nanswers, conjugate, n, config, GrOut, delegate = True)
        

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


    matrix : List[List[bool]] =[[True]*n for _ in range(n)]
    for i in range(nb):
        matrix[lst[i]][lst[i]] = False
    if nb == 1:
        print(lst)
        import copy
        pri = copy.deepcopy(matrix)
        for i in range(n):
            for j in range(n):
                if pri[i][j]:
                    pri[i][j] = 0
                else:
                    pri[i][j] = 'X'
        for col in pri:
            print(col)
                
        raise RuntimeError("BUGG")

    
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
    
    
    ### Analysis of the matrix
    def extractSquareMatrix(mat, tab): # extract the square matrix with the indexes given by tab
        size = len(tab)
        rep = [[True]*size for _ in range(size)]
        for i in range(size):
            for j in range(size):
                rep[i][j] = mat[tab[i]][tab[j]]
        return rep
    
    def extractMatrix(mat, col, rows): # extract the square matrix with the indexes given by tab
        size = len(col)
        lenght = len(rows)
        rep = [[True]*lenght for _ in range(size)]
        for i in range(size):
            for j in range(lenght):
                rep[i][j] = mat[col[i]][rows[j]]
        return rep
    
    def isnull(mat): # Checks if a matrix is null
        for col in mat:
            for elt in col:
                if elt:
                    return False
        return True
    
    def two(mat, size) -> Tuple[bool, int, int]:
        idx1 = None
        idx2 = None
        for i in range(size): #Finding two disctincts nablas that each have a element that the other doesn't have
            for j in range(size):
                if mat[i][j]:
                    idx1 = i
                    idx2 = j
        if idx1 == None or idx2 == None:
            raise RuntimeError("trying to find two complementary subsets in a null matrix")
        

        tab1 = []
        for idx in mat[idx1]:
            if not mat[idx1][idx]:
                tab1.append(idx)
        tab2 = []
        for idx in mat[idx2]:
            if not mat[idx2][idx]:
                tab2.append(idx)       

        if not (isnull(extractSquareMatrix(mat, tab2)) and isnull(extractSquareMatrix(mat, tab1))): # If there is only two elements, each nabla contain exactly one element (A, B)
            return False, None, None
        
        ### Need to make sure that there isn't any other element

        # Every nabla contains one of the two elements (A or B)
        for i in range(size):
            if mat[idx1][i] and mat[idx2][i]:
                return False, None, None
        
        # If there is a third element C, we have a nabla that contains C and not A and another that contain C and not B
        # So one that contain A and C and another B and C (since each nabla contains A or B)
        # The intersection of those 2 should not fail

        firstNotsecond = []
        for idx in tab1:
            if mat[idx2][idx]:
                firstNotsecond.append(idx)
        secondNotFirst = []
        for idx in tab2:
            if mat[idx1][idx]:
                firstNotsecond.append(idx)
        if not isnull(extractMatrix(mat, firstNotsecond, secondNotFirst)):
            return False, None, None
        return True, idx1, idx2
            

    
    omega = sum(subdiv, [])



    ### If only one failing subset (deg = 1) #########################################################################
    if isnull(extractSquareMatrix(matrix, lst)):

        # Launching calculus on the full intersection
        newDelta = omega
        for idx in lst:
            newDelta = TaskEnv.listminus(newDelta, subdiv[idx])
        
        Gr1 = Graph() if gPrint else None
        newdivision = []
        for idx in range(n):
            if idx in lst:
                continue
            if len(subdiv[idx]) == 1:
                newdivision.append(subdiv[idx])
            else:
                temp = TaskEnv.split(subdiv[idx], 2)
                newdivision.append(temp[0])
                newdivision.append(temp[1])
        res =  MultiResultHandle([nTask.invoke(newDelta, newdivision, config, Gr1, True, delegate=True)])
        
        GrOut = None

        ### PrintGraph ###
        if gPrint:
            me.addLabel(f"One subset")
            GrOut = Graph(emphas="blue")
            me.down(Gr1, newDelta)
            out = Gr1.out[0]
            while out != out.out[0]:
                out = out.out[0]
            GrOut.sup(*out.out)
            me.sout(GrOut, None)
                
        
        return Corrector.invoke(1, subdiv, res, matrix, n, config, GrOut, delegate=True)
    


    ### If there is two failing subsets (deg = 2) ####################################################################
    test, idx1, idx2 = two(extractMatrix(matrix, lst, lst), nb)
    if test:
        idx1 = lst[idx1]
        idx2 = lst[idx2]
        tab1 = []
        for idx in range(n):
            if not matrix[idx1][idx]:
                tab1.append(idx)
        tab2 = []
        for idx in range(n):
            if not matrix[idx2][idx]:
                tab2.append(idx)   

        NewNabla1 = omega
        for idx in tab1:
            NewNabla1 = TaskEnv.listminus(NewNabla1, subdiv[idx])
        Gr1 = Graph() if gPrint else None
        
        NewNabla2 = omega
        for idx in tab2:
            NewNabla2 = TaskEnv.listminus(NewNabla2, subdiv[idx])
        Gr2 = Graph() if gPrint else None

        newdivision1 = []
        for idx in range(n):
            if idx in tab1:
                continue
            if len(subdiv[idx]) == 1:
                newdivision1.append(subdiv[idx])
            else:
                temp = TaskEnv.split(subdiv[idx], 2)
                newdivision1.append(temp[0])
                newdivision1.append(temp[1])
        newdivision2 = []
        for idx in range(n):
            if idx in tab2:
                continue
            if len(subdiv[idx]) == 1:
                newdivision2.append(subdiv[idx])
            else:
                temp = TaskEnv.split(subdiv[idx], 2)
                newdivision2.append(temp[0])
                newdivision2.append(temp[1])

        
        Args = [(NewNabla1, newdivision1, config, Gr1), (NewNabla2, newdivision2, config, Gr2)]
        res = nTask.map_invoke(Args)
        GrOut = None

        ### PrintGraph ###
        if gPrint:
            me.addLabel(f"Two subsets")
            GrOut = Graph(emphas="blue")
            me.down(Gr1, NewNabla1)
            out = Gr1.out[0]
            while out != out.out[0]:
                out = out.out[0]
            GrOut.sup(*out.out)

            me.down(Gr2, NewNabla2)
            out = Gr2.out[0]
            while out != out.out[0]:
                out = out.out[0]
            GrOut.sup(*out.out)
            me.sout(GrOut, None)

        return Corrector.invoke(2, subdiv, res, matrix, n, config, GrOut, delegate = True)
        

    
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


#########################################################################################################
### Corrector
#########################################################################################################

@task(active=onArmoniK)
def Corrector(mode : int, subdiv : List[list], answers : List[Tuple[List[list] | None, bool]], matrix : List[List[bool]], n : int, config : TaskEnv.Config, me):
    ### PrintGraph ###
    gPrint = (me != None)
    if gPrint:
        from controllers import Graph
        me.setType("Checked")


    if mode == 1:
        if not answers[0][1]:

            ### PrintGraph ###
            if gPrint:
                me.addLabel("Simple")
                me.sout(me, answers[0])
            return answers[0]
    if mode == 2:
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
        if not answers[0][1] and not answers[1][1]:
            rep = merge(answers)
            ### PrintGraph ###
            if gPrint:
                me.addLabel("Double")
                me.sout(me, [rep, False])
            return rep, False
        
    raise RuntimeError("Gestion du fail guess non implémentée")