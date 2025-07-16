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

    def print1(self, g: Graph):
        if g.up:
            mem = {}
            for _in in g.up:
                out = self.findOut(_in[0])
                dataId = "d_" + out.id
                data = out.out[1][0]
                if data == None:
                    self.Gr.edge(dataId, g.id)
                    continue
                data = data.__str__()
                if not data in mem:
                    self.Gr.edge(dataId, g.id)
                    mem[data] = 1
                else:
                    self.Gr.edge(dataId, g.id, color="red")
        if g.son:
            for _son in g.son:
                son = _son[0]
                data = _son[1]
                self.Gr.node(son.id, son.type)
                dataId = "i_" + son.id
                self.Gr.node(dataId, data.__str__(), shape="box")
                self.Gr.edge(g.id, dataId)
                self.Gr.edge(dataId, son.id)
                self.print1(son)
        if g.out[1] == None:
            self.Gr.node(g.out[0].id, g.out[0].type)
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
        self.Gr.node(self.start.id, self.start.type)
        self.print1(self.start)
        self.Gr.render("graphic", format="pdf", view=True)