# Spherical Geometry Visualization
# Version 1.0 (Sept. 7, 2013)
# Version 1.1 (May 26, 2014)
# Matthew Zhu

# This provides a visual interface for spherical geometry, which can be
# difficult to picture mentally or in an exclusively 2D medium. Features include:
# --a rotatable and scalable 3D VPython environment in which a point can be viewed from any angle
# --dynamic coordinate manipulation, with values given
# --highlighting of the major components of the graph
# --short explanation of each coordinate

# And possibly to come:
# --finding the distance between two points given in spherical coordinates, with visual interpretation

from __future__ import print_function, division
from visual import *

sphericalGraph = display(title = "Spherical Graph", x=0, y=0, width=450, height=500, forward=(-1,-1,-1), up=(0,0,1))

# define the keys to press for each function
expand = 'r'
contract = 'f'
incTheta = 'd'
decTheta = 'a'
incPhi = 'w'
decPhi = 's'

# define the starting position spherical coordinates and coordinate axes
rho = 5
theta = pi/3 #radians
phi = pi/4 #radians
xAxis = arrow(pos = (0,0,0), axis = (1,0,0), color = (1,0,0), length = rho + 1, shaftwidth = 0.1, fixedwidth = True)
yAxis = arrow(pos = (0,0,0), axis = (0,1,0), color = (0,1,0), length = rho + 1, shaftwidth = 0.1, fixedwidth = True)
zAxis = arrow(pos = (0,0,0), axis = (0,0,1), color = (0,0,1), length = rho + 1, shaftwidth = 0.1, fixedwidth = True)
xLabel = label(pos = (rho,0,0), text = "X", box = False, color = color.red)
yLabel = label(pos = (0,rho,0), text = "Y", box = False, color = color.green)
zLabel = label(pos = (0,0,rho), text = "Z", box = False, color = color.cyan)

def sphToCart(rho, theta, phi):
    x = rho * sin(phi) * cos(theta)
    y = rho * sin(phi) * sin(theta)
    z = rho * cos(phi)
    return (x,y,z)

# place the point initially with the given coordinates
pt = points(pos = [sphToCart(rho, theta, phi)], size = 15, color = color.white)
ball = sphere(pos = (0,0,0), opacity = 0.3, radius = rho)

### MAKING LINES ###

ptloc = pt.pos[0]
origin = (0,0,0)
x = ptloc[0]
y = ptloc[1]
z = ptloc[2]
# creating default lines to be updated later
l1 = curve(pos = [ptloc, origin], radius = 0.05, color = color.blue)
l2 = curve(pos = [ptloc,(x,y,0)])
l3 = curve(pos = [(x,y,0),(x,0,0)])
l4 = curve(pos = [(x,y,0),(0,y,0)])
l5 = curve(pos = [(x,y,0),origin], radius = 0.05, color = color.red)

def updateLines(pointObj): #given a point (x,y,z)
    point = pointObj.pos[0]
    origin = (0,0,0)
    x = point[0]
    y = point[1]
    z = point[2]
    # connect to origin
    l1.pos[0] = point
    l1.pos[1] = origin
    # drop into xy plane
    l2.pos[0] = point
    l2.pos[1] = (x,y,0)
    # connect to origin and perpendiculars to the x and y axes in the xy plane
    l3.pos[0] = (x,y,0)
    l3.pos[1] = (x,0,0)
    l4.pos[0] = (x,y,0)
    l4.pos[1] = (0,y,0)
    l5.pos[0] = (x,y,0)
    l5.pos[1] = origin

### MAKING THE GUI ###

infoWindow = display(title="Information", x=450, y=0, width=450, height=500,
                     userzoom=False, userspin=False, autoscale=False, range=6)
info1 = label(pos=(0,4), box=False, text=
"The spherical coordinate system describes a point \n\
as if it were on a sphere with latitude/longitude. \n\
One format for the coordinates is (rho, theta, phi), \n\
although conventions vary. \n\n")
info2 = label(pos=(0,1.5), box=False, text=
"The radius of the sphere is rho, the longitude of the \n\
point (measured from the positive x-axis) is theta, and \n\
the latitude of the point (measured from the positive \n\
z-axis) is phi. (Therefore, if uniqueness is to be \n\
preserved, rho is positive, theta is in [0, 2pi), and \n\
phi is in [0, pi), although this is not required.) \n\n")
info3 = label(pos=(0,-1), box=False, text=
"In this program, the angles are formed by the line \n\
segments marked with the same color. Theta has red \n\
lines, the positive x-axis and the xy-plane component \n\
of the location. Phi has blue lines, the positive\n\
z-axis and the distance to the origin.")

# creating default values to be updated later
rhoText = label(pos=(0,-3.5), box=False, text="Rho (" + expand + "/" + contract + " to increase/decrease): " + str(round(rho,2)))
thetaText = label(pos=(0,-4.5), box=False, text=
                  "Theta (" + incTheta + "/" + decTheta + " to increase/decrease): " + str(round(theta,4)) + " rad (" + str(round(degrees(theta), 2)) + " deg)")
phiText = label(pos=(0,-5.5), box=False, text=
                "Phi (" + incPhi + "/" + decPhi + " to increase/decrease): " + str(round(phi,4)) + " rad (" + str(round(degrees(phi), 2)) + " deg)")

def updateRhoGUI(r):
    rhoText.text = "Rho (" + expand + " to increase; " + contract + " to decrease): " + str(round(r,2))
def updateThetaGUI(t):
    thetaText.text = "Theta (" + incTheta + "/" + decTheta + " to increase/decrease): " + str(round(t,4)) + " rad (" + str(round(degrees(t), 2)) + " deg)"
def updatePhiGUI(p):
    phiText.text = "Phi (" + incPhi + "/" + decPhi + " to increase/decrease): " + str(round(p,4)) + " rad (" + str(round(degrees(p), 2)) + " deg)"

### UPDATING COORDINATES ###
# which in turn updates the connecting lines and GUI

def updateRho(r):
    ball.radius = r
    pt.pos[0] = sphToCart(r, theta, phi) #angles stay the same, r scales
    updateLines(pt)
    updateRhoGUI(r)
def updateTheta(t):
    pt.pos[0] = sphToCart(rho, t, phi) #keep others constant
    updateLines(pt)
    updateThetaGUI(t)
def updatePhi(p):
    pt.pos[0] = sphToCart(rho, theta, p) #keep others constant
    updateLines(pt)
    updatePhiGUI(p)

### MAIN LOOP ###

while 1:
    rate(50)
    press = sphericalGraph.kb.getkey()
    ### RADIUS
    if press == expand:
        rho += 0.05 #expand
        updateRho(rho)
    elif press == contract:
        rho -= 0.05 #contract
        updateRho(rho)
    ### THETA ranges from 0 to 2pi and is periodic ("longitude")
    elif press == incTheta:
        theta += pi/36 #increase theta
        updateTheta(theta)
    elif press == decTheta:
        theta -= pi/36 #decrease theta
        updateTheta(theta)
    ### PHI ranges from 0 to pi ("latitude")
    elif press == incPhi:
        phi += pi/36
        updatePhi(phi) #increase phi
    elif press == decPhi:
        phi -= pi/36
        updatePhi(phi) #decrease phi
