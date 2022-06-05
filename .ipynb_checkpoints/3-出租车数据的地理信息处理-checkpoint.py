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

###########读取shapefile文件
shp = r'shapefile/sz.shp'

# geopandas的格式，就是类似pandas的表格，但是加上一列geometry，记录了每行记录的地理信息
sz = geopandas.GeoDataFrame.from_file(shp, encoding='utf-8')

# 绘制看看长什么样
sz.plot()
plt.show()

sz.head()

# 每行记录的geometry，它的格式是shapely包的Polygon
sz['geometry'].iloc[0]

# 用unary_union可以将一个geopandas的所有记录合并为一个图形，合并出来的结果是Polygon
sz.unary_union

################ 栅格化

# 我们需要写一个代码，能够直接批量算出来一批经纬度的栅格编号

import math

# 划定栅格划分范围
lon1 = 113.75194
lon2 = 114.624187
lat1 = 22.447837
lat2 = 22.864748

latStart = min(lat1, lat2);
lonStart = min(lon1, lon2);

# 定义栅格大小(单位m)
accuracy = 500;

# 计算栅格的经纬度增加量大小▲Lon和▲Lat
deltaLon = accuracy * 360 / (2 * math.pi * 6371004 * math.cos((lat1 + lat2) * math.pi / 360));
deltaLat = accuracy * 360 / (2 * math.pi * 6371004);

# 定义一个测试栅格化的经纬度
testlon = 114
testlat = 22.5

# 计算栅格的经纬度编号
LONCOL = divmod(float(testlon) - (lonStart - deltaLon / 2), deltaLon)[0]
LATCOL = divmod(float(testlat) - (latStart - deltaLat / 2), deltaLat)[0]

# 计算栅格的中心点经纬度
HBLON = LONCOL * deltaLon + (lonStart - deltaLon / 2)  # 格子编号*格子宽+起始横坐标-半个格子宽=格子中心横坐标
HBLAT = LATCOL * deltaLat + (latStart - deltaLat / 2)

# 把算好的东西print出来看看
LONCOL, LATCOL, HBLON, HBLAT, deltaLon, deltaLat

# 另外，我们要生成这些栅格的geopandas数据

from shapely.geometry import Point, Polygon, shape

Polygon([(HBLON + deltaLon / 2, HBLAT - deltaLat / 2),
         (HBLON + deltaLon / 2, HBLAT + deltaLat / 2),
         (HBLON - deltaLon / 2, HBLAT + deltaLat / 2),
         (HBLON - deltaLon / 2, HBLAT - deltaLat / 2)])

# 定义空的geopandas表
data = geopandas.GeoDataFrame()

# 定义空的list，后面循环一次就往里面加东西
LONCOL = []
LATCOL = []
geometry = []
HBLON1 = []
HBLAT1 = []

# 计算总共要生成多少个栅格
# lon方向是lonsnum个栅格
lonsnum = int((lon2 - lon1) / deltaLon) + 1
# lat方向是latsnum个栅格
latsnum = int((lat2 - lat1) / deltaLat) + 1

for i in range(lonsnum):
    for j in range(latsnum):
        HBLON = i * deltaLon + (lonStart - deltaLon / 2)
        HBLAT = j * deltaLat + (latStart - deltaLat / 2)
        # 把生成的数据都加入到前面定义的空list里面
        LONCOL.append(i)
        LATCOL.append(j)
        HBLON1.append(HBLON)
        HBLAT1.append(HBLAT)

        # 生成栅格的Polygon形状
        # 这里我们用周围的栅格推算三个顶点的位置，否则生成的栅格因为小数点取值的问题会出现小缝，无法完美覆盖
        HBLON_1 = (i + 1) * deltaLon + (lonStart - deltaLon / 2)
        HBLAT_1 = (j + 1) * deltaLat + (latStart - deltaLat / 2)
        geometry.append(Polygon([
            (HBLON - deltaLon / 2, HBLAT - deltaLat / 2),
            (HBLON_1 - deltaLon / 2, HBLAT - deltaLat / 2),
            (HBLON_1 - deltaLon / 2, HBLAT_1 - deltaLat / 2),
            (HBLON - deltaLon / 2, HBLAT_1 - deltaLat / 2)]))

# 为geopandas文件的每一列赋值为刚刚的list
data['LONCOL'] = LONCOL
data['LATCOL'] = LATCOL
data['HBLON'] = HBLON1
data['HBLAT'] = HBLAT1
data['geometry'] = geometry

data.plot()
plt.show()

data.head(5)

################ 取栅格和深圳行政区划的交集栅格
grid = data[data.intersects(sz.unary_union)]
grid.plot()
plt.show()

# 保存
grid.to_file(r'shapefile\grid', encoding='utf-8')

################ 将数据对应到栅格

TaxiOD = pd.read_csv(r'data-sample/TaxiOD.csv')
TaxiOD.columns = ['VehicleNum', 'Stime', 'SLng', 'SLat',
                  'ELng', 'ELat', 'Etime']
TaxiOD.head(5)

TaxiOD = TaxiOD[-TaxiOD['ELng'].isnull()].copy()
TaxiOD['SLONCOL'] = ((TaxiOD['SLng'] - (lonStart - deltaLon / 2)) / deltaLon).astype('int')
TaxiOD['SLATCOL'] = ((TaxiOD['SLat'] - (latStart - deltaLat / 2)) / deltaLat).astype('int')
TaxiOD['SHBLON'] = TaxiOD['SLONCOL'] * deltaLon + (lonStart - deltaLon / 2)
TaxiOD['SHBLAT'] = TaxiOD['SLATCOL'] * deltaLat + (latStart - deltaLat / 2)
TaxiOD['ELONCOL'] = ((TaxiOD['ELng'] - (lonStart - deltaLon / 2)) / deltaLon).astype('int')
TaxiOD['ELATCOL'] = ((TaxiOD['ELat'] - (latStart - deltaLat / 2)) / deltaLat).astype('int')
TaxiOD['EHBLON'] = TaxiOD['ELONCOL'] * deltaLon + (lonStart - deltaLon / 2)
TaxiOD['EHBLAT'] = TaxiOD['ELATCOL'] * deltaLat + (latStart - deltaLat / 2)

# 筛选去掉起点终点在同一个格子里的OD
TaxiOD = TaxiOD[-((TaxiOD['SLONCOL'] == TaxiOD['ELONCOL']) & (TaxiOD['SLATCOL'] == TaxiOD['ELATCOL']))]
# 筛选去掉不在研究范围内的栅格
TaxiOD = TaxiOD[
    (TaxiOD['SLONCOL'] >= 0) & (TaxiOD['SLATCOL'] >= 0) & (TaxiOD['ELONCOL'] >= 0) & (TaxiOD['ELATCOL'] >= 0) &
    (TaxiOD['SLONCOL'] <= lonsnum) & (TaxiOD['SLATCOL'] <= latsnum) & (TaxiOD['ELONCOL'] <= lonsnum) & (
                TaxiOD['ELATCOL'] <= latsnum)]

TaxiOD.head(5)

################# 集计栅格OD（全天、高峰时段）

# 这个是对每一列都计数了，所以取其中一列出来，例如我这里取了['VehicleNum']
OD = TaxiOD.groupby(['SLONCOL', 'SLATCOL', 'ELONCOL', 'ELATCOL'])['VehicleNum'].count().reset_index()
# 注意：VehicleNum变量在这里groupby了以后，这个字段就变成了计数count数量，不再是车牌号了

# OD按大小排序
OD = OD.sort_values(by='VehicleNum', ascending=False)

################## 绘制栅格的OD图

# 取前200的OD
Topod = OD.iloc[:200].copy()
# Topod = OD.iloc[:].copy()

# 计算起点栅格的中心点经纬度
Topod['SHBLON'] = Topod['SLONCOL'] * deltaLon + (lonStart - deltaLon / 2)
Topod['SHBLAT'] = Topod['SLATCOL'] * deltaLat + (latStart - deltaLat / 2)

# 计算终点栅格的中心点经纬度
Topod['EHBLON'] = Topod['ELONCOL'] * deltaLon + (lonStart - deltaLon / 2)
Topod['EHBLAT'] = Topod['ELATCOL'] * deltaLat + (latStart - deltaLat / 2)

fig = plt.figure(1, (10, 8), dpi=80)
ax = plt.subplot(111)
plt.sca(ax)

# 把刚才生成的栅格在ax上绘制
grid.plot(ax=ax, edgecolor=(0, 0, 0, 0.8), facecolor=(0, 0, 0, 0), linewidths=0.2)

# 把合并的行政区划变成一个geopandas，在ax上绘制
SZ_all = geopandas.GeoDataFrame()
SZ_all['geometry'] = [sz.unary_union]
SZ_all.plot(ax=ax, edgecolor=(0, 0, 0, 1), facecolor=(0, 0, 0, 0), linewidths=0.5)

for i in range(len(Topod)):
    plt.plot([Topod['SHBLON'].iloc[i], Topod['EHBLON'].iloc[i]], [Topod['SHBLAT'].iloc[i], Topod['EHBLAT'].iloc[i]])

# 不显示坐标轴
plt.axis('off')

plt.show()

############################################# 绘制全部的OD

# 我们还是把多一点OD画出来吧，这个时候我们要用OD的粗细，颜色深度，和透明度，来表示OD量大小


OD1 = OD[OD['VehicleNum'] > 10].copy()

# OD从小到大排序方便我们后续操作，因为我们希望小的OD先画，放在最底下，大的OD后画，放在最上面
OD1 = OD1.sort_values(by='VehicleNum')

# 计算起点栅格的中心点经纬度
OD1['SHBLON'] = OD1['SLONCOL'] * deltaLon + (lonStart - deltaLon / 2)
OD1['SHBLAT'] = OD1['SLATCOL'] * deltaLat + (latStart - deltaLat / 2)

# 计算终点栅格的中心点经纬度
OD1['EHBLON'] = OD1['ELONCOL'] * deltaLon + (lonStart - deltaLon / 2)
OD1['EHBLAT'] = OD1['ELATCOL'] * deltaLat + (latStart - deltaLat / 2)

# 对OD分5组，生成一个取值为0-1的列，每组的值相同，用以表示OD的粗细，取名linewidth
step = 5
OD1['linewidth'] = (np.array(range(len(OD1))) * step / len(OD1)).astype('int') / step + 0.1
OD1.head(5)

fig = plt.figure(1, (10, 8), dpi=80)
ax = plt.subplot(111)
plt.sca(ax)

# 把刚才生成的栅格在ax上绘制
grid.plot(ax=ax, edgecolor=(0, 0, 0, 0.8), facecolor=(0, 0, 0, 0), linewidths=0.2)

# 绘制整个深圳的范围
SZ_all.plot(ax=ax, edgecolor=(0, 0, 0, 1), facecolor=(0, 0, 0, 0), linewidths=0.5)

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
import time

timeflag = time.time()
for i in range(len(OD1)):
    plt.plot([OD1['SHBLON'].iloc[i], OD1['EHBLON'].iloc[i]], [OD1['SHBLAT'].iloc[i], OD1['EHBLAT'].iloc[i]],
             color=cmap(i / len(OD1)))

print('绘制OD用时', time.time() - timeflag, '秒')

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

##################### 更快的绘制方法

# 如果遍历绘制OD，绘制速度比较慢。  
# 但是，如果把DataFrame变成GeoDataFrame，然后用自带的plot函数绘制，会快很多

# 生成geometry
# 把DataFrame变成GeoDataFrame
# 对每一行生成线的geometry
from shapely.geometry import LineString

OD1['geometry'] = OD1.apply(lambda r: LineString([[r['SHBLON'], r['SHBLAT']], [r['EHBLON'], r['EHBLAT']]]), axis=1)
OD1 = geopandas.GeoDataFrame(OD1)

OD1.head(5)

fig = plt.figure(1, (10, 8), dpi=80)
ax = plt.subplot(111)
plt.sca(ax)

# 计时
import time

timeflag = time.time()
# 绘制底图
grid.plot(ax=ax, edgecolor=(0, 0, 0, 0.8), facecolor=(0, 0, 0, 0), linewidths=0.2)
SZ_all.plot(ax=ax, edgecolor=(0, 0, 0, 1), facecolor=(0, 0, 0, 0), linewidths=0.5)
print('绘制底图用时', time.time() - timeflag, '秒')

# 设置colormap的数据
vmax = OD['VehicleNum'].max()
cmapname = 'autumn_r'
cmap = matplotlib.cm.get_cmap(cmapname)

timeflag = time.time()
# 绘制OD
OD1.plot(ax=ax, column='VehicleNum', vmax=vmax, vmin=0, cmap=cmap, linewidth=OD1['linewidth'])
print('绘制OD用时', time.time() - timeflag, '秒')

plt.axis('off')
plt.imshow([[0, vmax]], cmap=cmap)
cax = plt.axes([0.08, 0.4, 0.02, 0.3])
plt.colorbar(cax=cax)
ax.set_xlim(113.6, 114.8)
ax.set_ylim(22.4, 22.9)
plt.show()

###################### 绘制起点的分布图

# 集计
Odistribution = OD.groupby(['SLONCOL', 'SLATCOL'])['VehicleNum'].sum().reset_index()

# 将集计的结果与栅格的geopandas执行merge操作
gridtoplot = pd.merge(grid, Odistribution.rename(columns={'SLONCOL': 'LONCOL', 'SLATCOL': 'LATCOL'}),
                      on=['LONCOL', 'LATCOL'])
gridtoplot = gridtoplot.rename(columns={'VehicleNum': 'count'})

fig = plt.figure(1, (10, 8), dpi=80)
ax = plt.subplot(111)
plt.sca(ax)

# 设置colormap的数据
vmax = gridtoplot['count'].max()
# 设定一个标准化的工具，设定OD的colormap最大最小值，他的作用是norm(count)就会将count标准化到0-1的范围内
norm = mpl.colors.Normalize(vmin=0, vmax=vmax)
# 设定colormap的颜色
cmapname = 'autumn_r'
# cmap是一个获取颜色的工具，cmap(a)会返回颜色，其中a是0-1之间的值
cmap = matplotlib.cm.get_cmap(cmapname)

# 将gridtoplot这个geodataframe进行绘制
# 提示：用gridtoplot.plot，设定里面的参数是column = 'count'，以count这一列来绘制。参数cmap = cmap设定它的颜色
gridtoplot.plot(ax=ax, column='count', vmax=vmax, vmin=0, cmap=cmap)

# 绘制整个深圳的范围
SZ_all.plot(ax=ax, edgecolor=(0, 0, 0, 1), facecolor=(0, 0, 0, 0), linewidths=0.5)

# 不显示坐标轴
plt.axis('off')

# 绘制假的colorbar，这是因为，我们画的OD是线，没办法直接画出来colorbar
# 所以我们在一个看不见的地方画了一个叫imshow的东西，他的范围是0到vmax
# 然后我们再对imshow添加colorbar
plt.imshow([[0, vmax]], cmap=cmap)
# 设定colorbar的大小和位置
cax = plt.axes([0.08, 0.4, 0.02, 0.3])
plt.colorbar(cax=cax)

ax.set_xlim(113.6, 114.8)
ax.set_ylim(22.4, 22.9)

plt.show()
