from pymonik import Pymonik, task
import numpy as np
from Tasks import nTask, TaskEnv

import cloudpickle # Install cloudpickle
cloudpickle.register_pickle_by_value(TaskEnv) # Pour les modules de ton code tu fait du sort que ca soit pickler par value

N = 2**10
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

with Pymonik(endpoint="172.29.94.180:5001", environment={"pip":["numpy"]}):
    result = nTask.invoke(searchspace, 2).wait().get()#type: ignore
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

        print(counter(i) + " results : " + res.__str__() + "\n" +"-"*80)
        tot.extend(res)
        all = sum(result[0], [])
        searchspace = TaskEnv.listminus(searchspace, all)
        i+= 1
        result = nTask.invoke(searchspace, 2).wait().get()#type: ignore
    print("\n" + "-"*80 +"\n" + "-"*80  + "\n" + "Total results : " + tot.__str__()  +"\n" + "-"*80  +"\n" + "-"*80, end ="\n\n")
    if TaskEnv.Validate(tot):
        print("Success !!")
    else:
        print("Failure...")
        print("Theorical Set : \n" + TaskEnv.Pb.__str__())
