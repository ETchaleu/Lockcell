import controllers
from Tasks import TaskEnv

import cloudpickle # Install cloudpickle
cloudpickle.register_pickle_by_value(TaskEnv) # Pour les modules de ton code tu fait du sort que ca soit pickler par value
cloudpickle.register_pickle_by_value(controllers) # Pour les modules de ton code tu fait du sort que ca soit pickler par value
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

def say(res, i):
    print(counter(i) + " results : " + res.__str__() + "\n" +"-"*80)

def finalSay(res, i):
    print("\n" + "-"*80 +"\n" + "-"*80  + "\n" + "Recursions : " + i.__str__() + " | Total results : " + res.__str__()  +"\n" + "-"*80  +"\n" + "-"*80, end ="\n\n")

config = controllers.TestConfig([[1, 3], [2], [5], [291], [389]])

controllers.RDDMIN(searchspace, say, finalSay, config)
