# Representative_Palette_Extraction_and_Image_Recoloring

这是[《代表性调色板提取及图像重着色》](https://www.jcad.cn/cn/article/doi/10.3724/SP.J.1089.2023.19430)的实现。

![image](https://github.com/XiaZixun/Representative_Palette_Extraction_and_Image_Recoloring/assets/116243141/3b1619b5-5114-4d1d-bbca-a2fbd5590710)


实现由两个部分组成，`palette_extractor`针对给定图像提取调色板，`Palette_Recolor_GUI`使用给定的图像以及对应调色板进行重着色。

## Palette_Extractor

这部分代码基于以下环境

```
python=2.7
Cython
scipy
scikit-image
pillow
trimesh
cvxopt
```

安装完成后，调用

`palette_meanshift_delaunay.py ./path/to/input_image ./path/to/convexhull_palette/dir ./path/to/representative_palette/dir`

即可得到代表性调色板。

## Palette_Recolor_GUI

这部分代码使用 `C++14`以及 `Qt5`完成，同时需要 `OpenCV`作为支持。

![image](https://github.com/XiaZixun/Representative_Palette_Extraction_and_Image_Recoloring/assets/116243141/8200c4f8-a415-4c45-b09b-b5ef65d23a36)
