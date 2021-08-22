#! /usr/bin/python

import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import sys
import time

def cropImage(img, contours):
    min_x, max_x = [contours[0][0][1], 0]
    min_y, max_y = [contours[0][0][0], 0]

    for v in contours:
        if(min_x > v[0][1]):
            min_x = v[0][1]
        if(max_x < v[0][1]):
            max_x = v[0][1]
        if(min_y > v[0][0]):
            min_y = v[0][0]
        if(max_y < v[0][0]):
            max_y = v[0][0]

    return img[min_x:max_x, min_y:max_y]

def cropImageXY(img, y, x):
    return img[y[0]:y[1], x[0]:x[1]]

def reverseBW(imgBw):
    for i in range(0, imgBw.shape[0]):
        for j in range(0, imgBw.shape[1]):
            if(imgBw[i][j]):
                imgBw[i][j] = 0
            else:
                imgBw[i][j] = 255
    return imgBw

def drawLine(imgbw, imgBGR):
    height, width = [imgbw.shape[0], imgbw.shape[1]]

    #find all white orizontal lines
    lines = []
    for i in range(0, height):
        start = 0
        line_len = 0
        for j in range(0, width):
            if( imgbw[i][j] ): #is a white px ?
                if(not(line_len)): #if the lenght of line is 0 then position j is the starting point
                    start = j
                line_len += 1

        #save the line in memory only if is 8+ pixels
        if(line_len >= 8 ):
            #list = [ y position, line len, start point, end point]
            lines.append([i, line_len, start, start+line_len])

    #print(lines)
    unique_lines = []
    if(len(lines)):
        for i in range(0, len(lines)-1):
            if( lines[i][0]+1 != lines[i+1][0] ):
                unique_lines.append(lines[i])
        unique_lines.append(lines[len(lines)-1])

        #print(unique_lines)
        for l in unique_lines:
            for i in range(l[2], l[3]):
                imgBGR[l[0]][i] = [255, 0, 0]

def main(img_path):
    imgBGR = cv.imread(img_path)
    img = cv.cvtColor(imgBGR, cv.COLOR_BGR2GRAY)
    height, width = img.shape
    print( height, end=' ' )
    print( width )

    kernel = np.ones((1, 1), np.uint8)
    img = cv.dilate(img, kernel, iterations=1)
    img = cv.erode(img, kernel, iterations=1)

    ret,black_white = cv.threshold(img,127,255,cv.THRESH_BINARY)
    #cv.imwrite("bw.png", black_white)

    contours, h = cv.findContours(black_white, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    n = 0
    bw_cards = []
    possible_cards = []
    for c in contours:
        area = cv.contourArea(c)
        if( area > 3000 and area < height*width-3000 ):
            bw = cropImage(black_white, c)

            possible_cards.append(cropImage(imgBGR, c))
            bw = reverseBW(bw)
            bw_cards.append(bw)
             
            #cv.imwrite( "card"+str(n)+".png", possible_cards[n] )
            #cv.imwrite( "cardbw"+str(n)+".png", bw )
            n += 1

            cv.drawContours(imgBGR, [c], 0, [0, 255, 0], 2)

    cv.imwrite( "contours.png", imgBGR )

    n = 0
    nu = 0
    for card in bw_cards:

        cv.imwrite("prv"+str(n)+".png", card)
        bw_crop = cropImageXY(card, [0, int(card.shape[0]/2)], [0, int(card.shape[1]/2)])
        card_crop = cropImageXY(possible_cards[n], [0, int(card.shape[0]/2)], [0, int(card.shape[1]/2)])
        img_area = bw_crop.shape[0] * bw_crop.shape[1]
        
        contours, h = cv.findContours(bw_crop, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
        if(len(contours) > 0 ):
            for c in contours:
                area = cv.contourArea(c)
                if( area > 10 and area < img_area*0.015 ):
                    #cv.drawContours(card_crop, [c], 0, [0, 255, 0], 1)
                    #print("Image: " + str(nu))
                    cv.imwrite("possible_number"+str(nu)+".png", cropImage(bw_crop, c) )
                    print("Image "+str(nu))
                    drawLine(cropImage(bw_crop, c), cropImage(card_crop, c))
                    drawColumns(cropImage(bw_crop, c), cropImage(card_crop, c))
                    
                    nu += 1
            cv.imwrite("crop"+str(n)+".png", card_crop)
        
        n += 1

if __name__ == '__main__':
    main(sys.argv[1])
