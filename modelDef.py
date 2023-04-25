import mesa
import Agents
import Phys

class OverallModel(mesa.Model):

    def __init__(self, fixNodes, varNodes, transports): #note that these inputs are CSV FILES read in in MAIN
        self.schedule = mesa.time.RandomActivationByType(self)
        self.VnList = varNodes
        self.Tlist = transports
        self.FnList = fixNodes

        for i in self.FnList:
            a = Agents.FixNode( (int(i[1]), int(i[2]) ), {"a": None, "ex": None, "ey": None, "i": None, "RAAN": None, "f": None,}, int(i[3]), int(i[4]), i[0], self )
            Phys.PlaceNode(a) #- will generate the base orbital params
            self.schedule.add(a)
            print("Agent " + a.id + " added to schedule")

        for i in self.VnList:
            a = Agents.VarNode( (int(i[1]), int(i[2]) ), {"a": None, "ex": None, "ey": None, "i": None, "RAAN": None, "f": None,}, int(i[3]), int(i[4]), i[0],self )
            Phys.PlaceNode(a)
            self.schedule.add(a)
            print("Agent " + a.id + " added to schedule")


        #transporter init loop should inherit orbit params from orig node.
        for i in self.Tlist:
            a = Agents.Transporter(int(i[1]),(int(i[2]),int(i[3])), i[4], i[5],i[6],i[0],self)
            self.schedule.add(a)
            print("Agent " + a.id + " added to schedule")







