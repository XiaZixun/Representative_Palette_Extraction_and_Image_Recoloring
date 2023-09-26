#!/usr/bin/env python
# coding: utf-8

# In[1]:


from skvideo.io import FFmpegReader
import PIL.Image as Image
import time
import scipy
import json
import Additive_mixing_layers_extraction
from scipy.spatial import ConvexHull, Delaunay
import scipy.sparse
import PIL.Image as Image
import RGBXY_method
import numpy as np
from numpy import *
Additive_mixing_layers_extraction.DEMO=True
import threading
import os,os.path
import sys


base_dir = "./data"

file_paths = [
                "",
                "1-Brand-150",
				"2-Chicago-140",
				"3-Dubrovnik-176",
				"4-Forest-146",
				"5-Lake-118",
				"6-Mosque-145",
				"7-sunset-189",
				"8-Tokyo-187",
				"9-Bloom-123",
				"10-Water-150",
				"11-Season-143",
				"12-Light-103",
				"13-Dubai-133",
				"14-MusicHall-232",
				"15-Cloud-190",
				"16-Mountain-186",
				"17-Playground-114",

             ]

def GetPngCnt(dir):
    number = 0
    for root,dirname,filenames in os.walk(dir):
       for filename in filenames:
            if os.path.splitext(filename)[1]=='.png':
                #print(filename)
                number += 1
    return number

def compute_rgb_convex_hull(img_data, cvx_path) :
    start=time.time()
    palette_rgb = Additive_mixing_layers_extraction.Hull_Simplification_determined_version(img_data, cvx_path)
    end=time.time()

    M=len(palette_rgb)
    print("palette size: ", M)
    print("palette extraction time: ", end-start)


if __name__ == '__main__':

    start = int(sys.argv[1])
    end = int(sys.argv[2])

    for k in range(start,end+1):
        save_path = base_dir + "/convex_hull/" + file_paths[k]
        if os.path.exists(save_path) == False:
            os.makedirs(save_path)

        src_path = base_dir + "/raw_data/" + file_paths[k]

        img_cnt = GetPngCnt(src_path)

        all_imgs = []
        for i in range(1,img_cnt):

            filename = src_path + "/%05d.png" % i
            img = Image.open(filename)
            img = np.asarray(img)

            img_data_path = save_path + "/%05d" % i
            #Image.fromarray(img).save(img_data_path+".png")
            np.save(img_data_path + ".img.npz", img)

            img = img/255.0
            all_imgs.append(img)


        j = 125
        while j < len(all_imgs):
            threads = []
            scale = 1
            img_data = all_imgs[j]
            img_data = img_data[::scale,::scale,:]
            convexhull_path = save_path + "/rgb_cvx_%05d" % j

            t1 = threading.Thread(target=compute_rgb_convex_hull,args = (img_data,convexhull_path))
            threads.append(t1)

            j = j + 1
            if j < len(all_imgs):
                img_data = all_imgs[k]
                img_data = img_data[::scale,::scale,:]
                convexhull_path = save_path + "/rgb_cvx_%05d" % j

                t2 = threading.Thread(target=compute_rgb_convex_hull,args = (img_data,convexhull_path))
                threads.append(t2)


            j = j + 1
            if j < len(all_imgs):
                img_data = all_imgs[k]
                img_data = img_data[::scale,::scale,:]
                convexhull_path = save_path + "/rgb_cvx_%05d" % j

                t3 = threading.Thread(target=compute_rgb_convex_hull,args = (img_data,convexhull_path))
                threads.append(t3)


            j = j + 1
            if j < len(all_imgs):
                img_data = all_imgs[k]
                img_data = img_data[::scale,::scale,:]
                convexhull_path = save_path + "/rgb_cvx_%05d" % j

                t3 = threading.Thread(target=compute_rgb_convex_hull,args = (img_data,convexhull_path))
                threads.append(t3)


            for t in threads:
                t.setDaemon(True)
                t.start()

            for t in threads:
                t.join()

        print("finish!")