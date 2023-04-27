#File containing Agent class definitions and methods
import math
import mesa

#print("This is the agents file")

class VarNode(mesa.Agent):
    def __init__(self,Location,OrbitPars,resource,size, id,model):
        super().__init__(id, model)
        self.loc = Location #tuple of floats (x,y) coordinates
        self.OrbitPars = OrbitPars #Dictionary of structure {"a": float, "ex": float, "ey": float, "i": float, "RAAN": float, "f": true anomaly}
        self.resource = resource #float
        self.size = size #maximum number of spaces/docking ports, of type int
        self.ports = [None]*self.size
        self.id = id #Either a number (int) or string that identifies it, mainly so the transporters can reference it in origin or destination.

        #Jan's Variables
        self.margin = 0.05
        self.baseprice = -1
        self.capacity = 100 #Maximum capacity of node in units of resource
    
    def buy_price(self):
        inv_prem = 0 #price premium (or discount) due to current inventory level
        price = self.price * inv_prem #compute purchase price
        return price
    
    def sell_price(self, Transporter):
        inv_prem = 0 #price premium (or discount) due to current inventory level
        price = self.price * inv_prem
        if(Transporter.operator == self.operator):
            price = price * self.margin #account for margin when selling "out of network"
        return price
    
    def transact(self, Transporter, quantity): #returns the money exchange associated with the transaction
        if(quantity > 0): #indicates a purchase
            price = self.buy_price()
        else: #indicates a sale
            price = self.sell_price(Transporter)
        self.resource = self.resource + quantity
        return price * quantity

    def Dock(self, Transporter): #adds transporter to the ports array, corresponds to Dock method in transporter class
        return

    def Reserve(self, Transporter): #reserves port for transporter, corresponds to transporter reserve methods
        for i in self.ports:
            if self.ports[i] == None:
                self.ports[i] = Transporter.id
                break
            else:
                continue

        return

    #Define step and/or advance functions
    def step(self):
        #step function to move agent forward in its time step NOTE: use mesa scheduler
        return


class FixNode(VarNode): #fixed node class, inherit from VarNode
    pass



class Transporter(mesa.Agent):
    def __init__(self, fuel, loc, orig, dest, operator,id, model):
        super().__init__(id, model)
        self.fuel = fuel #floating point variable reflecting amount
        self.loc = loc # (x,y) tupleof cartesian coordinates
        self.orig  = orig #id of most recent originating node
        self.dest = dest #id of destination node
        self.operator = operator #id of operating company.
        self.Current_Node = self.orig
        self.id = id
        
        #Jan's variables
        self.resourceValue = -1 #current value/resource (includes value add)

    def Dock(self, Node):
        self.loc = Node.loc
        self.orig = Node.id
        return

    def Reserve(self):
        self.dest.Reserve(self)

    def step(self):
        # step function to move agent forward in its time step NOTE: use mesa scheduler
        return