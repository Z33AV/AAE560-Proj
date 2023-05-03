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
#      return

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

def ComputeTransfer(origin,dest):
    # Computes orbital transfer between a transporter and some destination
    # Input: origin node (obj), destination node (obj)
    # Output: TransferParams (dict: {"isPossible": bool,"dV": float,"TOF": float})
    
    # Constants
    mu = 398600.4418 # km^3/s^2
    
    # Initial and final destinations
    pre = origin.loc # Pre-maneuver position
    post = dest.loc  # Post-maneuver position
    
    r_i = numpy.sqrt(origin.loc[0]**2 + origin.loc[1]**2)
    r_f = numpy.sqrt(dest.loc[0]**2 + dest.loc[1]**2)
    
    # calcTransfer = 0
    # tof = -1
    # dv_tot = -1
    
    # Determine if transfer is possible
    try:
        ang = math.acos(numpy.dot(pre,post)/(r_i*r_f)) # rad, angle between two objects
    
        n_f = numpy.sqrt(mu/r_f**3)             # rad/s, mean motion of destination node
        a_t = 1/2 * (r_i + r_f)                 # km, transfer orbit SMA 
        tof = math.pi * numpy.sqrt(a_t**3/mu)   # s, time-of-flight
        phi = math.pi - n_f * tof               # rad, required phase angle
    
        # 5 deg tolerance for transfer geometry 
        if abs(phi - ang)*180/math.pi <= 5: 
            calcTransfer = 1
        else:
            calcTransfer = 0
            dv_tot = -1
            tof = -1
    except:
        calcTransfer = 0
        tof = -1
        dv_tot = -1

    if calcTransfer:        
        v_i = numpy.sqrt(mu/r_i)            # km/s, velocity before initial maneuver 
        v_p = numpy.sqrt(2*mu/r_i - mu/a_t) # km/s, velocity after initial maneuver
        dv_1 = v_p - v_i                    # km/s, first dV 

        v_a = numpy.sqrt(2*mu/r_f - mu/a_t) # km/s, velocity before final maneuver
        v_f = numpy.sqrt(mu/r_f)            # km/s, velocity after final maneuver
        dv_2 = v_f - v_a                    # km/s, last dV

        dv_tot = dv_1 + dv_2                # km/s, total dV

    TransferParams = {"isPossible": calcTransfer,"dV": dv_tot,"TOF":tof}
    
    return TransferParams

def PlaceNode(node):
    # Places nodes at initial orbits
    # Input: node agent 
    
    loc = node.loc                          # Grab node Cartesian position 
    pos = numpy.array([loc[0],loc[1],0])    # Create (1x3) position vector
    
    orbEls = Cart2Orb(pos)                  # Create dict of orbital elements 
    #node.OrbitPars = orbEls                 # Set agent's orbit parameters 
    
    return orbEls

def StepOrbit(obj,dt):
    # Updates position (node or transporter) after dt
    # Inputs: node, dt in seconds (float)
    
    mu = 398600.4418                    # Grav parameter of Earth, kg^3/s^2
    orbels = obj.OrbitPars  
    
    a = orbels["a"]
    n = numpy.sqrt(mu/a**3)             # Find mean motion, rad/s
    
    M0 = 0                              # Initial mean anomaly, rad
    M = (M0 + n*dt) * 180/math.pi       # Stepped mean anomaly, deg
    
    obj.OrbitPars["f"] = math.fmod(M,360)
    new_parm  = math.fmod(M,360)

    newPosition = Orb2Cart(obj.OrbitPars)
    #obj.loc = newPosition #does not work

    return newPosition, new_parm

def Cart2Orb(position):
    # Converts the Cartesian position vector [x,y,z] cartesian position vector to orbital elements
    # Inputs: position (1x3 array)
    # Outputs: orbels (dict{"a","ex","ey","inc","raan",f})
        
    mu = 398600.4418 # Grav. parameter of Earth, kg^3/s^2 
    
    # Radial direction
    rc = position
    rmag = numpy.sqrt(rc[0]**2 + rc[1]**2 + rc[2]**2)
    rhat = rc/rmag
    
    tan = math.atan2(rc[1],rc[0]) # rad
    if tan < 0:
        tan = tan + 2*math.pi

    dcm1 = numpy.array([[math.cos(tan),-math.sin(tan),0],[math.sin(tan),math.cos(tan),0],[0,0,1]])
    
    vcirc = numpy.array([0,numpy.sqrt(mu/rmag),0])
    vc = numpy.matmul(vcirc,numpy.linalg.inv(dcm1))
    
    # Normal direction
    h = numpy.cross(rc,vc)
    hmag = numpy.sqrt(h[0]**2 + h[1]**2 + h[2]**2)
    hhat = h/hmag
    
    # Transverse direction
    thetahat = numpy.cross(hhat,rhat)
    
    # Rotating to inertial DCM
    dcm = numpy.vstack((rhat,thetahat))
    dcm = numpy.vstack((dcm,hhat))
    icr = numpy.transpose(dcm)
    
    rdot = numpy.dot(rhat,vc)
    
    asc = 0
    if rdot < 0: # ascending in orbit flag
        asc = 1
    
    # Determine elements
    ecc1 = (vc[1]*h[2] - vc[2]*h[1])/mu - rc[0]/rmag
    ecc2 = (vc[2]*h[0] - vc[0]*h[2])/mu - rc[1]/rmag
    ecc3 = (vc[0]*h[1] - vc[1]*h[0])/mu - rc[2]/rmag
    eccv = numpy.array([ecc1,ecc2,ecc3]) # eccentricity vector
    ecc = numpy.linalg.norm(eccv) # eccentricity
    sma = (hmag**2/mu)/(1-ecc**2) # km, semimajor axis
    i = math.acos(icr[2,2]) * 180/math.pi # deg, inclination
    raan = 0 #math.atan2(icr[0,2],-icr[1,2]) * 180/math.pi
    theta = math.atan2(icr[2,0],icr[2,1]) * 180/math.pi # deg, argument of lat
    
    ebar = numpy.cross(vc,h)/mu - rc/rmag
    emag = numpy.sqrt(ebar[0]**2 + ebar[1]**2 + ebar[2]**2)
    
    if emag != 0:
        TA = math.acos(numpy.dot(ebar,rc)/emag/rmag) * 180/math.pi
    else: # Catch divide by zero error
        TA = math.acos(-1)
    
    if asc==0:
        TA = -1*TA
        TA = TA + 360
    
    argp = theta - TA # deg, argument of perigee
    
    if argp < 0:
        argp = argp + 360
        
    eccx = ecc*math.cos(argp*math.pi/180) # eccentricity in x
    eccy = ecc*math.sin(argp*math.pi/180) # eccentricity in y
    
    orbs = {"a":sma,"ex":eccx,"ey":eccy,"inc":i,"raan":raan,"f":tan*180/math.pi}
    
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
    
    p = sma*(1-ecc**2)
    r = p/(1+ecc*math.cos(f))
    
    r_rot = numpy.array([r,0,0])
    
    theta = theta * math.pi/180
    i = i * math.pi/180
    raan = raan * math.pi/180
    
    icr = numpy.array([[math.cos(raan)*math.cos(theta)-math.sin(raan)*math.cos(i)*math.sin(theta),-math.cos(raan)*math.sin(theta)-math.sin(raan)*math.cos(i)*math.cos(theta),math.sin(raan)*math.sin(i)],
    [math.sin(raan)*math.cos(theta)+math.cos(raan)*math.cos(i)*math.sin(theta),-math.sin(raan)*math.sin(theta)+math.cos(raan)*math.cos(i)*math.cos(theta),-math.cos(raan)*math.sin(i)],
    [math.sin(i)*math.sin(theta),math.sin(i)*math.cos(theta),math.cos(i)]])

    r_i = numpy.matmul(r_rot,numpy.linalg.inv(icr)) 
    
    return [r_i[0],r_i[1]]

# Updated