import mesa
import Agents
import Phys

#auxilaary func
def NodeLookup(str, list):
    #list is  a list of nodes
    #output = None
    for i in list:
        if (i.id.lower() == str.lower()):
            return i
    print("ERROR 69420 -> no node with matchin id to requested lookup")
    return

class OverallModel(mesa.Model):

    def __init__(self, fixNodes, varNodes, transports): #note that these inputs are CSV FILES read in in MAIN
        self.schedule = mesa.time.RandomActivation(self)
        self.VnList = varNodes
        self.Tlist = transports
        self.FnList = fixNodes
        self.NodeAglist =[]
        self.TransAglist = []
        self.FirstStepFlag = 1

        for i in self.FnList:
            a = Agents.FixNode( (float(i[1]), float(i[2]) ), {"a": None, "ex": None, "ey": None, "i": None, "RAAN": None, "f": None,}, int(i[3]), int(i[4]), i[0], self, 1 )
            Phys.PlaceNode(a) #- will generate the base orbital params
            self.schedule.add(a)
            self.NodeAglist.append(a)
            print("Agent " + a.id + " added to schedule")

        for i in self.VnList:
            a = Agents.VarNode( (float(i[1]), float(i[2]) ), {"a": None, "ex": None, "ey": None, "i": None, "RAAN": None, "f": None,}, int(i[3]), int(i[4]), i[0],self )
            Phys.PlaceNode(a)
            self.schedule.add(a)
            self.NodeAglist.append(a)
            print("Agent " + a.id + " added to schedule")


        #transporter init loop should inherit orbit params from orig node.
        for i in self.Tlist:
            a = Agents.Transporter(int(i[1]),(int(i[2]),int(i[3])), i[4], None ,i[6],i[0],self)
            a.Dock(NodeLookup(a.Current_Node,self.NodeAglist))
            self.schedule.add(a)
            self.TransAglist.append(a)
            print("Agent " + a.id + " added to schedule with origin "+a.Current_Node)
        print("INIT COMPLETE \n")


    def ContractingPhase(self):
        #Function to complete the entire bidding and contracting process

        tempTransferParams = {"isPossible": 0, "dV": -1, "TOF": -1}
        #targetNode =

        #ALL Agents make initial bids
        for i in self.TransAglist:
            if i.state == 0: #only available transporters make bids
                for j in self.NodeAglist:
                    if (j.id.lower() != i.Current_Node.lower()):
                        tempTransferParams = Phys.ComputeTransfer(NodeLookup(i.Current_Node,self.NodeAglist),j)
                        if (tempTransferParams['isPossible'] ==1) and i.isProfitable(j):
                            i.makeBids(j,tempTransferParams['TOF'])
                            print("Transporter " + i.id + " bids on node " +j.id)
            else:
                print("Transport " + i.id + " is unavailable and not bidding")


        for i in self.NodeAglist:
            minTOF = min(i.bidList, default=-1)
            if minTOF < 0: #no bids made on this node
                continue
            ind = i.bidList.index(minTOF)
            i.transBidList(ind).acceptedBid(i)

        #at this point, we have iterated through every transporter, and they have made their
        #bids on the lowest cost transfer, and then we iterated through every node and they
        #have accepted the lowest cost transfer.
        #the actual transfer of resources and

        #ToBeDone: each transporter needs to go and confirm it;s contract, and subseuently set its
        #destination paramters and such. Then, the step function for each agent type must be written to
        #propogate itself.
        return


    def step(self):
        if not self.FirstStepFlag:
            for i in self.NodeAglist:
                i.step()
        self.ContractingPhase()
        for j in self.TransAglist:
            j.step()
        return
