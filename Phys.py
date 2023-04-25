#physics file and methods definitions
import math
import numpy
import mesa
#
# Node parent node class w/ inheritance
# Attributes:
# current location (x,y: float) 
# orbits (a,ex,ey,i,raan,f: float)
# resource level (normalized float)

#=======
#yeet = 5.0


#REWORK: rework generic place function so that it generates orbital paramters at t = 0 based on location.
# # Methods called on node objects 
def PlaceNode(node):
#     # Method to place the fixed nodes at initial time
#     # Inputs: self
#     # physically places nodes on grid (build our own grid)
      #computes initial orbital paramters from initial location
     return

# def PlaceTransporters(transporter):
#     # Method to place the transporters at initial time
#     # Inputs:
#     # 
#     return

def StepOrbit(agent,dt):
    # Inputs: dt (float)
    # Method to step object to dt along its orbit
    #
    return

def ComputeTransfer(transporter):
    # Method to compute the orbit transfer between nodes
    # Inputs: 
    # Outputs: dictionary containing {"isPossible": bool, "dV": float, "cost": float}
    # 
    return

