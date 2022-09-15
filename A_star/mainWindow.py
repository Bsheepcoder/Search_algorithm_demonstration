#!/usr/bin/env python3
# -*- coding:utf-8 -*-
##############################
# *** Can we do better ? *** #
##############################
import types
import sys
import time
import json
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np
from main_Ui import Ui_mainWindow


# 参数设定
class Config:
    # 地图位置,左上角位置
    MAP_X = 240
    MAP_Y = 30
    # 地图尺寸
    SIZE_W = 900
    SIZE_H = 750
    # 方块大小
    blockLength = 150  # 绘制画面时每一个节点方块的边长
    blockLengthList = [150, 75, 50, 30, 25, 15, 10, 5]  # 可选方块大小，最大宽和高的最大公约数
    # 方块数量
    WIDTH = int(SIZE_W / blockLength)  # 方块列数
    HEIGHT = int(SIZE_H / blockLength)  # 方块行数

    def __init__(self):
        self.gcd(self.SIZE_H, self.SIZE_W)

    def gcd(self, a, b):
        if a >= b:
            num = b
        else:
            num = a
        for i in range(1, num):
            if ((a % num) == 0) and ((b % num) == 0):
                self.blockLengthList.append(i)


# 节点类
class Point:
    _list = []  # 储存所有的point类实例
    _tag = True  # 标记最新创建的实例是否为_list中的已有的实例，True表示不是已有实例

    def __new__(cls, x, y):  # 重写new方法实现对于同样的坐标只有唯一的一个实例
        for i in Point._list:
            if i.x == x and i.y == y:
                Point._tag = False
                return i
        # 这里是做到了单例引用，因为__new__先于__init__执行，
        # 并且__new__的作用是创建对象空间，重写new后return的是唯一的引用对象空间，
        # 则每次init初始化都会只初始化返回的唯一空间，具体参考 http://t.csdn.cn/0KtFa
        nt = super(Point, cls).__new__(cls)
        Point._list.append(nt)
        return nt

    def __init__(self, x, y):
        if Point._tag:
            self.x = x
            self.y = y
            self.father = None
            self.toEndCost = 0  # 如果算法需要，则表示当前点与终点距离，也就是估计的路程花费
            self.path = 0  # 起始点到该点的路径花费
        else:
            Point._tag = True

    @classmethod
    def clear(cls):  # clear方法，每次搜索结束后，将所有点数据清除，以便进行下一次搜索的时候点数据不会冲突。
        Point._list = []

    def __eq__(self, T):  # 重写==运算以便实现point类的in运算
        if type(self) == type(T):
            return (self.x, self.y) == (T.x, T.y)
        else:
            return False

    def __str__(self):
        return '(%d,%d)[father:(%s)]' % (
            self.x, self.y, str((self.father.x, self.father.y)) if self.father is not None else 'null')


# 不知情搜索


# 广度优先算法 breadth-first search
class BFS:

    def __init__(self, pointStart, pointEnd, searchMap):
        print("构造BFS")
        self.start = pointStart  # 储存此次搜索的开始点
        self.end = pointEnd  # 储存此次搜索的目的点
        self.map = searchMap  # 一个二维数组，为此次搜索的地图引用

        self.open = []  # 开放列表：储存即将被搜索的节点
        self.close = []  # 关闭列表：储存已经搜索过的节点
        self.result = []  # 搜索完成后保存路径
        self.searchCount = 0
        self.useTime = 0
        # 将起始点输入open
        self.open.append(self.start)

    def getAroundPoint(self, point):  # 获取指定点周围所有可通行的点

        x = point.x
        y = point.y
        print(x, y)
        allAroundPoint = [(x, y + 1), (x + 1, y + 1), (x + 1, y), (x + 1, y - 1),
                          (x, y - 1), (x - 1, y - 1), (x - 1, y), (x - 1, y + 1)]
        # 移除不在map上的点
        for p in allAroundPoint[::-1]:
            if p[0] < 0 or p[0] >= Config.WIDTH or p[1] < 0 or p[1] >= Config.HEIGHT:
                allAroundPoint.remove(p)

        # 当前节点可走的下一节点队列
        nextPointList = []
        for i in allAroundPoint:
            if self.map[i[1]][i[0]] == 0:
                nextPoint = Point(i[0], i[1])
                nextPointList.append(nextPoint)
        return nextPointList

    # 将可走的节点列表依次导入open，并连接父节点
    def addToOpen(self, probablyPointList, fatherPoint):
        for p in probablyPointList:
            if p not in self.open:
                if p not in self.close:
                    p.father = fatherPoint
                    self.open.append(p)
            else:
                pass

    def getOpen(self):
        if len(self.open) <= 0:
            return None
        t = self.open[0]
        return t

    # 生成器
    def process(self):
        print("进入 process")
        while True:
            print("运行中")
            self.searchCount += 1
            nowPoint = self.getOpen()
            if nowPoint is None:
                print("nowPoint is None")
                self.result = None
                self.searchCount = -1
                break
            else:
                print("nowPoint is not None")
                probablyPointList = self.getAroundPoint(nowPoint)
                self.addToOpen(probablyPointList, nowPoint)
                self.open.remove(nowPoint)
                self.close.append(nowPoint)
                if self.end in self.open:
                    r = self.end
                    self.result.append(r)
                    while True:
                        r = r.father
                        if r is None:
                            break
                        self.result.append(r)
                    yield nowPoint, self.open, self.close
                    break
                print(nowPoint)
            print("结束")
            yield nowPoint, self.open, self.close
    # self.useTime = time2 - time1


# 深度优先算法 depth-first search
class DFS:
    def __init__(self, pointStart, pointEnd, searchMap):
        print("构造DFS")
        self.start = pointStart  # 储存此次搜索的开始点
        self.end = pointEnd  # 储存此次搜索的目的点
        self.map = searchMap  # 一个二维数组，为此次搜索的地图引用

        self.open = []  # 开放列表：储存即将被搜索的节点
        self.close = []  # 关闭列表：储存已经搜索过的节点
        self.result = []  # 搜索完成后保存路径
        self.searchCount = 0
        self.useTime = 0
        # 将起始点输入open
        self.open.append(self.start)

    def getAroundPoint(self, point):  # 获取指定点周围所有可通行的点

        x = point.x
        y = point.y
        print(x, y)
        allAroundPoint = [(x, y + 1), (x + 1, y + 1), (x + 1, y), (x + 1, y - 1),
                          (x, y - 1), (x - 1, y - 1), (x - 1, y), (x - 1, y + 1)]
        # 移除不在map上的点
        for p in allAroundPoint[::-1]:
            if p[0] < 0 or p[0] >= Config.WIDTH or p[1] < 0 or p[1] >= Config.HEIGHT:
                allAroundPoint.remove(p)

        # 当前节点可走的下一节点队列
        nextPointList = []
        for i in allAroundPoint:
            if self.map[i[1]][i[0]] == 0:
                nextPoint = Point(i[0], i[1])
                nextPointList.append(nextPoint)
        return nextPointList

    # 将可走的节点列表依次导入open，并连接父节点
    def addToOpen(self, probablyPointList, fatherPoint):
        for p in probablyPointList:
            if p not in self.open:
                if p not in self.close:
                    p.father = fatherPoint
                    self.open.append(p)
            else:
                pass

    def getOpen(self):
        if len(self.open) <= 0:
            return None
        return self.open.pop()

    # 生成器
    def process(self):
        print("进入 process")
        while True:
            print("运行中")
            self.searchCount += 1
            nowPoint = self.getOpen()
            if nowPoint is None:
                print("nowPoint is None")
                self.result = None
                self.searchCount = -1
                break
            else:
                print("nowPoint is not None")
                probablyPointList = self.getAroundPoint(nowPoint)
                self.addToOpen(probablyPointList, nowPoint)
                self.close.append(nowPoint)
                if self.end in self.open:
                    r = self.end
                    self.result.append(r)
                    while True:
                        r = r.father
                        if r is None:
                            break
                        self.result.append(r)
                    yield nowPoint, self.open, self.close
                    break
                print(nowPoint)
            print("结束")
            yield nowPoint, self.open, self.close
        # self.useTime = time2 - time1


# 深度受限算法 depth-limited search
class DLS:
    def __init__(self, pointStart, pointEnd, searchMap):
        print("构造DLS")
        self.start = pointStart  # 储存此次搜索的开始点
        self.end = pointEnd  # 储存此次搜索的目的点
        self.map = searchMap  # 一个二维数组，为此次搜索的地图引用
        self.depth = 0  # 用来判断限制的深度
        self.wait = []  # 满足深度之后暂停等待的点
        self.open = []  # 开放列表：储存即将被搜索的节点
        self.close = []  # 关闭列表：储存已经搜索过的节点
        self.result = []  # 搜索完成后保存路径
        self.searchCount = 0
        self.useTime = 0
        # 将起始点输入open
        self.open.append(self.start)

    def getAroundPoint(self, point):  # 获取指定点周围所有可通行的点

        x = point.x
        y = point.y
        print(x, y)
        # 这个序列决定了根的顺序
        allAroundPoint = [(x, y + 1), (x + 1, y + 1), (x + 1, y), (x + 1, y - 1),
                          (x, y - 1), (x - 1, y - 1), (x - 1, y), (x - 1, y + 1)]
        # 移除不在map上的点
        for p in allAroundPoint[::-1]:
            if p[0] < 0 or p[0] >= Config.WIDTH or p[1] < 0 or p[1] >= Config.HEIGHT:
                allAroundPoint.remove(p)

        # 当前节点可走的下一节点队列
        nextPointList = []
        for i in allAroundPoint:
            if self.map[i[1]][i[0]] == 0:
                nextPoint = Point(i[0], i[1])
                nextPointList.append(nextPoint)
        return nextPointList

        # 将可走的节点列表依次导入open，并连接父节点

    def addToOpen(self, probablyPointList, fatherPoint):
        for p in probablyPointList:
            if p not in self.open:
                if p not in self.close:
                    p.father = fatherPoint
                    self.open.append(p)
            else:
                pass

    def getOpen(self):
        if len(self.open) <= 0:
            return None
        if self.depth >= 10:
            self.depth = 0
            self.wait.append(self.close[-1])
            for i in self.close:
                for j in self.open:
                    if j.father is i:
                        p = j
                        self.open.remove(j)
                        return p
            if self.wait[0] is None:
                return None
            return self.wait.pop()
        self.depth += 1
        return self.open.pop()

        # 生成器

    def process(self):
        print("进入 process")
        while True:
            print("运行中")
            self.searchCount += 1
            nowPoint = self.getOpen()
            if nowPoint is None:
                print("nowPoint is None")
                self.result = None
                self.searchCount = -1
                break
            else:
                print("nowPoint is not None")
                probablyPointList = self.getAroundPoint(nowPoint)
                self.addToOpen(probablyPointList, nowPoint)
                self.close.append(nowPoint)
                if self.end in self.open:
                    r = self.end
                    self.result.append(r)
                    while True:
                        r = r.father
                        if r is None:
                            break
                        self.result.append(r)
                    yield nowPoint, self.open, self.close
                    break
                print(nowPoint)
            print("结束")
            yield nowPoint, self.open, self.close
    # self.useTime = time2 - time1


# 迭代加深算法  iterative deepening search
class IDS:
    def __init__(self, pointStart, pointEnd, searchMap):
        print("构造IDS")
        self.start = pointStart  # 储存此次搜索的开始点
        self.end = pointEnd  # 储存此次搜索的目的点
        self.map = searchMap  # 一个二维数组，为此次搜索的地图引用

        self.depth = 0  # 用来判断限制的深度
        self.depthAdd = 2  # 放开深度限制的判断条件
        self.wait = []  # 满足深度限制之后暂停等待的点
        self.open = []  # 开放列表：储存即将被搜索的节点
        self.close = []  # 关闭列表：储存已经搜索过的节点
        self.result = []  # 搜索完成后保存路径
        self.searchCount = 0
        self.useTime = 0
        # 将起始点输入open
        self.open.append(self.start)

    def getAroundPoint(self, point):  # 获取指定点周围所有可通行的点

        x = point.x
        y = point.y
        print(x, y)
        # 这个序列决定了点出发方向顺序
        allAroundPoint = [(x, y + 1), (x + 1, y + 1), (x + 1, y), (x + 1, y - 1),
                          (x, y - 1), (x - 1, y - 1), (x - 1, y), (x - 1, y + 1)]
        # 移除不在map上的点
        for p in allAroundPoint[::-1]:
            if p[0] < 0 or p[0] >= Config.WIDTH or p[1] < 0 or p[1] >= Config.HEIGHT:
                allAroundPoint.remove(p)

        # 当前节点可走的下一节点队列
        nextPointList = []
        for i in allAroundPoint:
            if self.map[i[1]][i[0]] == 0:
                nextPoint = Point(i[0], i[1])
                nextPointList.append(nextPoint)
        return nextPointList

        # 将可走的节点列表依次导入open，并连接父节点

    def addToOpen(self, probablyPointList, fatherPoint):
        for p in probablyPointList:
            if p not in self.open:
                if p not in self.close:
                    p.father = fatherPoint
                    self.open.append(p)
            else:
                pass

    def getOpen(self):
        if len(self.open) <= 0:
            return None
        if self.depth >= self.depthAdd:
            self.depth = 0
            self.wait.append(self.close[-1])
            for i in self.close:
                for j in self.open:
                    if j.father is i:
                        p = j
                        self.depthAdd += 1
                        self.open.remove(j)
                        return p
            if self.wait[0] is None:
                return None
            return self.wait.pop()
        self.depth += 1
        return self.open.pop()

        # 生成器

    def process(self):
        while True:
            self.searchCount += 1
            nowPoint = self.getOpen()
            if nowPoint is None:
                self.result = None
                self.searchCount = -1
                break
            else:
                probablyPointList = self.getAroundPoint(nowPoint)
                self.addToOpen(probablyPointList, nowPoint)
                self.close.append(nowPoint)
                if self.end in self.open:
                    r = self.end
                    self.result.append(r)
                    while True:
                        r = r.father
                        if r is None:
                            break
                        self.result.append(r)
                    yield nowPoint, self.open, self.close
                    break
            yield nowPoint, self.open, self.close
    # self.useTime = time2 - time1


# 双向搜索(BFS) bidirectional search
class BS:

    def __init__(self, pointStart, pointEnd, searchMap):
        print("构造BS")
        self.start = pointStart  # 储存此次搜索的开始点
        self.end = pointEnd  # 储存此次搜索的目的点
        self.map = searchMap  # 一个二维数组，为此次搜索的地图引用
        # 起点
        self.open_s = []  # 开放列表：储存即将被搜索的节点
        # 终点
        self.open_e = []  # 开放列表：储存即将被搜索的节点

        self.close = []  # 关闭列表：储存已经搜索过的节点
        self.result = []  # 搜索完成后保存路径
        self.searchCount = 0
        self.useTime = 0
        # 将起始点输入open
        self.open_s.append(self.start)
        self.open_e.append(self.end)

    def getAroundPoint(self, point):  # 获取指定点周围所有可通行的点

        x = point.x
        y = point.y
        print(x, y)
        allAroundPoint = [(x, y + 1), (x + 1, y + 1), (x + 1, y), (x + 1, y - 1),
                          (x, y - 1), (x - 1, y - 1), (x - 1, y), (x - 1, y + 1)]
        # 移除不在map上的点
        for p in allAroundPoint[::-1]:
            if p[0] < 0 or p[0] >= Config.WIDTH or p[1] < 0 or p[1] >= Config.HEIGHT:
                allAroundPoint.remove(p)

        # 当前节点可走的下一节点队列
        nextPointList = []
        for i in allAroundPoint:
            if self.map[i[1]][i[0]] == 0:
                nextPoint = Point(i[0], i[1])
                nextPointList.append(nextPoint)
        return nextPointList

    # 将可走的节点列表依次导入open，并连接父节点
    def addToOpen(self, probablyPointList, fatherPoint, openList):
        for p in probablyPointList:
            if p not in openList:
                if p not in self.close:
                    if p.father is not None:
                        # 这里用到python动态绑定，给点p增加了一个属性使得双向搜索可以链接起来
                        p.father2 = fatherPoint
                    else:
                        p.father = fatherPoint
                    openList.append(p)
            else:
                pass

    def getOpen(self, openList):
        if len(openList) <= 0:
            return None
        t = openList[0]
        return t

    # 生成器
    def process(self):
        print("进入 process")
        while True:
            print("运行中")
            self.searchCount += 2
            nowPoint_s = self.getOpen(self.open_s)
            nowPoint_e = self.getOpen(self.open_e)
            if nowPoint_s is None or nowPoint_e is None:
                print("nowPoint is None")
                self.result = None
                self.searchCount = -2
                break
            else:
                print("nowPoint is not None")
                probablyPointList_s = self.getAroundPoint(nowPoint_s)
                probablyPointList_e = self.getAroundPoint(nowPoint_e)
                self.addToOpen(probablyPointList_s, nowPoint_s, self.open_s)
                self.addToOpen(probablyPointList_e, nowPoint_e, self.open_e)
                self.open_s.remove(nowPoint_s)
                self.open_e.remove(nowPoint_e)
                self.close.append(nowPoint_s)
                self.close.append(nowPoint_e)
                # 用于退出循环
                flag1 = False
                flag2 = False
                for ps in self.open_s:
                    for pe in self.open_e:
                        if ps.x == pe.x and ps.y == pe.y:
                            r = ps
                            self.result.append(r)
                            while True:
                                r = r.father
                                if r is None:
                                    break
                                self.result.append(r)
                            r = ps.father2
                            self.result.append(r)
                            while True:
                                r = r.father
                                if r is None:
                                    break
                                self.result.append(r)
                            yield nowPoint_s, self.open_s, self.close
                            flag1 = True
                            break
                    if flag1:
                        flag2 = True
                        break
                if flag2:
                    break
                print(nowPoint_s)
            print("结束")
            yield nowPoint_s, self.open_s, self.close


# 知情搜索

# 爬山搜索  Hill Climbing search / 贪婪最佳优先搜索 greedy best-first search
class HCS:
    def __init__(self, pointStart, pointEnd, searchMap):
        print("构造HCS")
        self.start = pointStart  # 储存此次搜索的开始点
        self.end = pointEnd  # 储存此次搜索的目的点
        self.map = searchMap  # 一个二维数组，为此次搜索的地图引用

        self.MinCost = Config.WIDTH * Config.HEIGHT
        self.open = []  # 开放列表：储存即将被搜索的节点
        self.close = []  # 关闭列表：储存已经搜索过的节点
        self.result = []  # 搜索完成后保存路径
        self.searchCount = 0
        self.useTime = 0
        # 将起始点输入open
        self.open.append(self.start)

    def getAroundPoint(self, point):  # 获取指定点周围所有可通行的点

        x = point.x
        y = point.y
        print(x, y)
        allAroundPoint = [(x, y + 1), (x + 1, y + 1), (x + 1, y), (x + 1, y - 1),
                          (x, y - 1), (x - 1, y - 1), (x - 1, y), (x - 1, y + 1)]
        # 移除不在map上的点
        for p in allAroundPoint[::-1]:
            if p[0] < 0 or p[0] >= Config.WIDTH or p[1] < 0 or p[1] >= Config.HEIGHT:
                allAroundPoint.remove(p)

        # 当前节点可走的下一节点队列
        nextPointList = []
        for i in allAroundPoint:
            if self.map[i[1]][i[0]] == 0:
                nextPoint = Point(i[0], i[1])
                nextPointList.append(nextPoint)
        return nextPointList

        # 返回传入点到终点的花费

    def cost(self, point):
        return abs(point.x - self.end.x) + abs(point.y - self.end.y)

        # 将可走的节点列表依次导入open，并连接父节点

    def addToOpen(self, probablyPointList, fatherPoint):
        tag = None
        Max = Config.WIDTH * Config.HEIGHT
        Flag = False
        for p in probablyPointList:
            if p not in self.open:
                if p not in self.close:
                    c = self.cost(p)
                    if c < self.MinCost:
                        Flag = True
                        self.MinCost = c
                        tag = p
        if Flag:
            tag.father = fatherPoint
            self.open.append(tag)

    def getOpen(self):
        if len(self.open) <= 0:
            return None
        return self.open.pop()

        # 生成器

    def process(self):
        print("进入 process")
        while True:
            print("运行中")
            self.searchCount += 1
            nowPoint = self.getOpen()
            if nowPoint is None:
                print("nowPoint is None")
                self.result = None
                self.searchCount = -1
                break
            else:
                print("nowPoint is not None")
                probablyPointList = self.getAroundPoint(nowPoint)
                self.addToOpen(probablyPointList, nowPoint)
                self.close.append(nowPoint)
                if self.end in self.open:
                    r = self.end
                    self.result.append(r)
                    while True:
                        r = r.father
                        if r is None:
                            break
                        self.result.append(r)
                    yield nowPoint, self.open, self.close
                    break
                print(nowPoint)
            print("结束")
            yield nowPoint, self.open, self.close
        # self.useTime = time2 - time1


# 集束搜索 beam search  W = 3
class BeamS:
    def __init__(self, pointStart, pointEnd, searchMap):
        print("构造BeamS")
        self.start = pointStart  # 储存此次搜索的开始点
        self.end = pointEnd  # 储存此次搜索的目的点
        self.map = searchMap  # 一个二维数组，为此次搜索的地图引用

        self.W = 3  # 表示集束的薄厚，也就是取几个最小的点
        self.MinCost = Config.WIDTH * Config.HEIGHT  # 用来判断并取得最小值
        self.open = []  # 开放列表：储存即将被搜索的节点
        self.close = []  # 关闭列表：储存已经搜索过的节点
        self.result = []  # 搜索完成后保存路径
        self.searchCount = 0
        self.useTime = 0
        # 将起始点输入open
        self.open.append(self.start)

    def getAroundPoint(self, point):  # 获取指定点周围所有可通行的点

        x = point.x
        y = point.y
        print(x, y)
        allAroundPoint = [(x, y + 1), (x + 1, y + 1), (x + 1, y), (x + 1, y - 1),
                          (x, y - 1), (x - 1, y - 1), (x - 1, y), (x - 1, y + 1)]
        # 移除不在map上的点
        for p in allAroundPoint[::-1]:
            if p[0] < 0 or p[0] >= Config.WIDTH or p[1] < 0 or p[1] >= Config.HEIGHT:
                allAroundPoint.remove(p)

        # 当前节点可走的下一节点队列
        nextPointList = []
        for i in allAroundPoint:
            if self.map[i[1]][i[0]] == 0:
                nextPoint = Point(i[0], i[1])
                nextPointList.append(nextPoint)
        return nextPointList

    # 返回传入点到终点的花费
    def cost(self, point):
        return abs(point.x - self.end.x) + abs(point.y - self.end.y)

    # 将可走的节点列表依次导入open，并连接父节点
    def addToOpen(self, probablyPointList, fatherPoint):
        tag = None
        Max = Config.WIDTH * Config.HEIGHT
        Flag = False
        for i in range(0, self.W):
            for p in probablyPointList:
                if p not in self.open:
                    if p not in self.close:
                        c = self.cost(p)
                        if c < self.MinCost:
                            Flag = True
                            self.MinCost = c
                            tag = p
            if Flag:
                tag.father = fatherPoint
                self.open.append(tag)
                probablyPointList.remove(tag)
                self.MinCost = Config.WIDTH * Config.HEIGHT
                Flag = False
        if len(probablyPointList) > 1:
            self.W = 1

    # 形式上使用了优先队列
    def getOpen(self):
        if len(self.open) <= 0:
            return None
        tag = self.open[0]
        m = self.open[0].toEndCost
        for i in self.open:
            if i.toEndCost < m:
                m = i.toEndCost
                tag = i
        self.open.remove(tag)
        return tag

    # 生成器
    def process(self):
        print("进入 process")
        while True:
            print("运行中")
            self.searchCount += 1
            nowPoint = self.getOpen()
            if nowPoint is None:
                print("nowPoint is None")
                self.result = None
                self.searchCount = -1
                break
            else:
                print("nowPoint is not None")
                probablyPointList = self.getAroundPoint(nowPoint)
                self.addToOpen(probablyPointList, nowPoint)
                self.close.append(nowPoint)
                if self.end in self.open:
                    r = self.end
                    self.result.append(r)
                    while True:
                        r = r.father
                        if r is None:
                            break
                        self.result.append(r)
                    yield nowPoint, self.open, self.close
                    break
                print(nowPoint)
            print("结束")
            yield nowPoint, self.open, self.close
        # self.useTime = time2 - time1


# 最佳优先搜索 best-first search+
class GBFS:
    def __init__(self, pointStart, pointEnd, searchMap):
        print("构造DFS")
        self.start = pointStart  # 储存此次搜索的开始点
        self.end = pointEnd  # 储存此次搜索的目的点
        self.map = searchMap  # 一个二维数组，为此次搜索的地图引用

        self.MinCost = Config.WIDTH * Config.HEIGHT
        self.open = []  # 开放列表：储存即将被搜索的节点
        self.close = []  # 关闭列表：储存已经搜索过的节点
        self.result = []  # 搜索完成后保存路径
        self.searchCount = 0
        self.useTime = 0
        # 将起始点输入open
        self.open.append(self.start)

    def getAroundPoint(self, point):  # 获取指定点周围所有可通行的点

        x = point.x
        y = point.y
        print(x, y)
        allAroundPoint = [(x, y + 1), (x + 1, y + 1), (x + 1, y), (x + 1, y - 1),
                          (x, y - 1), (x - 1, y - 1), (x - 1, y), (x - 1, y + 1)]
        # 移除不在map上的点
        for p in allAroundPoint[::-1]:
            if p[0] < 0 or p[0] >= Config.WIDTH or p[1] < 0 or p[1] >= Config.HEIGHT:
                allAroundPoint.remove(p)

        # 当前节点可走的下一节点队列
        nextPointList = []
        for i in allAroundPoint:
            if self.map[i[1]][i[0]] == 0:
                nextPoint = Point(i[0], i[1])
                nextPointList.append(nextPoint)
        return nextPointList

    # 返回传入点到终点的花费
    def cost(self, point):
        return abs(point.x - self.end.x) + abs(point.y - self.end.y)

    # 将可走的节点列表依次导入open，并连接父节点
    def addToOpen(self, probablyPointList, fatherPoint):
        for p in probablyPointList:
            if p not in self.open:
                if p not in self.close:
                    p.toEndCost = self.cost(p)
                    p.father = fatherPoint
                    self.open.append(p)

    # 形式上使用了优先队列
    def getOpen(self):
        if len(self.open) <= 0:
            return None
        tag = self.open[0]
        m = self.open[0].toEndCost
        for i in self.open:
            if i.toEndCost < m:
                m = i.toEndCost
                tag = i
        self.open.remove(tag)
        return tag

    # 生成器
    def process(self):
        print("进入 process")
        while True:
            print("运行中")
            self.searchCount += 1
            nowPoint = self.getOpen()
            if nowPoint is None:
                print("nowPoint is None")
                self.result = None
                self.searchCount = -1
                break
            else:
                print("nowPoint is not None")
                probablyPointList = self.getAroundPoint(nowPoint)
                self.addToOpen(probablyPointList, nowPoint)
                self.close.append(nowPoint)
                if self.end in self.open:
                    r = self.end
                    self.result.append(r)
                    while True:
                        r = r.father
                        if r is None:
                            break
                        self.result.append(r)
                    yield nowPoint, self.open, self.close
                    break
                print(nowPoint)
            print("结束")
            yield nowPoint, self.open, self.close
        # self.useTime = time2 - time1


# 统一代价搜索 uniform-cost search
class UCS:
    def __init__(self, pointStart, pointEnd, searchMap):
        print("构造DFS")
        self.start = pointStart  # 储存此次搜索的开始点
        self.end = pointEnd  # 储存此次搜索的目的点
        self.map = searchMap  # 一个二维数组，为此次搜索的地图引用

        self.bestCost = Config.WIDTH * Config.HEIGHT  # 最终花费值
        self.costList = []
        self.MinCost = Config.WIDTH * Config.HEIGHT
        self.open = []  # 开放列表：储存即将被搜索的节点
        self.close = []  # 关闭列表：储存已经搜索过的节点
        self.result = []  # 搜索完成后保存路径
        self.searchCount = 0
        self.useTime = 0
        # 将起始点输入open
        self.open.append(self.start)

    def getAroundPoint(self, point):  # 获取指定点周围所有可通行的点

        x = point.x
        y = point.y
        print(x, y)
        allAroundPoint = [(x, y + 1), (x + 1, y + 1), (x + 1, y), (x + 1, y - 1),
                          (x, y - 1), (x - 1, y - 1), (x - 1, y), (x - 1, y + 1)]
        # 移除不在map上的点
        for p in allAroundPoint[::-1]:
            if p[0] < 0 or p[0] >= Config.WIDTH or p[1] < 0 or p[1] >= Config.HEIGHT:
                allAroundPoint.remove(p)

        # 当前节点可走的下一节点队列
        nextPointList = []
        for i in allAroundPoint:
            if self.map[i[1]][i[0]] == 0:
                nextPoint = Point(i[0], i[1])
                nextPointList.append(nextPoint)
        return nextPointList

        # 返回传入点到终点的花费

    def cost(self, point):
        return abs(point.x - self.end.x) + abs(point.y - self.end.y)

    def path(self, point):
        p = point
        count = 0
        while p is not None:
            if p.father is not None:
                count += 1
                p = p.father
        return count

        # 将可走的节点列表依次导入open，并连接父节点

    def addToOpen(self, probablyPointList, fatherPoint):
        for p in probablyPointList:
            if p not in self.open:
                if p not in self.close:
                    p.toEndCost = self.cost(p)
                    p.father = fatherPoint
                    if p.father is not None:
                        p.path = p.father.path + 1
                        print(p.path)
                    self.open.append(p)

        # 形式上使用了优先队列

    def getOpen(self):
        if len(self.open) <= 0:
            return None
        tag = None
        if self.bestCost == Config.WIDTH * Config.HEIGHT:
            m = self.open[0].path + self.open[0].toEndCost
            for i in self.open:
                n = i.toEndCost + i.path
                if n <= m:
                    m = n
                    tag = i
            self.open.remove(tag)
            return tag

        else:
            m = self.bestCost
            for i in self.open:
                n = i.toEndCost + i.path
                if n <= m:
                    tag = i
                    self.open.remove(tag)
                    return tag
        return None
        # 生成器

    def process(self):
        print("进入 process")
        while True:
            print("运行中")
            self.searchCount += 1
            nowPoint = self.getOpen()
            if nowPoint is None:
                if len(self.open) == 0:
                    print("nowPoint is None")
                    self.result = None
                    self.searchCount = -1
                    break
            else:
                print("nowPoint is not None")
                probablyPointList = self.getAroundPoint(nowPoint)
                self.addToOpen(probablyPointList, nowPoint)
                self.close.append(nowPoint)

                # 判断是否检测到终点
                if self.end in self.open:
                    self.open.remove(self.end)
                    if nowPoint.path + nowPoint.toEndCost < self.bestCost:
                        self.bestCost = nowPoint.path + nowPoint.toEndCost
                        self.costList.append(nowPoint)
                    tag = True
                    # 判断是否存在 path + endCost < 当前终点的 path + endCost 的点
                    for i in self.open:
                        if (i.path + i.toEndCost) <= self.bestCost:
                            tag = False
                            break
                    if tag:
                        r = self.end
                        self.result.append(r)
                        r = self.costList.pop()
                        self.result.append(r)
                        while True:
                            r = r.father
                            if r is None:
                                break
                            self.result.append(r)
                        yield nowPoint, self.open, self.close
                        break
                print(nowPoint)
            print("结束")
            yield nowPoint, self.open, self.close
        # self.useTime = time2 - time1


# A*搜索     f(n) = path(n)  + toEndCost(n)
class A_Star:
    def __init__(self, pointStart, pointEnd, searchMap):
        print("构造DFS")
        self.start = pointStart  # 储存此次搜索的开始点
        self.end = pointEnd  # 储存此次搜索的目的点
        self.map = searchMap  # 一个二维数组，为此次搜索的地图引用

        self.bestCost = Config.WIDTH * Config.HEIGHT  # 最终花费值
        self.costList = []
        self.MinCost = Config.WIDTH * Config.HEIGHT
        self.open = []  # 开放列表：储存即将被搜索的节点
        self.close = []  # 关闭列表：储存已经搜索过的节点
        self.result = []  # 搜索完成后保存路径
        self.searchCount = 0
        self.useTime = 0
        # 将起始点输入open
        self.open.append(self.start)

    def getAroundPoint(self, point):  # 获取指定点周围所有可通行的点

        x = point.x
        y = point.y
        print(x, y)
        allAroundPoint = [(x, y + 1), (x + 1, y + 1), (x + 1, y), (x + 1, y - 1),
                          (x, y - 1), (x - 1, y - 1), (x - 1, y), (x - 1, y + 1)]
        # 移除不在map上的点
        for p in allAroundPoint[::-1]:
            if p[0] < 0 or p[0] >= Config.WIDTH or p[1] < 0 or p[1] >= Config.HEIGHT:
                allAroundPoint.remove(p)

        # 当前节点可走的下一节点队列
        nextPointList = []
        for i in allAroundPoint:
            if self.map[i[1]][i[0]] == 0:
                nextPoint = Point(i[0], i[1])
                nextPointList.append(nextPoint)
        return nextPointList

        # 返回传入点到终点的花费

    def cost(self, point):
        return abs(point.x - self.end.x) + abs(point.y - self.end.y)

    def path(self, point):
        p = point
        count = 0
        while p is not None:
            if p.father is not None:
                count += 1
                p = p.father
        return count

        # 将可走的节点列表依次导入open，并连接父节点

    def addToOpen(self, probablyPointList, fatherPoint):
        for p in probablyPointList:
            if p not in self.open:
                if p not in self.close:
                    p.toEndCost = self.cost(p)
                    p.father = fatherPoint
                    if p.father is not None:
                        p.path = p.father.path + 1
                        print(p.path)
                    self.open.append(p)

    # 形式上使用了优先队列
    def getOpen(self):
        if len(self.open) <= 0:
            return None
        tag = None
        m = self.open[0].path + self.open[0].toEndCost
        for i in self.open:
            n = i.toEndCost + i.path
            if n <= m:
                m = n
                tag = i
        self.open.remove(tag)
        return tag
        # 生成器

    def process(self):
        print("进入 process")
        while True:
            print("运行中")
            self.searchCount += 1
            nowPoint = self.getOpen()
            if nowPoint is None:
                if len(self.open) == 0:
                    print("nowPoint is None")
                    self.result = None
                    self.searchCount = -1
                    break
            else:
                print("nowPoint is not None")
                probablyPointList = self.getAroundPoint(nowPoint)
                self.addToOpen(probablyPointList, nowPoint)
                self.close.append(nowPoint)
                # 判断是否检测到终点
                if self.end in self.open:
                    r = self.end
                    self.result.append(r)
                    while True:
                        r = r.father
                        if r is None:
                            break
                        self.result.append(r)
                    yield nowPoint, self.open, self.close
                    break
                print(nowPoint)
            print("结束")
            yield nowPoint, self.open, self.close
        # self.useTime = time2 - time1


# 窗口类
class MainWindow(QMainWindow, Ui_mainWindow):

    def __init__(self):
        print("初始化地图")

        # 初始化参数
        self.Map = []
        self.startPoint = None
        self.endPoint = None
        self.centerTimer = None  # 全局时间
        self.search = None
        self.yi = None
        self.special = None
        self.config = Config()
        # 根据参数设定，初始化地图的二维list
        for i in range(Config.HEIGHT):
            col = []
            for j in range(Config.WIDTH):
                col.append(0)
            self.Map.append(col)

        # 继承QMainWindow需要调用超类的__init__()
        super().__init__()

        # 导入UI
        self.ui = self.setupUi(self)
        self.initUI()

    # 初始化UI
    def initUI(self):

        lineEdit = QLineEdit()
        lineEdit.setReadOnly(True)  # 设置只读
        lineEdit.setAlignment(Qt.AlignCenter)  # 设置文字居中
        self.comboBoxSearch.setLineEdit(lineEdit)
        for i in self.config.blockLengthList:
            self.comboBoxBlockSize.addItem(str(i), i)
        self.setFixedSize(self.width(), self.height())
        self.setWindowIcon(QIcon("./GeekLogo.ico"))
        self.setObjectName("MainWindow")
        self.setStyleSheet("#MainWindow{border-image:url(7.png)}")
        # 控件绑定事件
        self.button_CreatetMap.clicked.connect(self.event_SaveMap)
        self.button_InputMap.clicked.connect(self.event_GetMap)
        self.button_Run.clicked.connect(self.event_StartSearch)
        self.button_ClearMap.clicked.connect(self.event_ClearMap)
        self.button_EndSearch.clicked.connect(self.event_EndSearch)
        self.button_RandomMap.clicked.connect(self.event_RandomMap)
        self.comboBoxBlockSize.currentIndexChanged.connect(self.event_SetBlockSize)

        # 程序初始化成功...
        self.ToNote('---------新思路Geek组--------\n'
                    '|          好奇之心，改变之力    |\n'
                    '|         QQ群:299263121       |\n'
                    '初始化成功...\n'
                    '请设计地图或导入map.txt...')

    # 发送通知到窗口
    def ToNote(self, message):
        self.plainTextEdit_ShowMessage.appendPlainText(message)

    # #自定义事件
    #
    # 保存地图
    def event_SaveMap(self):
        with open('./map/map.txt', 'w') as f:
            f.write(json.dumps(self.Map))
        self.ToNote("N: 生成地图成功！在该应用路径内查看")

    # 导入地图
    def event_GetMap(self):
        try:
            with open('./map/map.txt', 'r') as f:
                self.Map = json.loads(f.read())
                Config.HEIGHT = len(self.Map)
                Config.WIDTH = len(self.Map[0])
                self.repaint()
        except Exception as e:
            print('失败', e, type(e))
            if type(e) == FileNotFoundError:
                self.ToNote('Error: 地图加载失败:地图文件不存在')
            elif type(e) == json.decoder.JSONDecodeError:
                self.ToNote('Error: 地图加载失败,错误的地图文件')

    # 清空地图
    def event_ClearMap(self):
        for i in range(len(self.Map)):
            for j in range(len(self.Map[i])):
                self.Map[i][j] = 0
        self.repaint()
        self.ToNote('N: 地图已清空')

    # 随机生成地图
    def event_RandomMap(self):
        Map = []
        for i in range(0, Config.HEIGHT):
            Map.append(np.random.randint(0, 2, Config.WIDTH).tolist())
        self.Map = Map
        self.repaint()

    # 方块大小响应事件
    def event_SetBlockSize(self):
        Config.blockLength = int(self.comboBoxBlockSize.currentText())
        print(Config.blockLength)
        # 方块数量
        Config.WIDTH = int(Config.SIZE_W / Config.blockLength)  # 方块列数
        Config.HEIGHT = int(Config.SIZE_H / Config.blockLength)  # 方块行数
        self.Map = []
        # 根据参数设定，初始化地图的二维list
        for i in range(Config.HEIGHT):
            col = []
            for j in range(Config.WIDTH):
                col.append(0)
            self.Map.append(col)
        self.repaint()

    # 开始搜索事件
    def event_StartSearch(self):

        if self.startPoint is not None and self.endPoint is not None:
            if self.centerTimer is None:
                self.centerTimer = QBasicTimer()  # 设置定时器
            self.button_Run.setEnabled(False)
            self.button_ClearMap.setEnabled(False)
            self.button_InputMap.setEnabled(False)
            self.button_CreatetMap.setEnabled(False)
            self.button_RandomMap.setEnabled(False)
            # 开始计时
            self.centerTimer.start(800 / self.horizontalSlider_Speed.value(), self)
            # 算法实例化
            self.search = self.selectAlgorithm(self.comboBoxSearch.currentIndex())
            self.yi = self.search.process()
            self.ToNote('N: 开始搜索》》》')
        else:
            self.ToNote('Error: 请先设置起点或终点')

    # 搜索算法选择
    def selectAlgorithm(self, select):
        # 简化书写，优化代码
        alg = None
        sx = self.startPoint[0]
        sy = self.startPoint[1]
        ex = self.endPoint[0]
        ey = self.endPoint[1]

        if select == 0:
            alg = BFS(Point(sx, sy), Point(ex, ey), self.Map)
        elif select == 1:
            alg = DFS(Point(sx, sy), Point(ex, ey), self.Map)
        elif select == 2:
            alg = DLS(Point(sx, sy), Point(ex, ey), self.Map)
        elif select == 3:
            alg = IDS(Point(sx, sy), Point(ex, ey), self.Map)
        elif select == 4:
            alg = BS(Point(sx, sy), Point(ex, ey), self.Map)
        elif select == 5:
            alg = HCS(Point(sx, sy), Point(ex, ey), self.Map)
        elif select == 6:
            alg = BeamS(Point(sx, sy), Point(ex, ey), self.Map)
        elif select == 7:
            alg = GBFS(Point(sx, sy), Point(ex, ey), self.Map)
        elif select == 8:
            alg = UCS(Point(sx, sy), Point(ex, ey), self.Map)
        elif select == 9:
            alg = A_Star(Point(sx, sy), Point(ex, ey), self.Map)
            pass
        return alg

    # 结束搜索事件
    def event_EndSearch(self):
        self.centerTimer.stop()
        self.search = None
        self.yi = None
        self.special = None
        Point.clear()
        self.button_Run.setEnabled(True)
        self.button_ClearMap.setEnabled(True)
        self.button_InputMap.setEnabled(True)
        self.button_CreatetMap.setEnabled(True)
        self.button_RandomMap.setEnabled(True)
        self.repaint()

    # #重写内置事件
    #
    # 鼠标点击事件
    def mousePressEvent(self, event):  # event是鼠标事件，包含了坐标x、y元素
        # 获取鼠标点击地图中的坐标
        x, y = event.x() - Config.MAP_X, event.y() - Config.MAP_Y

        # 将x和y整除Config.blockLength结果赋给x,y
        x = x // Config.blockLength
        y = y // Config.blockLength

        if 0 <= x <= 19 and 0 <= y <= 19:
            print(f"鼠标点击坐标[{x},{y}]")

        # 判读鼠标响应事件范围
        if 0 <= x < Config.WIDTH and 0 <= y < Config.HEIGHT:
            # 鼠标左键点击
            if Qt.LeftButton == event.button():
                # 判断当前点是否是起点或者终点
                if (x, y) != self.startPoint and (x, y) != self.endPoint:
                    # 地图块1置为0，0置为1
                    if self.Map[y][x] == 0:
                        self.ToNote('N: 坐标(%d,%d)，设置为墙' % (x, y))
                    else:
                        self.ToNote('N: 坐标(%d,%d)，墙移除' % (x, y))
                    self.Map[y][x] = (1 if self.Map[y][x] == 0 else 0)

            if Qt.RightButton == event.button():
                if self.Map[y][x] == 0:
                    if self.startPoint is None:
                        self.startPoint = (x, y)
                        self.ToNote('N: 添加起点:(%d,%d)' % (x, y))
                    elif self.endPoint is None and self.startPoint != (x, y):
                        self.endPoint = (x, y)
                        self.ToNote('N: 添加终点:(%d,%d)' % (x, y))
                    else:
                        self.ToNote('N: 清除起点终点')
                        self.endPoint = None
                        self.startPoint = None
        # 重绘
        self.repaint()

    # 绘画事件
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawSearch(qp)
        qp.end()

    # 绘制搜索路径
    def drawSearch(self, qp):
        pen = QPen(QColor(8, 44, 137), 2, Qt.SolidLine) # 8, 44, 137
        qp.setPen(pen)
        # 画地图
        self.drawMap(qp)

        # 画当前点
        if self.search is not None:
            if self.special is not None:
                qp.setBrush(QColor(24, 90, 54))  # 绿色  24, 90, 54
                qp.drawRect(Config.MAP_X + self.special[0].x * Config.blockLength,
                            Config.MAP_Y + self.special[0].y * Config.blockLength,
                            Config.blockLength, Config.blockLength)
                for p in self.special[2]:   # 24, 92, 55
                    qp.setBrush(QColor(24, 92, 55))  # 深绿色
                    qp.drawRect(Config.MAP_X + p.x * Config.blockLength,
                                Config.MAP_Y + p.y * Config.blockLength,
                                Config.blockLength, Config.blockLength)
            for i in self.search.result:  # 28, 214, 108
                qp.setBrush(QColor(28, 214, 108))  # 绿
                qp.drawRect(Config.MAP_X + i.x * Config.blockLength,
                            Config.MAP_Y + i.y * Config.blockLength,
                            Config.blockLength, Config.blockLength)

        for i in range(len(self.Map)):
            for j in range(len(self.Map[i])):
                # 配置方格颜色
                if (j, i) == self.startPoint:
                    qp.setBrush(QColor(243, 139, 0))  # 橘色起点
                    qp.drawRect(Config.MAP_X + j * Config.blockLength,
                                Config.MAP_Y + i * Config.blockLength,
                                Config.blockLength, Config.blockLength)
                elif (j, i) == self.endPoint:
                    qp.setBrush(QColor(225, 218, 48))  # 黄色终点
                    qp.drawRect(Config.MAP_X + j * Config.blockLength,
                                Config.MAP_Y + i * Config.blockLength,
                                Config.blockLength, Config.blockLength)
                else:
                    pass

    # 绘制地图
    def drawMap(self, qp):
        # 根据Map画方格
        for i in range(len(self.Map)):
            for j in range(len(self.Map[i])):
                if self.Map[i][j] == 0:
                    qp.setBrush(QColor(4, 11, 4))
                else:                 # 24, 90, 189
                    qp.setBrush(QColor(24, 90, 189)) # 255, 214, 98
                # 画方格
                qp.drawRect(Config.MAP_X + j * Config.blockLength,
                            Config.MAP_Y + i * Config.blockLength,
                            Config.blockLength, Config.blockLength)

    # 时间事件，隔一段时间执行一次
    def timerEvent(self, e):
        print("")
        try:
            data = next(self.yi)
        except Exception as e:
            self.ToNote('N: 搜索结束 !')
            if self.search.result is None:
                self.ToNote('N: 未找到可行路径!')
            else:
                self.ToNote('N: 总计搜索节点数：%d' % self.search.searchCount)
                self.ToNote('N: 最终路径长度：%d' % len(self.search.result))
            self.centerTimer.stop()
            self.search = None
            self.yi = None
            self.special = None
            Point.clear()
            self.button_Run.setEnabled(True)
            self.button_ClearMap.setEnabled(True)
            self.button_InputMap.setEnabled(True)
            self.button_CreatetMap.setEnabled(True)
            self.button_RandomMap.setEnabled(True)
        else:
            self.special = data
            self.repaint()
