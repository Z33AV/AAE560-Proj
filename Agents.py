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

        #Jan's Variables
        self.margin = 0.05
        self.baseprice = -1
        self.capacity = 100 #Maximum capacity of node in units of resource
        self.buyer = True #is this node buying?
        self.seller = True #is this node selling?
        self.bidList = []
        self.incoming = 0
    
    def buy_price(self):
        inv_prem = self.getInvPrem(0) #price premium (or discount) due to current inventory level
        price = self.price * inv_prem #compute purchase price
        return price
    
    def sell_price(self, trans):
        inv_prem = self.getInvPrem(1) #price premium (or discount) due to current inventory level
        price = self.price * inv_prem
        if(trans.operator != self.operator):
            price = price * self.margin #account for margin when selling "out of network"
        return price
    
    def max_amt(self, t): #returns the maximum allowable resource transfer based on inventory constraints
        #t = 0 -> buy, t = 1 -> sell
        if(t == 0):
            return self.resource #can't sell more than I have
        else:
            return self.capacity-self.resource #can't buy more than I have space for
    
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
    
    def takeBid(self, time):
        self.bidList.append(time)
    
    def bestBid(self):
        return min(self.bidList)

    def acceptBid(self, amount):
        self.bidList = []
        self.incoming = amount

    def bidComplete(self):
        self.incoming = 0
        self.bidList = []
        pass

    #Define step and/or advance functions
    def step(self):
        #step function to move agent forward in its time step NOTE: use mesa scheduler
        return


class FixNode(VarNode): #fixed node class, inherit from VarNode
    def __init__(self, Location, OrbitPars, resource, size, id, model, c_rate):
        super().__init__(Location, OrbitPars, resource, size, id, model)
        self.consume_rate = c_rate #rate of resource consumption, negative for resource supplier

    def step(self):
        self.resource = self.resource - self.consume_rate
        if(self.resource < 0):
            self.resource = 0
        elif(self.resource > self.capacity):
            self.resource = self.capacity



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
    
    def transact(self, Node, price, t): #conduct a transaction
        #t = 0 -> buy, t = 1 -> sell (Node POV!!)
        if(t == 0):
            tmp = self.resource - (self.fuel_reserve * self.capacity)
            amount = min(Node.max_amt(t), tmp)
        else:
            amount = min(Node.max_amt(t), self.capacity - self.resource)
            amount = amount * -1
        self.resource = self.resource - amount
        Node.transact(self, amount)
        return price*amount #return net transaction value to transporter!
    
    def sellprice(self, Node): #check sale price
        prem = self.compPrems(1) #price premium (or discount) due to current inventory level
        price = self.price * prem
        if(Node.operator != self.operator):
            price = price * self.margin #account for margin when selling "out of network"
        return price
    
    def buyprice(self): #check buy price
        prem = self.compPrems(0) #price premium (or discount) due to current inventory level
        price = self.price * prem #compute purchase price
        return price
    
    def compPrems(self, t): #t = 0 -> buy (transporter POV), t = 1 -> sell (transporter POV)
        return 1
    
    def makeBids(self):
        return

    def Reserve(self):
        self.dest.Reserve(self)

    def step(self):
        # step function to move agent forward in its time step NOTE: use mesa scheduler
        return