#!/usr/bin/env python
# coding: utf-8

import pandas as pd

# 读取数据
data = pd.read_csv(r'data-sample\TaxiData-Sample', header=None)
# 给数据命名列
data.columns = ['VehicleNum', 'Stime', 'Lng', 'Lat', 'OpenStatus', 'Speed']

# 筛选范围内数据
bounds = [113.7, 22.42, 114.3, 22.8]
data = data[
    (data['Lng'] > bounds[0]) & (data['Lng'] < bounds[2]) & (data['Lat'] > bounds[1]) & (data['Lat'] < bounds[3])]

# 经纬度小数点保留三位小数
data2 = data[['Lng', 'Lat']].round(3).copy()

# 集计每个小范围内数据量
data2['count'] = 1
data2 = data2.groupby(['Lng', 'Lat'])['count'].count().reset_index()

# 排序数据，让数据量小的放上面先画，数据大的放下面最后画
data2.sort_values(by='count')

data2.head(5)

# # 散点图绘制

bounds = [113.7, 22.42, 114.3, 22.8]

import matplotlib as mpl
import matplotlib.pyplot as plt
import plot_map
import seaborn as sns

fig = plt.figure(1, (8, 8), dpi=100)
ax = plt.subplot(111)
plt.sca(ax)
fig.tight_layout(rect=(0.05, 0.1, 1, 0.9))

import importlib

importlib.reload(plot_map)

# 背景
plot_map.plot_map(plt, bounds, zoom=12, style=4)

# colorbar
pallete_name = "BuPu"
colors = sns.color_palette(pallete_name, 3)
colors.reverse()
cmap = mpl.colors.LinearSegmentedColormap.from_list(pallete_name, colors)
vmax = data2['count'].quantile(0.99)
norm = mpl.colors.Normalize(vmin=0, vmax=vmax)

# plot scatters
plt.scatter(data2['Lng'], data2['Lat'], s=1, alpha=1, c=data2['count'], cmap=cmap, norm=norm)
plt.axis('off')
plt.xlim(bounds[0], bounds[2])
plt.ylim(bounds[1], bounds[3])

# 加比例尺和指北针
plot_map.plotscale(ax, bounds=bounds, textsize=10, compasssize=1, accuracy=2000, rect=[0.06, 0.03])

# 假的 colorbar
plt.imshow([[0, vmax]], cmap=cmap)
cax = plt.axes([0.13, 0.33, 0.02, 0.3])
plt.colorbar(cax=cax)

plt.show()
