import pygame as pg
import maths_functions as mfn
import math

def pollTexture(image,wres,hres,w,h):
    # returns a 2D array where each entry is essentially a point
    # also returns a 2D array with a colour for each polygon; there's an extra row and column
    # in the row array so each colour represents the polygon formed by the points:
    # (i,j),(i,j+1),(i+1,j) and (i+1,j+1) if it's at (i,j,) in the colour array
    texture = pg.transform.scale(pg.image.load("textures//"+image+".png").convert(), (w,h))
    wPolys = round(w/wres)
    hPolys = round(h/hres)
    polyCoords = [[] for i in range(hPolys+1)]
    colours = [[] for i in range(hPolys)]
    for i in range(hPolys+1):
        for j in range(wPolys+1):
            if(i == 0 and j == 0):
                polyCoords[i] = [(0,0)]
            elif(i == 0):
                polyCoords[i].append((polyCoords[i][j-1][0]+round((w-polyCoords[i][j-1][0])/(wPolys+1-j)),0))
            elif(j == 0):
                polyCoords[i] = [(0,polyCoords[i-1][j][1]+round((h-polyCoords[i-1][j][1])/(hPolys+1-i)))]
            else:
                polyCoords[i].append((polyCoords[i][j-1][0]+round((w-polyCoords[i][j-1][0])/(wPolys+1-j)),polyCoords[i-1][j-1][1]+round((h-polyCoords[i-1][j-1][1])/(hPolys+1-i))))
            if(i > 0 and j > 0):
                colour = texture.get_at((polyCoords[i-1][j-1][0]+int((polyCoords[i][j][0]-polyCoords[i-1][j-1][0])/2),
                                         polyCoords[i-1][j-1][1]+int((polyCoords[i][j][1]-polyCoords[i-1][j-1][1])/2)))
                if(j == 0):
                    colours[i-1] = [colour]
                else:
                    colours[i-1].append(colour)

    return(polyCoords,colours)

def genRawCubeCoords(c,d): # center, dimension
    v = [(c[0]-int(d/2),c[1]+int(d/2),c[2]-int(d/2)),(c[0]+int(d/2),c[1]+int(d/2),c[2]-int(d/2)),
                (c[0]+int(d/2),c[1]-int(d/2),c[2]-int(d/2)),(c[0]-int(d/2),c[1]-int(d/2),c[2]-int(d/2)),
                (c[0]-int(d/2),c[1]+int(d/2),c[2]+int(d/2)),(c[0]+int(d/2),c[1]+int(d/2),c[2]+int(d/2)),
                (c[0]+int(d/2),c[1]-int(d/2),c[2]+int(d/2)),(c[0]-int(d/2),c[1]-int(d/2),c[2]+int(d/2))]
    cube = {
        "front": [v[0],v[1],v[2],v[3]],
        "back": [v[5],v[4],v[7],v[6]],
        "left": [v[4],v[0],v[3],v[7]],
        "right": [v[1],v[5],v[6],v[2]],
        "top": [v[4],v[5],v[1],v[0]],
        "bottom": [v[3],v[2],v[6],v[7]]}
    return(cube)

def genRawCuboidCoords(c,w,h,d): # center, width, height, depth; not window width or height
    v = [(c[0]-int(w/2),c[1]+int(h/2),c[2]-int(d/2)),(c[0]+int(w/2),c[1]+int(h/2),c[2]-int(d/2)),
                (c[0]+int(w/2),c[1]-int(h/2),c[2]-int(d/2)),(c[0]-int(w/2),c[1]-int(h/2),c[2]-int(d/2)),
                (c[0]-int(w/2),c[1]+int(h/2),c[2]+int(d/2)),(c[0]+int(w/2),c[1]+int(h/2),c[2]+int(d/2)),
                (c[0]+int(w/2),c[1]-int(h/2),c[2]+int(d/2)),(c[0]-int(w/2),c[1]-int(h/2),c[2]+int(d/2))]
    cuboid = {
        "front": [v[0],v[1],v[2],v[3]], # faces need to be TL,TR,BR,BL as you face them
        "back": [v[5],v[4],v[7],v[6]],
        "left": [v[1],v[5],v[6],v[2]],
        "right": [v[4],v[0],v[3],v[7]],
        "top": [v[4],v[5],v[1],v[0]],
        "bottom": [v[3],v[2],v[6],v[7]]}
    return(cuboid)

def genBlitLocs(w,h,objects,fov): # assuming direction of view is always z axis and pos is always origin
    blitPolygons = []
    blitObjects = []
    for i in range(len(objects)):
        polygons = {}
        for key in objects[i]:
            angles,inView = mfn.getVertAngles((0,0,0),(0,0,1),fov,objects[i][key])
            
            if(inView): # logic to decide if this polygon should be blitted
                objMidPoint = mfn.calcObjectMidpoint(objects[i])
                planeMidPoint = mfn.calcPlaneMidpoint(objects[i][key])
                normalVector = mfn.calcNormalVector(objects[i][key])
                cosTheta = mfn.calcViewlineAngle(normalVector,planeMidPoint,objMidPoint)
                if(cosTheta > 0):
                    normalVector = (-normalVector[0],-normalVector[1],-normalVector[2]) # makes sure normalVector points outwards
                cosTheta = mfn.calcViewlineAngle(tuple(normalVector),planeMidPoint,(0,0,0)) # target point here is your pos, as
                # you've just made sure the normal vector points OUTWARDS, so for a "success", it will be facing you

                if(cosTheta > 0): # gets blit locs for the polygon, if decided that it should
                    blitLocs = []
                    for j in range(len(objects[i][key])):
                        xAngle = math.atan(objects[i][key][j][0]/max(objects[i][key][j][2],1)) # opp / adj = x pos / z pos
                        yAngle = math.atan(objects[i][key][j][1]/max(objects[i][key][j][2],1))
                        blitLocs.append((round(w/2+w*xAngle*180/(math.pi*fov*2)),
                                         round(h/2+h*yAngle*180/(math.pi*fov*2))))
                    polygons[key] = blitLocs
        blitPolygons.append(polygons)
        blitObjects.append(objects[i])

    return(blitPolygons,blitObjects)

def orderByDistance(blitPolygons,blitObjects):
    orderedBlitPolygons = []
    objDistance = {}
    objDistList = []
    for i in range(len(blitObjects)):
        midpoint = mfn.calcObjectMidpoint(blitObjects[i])
        dist = math.sqrt(midpoint[0]**2+midpoint[1]**2+midpoint[2]**2)
        objDistance[i] = dist
        
    for key in objDistance:
        tempArray = [i for i in objDistList]
        i = 0
        if(len(orderedBlitPolygons) == 1):
            if(objDistance[key] <= objDistList[0]):
                i = 1
        while(len(tempArray) > 1):
            if(objDistance[key] > tempArray[int(len(tempArray)/2)]):
                tempArray = tempArray[:int(len(tempArray)/2)]
            elif(objDistance[key] < tempArray[int(len(tempArray)/2)]):
                i += int(len(tempArray)/2)
                tempArray = tempArray[int(len(tempArray)/2):]
            elif(objDistance[key] == tempArray[int(len(tempArray)/2)]):
                i += int(len(tempArray)/2)
                break
            if(len(tempArray) == 1):
                if(objDistance[key] <= tempArray[0]):
                    i += 1
        orderedBlitPolygons.insert(i,blitPolygons[key]) # key is the list index in this case
        objDistList.insert(i,objDistance[key])
    return(orderedBlitPolygons)

def basicRenderTexture(polyCoords,colours,polygon):
    for i in range(len(colours)):
        for j in range(len(colours)):
            pointlist = [(polygon[0][0]+round(j*(polygon[1][0]-polygon[0][0])/len(colours[i])+i*(polygon[3][0]-polygon[0][0])/len(colours)), # top left tuple
                          polygon[0][1]+round(i*(polygon[3][1]-polygon[0][1])/len(colours)+j*(polygon[1][1]-polygon[0][1])/len(colours[i]))),
                         (polygon[0][0]+round((j+1)*(polygon[1][0]-polygon[0][0])/len(colours[i])+i*(polygon[3][0]-polygon[0][0])/len(colours)), # top right
                          polygon[0][1]+round(i*(polygon[3][1]-polygon[0][1])/len(colours)+(j+1)*(polygon[1][1]-polygon[0][1])/len(colours[i]))),
                         (polygon[0][0]+round((j+1)*(polygon[1][0]-polygon[0][0])/len(colours[i])+(i+1)*(polygon[3][0]-polygon[0][0])/len(colours)), # bottom right
                          polygon[0][1]+round((i+1)*(polygon[3][1]-polygon[0][1])/len(colours)+(j+1)*(polygon[1][1]-polygon[0][1])/len(colours[i]))),
                         (polygon[0][0]+round(j*(polygon[1][0]-polygon[0][0])/len(colours[i])+(i+1)*(polygon[3][0]-polygon[0][0])/len(colours)), # bottom left
                          polygon[0][1]+round((i+1)*(polygon[3][1]-polygon[0][1])/len(colours)+j*(polygon[1][1]-polygon[0][1])/len(colours[i])))]
            pg.draw.polygon(screen, colours[i][j], pointlist)
    return(screen)

def drawCube(screen,blitPolygons):
    colour = {
        "front": [200,200,200],
        "back": [255,0,0],
        "left": [0,255,0],
        "right": [0,0,255],
        "top": [255,255,0],
        "bottom": [0,0,0]}

    for i in range(len(blitPolygons)):
        for key in blitPolygons[i]:
            pg.draw.polygon(screen, colour[key], blitPolygons[i][key])
    return(screen)

def drawTexturedCube(screen,blitPolygons,textureDict,blitDict):
    # texture dict is key = front / back / left etc. : name of png texture file
    for i in range(len(blitPolygons)):
        for key in blitPolygons[i]:
            screen = basicRenderTexture(blitDict[key],textureDict[key],blitPolygons[i][key])
    return(screen)
