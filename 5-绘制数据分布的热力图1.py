#!/usr/bin/env python
# coding: utf-8

import pandas as pd

# 读取数据
data = pd.read_csv(r'data-sample\TaxiData-Sample', header=None)
# 给数据命名列
data.columns = ['VehicleNum', 'Stime', 'Lng', 'Lat', 'OpenStatus', 'Speed']
# 筛选范围内数据
bounds = [113.7, 22.42, 114.3, 22.8]

# # 热力图绘制(seaborn-kdeplot)

# seaborn-kdeplot也是绘制热力图的一种方式，但是这种方式缺点有以下几个：
# 1.由于kdeplot绘制不支持为数据点加权重，无法用先集计后绘制的方法，只能输入整个数据集绘制，如果数据量大，绘制速度极慢  
# 2.绘制的依据为进行核密度估计后的值，这一值是抽象的只能显示相对关系，无法对应实际的物理意义  
# 3.核密度会导致绘图精度丢失，你只能看到一坨东西在那

# [seaborn.kdeplot中文文档](https://www.cntofu.com/book/172/docs/25.md)


# 筛选范围内的数据点
data = data[
    (data['Lng'] > bounds[0]) & (data['Lng'] < bounds[2]) & (data['Lat'] > bounds[1]) & (data['Lat'] < bounds[3])]
# 抽样
datasample = data.sample(10000)

# 导入绘图包
import matplotlib as mpl
import matplotlib.pyplot as plt
import plot_map
import seaborn as sns
import numpy as np

#   -- plot --
fig = plt.figure(1, (10, 10), dpi=60)
ax = plt.subplot(111)
plt.sca(ax)
fig.tight_layout(rect=(0.05, 0.1, 1, 0.9))  # 调整整体空白

# 绘制底图
plot_map.plot_map(plt, bounds, zoom=12, style=4)

# colorbar的数据
import matplotlib

cmap = matplotlib.colors.LinearSegmentedColormap.from_list('cmap',
                                                           ['#9DCC42', '#FFFE03', '#F7941D', '#E9420E', '#FF0000'], 256)

plt.axis('off')
plt.xlim(bounds[0], bounds[2])
plt.ylim(bounds[1], bounds[3])

# 定义colorbar位置
cax = plt.axes([0.13, 0.32, 0.02, 0.3])
# 绘制热力图
sns.kdeplot(datasample['Lng'], datasample['Lat'],
            alpha=0.8,  # 透明度
            gridsize=100,  # 绘图精细度，越高越慢
            bw=0.03,  # 高斯核大小（经纬度），越小越精细
            shade=True,
            shade_lowest=False,
            cbar=True,
            cmap=cmap,
            ax=ax,  # 指定绘图位置
            cbar_ax=cax  # 指定colorbar位置
            )

plt.show()
