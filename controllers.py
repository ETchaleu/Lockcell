from pymonik import Pymonik, task
import numpy as np
from Tasks import nTask, TaskEnv

import cloudpickle # Install cloudpickle
cloudpickle.register_pickle_by_value(TaskEnv) # Pour les modules de ton code tu fait du sort que ca soit pickler par value

N = 2**10
searchspace = [i for i in range(N)]

def dd_min(searchspace :list):
    return nTask.invoke(searchspace, 2).wait().get() # type: ignore

def RDDMIN(searchspace : list, func, finalfunc):
    with Pymonik(endpoint="172.29.94.180:5001", environment={"pip":["numpy"]}):
        result = dd_min(searchspace) 
        i = 1
        tot = []
        while result[1] == False:
            print(result)
            dic = {}
            res = []
            for key in result[0]:
                if not (key.__str__() in dic):
                    res.append(key)
                    dic[key.__str__()] = True
            func(res, i)
            tot.extend(res)
            all = sum(result[0], [])
            searchspace = TaskEnv.listminus(searchspace, all)
            result = dd_min(searchspace)
        finalfunc(tot, i)

