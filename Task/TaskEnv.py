# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 11:02:38 2025

@author: etchaleungankeu
"""

Pb = [[1, 3], [2], [5], [291], [389]]


        

verb = False

def Validate(tab : list):
    dic = {}
    for i in Pb:
        dic[i.__str__()] = 0
    for i in tab:
        if not i.__str__() in dic:
            return False
        dic[i.__str__()] +=1
    for a in dic:
        if dic[a] != 1:
            return False
    return True


def verbose(tab : list, end =None): # type: ignore
    if end == None:
        end = ""
    if verb:
        for p in tab:
            print(p, end =end)
        print() 
      


# Test fonction from Delta Debug

def In(tab : list, test : list):
    res = True
    for i in test:
        if not (i in tab):
            res = False
            break
    return res

def Test(tab: list, Prob = Pb):
    for test in Prob:
        if In(tab, test):
            return False
    return True


# List manipulers

def split(tab : list, n: int):
    """Stub to overload in subclasses"""
    subsets = []
    start = 0
    for i in range(n):
        subset = tab[start:start + (len(tab) - start) // (n - i)]
        subsets.append(subset)
        start = start + len(subset)
    return subsets

def listminus(c1 :list, c2 :list):
    """Return a list of all elements of C1 that are not in C2."""
    s2 = {}
    for delta in c2:
        s2[delta] = 1

    c = []
    for delta in c1:
        if not delta in s2:
            c.append(delta)

    return c