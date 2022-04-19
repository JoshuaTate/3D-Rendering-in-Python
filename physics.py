import math

import maths_functions as mfn

class physicsParams:
    g = 980
    terminalV = 2000
    bounceCoeff = 0.1
    bounceKill = 5 # velocity at which you just stop bouncing to stop an overly long expon decay
    velocityKill = 1
    airDrag = 0
    friction = 5000 # speed loss per sec when not accelerating

def gravity(objects,velocity,types,frameTime):
    for i in range(len(objects)):
        if(types[i] == "dynamic"):
            velocity[i] = (velocity[i][0],
                           velocity[i][1]-frameTime*physicsParams.g,
                           velocity[i][2])
    return(objects,velocity)

def moveObjects(objects,velocity,types,frameTime):
    for i in range(len(objects)):
        for key in objects[i]:
            for j in range(len(objects[i][key])):
                objects[i][key][j] = (objects[i][key][j][0]+velocity[i][0]*frameTime,
                                      objects[i][key][j][1]+velocity[i][1]*frameTime,
                                      objects[i][key][j][2]+velocity[i][2]*frameTime)
    return(objects)

def playerPhysics(player,frameTime,objects,posChange,maxSpeed,accel):
    playerCuboidList,velocityList = gravity([player["box"]],[player["velocity"]],[player["type"]],frameTime)
    player["box"] = playerCuboidList[0]
    player["velocity"] = velocityList[0]
    player = movePlayer(posChange,player,maxSpeed,accel,frameTime)
    player = collisionDetection(objects,player,frameTime)
    playerCuboidList = moveObjects(playerCuboidList,velocityList,[player["type"]],frameTime)
    player["box"] = playerCuboidList[0]
    return(player)

def movePlayer(posChange,player,maxSpeed,accel,frameTime):
    
    velocity = (player["velocity"][0]+accel*posChange[0]*frameTime,
                player["velocity"][1],
                player["velocity"][2]+accel*posChange[2]*frameTime)
    
    if(posChange[0] >= 0 and velocity[0] < 0):
        velocity = (min(velocity[0]+physicsParams.friction*frameTime,0),velocity[1],velocity[2])
    elif(posChange[0] <= 0 and velocity[0] > 0):
        velocity = (max(velocity[0]-physicsParams.friction*frameTime,0),velocity[1],velocity[2])

    if(posChange[1] > 0):
        velocity = (velocity[0],maxSpeed,velocity[2])
    
    elif(posChange[2] <= 0 and velocity[2] > 0):
        velocity = (velocity[0],velocity[1],max(velocity[2]-physicsParams.friction*frameTime,0))
    magVel = math.sqrt(velocity[0]**2+velocity[2]**2)
    if(magVel > maxSpeed):
        factor = math.sqrt(magVel/maxSpeed)
        velocity = (velocity[0]/factor,velocity[1],velocity[2]/factor)

    vel = [velocity[0],velocity[1],velocity[2]]
    for i in range(len(vel)):
        if(-1 < vel[i] < 1):
            vel[i] = 0
    player["velocity"] = (vel[0],vel[1],vel[2])
    return(player)

def collisionDetection(objects,player,frameTime):
    oppositeSides = {
        "top": "bottom",
        "bottom": "top",
        "front": "back",
        "back": "front",
        "left": "right",
        "right": "left"}
    
    if(player["velocity"][0]**2+player["velocity"][1]**2+player["velocity"][2]**2 > 0): # make sure you don't get cheesed by an e.g. (1,0,-1) velocity (however unlikely)
        for i in range(len(objects)):
            if(player["velocity"][0]**2+player["velocity"][1]**2+player["velocity"][2]**2 == 0): # script errors for 0 velocity, so need to manually break it if velocity gets set to 0 within loop
                break
            else:
                objMidPoint = mfn.calcObjectMidpoint(objects[i])
                for key in objects[i]:
                    if(player["velocity"][0]**2+player["velocity"][1]**2+player["velocity"][2]**2 == 0):
                        break
                    else:
                        planeMidPoint = mfn.calcPlaneMidpoint(objects[i][key])
                        normalVector = mfn.calcNormalVector(objects[i][key])
                        cosTheta = mfn.calcViewlineAngle(normalVector,planeMidPoint,objMidPoint)
                        if(cosTheta > 0):
                            normalVector = (-normalVector[0],-normalVector[1],-normalVector[2]) # makes sure normalVector points outwards
                        cosTheta = mfn.calcViewlineAngle(normalVector,(0,0,0),player["velocity"])

                        if(cosTheta < 0): # having now seen that velocity is incident on surface, need to see precisely which component is
                            if((player["velocity"][0] < 0 and normalVector[0] > 0) or (player["velocity"][0] > 0 and normalVector[0] < 0)):
                                TL_BR_vec = (player["box"][oppositeSides[key]][0][1]-objects[i][key][3][1],
                                             player["box"][oppositeSides[key]][0][2]-objects[i][key][3][2])
                                BR_TL_vec = (player["box"][oppositeSides[key]][2][1]-objects[i][key][1][1],
                                             player["box"][oppositeSides[key]][2][2]-objects[i][key][1][2])
                                hypVec = (TL_BR_vec[0]-BR_TL_vec[0],TL_BR_vec[1]-BR_TL_vec[1])
                                hypSquared = hypVec[0]**2+hypVec[1]**2
                                angle = math.acos(max(-1,min(1,(TL_BR_vec[0]**2+TL_BR_vec[1]**2+BR_TL_vec[0]**2+BR_TL_vec[1]**2-hypSquared)/(2*math.sqrt(TL_BR_vec[0]**2+TL_BR_vec[1]**2)*math.sqrt(BR_TL_vec[0]**2+BR_TL_vec[1]**2)))))*180/math.pi
                                if(angle > 90):
                                    if((player["box"][oppositeSides[key]][0][0] <= objects[i][key][0][0] and player["velocity"][0] < 0) or ((player["box"][oppositeSides[key]][0][0] >= objects[i][key][0][0] and player["velocity"][0] > 0))):
                                        player["velocity"] = (-physicsParams.bounceCoeff*player["velocity"][0],player["velocity"][1],player["velocity"][2])
                                        if(player["velocity"][0] >= physicsParams.bounceKill or player["velocity"][0] <= -physicsParams.bounceKill):
                                            player["velocity"] = (0,player["velocity"][1],player["velocity"][2])

                            if((player["velocity"][1] < 0 and normalVector[1] > 0) or (player["velocity"][1] > 0 and normalVector[1] < 0)):
                                successes = 0
                                if((objects[i][key][1][0] < objects[i][key][3][0] and player["box"][oppositeSides[key]][0][0] < objects[i][key][3][0]) or
                                   ((objects[i][key][1][0] > objects[i][key][3][0] and player["box"][oppositeSides[key]][0][0] > objects[i][key][3][0]))):
                                    successes += 1
                                if((objects[i][key][1][2] < objects[i][key][3][2] and player["box"][oppositeSides[key]][0][2] < objects[i][key][3][2]) or
                                   ((objects[i][key][1][2] > objects[i][key][3][2] and player["box"][oppositeSides[key]][0][2] > objects[i][key][3][2]))):
                                    successes += 1
                                if((objects[i][key][1][0] < objects[i][key][3][0] and player["box"][oppositeSides[key]][2][0] > objects[i][key][1][0]) or
                                   ((objects[i][key][1][0] > objects[i][key][3][0] and player["box"][oppositeSides[key]][2][0] < objects[i][key][1][0]))):
                                    successes += 1
                                if((objects[i][key][1][2] < objects[i][key][3][2] and player["box"][oppositeSides[key]][2][2] > objects[i][key][1][2]) or
                                   ((objects[i][key][1][2] > objects[i][key][3][2] and player["box"][oppositeSides[key]][2][2] < objects[i][key][1][2]))):
                                    successes += 1

                                if(successes == 4):
                                    if(i == 0 and key == "top"):
                                        print("key:",key,"opposite key:",oppositeSides[key])
                                        print("overlap check:",player["box"][oppositeSides[key]][0][1],objects[i][key][0][1],player["velocity"][1])
                                    if((player["box"][oppositeSides[key]][0][1] <= objects[i][key][0][1] and player["velocity"][1] < 0) or
                                       (player["box"][oppositeSides[key]][0][1] >= objects[i][key][0][1] and player["velocity"][1] > 0)): # checks overlap
                                        if(i == 0 and key == "top"):
                                            print("orientation check:",player["box"][key][0][1],objects[i][oppositeSides[key]][0][1],player["velocity"][1])
                                        if((player["box"][key][0][1] > objects[i][oppositeSides[key]][0][1] and player["velocity"][1] < 0) or
                                           (player["box"][key][0][1] < objects[i][oppositeSides[key]][0][1] and player["velocity"][1] > 0)): # ensures object is on "right side" to collide
                                            for pkey in player["box"]:
                                                for j in range(len(player["box"][pkey])):
                                                    player["box"][pkey][j] = (player["box"][pkey][j][0],
                                                                              player["box"][pkey][j][1]+objects[i][key][0][1]-player["box"][oppositeSides[key]][0][1],
                                                                              player["box"][pkey][j][2])
                                            player["velocity"] = (player["velocity"][0],-physicsParams.bounceCoeff*player["velocity"][1],player["velocity"][2])
                                            if(player["velocity"][1] >= physicsParams.bounceKill or player["velocity"][1] <= -physicsParams.bounceKill):
                                                player["velocity"] = (player["velocity"][0],0,player["velocity"][2])

                            if((player["velocity"][2] < 0 and normalVector[2] > 0) or (player["velocity"][2] > 0 and normalVector[2] < 0)):
                                TL_BR_vec = (player["box"][oppositeSides[key]][0][0]-objects[i][key][3][0],
                                             player["box"][oppositeSides[key]][0][1]-objects[i][key][3][1])
                                BR_TL_vec = (player["box"][oppositeSides[key]][2][0]-objects[i][key][1][0],
                                             player["box"][oppositeSides[key]][2][1]-objects[i][key][1][1])
                                hypVec = (TL_BR_vec[0]-BR_TL_vec[0],TL_BR_vec[1]-BR_TL_vec[1])
                                hypSquared = hypVec[0]**2+hypVec[1]**2
                                angle = math.acos(max(-1,min(1,(TL_BR_vec[0]**2+TL_BR_vec[1]**2+BR_TL_vec[0]**2+BR_TL_vec[1]**2-hypSquared)/(2*math.sqrt(TL_BR_vec[0]**2+TL_BR_vec[1]**2)*math.sqrt(BR_TL_vec[0]**2+BR_TL_vec[1]**2)))))*180/math.pi
                                if(angle > 90):
                                    if((player["box"][oppositeSides[key]][0][2] <= objects[i][key][0][2] and player["velocity"][2] < 0) or ((player["box"][oppositeSides[key]][0][2] >= objects[i][key][0][2] and player["velocity"][2] > 0))):
                                        player["velocity"] = (player["velocity"][0],player["velocity"][1],-physicsParams.bounceCoeff*player["velocity"][2])
                                        if(player["velocity"][2] >= physicsParams.bounceKill or player["velocity"][2] <= -physicsParams.bounceKill):
                                            player["velocity"] = (player["velocity"][0],player["velocity"][1],0)

    return(player)





                    
    
