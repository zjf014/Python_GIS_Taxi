#!/usr/bin/env python
# coding: utf-8


########### 读取数据


# 读取GPS数据
import pandas as pd

data = pd.read_csv(r'data-sample/TaxiData-Sample', header=None)
data.columns = ['VehicleNum', 'Stime', 'Lng', 'Lat', 'OpenStatus', 'Speed']

# 读取OD数据
TaxiOD = pd.read_csv(r'data-sample/TaxiOD.csv')
TaxiOD.columns = ['VehicleNum', 'Stime', 'SLng', 'SLat',
                  'ELng', 'ELat', 'Etime']

# ########## 每小时GPS数据量绘图

# 我们要集计每小时的数据，那就需要有一列的内容表示数据哪个每小时，然后以那列数据为集计。因此这里我们对data的Stime列处理，得到该时间所属的小时，例如：
# 
# |Stime | |Hour |
# | ----------- |---|-----------|
# |22:54:04|→|22|


# 计时
import time
timeflag = time.time()

# 方法1：把时间当成字符串，用列自带的str方法，取前两位
data['Hour'] = data['Stime'].str.slice(0, 2)
# 计算耗时
print('方法1', time.time() - timeflag, 's')
##timeflag = time.time()
##
###方法2：把时间当成字符串，遍历取字符串前两位
##data['Hour'] = data['Stime'].apply(lambda r:r[:2])
###计算耗时
##print('方法2',time.time()-timeflag,'s')
##timeflag = time.time()
##
###方法3：转换为时间格式，后提取小时（非常慢）
##data['Hour'] = pd.to_datetime(data['Stime']).apply(lambda r:r.hour)
###计算耗时
##print('方法3',time.time()-timeflag,'s')
##timeflag = time.time()


# 集计每小时的数据量：


# 这个是对每一列都计数了，所以取其中一列出来，例如我这里取了['VehicleNum']
hourcount = data.groupby(data['Stime'].apply(lambda r: r[:2]))['VehicleNum'].count().reset_index()

# ## 开始绘图

# 第一部分：创建图
import matplotlib.pyplot as plt

# 创建一个图用plt.figure
# 其中fig你可以想象是整张图,ax是图上的其中一个小画板（一个大图可以有多个小画板）
# 而plt则是我们的画笔
fig = plt.figure(1, (8, 4))
ax = plt.subplot(111)
# 告诉画笔，我们要在ax上画图
plt.sca(ax)

# 第二部分：绘制
# 用plt.plot画折线
plt.plot(hourcount['Stime'], hourcount['VehicleNum'])

# 第三部分：调整

# 折线图调整颜色加上数据点
plt.plot(hourcount['Stime'], hourcount['VehicleNum'], 'k-', hourcount['Stime'], hourcount['VehicleNum'], 'k.')
# 加上条形图
plt.bar(hourcount['Stime'], hourcount['VehicleNum'], width=0.5)

plt.title('Hourly data Volume')

# 把y轴起点固定在0
plt.ylim(50000, 80000)
plt.ylabel('Data volumn')
plt.xlabel('Hour')
plt.show()

########### seaborn是基于matplotlib的另一个绘图包，它提供了一些绘图的主题画出来的图更好看一点，也对一些功能进行集合，很多用plt多行代码才能画出来的图它只需要一行。另外，我们可以用seaborn的主题来画matplotlib

# 加上seaborn的主题
import seaborn as sns

sns.set_style('darkgrid', {"xtick.major.size": 10, "ytick.major.size": 10})

plt.plot(hourcount['Stime'], hourcount['VehicleNum'], 'k-', hourcount['Stime'], hourcount['VehicleNum'], 'k.')

plt.title('Hourly data Volume')

plt.ylim(0, 80000)
plt.ylabel('Data Volume')
plt.xlabel('Hour')
plt.show()

########### 订单的持续时间箱型图

TaxiOD = TaxiOD[-TaxiOD['Etime'].isnull()]

# 计时
timeflag = time.time()
# 方法1：直接硬算
TaxiOD['order_time'] = TaxiOD['Etime'].str.slice(0, 2).astype('int') * 3600 + TaxiOD['Etime'].str.slice(3, 5).astype(
    'int') * 60 + TaxiOD['Etime'].str.slice(6, 8).astype('int') - TaxiOD['Stime'].str.slice(0, 2).astype('int') * 3600 - \
                       TaxiOD['Stime'].str.slice(3, 5).astype('int') * 60 - TaxiOD['Stime'].str.slice(6, 8).astype(
    'int')

# 计算耗时
print('方法1', time.time() - timeflag, 's')
##timeflag = time.time()
##
###方法2：转换为时间格式，相减后提取秒（非常慢）
##TaxiOD['order_time'] = (pd.to_datetime(TaxiOD['Etime'])-pd.to_datetime(TaxiOD['Stime']))
##TaxiOD['order_time'] = TaxiOD['order_time'].apply(lambda r:r.seconds)
##
###计算耗时
##print('方法2',time.time()-timeflag,'s')
##timeflag = time.time()


# 首先用plt.boxplot绘制全部数据分布的箱型图

plt.boxplot(TaxiOD['order_time'] / 60)

plt.ylabel('minutes')
plt.xlabel('order time')
plt.ylim(0, 60)
plt.show()

######## 这里，我想要制以每小时分组的订单时间分布


TaxiOD['Hour'] = TaxiOD['Stime'].str.slice(0, 2)

# 多分组的时候，plt的boxplot需要这样传入参数:
# >plt.boxplot([数据1,数据2,...])


# 整理数据
hour = TaxiOD['Hour'].drop_duplicates().sort_values()
datas = []
for i in range(len(hour)):
    datas.append(TaxiOD[TaxiOD['Hour'] == hour.iloc[i]]['order_time'] / 60)
# 绘制
plt.boxplot(datas)
# 更改x轴ticks的文字
plt.xticks(range(1, len(hour) + 1), list(hour))

plt.ylabel('Order time(minutes)')
plt.xlabel('Order start time')
plt.ylim(0, 60)

plt.show()

####### 用seaborn包绘制以每小时分组的订单时间分布，这时候我们只需要输入整个数据，就可以很方便的画出来

fig = plt.figure(1, (10, 5))
ax = plt.subplot(111)
plt.sca(ax)

order = list(set(TaxiOD['Hour']))
order.sort()
# 只需要一行
sns.boxplot(x="Hour", y=TaxiOD["order_time"] / 60, order=order, data=TaxiOD, ax=ax)
# sns.boxplot(x=TaxiOD['Hour'], y=TaxiOD["order_time"]/60, order=["Hour"], data=TaxiOD,ax = ax)

plt.ylabel('Order time(minutes)')
plt.xlabel('Order start time')
plt.ylim(0, 60)
plt.show()
