import numpy as np
from sklearn.cluster import MeanShift,estimate_bandwidth
from scipy.spatial import Delaunay
from PIL import Image

from Extrac_convex_hull_palette.Additive_mixing_layers_extraction import Hull_Simplification_determined_version

import sys
import os

def mean_shift(points):
    points=points.reshape((-1,3))
    radius=estimate_bandwidth(points,quantile=0.2,n_samples=512,n_jobs=-1)

    ms=MeanShift(bandwidth=radius,bin_seeding=True,n_jobs=-1).fit(points)
    centers=ms.cluster_centers_
    labels=ms.labels_
    _,cnt=np.unique(labels,return_counts=True)
    centers=centers[cnt>len(points)*0.03]
    return centers,radius

def read_cvx(cvx_path):
    with open(cvx_path,'r') as f:
        points=[]
        for line in f:
            elems=line.split()
            if elems[0]=="v":
                points.append(elems[1:])
        f.close()
        return np.array(points,dtype=np.float64)
    return None

def save_cvx_delaunay(cvx_path,points,tetras):
    with open(cvx_path,'w') as f:
        tris=tetras[:,np.array([[0,1,2],[0,1,3],[0,2,3],[1,2,3]])].reshape((-1,3))
        tris=np.sort(tris,axis=1)
        tris_unique,tris_cnt=np.unique(tris,return_counts=True,axis=0)
        surfs=tris_unique[tris_cnt==1]

        for p in points:
            f.write("v {} {} {}\n".format(p[0],p[1],p[2]))
        for s in surfs+1:
            f.write("f {} {} {}\n".format(s[0],s[1],s[2]))
        for t in tetras+1:
            f.write("t {} {} {} {}\n".format(t[0],t[1],t[2],t[3]))
        
        f.close()

def euclid_dist(a,b):
    return np.sqrt(np.sum((a-b)**2,axis=-1))

if __name__=='__main__':

    image_src_path,image_name=os.path.split(sys.argv[1])
    image_name,image_ext=os.path.splitext(image_name)
    cvx_src_path=sys.argv[2]
    cvx_delaunay_path=sys.argv[3]
    cvx_ext=".obj"

    image_src_path=os.path.join(image_src_path,image_name+image_ext)

    image_data=np.asarray(Image.open(image_src_path).convert("RGB"),dtype=np.float64)/255
    print image_data.shape
    print "read finish"
    
    Hull_Simplification_determined_version(image_data,os.path.join(cvx_src_path,image_name))
    cvx_vertices=read_cvx(os.path.join(cvx_src_path,image_name+cvx_ext))
    print "calculate simplify convex hull finish"

    cluster_vertices,radius=mean_shift(image_data)
    print "clustering finish"

    dis=np.array([[euclid_dist(i,j) for j in cvx_vertices] for i in cluster_vertices])
    dis=np.min(dis,axis=-1)
    cluster_vertices=cluster_vertices[dis>1.0*radius]
    vertices=np.concatenate((cvx_vertices,cluster_vertices),axis=0)
    print "vertices merge finish"
    
    tetras=Delaunay(vertices).simplices
    save_cvx_delaunay(os.path.join(cvx_delaunay_path,image_name+cvx_ext),vertices,tetras)
