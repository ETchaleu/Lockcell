"""
Created on : 2025-07-07
Author   : Erwan Tchaleu
Email    : erwan.tchale@gmail.com

"""


from pymonik import Pymonik, task

from Tasks import nTask, TaskEnv
import copy

class TestConfig(TaskEnv.Config):
    def __init__(self, *args, nbRun = None):
        self.Pb = []
        super().__init__(nbRun)
        if args:
            self.Pb = copy.deepcopy(args[0])
        super().__init__()
    
    def GenProb(self, N :int, *args): # TODO: faire en sorte que les ensembles ne se surperposent pas
        self.Pb = []
        if args:
            for (cle, nbr, et, p) in args:
                try:
                    cle_int = int(cle)
                    if cle_int <=0:
                        raise ValueError("Génération du problem set impossible, la taille de l'ensemble passée est négative")
                    for _ in range(cle):
                        self.Pb.append([GenCloseSet(N, nbr, et), p])
                except ValueError as e:
                    raise ValueError("Erreur lors de la génération du problem set : conversion en entier | " + str(e))
        else:
            raise ValueError("Erreur lors de la génération du problem set : veuillez donner une taille d'ensemble minimaux au format \"taille de l'ensemble\" : nombre")
        
    
    
    def Test(self, subspace):
        for test in self.Pb:
            if TestConfig.In(subspace, test[0]):
                    return False
        return True
    
    @staticmethod
    def In(tab : list, test : list):
        res = True
        for i in test:
            if not (i in tab):
                res = False
                break
        return res
    
    def copy(self):
        newCopy = TestConfig(self.Pb, self.nbRun)
        return newCopy

def GenCloseSet(N : int, size : int, ET : float):
    import numpy as np
    center = np.random.randint(0, N)
    val = [center]
    for _ in range(1, size):
        step = round(np.random.normal(loc = 0, scale = ET))
        center += step
        i = 1
        while center in val:
            up = min(center + i, N -1)
            down = max(center - i, 0)
            if up not in val:
                center = up
            elif down not in val:
                center = down
            i += 1
        val.append(center)
    return val
            

N = 2**10
searchspace = [i for i in range(N)]

def dd_min(searchspace :list, config : TaskEnv.Config):
    return nTask.invoke(searchspace, 2, config) # type: ignore

def RDDMIN(searchspace : list, func, finalfunc, config : TaskEnv.Config):
    with Pymonik(endpoint="172.29.94.180:5001", environment={"pip":["numpy"]}):
        result = dd_min(searchspace, config).wait().get() 
        i = 1
        tot = []
        while result[1] == False:
            # On retire les doublons
            dic = {}
            res = []
            for key in result[0]:
                if not (key.__str__() in dic):
                    res.append(key)
                    dic[key.__str__()] = True
            # On transmet
            if func != None:
                func(res, i)
            
            #Ajout au total + réduction du searchspace, puis on relance un dd_min
            tot.extend(res)
            all = sum(result[0], [])
            searchspace = TaskEnv.listminus(searchspace, all)
            result = dd_min(searchspace, config).wait().get()
            i += 1
        if finalfunc != None:
            finalfunc(tot, i)
        return tot, i

def SRDDMIN(searchspace : list, nbRunTab : list, found, config : TaskEnv.Config):
    #TODO: Preprocessing of nbRunTab

    findback = {}
    i = 0
    tot = []
    for run in nbRunTab:
        findback[run] = i
        i += 1
    with Pymonik(endpoint="172.29.94.180:5001", environment={"pip":["numpy"]}):
        firstFail = False
        for run in nbRunTab:
            config.setNbRun(run)
            result = dd_min(searchspace, config).wait().get()
            if result[1] == True:
                continue
            while result[1] == False:
                firstFail = True
                config.setNbRun(run)
                done = False
                Args = [(res, 2, config) for res in result[0]]
                storeResult = nTask.map_invoke(Args).wait().get() 

                #TODO: Quand l'implem de la disponibilité au plus tot sera prête faudra adapter
                while not done:
                    ready = [i for i in range(len(storeResult))]
                    notReady = TaskEnv.listminus([i for i in range(len(storeResult))], ready)
                    nextArgs = []
                    waiting = [storeResult[idx] for idx in notReady]
                    didit = [storeResult[idx] for idx in ready]

                    #préparation des configuration pour les tâches suivantes,
                    for res in didit:
                        where = findback[res[2].nbRun]
                        if where + 1 >= len(nbRunTab): #Si on a déjà atteint le nombre de run max, on ajoute la sortie à tot et on réduit le search space
                            tot.extend(res[0])
                            all = sum(res[0], [])
                            found(res[0])
                            searchspace = TaskEnv.listminus(searchspace, all)
                            continue

                        nextrun = nbRunTab[where+1] # Sinon on trouve le nombre de run suivant et on prépare le lancement des tâches filles
                        onesized = []
                        for sub in res[0]:
                            if len(sub) == 1:
                                onesized.append(sub)
                                continue 
                            newconf = config.copy()
                            newconf.setNbRun(nextrun)
                            nextArgs.append((sub, 2, newconf))
                        if onesized != []:
                            tot.extend(onesized)
                            all = sum(onesized, [])
                            found(onesized)
                            searchspace = TaskEnv.listminus(searchspace, all)
                    if nextArgs:
                        if not waiting:
                            storeResult = nTask.map_invoke(nextArgs).wait().get()
                        else:
                            storeResult = waiting.extend(nTask.map_invoke(nextArgs)).wait().get()
                    else:
                        if not waiting:
                            done = True
                            continue
                        storeResult = waiting.wait().get()
                result = dd_min(searchspace, config).wait().get()
        if firstFail:    
            return tot
        raise RuntimeError(f"SRDDMin : testing the subset {nbRunTab[-1]} times has never returned false")


