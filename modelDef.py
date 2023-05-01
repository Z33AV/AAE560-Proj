import mesa
import Agents
import Phys

#auxilaary func
def NodeLookup(s, l):
    #list is  a list of nodes
    #output = None
    for i in l:
        if (i.id.lower() == s.lower()):
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

        self.time_step = 60 #timestep in seconds

        for i in self.FnList:
            a = Agents.Node((float(i[1]), float(i[2])), {"a": None, "ex": None, "ey": None, "i": None, "RAAN": None, "f": None,}, float(i[3]), float(i[4]), str(i[0]), str(i[5]), self, float(i[6]), float(i[7]), int(i[8]), True)
            Phys.PlaceNode(a) #- will generate the base orbital params
            self.schedule.add(a)
            self.NodeAglist.append(a)
            print("Agent " + a.id + " added to schedule")

        for i in self.VnList:
            a = Agents.Node((float(i[1]), float(i[2])), {"a": None, "ex": None, "ey": None, "i": None, "RAAN": None, "f": None,}, float(i[3]), float(i[4]), str(i[0]), str(i[5]), self, float(i[6]), 0.0, 0, False)
            Phys.PlaceNode(a)
            self.schedule.add(a)
            self.NodeAglist.append(a)
            print("Agent " + a.id + " added to schedule")


        #transporter init loop should inherit orbit params from orig node.
        for i in self.Tlist:
            a = Agents.Transporter(float(i[1]),NodeLookup(str(i[2]), self.NodeAglist), str(i[3]), str(i[0]),self)
            a.Dock(NodeLookup(a.Current_Node,self.NodeAglist))
            self.schedule.add(a)
            self.TransAglist.append(a)
            print("Agent " + a.id + " added to schedule with origin "+a.Current_Node)
        print("INIT COMPLETE \n")


    def ContractingPhase(self):
        #Function to complete the entire bidding and contracting process except final acceptance (transporter step)
        #ALL Agents make initial bids
        for i in self.TransAglist:
            if i.state == 0: #only available transporters make bids
                for j in self.NodeAglist:
                    if (j.buyer and (j.id.lower() != i.Current_Node.lower())): #don't bid on my current node or nodes that do not buy
                        tempTransferParams = Phys.ComputeTransfer(i.Current_Node,j)
                        if (tempTransferParams['isPossible'] ==1) and (i.Profit(j) > 0): #bid if possible and profitable
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
        return


    def step(self):
        self.ContractingPhase()
        for j in self.TransAglist:
            j.step()
        for i in self.NodeAglist:
            i.step()
        return
