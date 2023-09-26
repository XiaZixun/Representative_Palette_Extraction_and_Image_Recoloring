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



base_dir = "./data"

file_paths = [   
                "24-LasVegas"
             ]



def compute_rgb_convex_hull(img_data, cvx_path) : 
    start=time.time()
    palette_rgb = Additive_mixing_layers_extraction.Hull_Simplification_determined_version(img_data, cvx_path)
    end=time.time()    
    
    M=len(palette_rgb)
    print "palette size: ", M
    print "palette extraction time: ", end-start



# 运行 Jianchao 的算法，逐帧提取调色盘
if __name__ == '__main__':

    for x in range(0,1):
        index = x
        filepath= base_dir + "/raw_data/" + file_paths[index] + ".mp4"
        save_path = base_dir + "/convex_hull/" + file_paths[index]


        k = 0
        all_imgs = []

        reader = FFmpegReader(filepath)
        for img in reader.nextFrame():
            img_data_path = save_path + "/%05d" % k
            Image.fromarray(img).save(img_data_path+".png")
            np.save(img_data_path + ".img.npz", img)

            img = img / 255.0
            all_imgs.append(img)

            k = k + 1


        k = 0
        while k < len(all_imgs):
            threads = []
            
            img_data = all_imgs[k]
            img_data = img_data[::2,::2,:]    
            convexhull_path = save_path + "/rgb_cvx_%05d" % k
            
            t1 = threading.Thread(target=compute_rgb_convex_hull,args = (img_data,convexhull_path))
            threads.append(t1)
            
            k = k + 1
            
            if k < len(all_imgs):
                img_data = all_imgs[k]
                img_data = img_data[::2,::2,:]
                convexhull_path = save_path + "/rgb_cvx_%05d" % k
                
                t2 = threading.Thread(target=compute_rgb_convex_hull,args = (img_data,convexhull_path))
                threads.append(t2)
                
            
            k = k + 1
            
            if k < len(all_imgs):
                img_data = all_imgs[k]
                img_data = img_data[::2,::2,:]
                convexhull_path = save_path + "/rgb_cvx_%05d" % k
                
                t3 = threading.Thread(target=compute_rgb_convex_hull,args = (img_data,convexhull_path))
                threads.append(t3)
                
            k = k + 1
            
            
            for t in threads:
                t.setDaemon(True)
                t.start()
                
            for t in threads:
                t.join()

    print("finish!")



# 运行 Jianchao 的算法，逐帧提取调色盘
# from imgs

for k in range(8,11):

    save_path = base_dir + "/convex_hull_copyrights/" + file_paths[k]

    for i in range(50):
        
        filename = base_dir + "/raw_data_copyrights/" + file_paths[k] + "/%05d.png" % i

        print(filename)
        img = Image.open(filename)
        img = np.asarray(img)


        img_data_path = save_path + "/%05d" % i
        print(img_data_path+".png")
        Image.fromarray(img).save(img_data_path+".png")
        print(img_data_path)
        np.save(img_data_path + ".img.npz", img)

        img=img/255.0
        #print(img)
        arr=img.copy()
        X,Y=np.mgrid[0:img.shape[0], 0:img.shape[1]]
        XY=np.dstack((X*1.0/img.shape[0],Y*1.0/img.shape[1]))
        data=np.dstack((img, XY))
        print len(data.reshape((-1,5)))


        convexhull_path = save_path + '/rgb_cvx_%05d'% i

        start=time.time()
        #palette_rgb=Additive_mixing_layers_extraction.Hull_Simplification_determined_version(img, filepath[:-4]+"-convexhull_vertices")
        palette_rgb=Additive_mixing_layers_extraction.Hull_Simplification_determined_version(img, convexhull_path)
        end=time.time()    
        M=len(palette_rgb)
        print "palette size: ", M
        print "palette extraction time: ", end-start

    
print("finish!")


# In[ ]:




