#!/usr/bin/env python
# coding: utf-8

# 在这个教程中，你将会学到如何使用python的pandas包对出租车GPS数据进行数据清洗，识别出行OD
# 出租车原始GPS数据(在data-sample文件夹下，原始数据集的抽样500辆车的数据)

import pandas as pd

data = pd.read_csv(r'data-sample/TaxiData-Sample', header=None)  # 读取数据
data.columns = ['VehicleNum', 'Stime', 'Lng', 'Lat', 'OpenStatus', 'Speed']  # 给数据命名列

# 数据的格式：
# 
# VehicleNum —— 车牌  
# Stime —— 时间  
# Lng —— 经度  
# Lat —— 纬度  
# OpenStatus —— 是否有乘客(0没乘客，1有乘客)  
# Speed —— 速度  

# 显示数据的前5行
data.head(5)

# ############ 基础的数据操作

# ## DataFrame和Series

# DataFrame和Series
# 
#   当我们读一个数据的时候，我们读进来的就是DataFrame格式的数据表，而一个DataFrame中的每一列，则为一个Series  
#   也就是说，DataFrame由多个Series组成
# 

type(data)

# 如果我们想取DataFrame的某一列，想得到的是Series，那么直接用以下代码

data['Lng']

# 如果我们想取DataFrame的某一列或者某几列，想得到的是DataFrame，那么直接用以下代码

data[['Lng', 'Lat']]

# 得到车牌照为22271的所有数据
(data['VehicleNum'] == 22271).head(5)

data[data['VehicleNum'] == 22271].head(5)

# 删除车牌照为22271的所有数据
data[-(data['VehicleNum'] == 22271)].head(5)

# 获取列'Stime',注意，此操作不会影响到data，你在操作后必须将得到的表重新赋值给data才有影响
data[['Stime']].head(5)

# 定义列'Speed1'为Speed列的两倍,注意，此操作会影响到data
data['Speed1'] = data['Speed'] * 2
# 或者
data.loc[:, 'Speed1'] = data['Speed'] * 2

data.head(5)

# 删除列'Speed1',axis=1表示对列进行删除。注意，此操作不会影响到data，你在操作后必须将得到的表重新赋值给data才有影响
data = data.drop(['Speed1'], axis=1)
data.head(5)

# 获取Stime列的第4行数据
data['Stime'].iloc[3]

# ################## 数据清洗

# 首先，我们将数据按车牌、时间排序，特别要注意，data排序后需要再赋值给data，否则没作用
# 将数据排序,并把排序后的数据赋值给原来的数据
data = data.sort_values(by=['VehicleNum', 'Stime'])
data.head(5)

# 我们现在要做的是，用出租车GPS数据识别OD：
# 数据按车牌、时间排序后，正常情况下的OpenStatus是这样的：
# 
# |OpenStatus |  |
# | :-----------: |-----------|
# |0||
# |0||
# |0||
# |0||
# |0||
# |1|←此时乘客上车了|
# |1||
# |1||
# |1||
# |1||
# |1||
# |1||
# |0|     ←此时乘客下车了|
# |0||
# |0||
# |0||
# 
# 但是，也会有时候有数据异常出现，比如：
# 
# |OpenStatus |  |
# | ----------- |-----------|
# |0||
# |0||
# |0||
# |0||
# |0||
# |1|←异常|
# |0||
# |0||
# |0||
# |0||
# 
# 或者
# 
# |OpenStatus |  |
# | ----------- |-----------|
# |1||
# |1||
# |1||
# |1||
# |1||
# |0|←异常|
# |1||
# |1||
# |1||
# |1||
# 
# 前后都是0，突然有一条数据变成1，或者前后都是1，突然变成0。这种异常情况我们是要排除的

# 在pandas的数据处理过程中，我们筛掉不要的数据用下面的方法是最好的
# 
#     data[条件]是保留符合条件的数据  
#     data[-(条件)]是删除符合条件的数据

#     Series的shift()函数能够将数据按顺序后移一位
#     Series的shift(-1)函数能够将数据按顺序前移一位
#     因此我们要判断的是，如果：
#     后一位和前一位相等，但是后一位与中间一位不等，那么中间一位的数据就要删除（前一条数据，中间一条数据，后一条数据的车牌必须相等）
#     


# 筛选前的数据量
len(data)

# 这里，把上述异常数据清洗出来
# 用到的条件是：
# 1.后一位和前一位相等
# 2.但是后一位与中间一位不等
# 3.前一条数据，后一条数据的车牌相等
# 4.中间一条数据，后一条数据的车牌相等

data = data[-((data['OpenStatus'].shift(-1) == data['OpenStatus'].shift()) &
              (data['OpenStatus'].shift(-1) != data['OpenStatus']) &
              (data['VehicleNum'].shift(-1) == data['VehicleNum'].shift()) &
              (data['VehicleNum'].shift(-1) == data['VehicleNum']))]

# 如果你代码对的话，筛选完了data的数据量应该是
len(data)

# ########### 乘客上下车的状态变化识别

# 接下来，我们把下一条数据的信息放到前一条数据上，这样子，就能很方便的比较这条数据和下条数据的差异
# 在字段名加个1，代表后面一条数据的值
# 另外我们定义StatusChange为下一条数据的OpenStatus减去这一条数据的OpenStatus，这样就会出现：

# 
# |OpenStatus     |   OpenStatus1    |  StatusChange||
# | ----------- |-----------|||
# |0          |       0    |             0||
# |0          |       0    |             0||
# |0         |        0    |             0||
# |0          |       1    |             1 |    ←此时乘客上车了|
# |1          |       1    |             0  |   ←此时乘客上车了|
# |1          |       1    |             0||
# |1          |       1    |             0||
# |1          |       1    |             0||
# |1          |       1    |             0||
# |1          |       1    |             0||
# |1          |       1    |             0||
# |1          |       1    |             0||
# |1          |       1    |             0||
# |1          |       0    |             -1|    ←此时乘客下车了|
# |0          |       0    |             0  |  ←此时乘客下车了|
# |0          |       0    |             0||
# |0          |       0    |             0||
# |0          |       0    |             0||
# 

# 让这几个字段的下一条数据赋值给新的字段，在字段名加个1，代表后面一条数据的值
data.loc[:, 'OpenStatus1'] = data['OpenStatus'].shift(-1)
data.loc[:, 'VehicleNum1'] = data['VehicleNum'].shift(-1)
# data.loc[:, 'Lng1'] = data['Lng'].shift(-1)
# data.loc[:, 'Lat1'] = data['Lat'].shift(-1)
# data.loc[:, 'Stime1'] = data['Stime'].shift(-1)

data.loc[:, 'StatusChange'] = data['OpenStatus1'] - data['OpenStatus']

# ## 将上下车状态整理为OD

#     这里，我只想保留StatusChange字段为1或者-1的数据，因此要把这些数据筛出来
#     不过，还得加一个条件，就是这条数据和下一条数据的车辆ID必须是相同的

data = data[((data['StatusChange'] == 1) | (data['StatusChange'] == -1))
            & (data['VehicleNum'] == data['VehicleNum1'])]

# data数据只保留一些我们需要的字段
data = data[['VehicleNum', 'Stime', 'Lng', 'Lat', 'StatusChange']]
data.head(5)

#     我们现在就得到了乘客哪里上车，哪里下车。
#     而我们想要得到的OD数据形式是，每一行记录包括了信息：车辆ID，上车时间，上车地点，下车时间，下车地点
#     这样一行数据就是一个OD


data = data.rename(columns={'Lng': 'SLng', 'Lat': 'SLat'})
data['ELng'] = data['SLng'].shift(-1)
data['ELat'] = data['SLat'].shift(-1)
data['Etime'] = data['Stime'].shift(-1)
data = data[data['StatusChange'] == 1]
data = data.drop('StatusChange', axis=1)

# ########## 保存

data.to_csv(r'data-sample\TaxiOD-Sample.csv', index=None)
