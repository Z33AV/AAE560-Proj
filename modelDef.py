import mesa
import Agents
import Phys
import os

#auxilaary func
def NodeLookup(s, l):
    #list is  a list of nodes
    #output = None
    for i in l:
        if (i.id.lower() == s.lower()):
            return i
    print("ERROR 69420 -> no node with matchin id to requested lookup")
    return

def make_my_dir(filename): #creates directory if it does not already exist
    if(not os.path.exists(os.path.dirname(filename))):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:
            print(filename)
            print("Error making: "+filename)
            print(exc)

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
        self.model_time = 0

        #define filenames for later
        self.root_path = "./560_Project_Runs/"
        self.run_name = "Run_1/"
        self.main_output = None
        self.main_data = None
        self.ledger = None
        self.trans_files = []
        self.node_files = []

        self.start_main_out()

        for i in self.FnList:
            a = Agents.Node((float(i[1]), float(i[2])), {"a": None, "ex": None, "ey": None, "i": None, "RAAN": None, "f": None,}, float(i[3]), float(i[4]), str(i[0]), str(i[5]), self, float(i[6]), float(i[7]), int(i[8]), True)
            a.OrbitPars = Phys.PlaceNode(a) #- will generate the base orbital params
            self.schedule.add(a)
            self.NodeAglist.append(a)
            print("Agent " + a.id + " added to schedule")

        for i in self.VnList:
            a = Agents.Node((float(i[1]), float(i[2])), {"a": None, "ex": None, "ey": None, "i": None, "RAAN": None, "f": None,}, float(i[3]), float(i[4]), str(i[0]), str(i[5]), self, float(i[6]), 0.0, 0, False)
            a.OrbitPars = Phys.PlaceNode(a)
            self.schedule.add(a)
            self.NodeAglist.append(a)
            print("Agent " + a.id + " added to schedule")

        #transporter init loop should inherit orbit params from orig node.
        for i in self.Tlist:
            a = Agents.Transporter(float(i[1]),NodeLookup(str(i[2]), self.NodeAglist), str(i[3]), str(i[0]),self)
            a.Dock(a.Current_Node)
            self.schedule.add(a)
            self.TransAglist.append(a)
            print("Agent " + a.id + " added to schedule with origin "+a.Current_Node.id)
        

        self.start_collection()
        print("INIT COMPLETE \n\n")


    def ContractingPhase(self):
        #Function to complete the entire bidding and contracting process except final acceptance (transporter step)
        #ALL Agents make initial bids
        for i in self.TransAglist:
            if i.state == 0: #only available transporters make bids
                self.main_output.write("\n Time: "+str(self.model_time)+" || "+i.id+" available to bid. Options:\n")
                for j in self.NodeAglist:
                    if (j.buyer and (j.id.lower() != i.Current_Node.id.lower())): #don't bid on my current node or nodes that do not buy
                        tempTransferParams = Phys.ComputeTransfer(i.Current_Node,j)
                        self.main_output.write("Node: "+j.id+" || Possible: "+str(tempTransferParams['isPossible'])+" || Profit: "+str(i.profit(j))+"\n")
                        if (tempTransferParams['isPossible'] ==1) and (i.profit(j) > 0): #bid if possible and profitable
                            i.makeBids(j,tempTransferParams['TOF'])
                            self.main_output.write("\nTransporter " + i.id + " bids on node " +j.id+"\n")
                            self.main_output.write("Profit: "+str(i.profit(j))+"\n")
                            self.main_output.write("TOF: "+str(tempTransferParams['TOF'])+"\n\n")
            else:
                pass
                #print("Transport " + i.id + " is unavailable and not bidding")


        for i in self.NodeAglist:
            minTOF = min(i.bidList, default=-1)
            if minTOF < 0: #no bids made on this node
                continue
            else:
                ind = i.bidList.index(minTOF)
                i.transbidlist[ind].acceptedBid(i)
            i.transbidlist = []
            i.bidList = []
        return

    def start_collection(self): #start data collection
        print("Starting Data Collection")
        #define file paths
        ledger_name = "ledger.csv"

        t_fold = "Transporters/"
        fn_fold = "Fixed_Nodes/"
        vn_fold = "Variable_Nodes/"

        #make directories
        make_my_dir(self.root_path+self.run_name+ledger_name)
        make_my_dir(self.root_path+self.run_name+t_fold)
        make_my_dir(self.root_path+self.run_name+fn_fold)
        make_my_dir(self.root_path+self.run_name+vn_fold)

        #open main files for writing
        self.ledger = open(self.root_path+self.run_name+ledger_name, 'w')
        self.ledger.write("Time,Transporter,Node,TT,Quantity,Price,Value\n")

        #open transporter files for writing
        for t in self.TransAglist:
            fname = t.id+".csv"
            make_my_dir(fname)
            f = open(self.root_path+self.run_name+t_fold+fname, 'w')
            f.write("Time,state,curr_node,dest_node,remaining_TOF,resources,capacity,Buy_price,Sell_price\n")
            self.trans_files.append(f)
        
        #open node files for writing
        for n in self.NodeAglist:
            fname = n.id+".csv"
            if(n.fixed):
                fold = fn_fold
            else:
                fold = vn_fold
            tmp = self.root_path+self.run_name+fold+fname
            make_my_dir(tmp)
            f = open(tmp, 'w')
            f.write("Time,x,y,resources,incoming,capacity,ports_filled,Buy_price,Sell_price\n")
            self.node_files.append(f)
    
    def start_main_out(self):
        main_log = "main_log.txt"
        make_my_dir(self.root_path+self.run_name)
        make_my_dir(self.root_path+self.run_name+main_log)
        self.main_output = open(self.root_path+self.run_name+main_log, 'w')

    def close_model(self): #stop data collection & shutdown
        self.main_output.close()
        self.ledger.close()
        for f in self.trans_files: #close transporter files
            f.close()
        for f in self.node_files: #close node files
            f.close()
        print("End Data Collection")

    def step(self):
        self.ContractingPhase()
        for j in range(len(self.TransAglist)):
            t = self.TransAglist[j]
            t.step()
            self.trans_files[j].write(t.step_output())
        for i in range(len(self.NodeAglist)):
            n = self.NodeAglist[i]
            n.step()
            self.node_files[i].write(n.step_output())
        self.model_time = self.model_time + self.time_step
        return
