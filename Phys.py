#physics file and methods definitions
import math
import numpy
import mesa
import Agents
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
# def PlaceNode(node):
#     # Method to place the fixed nodes at initial time
#     # Inputs: self
#     # physically places nodes on grid (build our own grid)
      #computes initial orbital paramters from initial location
#     return

# def PlaceTransporters(transporter):
#     # Method to place the transporters at initial time
#     # Inputs:
#     # 
#     return

# def StepOrbit(agent,dt):
#     # Inputs: dt (float)
#     # Method to step object to dt along its orbit
#     #
#     return

def ComputeTransfer(transporter):
    # Method to compute the orbit transfer between nodes
    # Inputs: 
    # Outputs: dictionary containing {"isPossible": bool, "dV": float, "cost": float}
    # 
    return

def PlaceNodes(node):
    # Places nodes at initial orbits
    # Input: node agent 
    
    loc = node.loc                          # Grab node Cartesian position 
    pos = numpy.array([loc[0],loc[1],0])    # Create (1x3) position vector
    
    orbEls = Cart2Orb(pos)                  # Create dict of orbital elements 
    node.OrbitPars = orbEls                 # Set agent's orbit parameters 
    
    return 

def StepOrbit(obj,dt):
    # Updates position (node or transporter) after dt
    # Inputs: node, dt in seconds (float)
    
    mu = 398600.4418                    # Grav parameter of Earth, kg^3/s^2
    orbels = obj.OrbitPars  
    
    a = orbels["a"]
    n = numpy.sqrt(mu/a**3)             # Find mean motion, rad/s
    
    M0 = 0                              # Initial mean anomaly, rad
    M = (M0 + n*dt) * 180/math.pi       # Stepped mean anomaly, deg
    
    newOrbit = {"a":orbels["a"],"ex": orbels["ex"],"ey":orbels["ey"],"inc":orbels["inc"],"raan":orbels["raan"],"f":M}
    obj.OrbitPars = newOrbit

    newPosition = Orb2Cart(newOrbit)
    obj.loc = newPosition

    return 

def Cart2Orb(position):
    # Converts the Cartesian position vector [x,y,z] cartesian position vector to orbital elements
    # Inputs: position (1x3 array)
    # Outputs: orbels (dict{"a","ex","ey","inc","raan",f})
        
    mu = 398600.4418 # Grav. parameter of Earth, kg^3/s^2 
    
    # Radial direction
    rc = position
    rmag = numpy.sqrt(rc[0]**2 + rc[1]**2 + rc[2]**2)
    rhat = rc/rmag
    
    vcirc = numpy.sqrt(mu/rmag)
    vc = numpy.array([0,vcirc,0])
    vmag = numpy.sqrt(vc[0]**2 + vc[1]**2 + vc[2]**2)
    
    # Normal direction
    h = numpy.cross(rc,vc)
    hhat = h/numpy.sqrt(h[0]**2 + h[1]**2 + h[2]**2)
    
    # Transverse direction
    thetahat = numpy.cross(hhat,rhat)
    
    # Rotating to inertial DCM
    dcm = numpy.vstack((rhat,thetahat))
    dcm = numpy.vstack((dcm,hhat))
    icr = numpy.transpose(dcm)
    
    rdot = numpy.dot(rhat,vc)
    
    asc = 0
    if rdot < 0:
        asc = 1
    
    # Determine elements
    sma = (-mu/2)*(vmag**2/2 - mu/rmag)**(-1)
    ecc = numpy.sqrt(1-h**2/(mu*sma))
    i = math.acos(icr[2,2]) * 180/math.pi
    raan = math.atan2(icr[0,2],-icr[1,2]) * 180/math.pi
    theta = math.atan2(icr[2,0],icr[2,1]) * 180/math.pi
    
    ebar = numpy.cross(vc,h)/mu - rc/rmag
    emag = numpy.sqrt(ebar[0]**2 + ebar[1]**2 + ebar[2]**2)
    TA = math.acos(numpy.dot(ebar,rc)/(emag/rmag)) * 180/math.pi
    
    if asc==0:
        TA = -1*TA
        TA = TA + 360
    
    argp = theta - TA
    
    if argp < 0:
        argp = argp + 360
        
    eccx = ecc*math.cos(argp*math.pi/180)
    eccy = ecc*math.sin(argp*math.pi/180)
    
    orbs = {"a":sma,"ex":eccx,"ey":eccy,"inc":i,"raan":raan,"f":TA}
    
    return orbs

def Orb2Cart(orbels):
    # Converts between orbital elements and Cartesian elements
    # Inputs: orbels (dict)
    # Outputs: x,y position in Cartesian coordinates (tuple)
    
    # mu = 398600.4418 # kg^3/s^2
    
    sma = orbels["a"]
    exx = orbels["ex"]
    eyy = orbels["ey"]
    i = orbels["inc"]
    raan = orbels["raan"]
    theta = orbels["f"]
    
    ecc = numpy.sqrt(exx**2 + eyy**2)
    argp = math.atan2(exx,eyy)
    f = theta*math.pi/180-argp
    
    if f<0:
        f = f+2*math.pi
    
    # if ecc == 0:
    #     asc = -1
    # else:
    #     if (f>0) and (f<math.pi):
    #         if i < math.pi/2:
    #             asc = 1
    #         elif i > math.pi/2:
    #             asc = 0
    #     elif (f==0) or (f==math.pi):
    #         asc = -1
    #     else:
    #         if i < math.pi/2:
    #             asc = 0
    #         elif i > math.pi/2:
    #             asc = 1
    
    p = sma*(1-ecc**2)
    r = p/(1+ecc*math.acos(f))
    # v = numpy.sqrt(mu*(2/r - 1/sma))
    # h = numpy.sqrt(p*mu)
    
    # if asc == 1:
    #     gamma = math.acos(h/(r*v))
    # elif asc == 0:
    #     gamma = -math.acos(h/(r*v))
    # else:
    #     gamma = 0
    
    r_rot = numpy.array([r,0,0])
    # v_rot = numpy.array([v*math.sin(gamma),v*math.cos(gamma),0])
    
    icr = numpy.array([[math.cos(raan)*math.cos(theta)-math.sin(raan)*math.cos(i)*math.sin(theta),-math.cos(raan)*math.sin(theta)-math.sin(raan)*math.cos(i)*math.cos(theta),math.sin(raan)*math.sin(i)],
    [math.sin(raan)*math.cos(theta)+math.cos(raan)*math.cos(i)*math.sin(theta),-math.sin(raan)*math.sin(theta)+math.cos(raan)*math.cos(i)*math.cos(theta),-math.cos(raan)*math.sin(i)],
    [math.sin(i)*math.sin(theta),math.sin(i)*math.cos(theta),math.cos(i)]])

    r_i = numpy.matmul(r_rot,numpy.linalg.inv(icr)) 
    
    return [r_i[0],r_i[1]]