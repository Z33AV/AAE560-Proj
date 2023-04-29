# -*- coding: utf-8 -*-
"""
Created on Sat Apr 29 17:50:59 2023

@author: Sarah Reilly
"""

import Phys as p
import numpy as np

class Object(object):
    pass

# Passing tolerance of unit test
tol = 1e-5

def TestOrb(testObj, truthOrb, eps):
    p.PlaceNode(testObj)
    return 1
def TestStep(obj, time, truthStep, eps):
    p.StepOrbit(obj,time)
    
    return 1
def TestTransfer(obj1, obj2):
    return 1

# Test case 1 - LEO
agent1 = Object()
agent1.loc = np.array([7500,0]) # km
truth = [1] # km
step = 100
dt = 60 # s
print("Orbit assignment correct: ", TestOrb(agent1,truth,tol))
# print("Orbit propagation correct: ", TestStep(agent1,dt,step,tol))

# # Test case 1 - LEO
# agent1 = Object()
# agent1.loc = [6985.362907528133,452.4475800875305]
# PlaceNodes(agent1)
# agent1.OrbitPars
# StepOrbit(agent1,3020.961524150334)
# agent1.OrbitPars

# # Test case 2 - MEO
# agent2 = Object()
# agent2.loc = [9629.112239900458,11501.31285860006]
# PlaceNodes(agent2)
# agent2.OrbitPars
# StepOrbit(agent2,40053.97066354053)
# agent2.OrbitPars

# # Test case 3 - Cislunar
# agent3 = Object()
# agent3.loc = [314615.9586253481, -220862.306830004]
# PlaceNodes(agent3)
# agent3.OrbitPars
# StepOrbit(agent3,3020.961524150334)
# agent3.OrbitPars

# # Test case 4 - GEO
# agent4 = Object()
# agent4.loc = [-33991.62619147076, -8340.824231411983]
# PlaceNodes(agent4)
# agent4.OrbitPars

# StepOrbit(agent4,63881.41956450418)
# agent4.OrbitPars
