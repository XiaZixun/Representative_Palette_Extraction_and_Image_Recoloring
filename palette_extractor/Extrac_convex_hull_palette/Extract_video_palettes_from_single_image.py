#!/usr/bin/env python
# coding: utf-8

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


# def compute_rgb_convex_hull(file_name, cvx_path) : 

if __name__ == '__main__':
	file_name = sys.argv[1]
	cvx_path = sys.argv[2]

	img = Image.open(filename)
    img = np.asarray(img)
    img = img / 255.0

    start=time.time()
    palette_rgb = Additive_mixing_layers_extraction.Hull_Simplification_determined_version(img_data, cvx_path)
    end=time.time()    
    
    M=len(palette_rgb)
    print "palette size: ", M
    print "palette extraction time: ", end-start