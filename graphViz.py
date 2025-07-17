"""
Created on : 2025-07-17
Author   : Erwan Tchaleu
Email    : erwan.tchale@gmail.com

"""

### AFFICHAGE DU GRAPHE DES TÂCHES

from graphviz import Digraph
from controllers import Graph


class VizPrint:
    def __init__(self):
        self.Gr = Digraph()
        self.start = Graph()
        
    def findOut(self, g : Graph) -> Graph:
        out = g.out[0]
        while out != out.out[0]:
            out = out.out[0]
        return out

    def TrueFalse(self, val):
        return "green" if val else "black"

    def UpColorSelector(self, g : Graph):
        res = ["black"]*len(g.up)
        mem = {}
        mem2 = {}
        for (idx, _in) in enumerate(g.up):
                out = self.findOut(_in[0])

                data = out.out[1][0]
                if data == None:
                    continue

                for dat in data: # On vérifie si tous les sous ensembles de data on déjà été vus
                    val = dat.__str__()
                    if not val in mem2:
                        mem2[val] = [idx]
                    else:
                        mem2[val].append(idx)

                data = data.__str__() 
                if not data in mem:   # Qqn a-t-il déjà fait exactement la même chose ?
                    mem[data] = [idx]
                else:
                    mem[data].append(idx)

        for _, val in mem2.items():
            if len(val) >= 2:
                for idx in val:
                    res[idx] = "orange"

        for _, val in mem.items():
            if len(val) >= 2:
                for idx in val:
                    res[idx] = "red"
        return res

    def print1(self, g: Graph):
        if g.up:
            color = self.UpColorSelector(g)
            i = 0
            for _in in g.up:
                out = self.findOut(_in[0])
                dataId = "d_" + out.id
                self.Gr.edge(dataId, g.id, color=color[i])
                i+= 1
        if g.son:
            for _son in g.son:
                son = _son[0]
                data = _son[1]
                label = _son[2]
                self.Gr.node(son.id, son.type, color = son.emphasis)
                dataId = "i_" + son.id
                self.Gr.node(dataId, label + data.__str__(), shape="box")
                self.Gr.edge(g.id, dataId)
                self.Gr.edge(dataId, son.id)
                self.print1(son)
        if g.out[1] == None:
            self.Gr.node(g.out[0].id, g.out[0].type, color = g.out[0].emphasis)
            self.print1(g.out[0])
        else:
            data = g.out[1]
            color = self.TrueFalse(data[1])
            data = data[0]
            self.Gr.node("d_" + g.id, data.__str__(), shape="box", fontcolor=color)
            self.Gr.edge(g.id, "d_" + g.id)

    def getGraph(self, print : bool = True):
        if print:
            return self.start
        return None

    def aff(self):
        self.Gr.node(self.start.id, self.start.type, color = self.start.emphasis)
        self.print1(self.start)
        self.Gr.render("graphic", format="pdf", view=True)