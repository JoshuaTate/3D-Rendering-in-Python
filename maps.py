import render as r

def constructWalls(floor,h,d,zPos,zNeg,xPos,xNeg):
    # zPos, etc. are bools to say whether or not you want a wall there of form "axisDirection"
    walls = []
    if(zPos):
        w = floor["back"][0][0]-floor["back"][1][0]
        c = (floor["back"][1][0]+round(w/2),floor["back"][1][1]+round(h/2),floor["back"][1][2]+round(d/2))
        wall = r.genRawCuboidCoords(c,w,h,d)
        walls.append(wall)
    if(zNeg):
        w = floor["front"][1][0]-floor["front"][0][0]
        c = (floor["front"][0][0]+round(w/2),floor["front"][0][1]+round(h/2),floor["front"][0][2]-round(d/2))
        wall = r.genRawCuboidCoords(c,w,h,d)
        walls.append(wall)
    if(xPos): # w and d swap for x axis
        w = floor["right"][1][2]-floor["right"][0][2]
        c = (floor["right"][0][0]+round(d/2),floor["right"][0][1]+round(h/2),floor["right"][0][2]+round(w/2))
        wall = r.genRawCuboidCoords(c,d,h,w)
        walls.append(wall)
    if(xNeg):
        w = floor["left"][0][2]-floor["left"][1][2]
        c = (floor["left"][1][0]-round(d/2),floor["left"][1][1]+round(h/2),floor["left"][1][2]+round(w/2))
        wall = r.genRawCuboidCoords(c,d,h,w)
        walls.append(wall)
    return(walls)
        
def genBasicMap():
    floor = r.genRawCuboidCoords((0,-200,0),10000,100,10000)
    walls = constructWalls(floor,2000,10,True,True,True,True)
    cube = r.genRawCubeCoords((500,-100,500),200)
    objects = [floor,cube]
    for i in walls:
        objects.append(i)
    types = ["static" for i in range(len(objects))]
    return(objects,types)
