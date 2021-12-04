#!/usr/bin/env python
# coding: utf-8

import pandas as pd

# 读取数据
data = pd.read_csv(r'data-sample\TaxiData-Sample', header=None)
# 给数据命名列
data.columns = ['VehicleNum', 'Stime', 'Lng', 'Lat', 'OpenStatus', 'Speed']

# 筛选范围内数据
bounds = [113.7, 22.42, 114.3, 22.8]

# 筛选范围内的数据点
data = data[
    (data['Lng'] > bounds[0]) & (data['Lng'] < bounds[2]) & (data['Lat'] > bounds[1]) & (data['Lat'] < bounds[3])]
# 抽样
datasample = data.sample(10000)

# 经纬度小数点保留三位小数
data2 = data[['Lng', 'Lat']].round(3).copy()

# 集计每个小范围内数据量
data2['count'] = 1
data2 = data2.groupby(['Lng', 'Lat'])['count'].count().reset_index()

import scipy

scipy.__version__

# 导入绘图包
import matplotlib as mpl
import matplotlib.pyplot as plt
import plot_map
import seaborn as sns
import numpy as np


def heatmapplot(data, weight, gridsize=100, bw='scott', cmap=plt.cm.gist_earth_r, ax=None, **kwargs):
    # 数据整理
    from scipy import stats
    m1 = data[:, 0]
    m2 = data[:, 1]
    xmin = m1.min()
    xmax = m1.max()
    ymin = m2.min()
    ymax = m2.max()
    X, Y = np.mgrid[xmin:xmax:(xmax - xmin) / gridsize, ymin:ymax:(ymax - ymin) / gridsize]
    positions = np.vstack([X.ravel(), Y.ravel()])
    values = np.vstack([m1, m2])
    # 用scipy计算带权重的高斯kde
    kernel = stats.gaussian_kde(values, bw_method=bw, weights=weight)
    Z = np.reshape(kernel(positions).T, X.shape)
    # 绘制contourf
    cset = ax.contourf(Z.T, extent=[xmin, xmax, ymin, ymax], cmap=cmap, **kwargs)
    # 设置最底层为透明
    cset.collections[0].set_alpha(0)

    return cset


#   -- plot --
fig = plt.figure(1, (10, 10), dpi=60)
ax = plt.subplot(111)
plt.sca(ax)
fig.tight_layout(rect=(0.05, 0.1, 1, 0.9))  # 调整整体空白

# 绘制底图
plot_map.plot_map(plt, bounds, zoom=12, style=4)

# colorbar的数据
cmap = mpl.colors.LinearSegmentedColormap.from_list('cmap', ['#9DCC42', '#FFFE03', '#F7941D', '#E9420E', '#FF0000'],
                                                    256)

# 设定位置
plt.axis('off')
plt.xlim(bounds[0], bounds[2])
plt.ylim(bounds[1], bounds[3])

# 绘制热力图
cset = heatmapplot(data2.values,  # 输入经纬度数据
                   data2['count'],  # 输入每个点的权重
                   alpha=0.8,  # 透明度
                   gridsize=80,  # 绘图精细度，越高越慢
                   bw=0.03,  # 高斯核大小（经纬度），越小越精细
                   cmap=cmap,
                   ax=ax
                   )

# 定义colorbar位置
cax = plt.axes([0.13, 0.32, 0.02, 0.3])
plt.colorbar(cset, cax=cax)

plt.show()
