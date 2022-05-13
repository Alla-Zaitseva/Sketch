import svgpathtools as svg
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import numpy as np
import math
import cv2

from random import random

def stackImages(scale, imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range(0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape[:2]:
                    imgArray[x][y]=cv2.resize(imgArray[x][y],(0,0),None,scale,scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y] = cv2.cvtColor(imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank] * rows
        hor_con = [imageBlank] * rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None, scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x],cv2.COLOR_GRAY2BGR)
        hor = np.hstack(imgArray)
        ver = hor
    return ver

def choose(probs,k):
    choices = []
    remaining = 1
    p = probs[:]
    for i in range(k):
        r = remaining * random()
        i = 0
        s = p[i]
        while s < r:
            i += 1
            s += p[i]
        choices.append(i)
        remaining -= p[i]
        p[i] = 0
    return choices

def delete_multiple_element(list_object, indices):
    indices = sorted(indices, reverse=True)
    for idx in indices:
        if idx < len(list_object):
            list_object.pop(idx)

def split_lines(paths, attributes):
    new_paths = []
    new_attributes = []
    for path, attribute in zip(paths, attributes):
        contin_subpaths = path.continuous_subpaths()
        new_paths += contin_subpaths
        new_attributes += [attribute] * len(contin_subpaths)
    
    return new_paths, new_attributes

def draw_instructions(svg_file_input, output_dir):
    paths, attributes = svg.svg2paths(svg_file_input)

    # FIXME: think about attributes
    # print("Lines before: ", len(paths))
    # paths, attributes = split_lines(paths, attributes)
    # attributes = []
    print("Lines: ", len(paths))

    elems_count = len(paths)
    elems_to_erase = math.ceil(elems_count / 6)
    

    all_images = []
    
    for i in range(1, 7):
        lens = []
        for path in paths:
            lens.append(path.length())
        lens = np.array(lens)

        # This is using exp equation
        # 
        # alpha = 0.05
        # lens = 1. / np.exp(alpha * lens)

        # This is using linear equation
        # 
        alpha = 0.5
        lens = 1. / (alpha * lens)

        if np.sum(lens) == 0:
            break

        lens = lens * (1. / np.sum(lens))

        if len(paths) - elems_to_erase <= 0:
            elems_to_erase = len(paths) - 5
            if elems_to_erase <= 0:
                break

        choosed = choose(lens, elems_to_erase)

        delete_multiple_element(paths, choosed)

        print('Paths on iteration {}: {}'.format(i, len(paths)))

        if len(paths) == 0:
            break

        svg.wsvg(paths, attributes=attributes, filename='{}/pic_{}.svg'.format(output_dir, i))

        # Save it in png
        drawing = svg2rlg('{}/pic_{}.svg'.format(output_dir, i))
        renderPM.drawToFile(drawing, '{}/pic_{}.png'.format(output_dir, i), fmt='PNG')

        all_images.append(cv2.imread("{}/pic_{}.png".format(output_dir, i)))
        

    imgarray = (all_images, )
    stackImage = stackImages(1.0, imgarray)

    stackImage = cv2.rotate(stackImage, cv2.ROTATE_180)
    cv2.imwrite("{}/output.png".format(output_dir), stackImage)
