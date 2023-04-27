#File containing Agent class definitions and methods
import math
import mesa

#print("This is the agents file")

class VarNode(mesa.Agent):
    def __init__(self,Location,OrbitPars,resource,size,id,model):
        super().__init__(id, model)
        self.loc = Location #tuple of floats (x,y) coordinates
        self.OrbitPars = OrbitPars #Dictionary of structure {"a": float, "ex": float, "ey": float, "i": float, "RAAN": float, "f": true anomaly}
        self.resource = resource #float
        self.size = size #maximum number of spaces/docking ports, of type int
        self.ports = [None]*self.size
        self.id = id #Either a number (int) or string that identifies it, mainly so the transporters can reference it in origin or destination.
        self.buyer = True #is this node buying?
        self.seller = True #is this node selling?

        #Jan's Variables
        self.margin = 0.05
        self.baseprice = -1
        self.capacity = 100 #Maximum capacity of node in units of resource
    
    def buy_price(self):
        inv_prem = self.getInvPrem(0) #price premium (or discount) due to current inventory level
        price = self.price * inv_prem #compute purchase price
        return price
    
    def sell_price(self, trans):
        inv_prem = self.getInvPrem(1) #price premium (or discount) due to current inventory level
        price = self.price * inv_prem
        if(trans.operator == self.operator):
            price = price * self.margin #account for margin when selling "out of network"
        return price
    
    def transact(self, trans, quantity): #returns the money exchange associated with the transaction
        if(quantity > 0): #indicates a purchase
            price = self.buy_price()
        else: #indicates a sale
            price = self.sell_price(trans)
        self.resource = self.resource + quantity
        return price * quantity
    
    def getInvPrem(self, t): #t: 0 = buy, 1 = sell
        prem = 1
        inv = self.resource/self.capacity
        if(t == 0): #indicates a buy price check
            if(inv > 0.75):
                prem = 0.9
            elif(inv < 0.25):
                prem = 1.10 #10% increase if inventory is low
        else:
            if(inv < 0.25):
                prem = 1.10
            elif(inv > 0.75):
                prem = 0.9 #indicates 10% discount
        return prem

    def Dock(self, trans): #adds transporter to the ports array, corresponds to Dock method in transporter class
        return

    def Reserve(self, trans): #reserves port for transporter, corresponds to transporter reserve methods
        for i in self.ports:
            if self.ports[i] == None:
                self.ports[i] = trans.id
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
    def __init__(self, resource, loc, orig, dest, operator,id, model):
        super().__init__(id, model)
        self.resource = resource #floating point variable reflecting amount
        self.loc = loc # (x,y) tupleof cartesian coordinates
        self.orig  = orig #id of most recent originating node
        self.dest = dest #id of destination node
        self.operator = operator #id of operating company.
        self.Current_Node = self.orig
        self.id = id
        
        #Jan's variables
        self.resourceValue = -1 #current value/resource (includes value add)
        self.capacity = 100 #total capacity level
        self.margin = 0.05 #desired margin

    def Dock(self, Node):
        self.loc = Node.loc
        self.orig = Node.id
        return
    
    def transact(self, Node): #conduct a transaction
        return
    
    def sellprice(self, Node): #check sale price
        return
    
    def buyprice(self): #check buy price
        return
    
    def compPrems(self):
        return
    
    def makeBids(self):
        return

    def Reserve(self):
        self.dest.Reserve(self)

    def step(self):
        # step function to move agent forward in its time step NOTE: use mesa scheduler
        return