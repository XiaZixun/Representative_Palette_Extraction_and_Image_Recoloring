import numpy as np
import numpy as np
from scipy.spatial import Delaunay
from PIL import Image

import sys
import os

def euclid_dist(a,b):
    return np.sqrt(np.sum((a-b)**2,axis=-1))

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

def farest_point_sample(k,points,anchor):
    n,k0=len(points),len(anchor)
    sample=[p for p in anchor]

    while len(sample)<k0+k and len(sample)<n:
        sample_cpy=np.tile(np.array(sample),(n,1,1))
        points_cpy=np.tile(points,(len(sample),1,1))
        points_cpy=points_cpy.transpose((1,0,2))

        dist=euclid_dist(points_cpy,sample_cpy)
        dist=np.min(dist,axis=1)

        sample.append(points[np.argmax(dist)])
    
    return np.array(sample)

def kmeans(k1,points,anchor):
    points=points.reshape((-1,3))
    n,k0=len(points),len(anchor)
    verts=farest_point_sample(k1,points,anchor)
    k=k0+k1
    eps=1e-6

    while True:
        verts_cpy=np.tile(verts,(n,1,1))
        points_cpy=np.tile(points,(k,1,1))
        points_cpy=points_cpy.transpose((1,0,2))

        dist=euclid_dist(points_cpy,verts_cpy)
        idx=np.argmin(dist,axis=1)

        max_shift=0
        for i in range(k0,k,1):
            cluster_points=points[idx==i]
            new_vert=np.sum(cluster_points,axis=0)/len(cluster_points)
            shift_dist=euclid_dist(verts[i],new_vert)
            max_shift=max(max_shift,shift_dist)
            verts[i]=new_vert
        print max_shift
        if max_shift<eps:
            break
        
    return verts

if __name__=='__main__':

    image_src_path,image_name=os.path.split(sys.argv[1])
    image_name,image_ext=os.path.splitext(image_name)
    cvx_src_path=sys.argv[2]
    cvx_delaunay_path=sys.argv[3]
    cvx_ext=".obj"

    image_src_path=os.path.join(image_src_path,image_name+image_ext)
    cvx_delaunay_path=os.path.join(cvx_delaunay_path,image_name+cvx_ext)

    image_data=np.asarray(Image.open(image_src_path).convert("RGB"),dtype=np.float64)/255
    print image_data.shape
    print "read finish"

    cvx_vertices=read_cvx(cvx_src_path)
    cluster_vertices=kmeans(2,image_data,cvx_vertices)
    print "cluster finish"
    
    tetras=Delaunay(cluster_vertices).simplices
    save_cvx_delaunay(cvx_delaunay_path,cluster_vertices,tetras)