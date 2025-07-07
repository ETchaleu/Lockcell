from pymonik import Pymonik, task

from Tasks import nTask, TaskEnv
import copy

class TestConfig(TaskEnv.Config):
    def __init__(self, *args, nbRun = None):
        self.Pb = []
        self.nbRun = 1
        if nbRun != None:
            self.nbRun = nbRun
        if args:
            self.Pb = copy.deepcopy(args[0])
        super().__init__()
    
    def GenProb(self, N :int, *args):
        import numpy as np
        if args:
            for (cle, nbr, et) in args:
                try:
                    cle_int = int(cle)
                    if cle_int <=0:
                        raise ValueError("Génération du problem set impossible, la taille de l'ensemble passée est négative")
                    for _ in range(cle):
                        self.Pb.append(GenCloseSet(N, nbr, et))
                except ValueError as e:
                    raise ValueError("Erreur lors de la génération du problem set : conversion en entier | " + str(e))
        else:
            raise ValueError("Erreur lors de la génération du problem set : veuillez donner une taille d'ensemble minimaux au format \"taille de l'ensemble\" : nombre")
        
    
    
    def Test(self, subspace):
        for test in self.Pb:
            if TestConfig.In(subspace, test):
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

def GenCloseSet(N : int, size : int, ET : float):
    import numpy as np
    center = np.random.randint(0, N)
    val = [center]
    for _ in range(1, size):
        step = round(np.random.normal(loc = 0, scale = ET))
        center += step
        i = 1
        while center in val:
            up = center + i
            down = center - i
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

