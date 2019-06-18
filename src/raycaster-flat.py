"""
Flat raycaster written in Python by Sloan Kelly. Based on raycaster_flat.cpp by Lode Vandevenne
https://lodev.org/cgtutor/files/raycaster_flat.cpp. Original CPP file is (C) 2004-2007 Lode 
Vandevenne. See https://lodev.org/cgtutor/raycasting.html
"""

import pygame, os, sys
from pygame.locals import *
from math import sin, cos

mapWidth = 24
mapHeight = 24
screenSize = (512, 384)

worldMap = [
  [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
  [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
  [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
  [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
  [1,0,0,0,0,0,2,2,2,2,2,0,0,0,0,3,0,3,0,3,0,0,0,1],
  [1,0,0,0,0,0,2,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,1],
  [1,0,0,0,0,0,2,0,0,0,2,0,0,0,0,3,0,0,0,3,0,0,0,1],
  [1,0,0,0,0,0,2,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,1],
  [1,0,0,0,0,0,2,2,0,2,2,0,0,0,0,3,0,3,0,3,0,0,0,1],
  [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
  [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
  [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
  [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
  [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
  [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
  [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
  [1,4,4,4,4,4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
  [1,4,0,4,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
  [1,4,0,0,0,0,5,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
  [1,4,0,4,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
  [1,4,0,4,4,4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
  [1,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
  [1,4,4,4,4,4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
  [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

pygame.init()
surface = pygame.display.set_mode(screenSize)
fpsClock = pygame.time.Clock()
pygame.display.set_caption('Raycaster')

posX = 22 # x and y start position
posY = 11.5

dirX = -1 # initial direction vector
dirY = 0 

planeX = 0 # the 2d raycaster version of camera plane
planeY = 0.66 

time = 0 # time of current frame
oldTime = 0 # time of previous frame
frameTime = 0.0

while True:
    for evt in pygame.event.get():
        if evt.type == QUIT:
            pygame.quit()
            sys.exit()

    x = 0
    w = screenSize[0] * 1.0 # width
    h = screenSize[1] * 1.0 # height

    surface.fill((1, 0, 0)) # fill the surface with black

    while x < w:
        # calculate ray position and direction
        cameraX = 2.0 * x / w - 1.0 # x-coordinate in camera space
        if cameraX == 0:
            x = x + 1 # Skip?!
            continue

        rayDirX = dirX + planeX * cameraX
        rayDirY = dirY + planeY * cameraX

        # which box of the map we're in
        mapX = int(posX)
        mapY = int(posY)

        # length of ray from current position to next x or y-side
        sideDistX = 0.0
        sideDistY = 0.0

        # length of ray from one x or y-side to next x or y-side
        deltaDistX = abs(1 / rayDirX)
        if (rayDirY == 0):
            deltaDistY = float('inf')
        else:
            deltaDistY = abs(1 / rayDirY)
        perpWallDist = 0.0

        # what direction to step in x or y-direction (either +1 or -1)
        stepX = 0
        stepY = 0

        hit = 0 # was there a wall hit?
        side = 0 # was a NS or a EW wall hit?

        # calculate step and initial sideDist
        if (rayDirX < 0):
            stepX = -1
            sideDistX = (posX - mapX) * deltaDistX
        else:
            stepX = 1
            sideDistX = (mapX + 1.0 - posX) * deltaDistX

        if (rayDirY < 0):
            stepY = -1
            sideDistY = (posY - mapY) * deltaDistY
        else:
            stepY = 1
            sideDistY = (mapY + 1.0 - posY) * deltaDistY

      # perform DDA
        while (hit == 0):
            # jump to next map square, OR in x-direction, OR in y-direction
            if (sideDistX < sideDistY):
                sideDistX += deltaDistX
                mapX += stepX
                side = 0
            else:
                sideDistY += deltaDistY
                mapY += stepY
                side = 1

            # Check if ray has hit a wall
            if (worldMap[mapX][mapY] > 0):
                hit = 1

        # Calculate distance projected on camera direction (Euclidean distance will give fisheye effect!)
        if (side == 0):
            perpWallDist = (mapX - posX + (1 - stepX) / 2) / rayDirX
        else:
            perpWallDist = (mapY - posY + (1 - stepY) / 2) / rayDirY

        # Calculate height of line to draw on screen
        lineHeight = int(h / perpWallDist)

        # calculate lowest and highest pixel to fill in current stripe
        drawStart = -lineHeight / 2 + h / 2
        if(drawStart < 0):
            drawStart = 0
        drawEnd = lineHeight / 2 + h / 2
        if(drawEnd >= h):
            drawEnd = h - 1

        # choose wall color
        color = (1, 1 ,0)
        if (worldMap[mapX][mapY] == 1):
            color = (255, 0, 0) # red
        elif (worldMap[mapX][mapY] == 2):
            color = (0, 255, 0) # green
        elif (worldMap[mapX][mapY] == 3):
            color = (0, 0, 255) # blue
        elif (worldMap[mapX][mapY] == 4):
            color = (255, 255, 255) # white

        # give x and y sides different brightness
        if (side == 1):
            color = (color[0] / 2, color[1] / 2, color[2] / 2)

        # draw the pixels of the stripe as a vertical line
        pygame.draw.line(surface, color, (x, drawStart), (x, drawEnd), 1)
        x = x + 1

    # speed modifiers
    moveSpeed = frameTime/180.0 # * 5.0; # the constant value is in squares/second
    rotSpeed = frameTime/180.0 # * 3.0; # the constant value is in radians/second
    keys = pygame.key.get_pressed()
    # move forward if no wall in front of you
    if (keys[K_UP]):
        if(worldMap[int(posX + dirX * moveSpeed)][int(posY)] == False):
            posX += dirX * moveSpeed
        if(worldMap[int(posX)][int(posY + dirY * moveSpeed)] == False):
            posY += dirY * moveSpeed
    
    # move backwards if no wall behind you
    if (keys[K_DOWN]):
        if (worldMap[int(posX - dirX * moveSpeed)][int(posY)] == False):
            posX -= dirX * moveSpeed
        if (worldMap[int(posX)][int(posY - dirY * moveSpeed)] == False):
            posY -= dirY * moveSpeed
    
    # rotate to the right
    if (keys[K_RIGHT]):
        # both camera direction and camera plane must be rotated
        oldDirX = dirX
        dirX = dirX * cos(-rotSpeed) - dirY * sin(-rotSpeed)
        dirY = oldDirX * sin(-rotSpeed) + dirY * cos(-rotSpeed)
        oldPlaneX = planeX
        planeX = planeX * cos(-rotSpeed) - planeY * sin(-rotSpeed)
        planeY = oldPlaneX * sin(-rotSpeed) + planeY * cos(-rotSpeed)

    # rotate to the left
    if (keys[K_LEFT]):
        # both camera direction and camera plane must be rotated
        oldDirX = dirX
        dirX = dirX * cos(rotSpeed) - dirY * sin(rotSpeed)
        dirY = oldDirX * sin(rotSpeed) + dirY * cos(rotSpeed)
        oldPlaneX = planeX
        planeX = planeX * cos(rotSpeed) - planeY * sin(rotSpeed)
        planeY = oldPlaneX * sin(rotSpeed) + planeY * cos(rotSpeed)

    frameTime = fpsClock.tick(30)
    pygame.display.update()