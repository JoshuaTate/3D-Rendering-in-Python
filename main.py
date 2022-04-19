import pygame as pg
import ctypes
import math
import time

import maths_functions as mfn
import physics as px
import render as r
import maps

class playerSettings:
    startPos = (0,0,0) # center of player model
    startDirection = [0,0]
    accel = 50000
    speed = 10000
    fov = 45
    sens = 1
    hitbox = (10,200,10) # dimensions
    eyes = (0,80,5) # relative to startPos - so at front of player at 180 height relative to box

def basicCyle(screen,w,h,clock,realPhysics=True):
    framerate = 0
    startTime = time.time()
    pg.mouse.set_visible(False)

    pos = (playerSettings.startPos[0]+playerSettings.eyes[0],
           playerSettings.startPos[1]+playerSettings.eyes[1],
           playerSettings.startPos[2]+playerSettings.eyes[2])
    
    totalRot = playerSettings.startDirection
    sens = playerSettings.sens
    fov = playerSettings.fov
    speed = playerSettings.speed

    size = 100
    res = 10
    grassCoords,grassColours = r.pollTexture("grass",res,res,size,size)
    sandCoords,sandColours = r.pollTexture("sand",res,res,size,size)
    steelCoords,steelColours = r.pollTexture("steel",res,res,size,size)

    objects,types = maps.genBasicMap()
    hitbox = playerSettings.hitbox
    playerCuboid = r.genRawCuboidCoords(pos,hitbox[0],hitbox[1],hitbox[2])
    player = {
        "box": playerCuboid,
        "velocity": (0,0,0),
        "type": "dynamic"}
    velocity = [(0,0,0) for i in objects]
    
    textureDict = {
        "front": grassColours,
        "back": grassColours,
        "left": sandColours,
        "right": sandColours,
        "top": steelColours,
        "bottom": steelColours}
    blitDict = {
        "front": grassCoords,
        "back": grassCoords,
        "left": sandCoords,
        "right": sandCoords,
        "top": steelCoords,
        "bottom": steelCoords}

    frameTime = 1/60
    while True:
        frameStartTime = time.time()
        framerate += 1
        screen.fill([255,255,255])
        check = clock.tick(60)

        if(time.time() - startTime >= 1):
            print(framerate)
            startTime = time.time()
            framerate = 0
       
        rotation = pg.mouse.get_rel()
        pg.mouse.set_pos((int(w/2),int(h/2)))
        dummy = pg.mouse.get_rel()

        pressed = pg.key.get_pressed()
        for event in pg.event.get():
            pg.event.set_grab(True)
            if(event.type == pg.KEYDOWN):
                if(event.key == pg.K_ESCAPE):
                    pg.quit()

        rotVec = (math.sin(totalRot[0]*math.pi/180),math.cos(totalRot[0]*math.pi/180))
        posChange = (0,0,0)
        if(pressed[pg.K_w] == True):
            posChange = (posChange[0]+rotVec[0],posChange[1],posChange[2]-rotVec[1])
        if(pressed[pg.K_s] == True):
            posChange = (posChange[0]-rotVec[0],posChange[1],posChange[2]+rotVec[1])
        if(pressed[pg.K_a] == True):
            rotVec = mfn.rotate2Dvector(rotVec,270)
            posChange = (posChange[0]+rotVec[0],posChange[1],posChange[2]-rotVec[1])
        if(pressed[pg.K_d] == True):
            rotVec = mfn.rotate2Dvector(rotVec,90)
            posChange = (posChange[0]+rotVec[0],posChange[1],posChange[2]-rotVec[1])
        if(pressed[pg.K_LSHIFT] == True):
            posChange = (posChange[0],posChange[1]-1,posChange[2])
        if(pressed[pg.K_SPACE] == True):
            posChange = (posChange[0],posChange[1]+1,posChange[2])

        player = px.playerPhysics(player,frameTime,objects,posChange,playerSettings.speed,playerSettings.accel,realPhysics)
        
        pos = mfn.calcObjectMidpoint(player["box"])
        pos = (pos[0]+playerSettings.eyes[0],
               pos[1]+playerSettings.eyes[1],
               pos[2]+playerSettings.eyes[2])

        renderedObjects = []
        for i in range(len(objects)):
            rendDict = {}
            for key in objects[i]:
                rendDict[key] = []
                for j in range(len(objects[i][key])):
                    rendDict[key].append(objects[i][key][j])
            renderedObjects.append(rendDict)
        
        renderedObjects = mfn.translateCoords(renderedObjects,pos)
        objMidPoint = mfn.calcObjectMidpoint(renderedObjects[0])
        totalRot[0] += sens*rotation[0]/fov
        totalRot[1] += sens*rotation[1]/fov
        
        if(totalRot[0] >= 360):
            totalRot[0] -= 360
        elif(totalRot[0] < 0):
            totalRot[0] += 360
        if(90 < totalRot[1] < 180):
            totalRot[1] = 90
        if(180 < totalRot[1] < 270):
            totalRot[1] = 270
        if(totalRot[1] >= 360):
            totalRot[1] -= 360
        elif(totalRot[1] < 0):
            totalRot[1] += 360

        renderedObjects = mfn.rotateAroundOrigin(renderedObjects,totalRot[0],180-totalRot[1],0)
        blitPolygons,blitObjects = r.genBlitLocs(w,h,renderedObjects,fov)
        blitPolygons = r.orderByDistance(blitPolygons,blitObjects)
        screen = r.drawCube(screen,blitPolygons)
        #screen = drawTexturedCube(screen,blitPolygons,textureDict,blitDict)

        pg.display.update()
        frameTime = time.time()-frameStartTime

if(__name__ == "__main__"):
    pg.init()
    ctypes.windll.user32.SetProcessDPIAware()
    true_res = (ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))
    #screen = pg.display.set_mode((0,0), pg.FULLSCREEN)
    screen = pg.display.set_mode((720,480))
    screen.fill([255,255,255])
    pg.display.set_caption("3D test")
    w, h = pg.display.get_surface().get_size()
    clock = pg.time.Clock()
    
    # program works by having a master list of 'objects', where each element is a dict
    # each dict is "face": [vertices], where the key is a description of the face
    # and the vertices are polygon coords 
    
    basicCyle(screen,w,h,clock,realPhysics=False)

    
    
