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
        self.main_output = None
        self.main_data = None
        self.ledger = None
        self.trans_files = []
        self.node_files = []

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
            a.Dock(a.Current_Node)
            self.schedule.add(a)
            self.TransAglist.append(a)
            print("Agent " + a.id + " added to schedule with origin "+a.Current_Node.id)
        print("INIT COMPLETE \n\n")


    def ContractingPhase(self):
        #Function to complete the entire bidding and contracting process except final acceptance (transporter step)
        #ALL Agents make initial bids
        for i in self.TransAglist:
            if i.state == 0: #only available transporters make bids
                for j in self.NodeAglist:
                    if (j.buyer and (j.id.lower() != i.Current_Node.id.lower())): #don't bid on my current node or nodes that do not buy
                        tempTransferParams = Phys.ComputeTransfer(i.Current_Node,j)
                        if (tempTransferParams['isPossible'] ==1) and (i.profit(j) > 0): #bid if possible and profitable
                            i.makeBids(j,tempTransferParams['TOF'])
                            print("Transporter " + i.id + " bids on node " +j.id)
            else:
                pass
                #print("Transport " + i.id + " is unavailable and not bidding")


        for i in self.NodeAglist:
            minTOF = min(i.bidList, default=-1)
            if minTOF < 0: #no bids made on this node
                continue
            ind = i.bidList.index(minTOF)
            i.transbidlist[ind].acceptedBid(i)
        return

    def start_collection(self): #start data collection
        #define file paths
        root_path = "/Users/jbalk/Documents/560_Project_Runs/"
        run_name = "Run_1/"
        ledger_name = "ledger.csv"
        main_log = "main_log.txt"

        t_fold = "Transporters/"
        fn_fold = "Fixed_Nodes/"
        vn_fold = "Variable_Nodes/"

        #make directories
        make_my_dir(root_path+run_name)
        make_my_dir(root_path+run_name+main_log)
        make_my_dir(root_path+run_name+ledger_name)
        make_my_dir(root_path+run_name+t_fold)
        make_my_dir(root_path+run_name+fn_fold)
        make_my_dir(root_path+run_name+vn_fold)

        #open main files for writing
        self.main_output = open(root_path+run_name+main_log, 'rw')
        self.ledger = open(root_path+run_name+ledger_name, 'rw')
        self.ledger.write("Time,Transporter,Node,TT,Quantity,Price,Value")

        #open transporter files for writing
        for t in self.TransAglist:
            fname = t.id+".csv"
            make_my_dir(fname)
            f = open(root_path+run_name+t_fold+fname, 'rw')
            f.write("Time,state,curr_node,dest_node,remaining_TOF,resources,capacity,buy_prem,sell_prem")
            self.trans_files.append(f)
        
        #open node files for writing
        for n in self.NodeAglist:
            fname = n.id+".csv"
            if(n.fixed):
                fold = fn_fold
            else:
                fold = vn_fold
            tmp = root_path+run_name+fold+fname
            make_my_dir(tmp)
            f = open(tmp, 'rw')
            f.write("Time,x,y,resources,capacity,ports_filled,buy_prem,sell_prem")
            self.node_files.append(f)


    def close_model(self): #stop data collection & shutdown
        self.main_output.close()
        self.ledger.close()
        for f in self.trans_files: #close transporter files
            f.close()
        for f in self.node_files: #close node files
            f.close()

    def step(self):
        self.ContractingPhase()
        for j in self.TransAglist:
            j.step()
            ind = self.TransAglist.index(j)
            self.trans_files[ind].write(j.step_output())
        for i in self.NodeAglist:
            i.step()
            ind = self.NodeAglist.index(j)
            self.node_files[ind].write(i.step_output())
        self.model_time = self.model_time + self.time_step
        return
