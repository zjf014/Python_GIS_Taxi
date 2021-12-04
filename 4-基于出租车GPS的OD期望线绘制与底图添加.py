#!/usr/bin/env python
# coding: utf-8


# 导入必要的包
import pandas as pd
import numpy as np

# 绘制图用的包
import matplotlib as mpl
import matplotlib.pyplot as plt

# geopandas包
import geopandas

# shapely包
from shapely.geometry import Point, Polygon, shape

############# 读取基础数据

# 行政区划数据
# 读取shapefile文件
shp = r'shapefile\sz.shp'
xzqh = geopandas.GeoDataFrame.from_file(shp, encoding='utf-8')

# 绘制看看长什么样
xzqh.plot()
plt.show()

# 栅格数据
# 读取shapefile文件
shp = r'shapefile\grid\grid.shp'
grid = geopandas.GeoDataFrame.from_file(shp, encoding='gbk')

# 绘制看看长什么样
grid.plot()
plt.show()

# ## 栅格OD数据
# 这个数据是前面教程2中，用公式计算出来的OD
OD = pd.read_csv(r'data-sample\taxi_od_grid.csv')
OD.head(5)

# 我们现在要做的是，将栅格与行政区匹配，希望得到的是，在栅格信息的后面加一列，表示这个栅格属于哪个行政区划
# 在这里，我们考虑以栅格中心点落在哪个空间单元来判断，比如某栅格中心点落在宝安区，那么认为这个栅格是宝安区的栅格
# 因此，下一步我们定义一个geoDataFrame变量，命名为grid_point，存储的是栅格的中心点


grid_point = grid.copy()
# 我们相当于把geometry这一列的信息由polygon改成point
grid_point['geometry'] = grid.centroid

grid_point.plot()
plt.show()

grid_point.head(5)

################# 空间连接sjoin
# 连接到行政区划
grid_point = geopandas.sjoin(grid_point, xzqh, how="inner", op='intersects')
grid_point.head(5)

grid_point.plot()
plt.show()

# 只取我们要的列
grid_point = grid_point[['LONCOL', 'LATCOL', 'qh', 'centroid_x', 'centroid_y']]

# 把OD表的起点终点和grid_point表连接

# 重命名grid_point 并用 df.merge 把 OD 和 grid_point 表merge起来
# 只有当要合并的列在两个表中的名称相同时，merge方法才起作用
grid_point.columns = ['SLONCOL', 'SLATCOL', 'Sqh', 'S_x', 'S_y']
OD = pd.merge(OD, grid_point, on=['SLONCOL', 'SLATCOL'])
grid_point.columns = ['ELONCOL', 'ELATCOL', 'Eqh', 'E_x', 'E_y']
OD = pd.merge(OD, grid_point, on=['ELONCOL', 'ELATCOL'])

# 集计行政区划的OD
OD = OD.groupby(['Sqh', 'S_x', 'S_y', 'Eqh', 'E_x', 'E_y'])['VehicleNum'].sum().reset_index()

# 只保留跨行政区的出行，即Sqh与Eqh相等的就不要了
OD = OD[-(OD['Sqh'] == OD['Eqh'])]

# 画期望线的时候，我们希望小的先画，大的后画，这样大的OD就会在最上面
OD = OD.sort_values(by='VehicleNum')
OD.head(5)

# ## 开始画图

# 导入绘图包
import matplotlib as mpl
import matplotlib.pyplot as plt

fig = plt.figure(1, (10, 8), dpi=80)
ax = plt.subplot(111)
plt.sca(ax)

# 绘制行政区划
xzqh.plot(ax=ax, edgecolor=(0, 0, 0, 1), facecolor=(0, 0, 0, 0), linewidths=0.5)

# 设置colormap的数据
import matplotlib

vmax = OD['VehicleNum'].max()
# 设定一个标准化的工具，设定OD的colormap最大最小值，他的作用是norm(count)就会将count标准化到0-1的范围内
norm = mpl.colors.Normalize(vmin=0, vmax=vmax)
# 设定colormap的颜色
cmapname = 'autumn_r'
# cmap是一个获取颜色的工具，cmap(a)会返回颜色，其中a是0-1之间的值
cmap = matplotlib.cm.get_cmap(cmapname)

# 绘制OD
for i in range(len(OD)):
    # 设定第i条线的color和linewidth
    color_i = cmap(norm(OD['VehicleNum'].iloc[i]))
    linewidth_i = norm(OD['VehicleNum'].iloc[i]) * 5

    # 绘制
    plt.plot([OD['S_x'].iloc[i], OD['E_x'].iloc[i]], [OD['S_y'].iloc[i], OD['E_y'].iloc[i]], color=color_i,
             linewidth=linewidth_i)

# 不显示坐标轴
plt.axis('off')

# 绘制假的colorbar，这是因为，我们画的OD是线，没办法直接画出来colorbar
# 所以我们在一个看不见的地方画了一个叫imshow的东西，他的范围是0到vmax
# 然后我们再对imshow添加colorbar
plt.imshow([[0, vmax]], cmap=cmap)
# 设定colorbar的大小和位置
cax = plt.axes([0.08, 0.4, 0.02, 0.3])
plt.colorbar(cax=cax)

# 然后要把镜头调整回到深圳地图那，不然镜头就在imshow那里了

ax.set_xlim(113.6, 114.8)
ax.set_ylim(22.4, 22.9)

plt.show()

################# 用plot_map包绘制底图

# 只需要用以下代码：
# 
# >plot_map(plt,bounds,zoom = 9,style = 1)
# 
# 
# 可以通过更改函数plot map中的“style”和“styleid”来更改地图样式
# 
# 
# 
# >bounds——设置绘图边界[lon1，lat1，lon2，lat2]（wgs1984）  
# zoom——地图的缩放级别  
# style——从1到7表示不同的地图样式，1-6表示openstreetmap，7表示mapbox，样式3和4不需要token  
# styleid——如果style设置为7（来自mapbox），则可以在此处更改styleid，用“深色”或“浅色”或您自己的样式

# In[24]:


import plot_map

fig = plt.figure(1, (10, 8), dpi=80)
ax = plt.subplot(111)
plt.sca(ax)

bounds = [113.6, 22.4, 114.8, 22.9]
plot_map.plot_map(plt, bounds, zoom=12, style=4)

# 绘制行政区划
xzqh.plot(ax=ax, edgecolor=(0, 0, 0, 1), facecolor=(0, 0, 0, 0.2), linewidths=0.5)

# 设置colormap的数据
import matplotlib

vmax = OD['VehicleNum'].max()
norm = mpl.colors.Normalize(vmin=0, vmax=vmax)
cmapname = 'autumn_r'
cmap = matplotlib.cm.get_cmap(cmapname)

# 绘制OD
for i in range(len(OD)):
    color_i = cmap(norm(OD['VehicleNum'].iloc[i]))
    linewidth_i = norm(OD['VehicleNum'].iloc[i]) * 5
    plt.plot([OD['S_x'].iloc[i], OD['E_x'].iloc[i]], [OD['S_y'].iloc[i], OD['E_y'].iloc[i]], color=color_i,
             linewidth=linewidth_i)

# 不显示坐标轴
plt.axis('off')

# 添加colorbar
plt.imshow([[0, vmax]], cmap=cmap)
# 设定colorbar的大小和位置
cax = plt.axes([0.13, 0.32, 0.02, 0.3])
plt.colorbar(cax=cax)

ax.set_xlim(113.6, 114.8)
ax.set_ylim(22.4, 22.9)

plt.show()
