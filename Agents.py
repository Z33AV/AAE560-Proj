#File containing Agent class definitions and methods
import math
import random

import mesa

#test msg - checkout switched to EconV2

import Phys
#from modelDef import NodeLookup

#Aux node lookup function
def NodeLookup(s, l):
    #list is  a list of nodes
    #output = None
    for i in l:
        if (i.id.lower() == s.lower()):
            return i
    print("ERROR 69420 -> no node with matchin id to requested lookup")
    return

#print("This is the agents file")
# CONSTANT
dt = 1800 #timestep in seconds
class Node(mesa.Agent):
    def __init__(self,Location,OrbitPars,resource,size,id,operator,model, capacity, econ_type, c_rate):
        super().__init__(id, model)
        self.loc = Location #tuple of floats (x,y) coordinates
        self.OrbitPars = OrbitPars #Dictionary of structure {"a": float, "ex": float, "ey": float, "i": float, "RAAN": float, "f": true anomaly}
        self.resource = resource #float
        self.num_ports = size #maximum number of spaces/docking ports, of type int
        self.ports = [None]*self.num_ports
        self.id = id #Either a number (int) or string that identifies it, mainly so the transporters can reference it in origin or destination.
        self.AcceptedTrans = None
        self.operator = operator
        self.consume_rate = c_rate #rate of resource consumption, negative for resource supplier
        
        #Jan's Variables
        self.margin = 0.05
        self.baseprice = -1
        self.capacity = capacity #Maximum capacity of node in units of resource
        if(econ_type == 0): #indicates variable node (buyer and seller)
            self.buyer = True #is this node buying?
            self.seller = True #is this node selling?
        elif(econ_type == 1): #indicates buyer fixed node
            self.buyer = True
            self.seller = False
        else: #indicates seller fixed node
            self.buyer = False
            self.seller = True

        self.bidList = []
        self.transbidlist = []
    
    def buy_price(self):
        prem = self.getPrem(0)
        price = self.baseprice * prem #compute purchase price
        return price
    
    def sell_price(self, trans):
        prem = self.getPrem(1) #price premium (or discount) due to current inventory level
        price = self.baseprice * prem
        if(trans.operator.lower() != self.operator.lower()):
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
    
    def getPrem(self, t): #t: 0 = buy, 1 = sell
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
    
    def takeBid(self, time, trans):
        self.bidList.append(time)
        self.transbidlist.append(trans)
        return
    
    def bestBid(self):
        #unused so far
        return min(self.bidList)

    def acceptBid(self, trans):
        self.bidList = []
        self.transbidlist = []
        self.AcceptedTrans = trans
        self.AcceptedTrans.dest = self
        #self.incoming = amount
        #print("self.incoming is " + self.incoming)

    def bidComplete(self):
        #self.incoming = 0
        self.bidList = []

        return

    def Consumption(self):
        self.resource = self.resource - self.consume_rate
        if(self.resource < 0):
            self.resource = 0
        elif(self.resource > self.capacity):
            self.resource = self.capacity
        return

    #Define step and/or advance functions
    def step(self):
        self.Consumption()
        Phys.StepOrbit(self,dt)
        print(self.id + " has been stepped")
        return


class Transporter(mesa.Agent):
    def __init__(self, resource, loc, orig, dest, operator,id, model):
        super().__init__(id, model)
        self.resource = resource #floating point variable reflecting amount
        self.loc = loc # (x,y) tupleof cartesian coordinates
        #self.orig  = orig #id of most recent originating node
        self.dest = dest # destination node OBJECT
        self.operator = operator #id of operating company.
        self.Current_Node = orig #JUST A STRING
        self.id = id
        self.orbitParams = None #will be inherited form node after first bidding phase
        self.dest_opts = []

        self.current_price = self.Current_Node.baseprice
        self.capacity = 100 #total capacity level
        self.margin = 0.05 #desired margin
        self.model = model
        self.compute = 0
        self.fuel_reserve = 0.2
        
        #state definition
        #0 -> available
        #1 -> acquiring resources
        #2 -> delivering resources
        #3 -> moving to seller

        self.state = 0 #all transporters begin as available

    def Dock(self, node):
        self.loc = node.loc
        node.Dock(self)
        self.Current_Node = node.id
        self.orbitParams = node.OrbitPars
        print(self.id + " has docked at " + node.id)

        return
    
    def transact(self, node, t): #conduct a transaction
        #t = 0 -> buy, t = 1 -> sell (Node POV!!)
        if(t == 0):
            tmp = self.resource - (self.fuel_reserve * self.capacity)
            amount = min(node.max_amt(t), tmp)
        else:
            amount = min(node.max_amt(t), self.capacity - self.resource)
            amount = amount * -1
        self.resource = self.resource - amount
        node.transact(self, amount)
        return self.current_price*amount #return net transaction value to transporter!
    
    def sellprice(self, node): #check sale price
        prem = self.compPrems(1) #price premium (or discount) due to current inventory level
        price = self.current_price * prem
        if(node.operator != self.operator):
            price = price * self.margin #account for margin when selling "out of network"
        return price
    
    def buyprice(self): #check buy price
        prem = self.compPrems(0) #price premium (or discount) due to current inventory level
        price = self.current_price * prem #compute purchase price
        return price
    
    def compPrems(self, t): #t = 0 -> buy (transporter POV), t = 1 -> sell (transporter POV)
        return 1
    
    def makeBids(self,TargetNode,tof):
        #write code to add bid to bidlist of Target Node, note that target node is the acutal objeect so you can reference it
        TargetNode.takeBid(tof,self)
        return
    
    def acceptedBid(self, node):
        self.dest_opts.append(node)
        return

    def Reserve(self):
        self.dest.Reserve(self) #broken because self.dest is a stringof the destination id, not the actual object
    
    def isProfitable(self, node):
        pass #fill in to determine if contract could be profitable

    def step(self):
       if(self.state == 2): #delivering resources phase
           if(TOF_remain > 0):
               TOF_remain = TOF_remain - 1 #step forward one stage
               return #all I need to do for now
           else:
               self.state = 3
               self.Dock(self.dest)
               self.dest = None
               self.transact(self.Current_Node, 0)
       elif(self.state == 3):
           pass #behavior for moving to 'best' seller node
       elif(self.state == 1):
           self.transact(self.Current_Node, 1)
           self.state = 2
       elif(self.state == 0):
           pass #participate in bidding
       else:
           print("STATE ERROR")
       TOF = 0 #default value
        # step function to move agent forward in its time step NOTE: use mesa scheduler
       if self.compute:
            TOF = Phys.ComputeTransfer(NodeLookup(self.Current_Node,self.model.NodeAglist),self.dest)['TOF']
            self.compute = 0
        #need to decide when to recalulate and when not, right now it recalculates every single time which is forcing the trnsporter to be infinitely waiting

       TOF_steps = int(TOF/dt)
       return