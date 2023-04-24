import mesa
import Agents
import Phys

class OverallModel(mesa.Model):

    def __init__(self, fixNodes, varNodes, transports): #note that these inputs are CSV FILES read in in MAIN
        self.schedule = mesa.time.RandomActivationByType(self)
        self.VnList = varNodes
        self.TList = transports
        self.FnList = fixNodes

        for i in self.FnList:
            a = Agents.FixNode( (self.FnList[i][1], self.FnList[i][2] ), {"a": None, "ex": None, "ey": None, "i": None, "RAAN": None, "f": None,}, self.FnList[i][3], self.FnList[i][4], self.FnList[i][0] )
            #Phys.Place(a) - will generate the base orbital params
            self.schedule.add(a)
            print("Agent " + a.id + " added to schedule")

        for i in self.VnList:
            a = Agents.FixNode( (self.VnList[i][1], self.VnList[i][2] ), {"a": None, "ex": None, "ey": None, "i": None, "RAAN": None, "f": None,}, self.VnList[i][3], self.VnList[i][4], self.VnList[i][0] )
            #Phys.place(a)
            self.schedule.add(a)
            print("Agent " + a.id + " added to schedule")


        #transporter init loop should inherit orbit params from orig node.







