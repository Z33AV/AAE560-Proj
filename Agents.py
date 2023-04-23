#File containing Agent class definitions and methods
import math
import mesa

#print("This is the agents file")

class VarNode(mesa.Agent):
    def __init__(self,Location,OrbitPars,resource,size, id):
        self.loc = Location #tuple of floats (x,y) coordinates
        self.OrbitPars = OrbitPars #Dictionary of structure {"a": float, "ex": float, "ey": float, "i": float, "RAAN": float, "f": true anomaly}
        self.resource = resource #float
        self.size = size #maximum number of spaces/docking ports, of type int
        self.ports = [None]*self.size
        self.id = id #Either a number (int) or string that identifies it, mainly so the transporters can reference it in origin or destination.

    def Dock(self, Transporter): #adds transporter to the ports array, corresponds to Dock method in transporter class
        return

    def Reserve(self, Transporter): #reserves port for transporter, corresponds to transporter reserve methods
        for i in self.ports:
            if self.ports
        return

    #Define step and/or advance functions
    def step(self):
        #step function to move agent forward in its time step NOTE: use mesa scheduler
        return


class FixNode(VarNode): #fixed node class, inherit from VarNode
    #def __init__(self):



class Transporter(mesa.Agent):
    def __init__(self, fuel, loc, orig, dest, operator):
        self.fuel = fuel #floating point variable reflecting amount
        self.loc = loc # (x,y) tupleof cartesian coordinates
        self.orig  = orig #id of most recent originating node
        self.dest = dest #id of destination node
        self.operator = operator #id of operating company.
        self.Current_Node = self.orig

    def Dock(self, Node):
        self.loc = Node.loc
        self.orig = Node.id
        return

    def Reserve(self):
        self.dest.Reserve(self)

    def step(self):
        # step function to move agent forward in its time step NOTE: use mesa scheduler
        return