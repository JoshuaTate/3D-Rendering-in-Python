import math

def magnitude(number):
    # simply returns the magnitude value of a number
    if(number < 0):
        return(-1*number)
    else:
        return(number)

def calcNormalVector(vertices):
    v1 = (vertices[1][0]-vertices[0][0],vertices[1][1]-vertices[0][1],vertices[1][2]-vertices[0][2])
    v2 = (vertices[2][0]-vertices[0][0],vertices[2][1]-vertices[0][1],vertices[2][2]-vertices[0][2])
    normalVector = [v1[1]*v2[2]-v1[2]*v2[1],
                    v1[2]*v2[0]-v1[0]*v2[2],
                    v1[0]*v2[1]-v1[1]*v2[0]]
    return(normalVector)

def calcPlaneMidpoint(vertices):
    midPoint = [0,0,0]
    for i in range(len(vertices)):
        for j in range(len(midPoint)):
            midPoint[j] += vertices[i][j]/len(vertices)
    return(midPoint)

def calcObjectMidpoint(obj):
    objMidPoint = [0,0,0]
    for key in obj:
        planeMidPoint = calcPlaneMidpoint(obj[key])
        for i in range(len(objMidPoint)):
            objMidPoint[i] += planeMidPoint[i]/len(obj)
    return(objMidPoint)

def calcViewlineAngle(targetVector,pos,targetPoint): # can also be used to find cosTheta between two vectors, if pos = (0,0,0) and targetPoint = vector 
    viewVector = (targetPoint[0]-pos[0],targetPoint[1]-pos[1],targetPoint[2]-pos[2])
    dotProduct = targetVector[0]*viewVector[0]+targetVector[1]*viewVector[1]+targetVector[2]*viewVector[2]
    targetMag = math.sqrt((targetVector[0])**2+(targetVector[1])**2+(targetVector[2])**2)
    viewMag = math.sqrt((viewVector[0])**2+(viewVector[1])**2+(viewVector[2])**2)
    cosTheta = dotProduct/(targetMag*viewMag)
    return(cosTheta)

def getVertAngles(pos,direction,fov,vertices):
    angles = []
    inView = False
    midPoint = [0,0,0]
    for i in range(len(vertices)):
        cosTheta = calcViewlineAngle(direction,pos,tuple(vertices[i]))
        angle = math.acos(cosTheta)*180/math.pi
        angles.append(angle)
        if(angle < fov + 20): # 20 being arbitrary over-estimate to avoid clipping
            inView = True
        for j in range(len(midPoint)):
            midPoint[j] += vertices[i][j]/len(vertices)
    if(len(vertices) == 4): # might need specialist statements for non-quad shape
        if(midPoint[2] > pos[2]):
            if((vertices[0][0] <= pos[0] <= vertices[2][0]) or (vertices[0][1] <= pos[1] <= vertices[2][1])):
                inView = True
    return(angles,inView)

def translateCoords(objects,v):
    for i in range(len(objects)):
        for key in objects[i]:
            for j in range(len(objects[i][key])):
                objects[i][key][j] = (tuple(objects[i][key][j])[0]-v[0],
                                      tuple(objects[i][key][j])[1]-v[1],
                                      tuple(objects[i][key][j])[2]-v[2])
    return(objects)

def rotateAroundOrigin(objects,xAngle,yAngle,zAngle):
    # slight notation malpractise, but xAngle is angle due to mouse movement in X direction
    # even though this is actually a rotation about Y axis, and vice versa for yAngle
    # BUT, zAngle IS the angle rotated about the Z axis (for orientation)
    if(xAngle != 0):
        for i in range(len(objects)):
            for key in objects[i]:
                for j in range(len(objects[i][key])):
                    hypVec = (objects[i][key][j][0],objects[i][key][j][2]-1)
                    if(hypVec == (0,0)):
                        newX = math.sin(xAngle*math.pi/180)
                        newZ = math.cos(xAngle*math.pi/180)
                    else:
                        hypSquared = hypVec[0]**2+hypVec[1]**2
                        oldX = math.acos((1+objects[i][key][j][0]**2+objects[i][key][j][2]**2-hypSquared)/(2*math.sqrt(objects[i][key][j][0]**2+objects[i][key][j][2]**2)))*180/math.pi 
                        if(hypVec[0] < 0):
                            oldX = 360 - oldX
                        newXa = oldX + xAngle
                        if(newXa >= 360):
                            newXa -= 360
                        elif(newXa < 0):
                            newXa += 360
                        newX = math.sqrt(hypSquared)*math.sin(newXa*math.pi/180)
                        newZ = math.sqrt(hypSquared)*math.cos(newXa*math.pi/180)
                    objects[i][key][j] = (newX,objects[i][key][j][1],newZ)
    if(yAngle != 0):
        for i in range(len(objects)):
            for key in objects[i]:
                for j in range(len(objects[i][key])):
                    hypVec = (objects[i][key][j][1],objects[i][key][j][2]-1)
                    if(hypVec == (0,0)):
                        newY = math.sin(yAngle*math.pi/180)
                        newZ = math.cos(yAngle*math.pi/180)
                    else:
                        hypSquared = hypVec[0]**2+hypVec[1]**2 # now for rot about x axis
                        oldY = math.acos((1+objects[i][key][j][1]**2+objects[i][key][j][2]**2-hypSquared)/(2*math.sqrt(objects[i][key][j][1]**2+objects[i][key][j][2]**2)))*180/math.pi
                        if(hypVec[0] < 0):
                            oldY = 360 - oldY
                        newYa = oldY + yAngle
                        if(newYa >= 360):
                            newYa -= 360
                        elif(newYa < 0):
                            newYa += 360
                        newY = math.sqrt(hypSquared)*math.sin(newYa*math.pi/180)
                        newZ = math.sqrt(hypSquared)*math.cos(newYa*math.pi/180)
                    objects[i][key][j] = (objects[i][key][j][0],newY,newZ)
    if(zAngle != 0):
        a = zAngle*math.pi/180
        Rz = [[math.cos(a),-math.sin(a),0],
              [math.sin(a),math.cos(a),0],
              [0,0,1]]
        for i in range(len(objects)):
            for key in objects[i]:
                for j in range(len(objects[i][key])):
                    newX = Rz[0][0]*objects[i][key][j][0]+Rz[0][1]*objects[i][key][j][1]+Rz[0][2]*objects[i][key][j][2]
                    newY = Rz[1][0]*objects[i][key][j][0]+Rz[1][1]*objects[i][key][j][1]+Rz[1][2]*objects[i][key][j][2]
                    newZ = Rz[2][0]*objects[i][key][j][0]+Rz[2][1]*objects[i][key][j][1]+Rz[2][2]*objects[i][key][j][2]
                    objects[i][key][j] = (newX,newY,newZ)
    return(objects)

def rotateSingleVector(v,xAngle,yAngle,zAngle):
    if(xAngle != 0):
        hypVec = (v[0],v[2]-1)
        if(hypVec == (0,0)):
            newX = math.sin(xAngle*math.pi/180)
            newZ = math.cos(xAngle*math.pi/180)
        elif(hypVec == (0,-1)):
            newX = 0
            newZ = 0
        else:
            hypSquared = hypVec[0]**2+hypVec[1]**2
            oldX = math.acos(max(-1,min(1,(1+v[0]**2+v[2]**2-hypSquared)/(2*math.sqrt(v[0]**2+v[2]**2)))))*180/math.pi # used 'SSS Law of Cosines' from like, GCSE
            if(hypVec[0] < 0):
                oldX = 360 - oldX
            newXa = oldX + xAngle
            if(newXa >= 360):
                newXa -= 360
            elif(newXa < 0):
                newXa += 360
            newX = math.sqrt(hypSquared)*math.sin(newXa*math.pi/180)
            newZ = math.sqrt(hypSquared)*math.cos(newXa*math.pi/180)
        v = (newX,v[1],newZ)

    if(yAngle != 0):
        hypVec = (v[1],v[2]-1)
        if(hypVec == (0,0)):
            newY = math.sin(yAngle*math.pi/180)
            newZ = math.cos(yAngle*math.pi/180)
        elif(hypVec == (0,-1)):
            newY = 0
            newZ = 0
        else:
            hypSquared = hypVec[0]**2+hypVec[1]**2 # now for rot about x axis
            oldY = math.acos(max(-1,min(1,(1+v[1]**2+v[2]**2-hypSquared)/(2*math.sqrt(v[1]**2+v[2]**2)))))*180/math.pi
            if(hypVec[0] < 0):
                oldY = 360 - oldY
            newYa = oldY + yAngle
            if(newYa >= 360):
                newYa -= 360
            elif(newYa < 0):
                newYa += 360
            newY = math.sqrt(hypSquared)*math.sin(newYa*math.pi/180)
            newZ = math.sqrt(hypSquared)*math.cos(newYa*math.pi/180)
        v = (v[0],newY,newZ)
        
    return(v)

def getXYanglesVector(v):
    # these are again opposite; xAngle is rotation about Y axis and vice versa
    # compares angle to Z axis; if you see just a '1' it's because I don't bother squaring it
    hypVec = (v[0],v[2]-1)
    if(hypVec == (0,-1)):
        xAngle = 0
    else:
        hypSquared = hypVec[0]**2+hypVec[1]**2
        xAngle = math.acos(max(-1,min(1,(1+v[0]**2+v[2]**2-hypSquared)/(2*math.sqrt(v[0]**2+v[2]**2)))))*180/math.pi # used 'SSS Law of Cosines' from like, GCSE
        if(hypVec[0] < 0):
            xAngle = 360 - xAngle
    hypVec = (v[1],v[2]-1)
    if(hypVec == (0,-1)):
        yAngle = 0
    else:
        hypSquared = hypVec[0]**2+hypVec[1]**2 # now for rot about x axis
        yAngle = math.acos(max(-1,min(1,(1+v[1]**2+v[2]**2-hypSquared)/(2*math.sqrt(v[1]**2+v[2]**2)))))*180/math.pi
        if(hypVec[0] < 0):
            yAngle = 360 - yAngle
    return(xAngle,yAngle)

def getXZPlaneVector(v):
    # returns a 3D vector normalised as it's projection onto X-Z plane, for player movement
    hypVec = (v[0],v[2]-1)
    if(hypVec == (0,-1)):
        v = (0,1)
    else:
        hypSquared = hypVec[0]**2+hypVec[1]**2
        xAngle = math.acos(max(-1,min(1,(1+v[0]**2+v[2]**2-hypSquared)/(2*math.sqrt(v[0]**2+v[2]**2)))))*180/math.pi # used 'SSS Law of Cosines' from like, GCSE
        if(hypVec[0] < 0):
            xAngle = 360 - xAngle
        v = (math.sin(xAngle*math.pi/180),math.cos(xAngle*math.pi/180))
    return(v)

def rotate2Dvector(v,angle):
    hypVec = (v[0],v[1]-1)
    if(hypVec == (0,0) or hypVec == (0,-1)):
        newX = math.sin(angle*math.pi/180)
        newZ = math.cos(angle*math.pi/180)
    else:
        hypSquared = hypVec[0]**2+hypVec[1]**2
        oldA = math.acos(max(-1,min(1,(1+v[0]**2+v[1]**2-hypSquared)/(2*math.sqrt(v[0]**2+v[1]**2)))))*180/math.pi
        if(hypVec[0] < 0):
            oldA = 360 - oldA
        newA = oldA + angle
        if(newA >= 360):
            newA -= 360
        elif(newA < 0):
            newA += 360
        newX = math.sin(newA*math.pi/180) # normalised to 1
        newZ = math.cos(newA*math.pi/180)
    v = (newX,newZ)
    return(v)

if(__name__=="__main__"):
    cosTheta = calcViewlineAngle((0,-1000000,0),(0,-205,0),(0,-200,0))
    print(cosTheta)
    cosTheta = calcViewlineAngle((0,1000000,0),(0,0,0),(3,-50,-5))
    print(cosTheta)
