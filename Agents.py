#File containing Agent class definitions and methods
import mesa
import Phys

#Aux node lookup function
def NodeLookup(s, l):
    #list is  a list of nodes
    #output = None
    for i in l:
        if (i.id.lower() == s.lower()):
            return i
    print("ERROR 69420 -> no node with matchin id to requested lookup")
    return

def node2str(node):
    if(node is None):
        return "None"
    else:
        return node.id
#print("This is the agents file")
# CONSTANT

class Node(mesa.Agent):
    def __init__(self,Location,OrbitPars,capacity,resource_lvl,iid,operator,model,price,c_rate,econ_type,fixed):
        super().__init__(iid, model)
        #input parameters
        self.loc = Location #tuple of floats (x,y) coordinates
        self.OrbitPars = OrbitPars #Dictionary of structure {"a": float, "ex": float, "ey": float, "i": float, "RAAN": float, "f": true anomaly}
        self.capacity = capacity #Maximum capacity of node in units of resource
        self.resource = resource_lvl*self.capacity
        self.id = iid #Either a number (int) or string that identifies it, mainly so the transporters can reference it in origin or destination.
        self.operator = operator
        self.consume_rate = c_rate/((24*60*60)/model.time_step) #rate of resource consumption, negative for resource supplier, normalized to per day consumption rate
        self.baseprice = price
        self.fixed = fixed

        #bookkeeping parameters
        self.ports = []
        self.AcceptedTrans = None
        self.margin = 0.05
        self.bidList = []
        self.transbidlist = []
        self.incoming = 0 #amount of resources incoming

        #determine type of economic behavior
        if(econ_type == 0): #indicates variable node (buyer and seller)
            self.buyer = True #is this node buying?
            self.seller = True #is this node selling?
        elif(econ_type == 1): #indicates buyer fixed node
            self.buyer = True
            self.seller = False
        else: #indicates seller fixed node
            self.buyer = False
            self.seller = True
    
    def buy_price(self):
        prem = self.getPrem(0)
        price = self.baseprice * prem #compute purchase price
        return price
    
    def sell_price(self, trans):
        prem = self.getPrem(1) #price premium (or discount) due to current inventory level
        price = self.baseprice * prem
        if(not type(trans) is Transporter): #check for type issue
            pass
        elif(trans.operator.lower() != self.operator.lower()):
            price = price * self.margin #account for margin when selling "out of network"
        return price
    
    def max_amt(self, t): #returns the maximum allowable resource transfer based on inventory constraints
        #t = 0 -> buy, t = 1 -> sell
        if(t == 1):
            return self.resource #can't sell more than I have
        else:
            return self.capacity-(self.resource+self.incoming) #can't buy more than I have space for (including contracted purchases)
    
    def transact(self, trans, quantity): #returns the money exchange associated with the transaction
        led_str = str(self.model.model_time)+","+trans.id+","+self.id+"," #string for the ledger entry
        if(quantity > 0): #indicates a purchase
            led_str = led_str+"b,"
            price = self.buy_price()
            self.incoming = self.incoming - quantity #adjust incoming quantity when it is received
        else: #indicates a sale
            led_str = led_str+"s,"
            price = self.sell_price(trans)
        self.resource = self.resource + quantity
        led_str = led_str+str(quantity)+","+str(price)+","+str(price * abs(quantity))+"\n"
        self.model.ledger.write(led_str)
        return price * quantity
    
    def getPrem(self, t): #t: 0 = buy, 1 = sell
        prem = 1
        inv = (self.resource+self.incoming)/self.capacity #normalized inventory level (including incoming)
        if(t == 0): #indicates a buy price check
            if(inv > 0.75):
                prem = 0.8
            elif(inv < 0.25):
                prem = 1.20 #20% increase if inventory is low
        else:
            if(inv < 0.25):
                prem = 1.20
            elif(inv > 0.75):
                prem = 0.8 #indicates 20% discount
        return prem

    def Dock(self, trans): #adds transporter to the ports array, corresponds to Dock method in transporter class
        self.ports.append(trans)
    
    def unDock(self, trans): #removes transporter from the ports array
        self.ports.remove(trans)

    def Reserve(self, amt): #reserves port for transporter, corresponds to transporter reserve methods
        self.incoming = self.incoming + amt #tell node to expect this much incoming cargo
    
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
        self.resource = self.resource - self.consume_rate*self.capacity
        if(self.resource < 0):
            self.resource = 0
        elif(self.resource > self.capacity):
            self.resource = self.capacity
        return
    
    def step_output(self):
        return str(self.model.model_time)+","+str(self.loc[0])+","+str(self.loc[1])+","+str(self.resource)+","+str(self.incoming)+","+str(self.capacity)+","+str(len(self.ports))+","+str(self.buy_price())+","+str(self.sell_price(-1))+"\n"

    #Define step and/or advance functions
    def step(self):
        self.Consumption()
        self.loc, self.OrbitPars["f"] = Phys.StepOrbit(self,self.model.model_time)
        return


class Transporter(mesa.Agent):
    def __init__(self, resource_lvl, orig, operator,iid, model):
        super().__init__(iid, model)
        #self.orig  = orig #id of most recent originating node
        self.dest = None # destination node OBJECT
        self.operator = operator #id of operating company.
        self.Current_Node = orig #Set the starting node
        self.loc = self.Current_Node.loc # (x,y) tupleof cartesian coordinates
        self.id = iid
        self.orbitParams = None #will be inherited form node after first bidding phase
        self.dest_opts = []

        self.current_price = self.Current_Node.baseprice
        self.capacity = 100 #total capacity level
        self.resource = resource_lvl*self.capacity #floating point variable reflecting amount
        self.margin = 0.05 #desired margin
        self.model = model
        self.compute = 0
        self.fuel_reserve = 0.2
        self.fuel_economy = 0.1 #dV/resource achievable by transporters
        self.idle = 0 #current idle time is 0
        self.tsfr = None #empty init method
        
        #state definition
        #0 -> available
        #1 -> acquiring resources
        #2 -> delivering resources
        #3 -> moving to seller
        #4 -> stuck, want to move to new seller

        self.state = 0 #all transporters begin as available
        self.TOF_remain = -1 #insert dummy value for now

    def Dock(self, node):
        self.loc = node.loc
        node.Dock(self)
        self.Current_Node = node
        self.orbitParams = node.OrbitPars
        self.model.main_output.write(self.id + " has docked at " + node.id+"\n")
        return
    
    def transact(self, node, t): #conduct a transaction
        #t = 0 -> buy, t = 1 -> sell (Node POV!!)
        self.model.main_output.write("\nTime: "+str(self.model.model_time)+"\n")
        if(t == 0): #sell resources to node
            tmp = self.resource - (self.fuel_reserve * self.capacity)
            amount = min(node.max_amt(t), tmp)
            self.model.main_output.write("Transaction: "+self.id+" selling to "+node.id+"\n")
        else: #buy resources from node
            amount = min(node.max_amt(t), self.capacity - self.resource)
            amount = amount * -1
            self.model.main_output.write("Transaction: "+self.id+" buying from "+node.id+"\n")
            self.current_price = (self.current_price*self.resource + (-amount)*node.sell_price(self))/(self.resource - amount) #current price is weighted average of existing and new unit price
        self.resource = self.resource - amount #update my resource stockpile
        price = node.transact(self, amount)
        self.model.main_output.write("Transaction Value: "+str(price)+"\n")
        self.model.main_output.write("Transaction Volume: "+str(abs(amount))+"\n")
        self.model.main_output.write("\n")
        return price #return net transaction value to transporter!
    
    def sellprice(self, node): #check sale price
        prem = self.compPrems(1) #price premium (or discount) due to current inventory level
        price = self.current_price * prem
        if(not type(node) is Node):
            pass
        elif(node.operator != self.operator):
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
    
    def acceptedBid(self, node): #called by node when bid is accepted
        self.dest_opts.append(node)
        return

    def Reserve(self): #reserve space a node
        self.dest.Reserve(self) #broken because self.dest is a stringof the destination id, not the actual object
    
    def unDock(self):
        self.Current_Node.unDock(self)
        self.Current_Node = None

    def profit(self, node):
        profit = min(node.max_amt(0), (1 - self.fuel_reserve) * self.capacity) * node.buy_price() #how much the delivery nets me
        profit = profit - self.current_price*self.resource #value of current inventory
        profit = profit - self.Current_Node.sell_price(self) * (self.capacity - self.resource) #cost to fill inventory
        res_val = ((self.resource*self.current_price) + (self.capacity-self.resource)*self.Current_Node.sell_price(self))/self.capacity #current resource value of hypothetical full inventory
        dv = Phys.ComputeTransfer(self.Current_Node, node)['dV']
        profit = profit - res_val*(dv/self.fuel_economy)
        return profit #return numerical profit to be made by completing transaction from current node
    
    def find_seller(self):
        opts = []
        opt_vs = []
        for i in self.model.NodeAglist:
            if(i.seller):
                tmp = Phys.ComputeTransfer(self.Current_Node, i)
                if(tmp['isPossible']):
                    opts.append(i)
                    p = -1
                    opt_vs.append(p)
        if(len(opts) < 1):
            return
        ind = opt_vs.index(max(opt_vs))
        self.dest = opts[ind]
        self.tsfr = Phys.ComputeTransfer(self.Current_Node, self.dest)
        self.TOF_remain = self.tsfr['TOF'] #compute and store time of flight
        self.resource = self.resource - self.tsfr['dV']/self.fuel_economy #use resources to transfer
        self.state = 3 #increment state appropriately
        self.unDock()
        self.model.main_output.write("\nTime: "+str(self.model.model_time)+"\n")
        self.model.main_output.write("Transporter "+self.id+" transferring to seller: "+self.dest.id+"\n")
        self.model.main_output.write("Flight Time: "+str(self.tsfr['TOF'])+"\n")
        self.model.main_output.write("dV: "+str(self.tsfr['dV'])+"\n")
    
    def step_output(self):
        return str(self.model.model_time)+","+str(self.state)+","+node2str(self.Current_Node)+","+node2str(self.dest)+","+str(self.TOF_remain)+","+str(self.resource)+","+str(self.capacity)+","+str(self.buyprice())+","+str(self.sellprice(-1))+"\n"

    def step(self):
        if(self.idle > 0): #allow idling
            self.idle = self.idle - self.model.time_step
            if(self.idle < 0):
                self.idle = 0
            return
        if(self.state == 2): #delivering resources phase
            if(self.TOF_remain > 0):
                self.TOF_remain = self.TOF_remain - self.model.time_step #step forward one stage
                return #all I need to do for now
            else:
                self.Dock(self.dest)
                self.dest = None
                self.transact(self.Current_Node, 0)
                self.state = 4 #move to stuck state & seek seller
        elif(self.state == 3):
            if(self.TOF_remain > 0): #in transit to seller
                self.TOF_remain = self.TOF_remain - self.model.time_step
            else: #arrived at seller - ready for next bid
                self.Dock(self.dest) #Dock at seller node
                self.dest = None
                self.state = 0
        elif(self.state == 4):
            self.find_seller() #look for a seller I can move to
        elif(self.state == 1):
            self.transact(self.Current_Node, 1)
            self.resource = self.resource - self.tsfr['dV']/self.fuel_economy
            self.model.main_output.write("\nTime: "+str(self.model.model_time)+"\n")
            self.model.main_output.write("Transporter "+self.id+" transferring to buyer: "+self.dest.id+"\n")
            self.model.main_output.write("Flight Time: "+str(self.tsfr['TOF'])+"\n")
            self.model.main_output.write("dV: "+str(self.tsfr['dV'])+"\n")
            self.state = 2
            self.unDock()
        elif(self.state == 0):
            if(len(self.dest_opts) < 1):
                self.model.main_output.write("Time: "+str(self.model.model_time)+"\n"+self.id+" failed to have any bids accepted\n")
                return #no accepted bids
            else:
                max_p = -1
                best = self.dest_opts[0]
                for n in self.dest_opts:
                    tp = self.profit(n)
                    if(tp > max_p): #find most profitable function
                        max_p = tp
                        best = n
                if(best is None):
                    print("Error: Failed to Assign Dest Node")
                else:
                    best.Reserve(self.capacity*(1-self.fuel_reserve)) #tell the node I accept and am on my way
                    self.model.main_output.write("Time: "+str(self.model.model_time)+"\n"+self.id+" accepted bid on "+best.id+"\n")
                    self.state = 1 #move to next state
                    self.dest = best
                    self.tsfr = Phys.ComputeTransfer(self.Current_Node, self.dest) #get transfer details
                    self.TOF_remain = self.tsfr['TOF']
                    self.dest_opts = []
        else:
            print("STATE ERROR")
        return