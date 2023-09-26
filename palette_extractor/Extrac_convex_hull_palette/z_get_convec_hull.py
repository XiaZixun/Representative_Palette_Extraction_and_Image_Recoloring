import Additive_mixing_layers_extraction
import sys
from PIL import Image
import numpy as np

import os

if __name__=='__main__':
    src_image_path=str(sys.argv[1])
    convex_path=str(sys.argv[2])
    image_name=os.path.splitext(os.path.split(src_image_path)[1])[0]
    print image_name

    src_image=np.asarray(Image.open(src_image_path).convert("RGB"),dtype=np.float64)/255

    palette_rgb = Additive_mixing_layers_extraction.Hull_Simplification_determined_version(src_image,os.path.join(convex_path,image_name))