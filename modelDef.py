import mesa
import Agents.py


class OveralModel(mesa.Model):

    def __init__(self, Num_transporters, num_VarNodes, num_FixNodes):
        self.schedule = mesa.time.RandomActivationByType(self)
        self.nVN = num_VarNodes
        self.nT = Num_transporters
        self.nFN = num_FixNodes


        #initialize all variable nodes
        for i in range(self.num_varNodes):
            a = Agents.VarNode(orbitParams, resource, size, id)
            self.schedule.add(a)

       # initialize all fix nodes
        for i in range(self.nFN):
            a = Agents.FixNode(orbitParams, resource, size, id)
            self.schedule.add(a)

        # initialize transporters
        for i in range(self.nT):
            a = Agents.Transporter(fuel, loc, orig, dest, operator)
            self.schedule.add(a)