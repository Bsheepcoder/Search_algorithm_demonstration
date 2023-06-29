# background
- 一个演示搜索类算法的地图模拟器

这个项目的最初版本源自一个B站up主 Minicking开放的代码，在其代码的基础上我进行了学习、更改和扩充
，视频链接[A*寻路算法动态演示](https://www.bilibili.com/video/BV1FJ411j7oG?share_source=copy_web&vd_source=e09e7d9860329cf23712dbc79e5ed45e)

# usage

目前使用帮助都写到了程序的页面，按照提示操作即可。

**注意事项：**
- **先生成地图再导入地图**，地图的文件名必须为map.txt，且将文件放在./map目录下
- 在导入前**导入的地图是否与当前的地图方块数**匹配，目前还没做报错、提醒的优化

# badge

现在的版本：1.1.0，使用python、PyQt5开发

技术点:

- 用python的类中的__new__ 方法实现点对象的唯一存储
- 用算法结合画图事件和时间事件的逻辑
- 用生成器来构造算法的执行过程
- 判断两点间的距离采用曼哈顿距离，相对欧拉距离速度更快
- 各类搜素算法的实现

# example
![Geek_YYDS](https://img-blog.csdnimg.cn/b298ebeb9d4346b7ab4d17e76c85bbd1.gif)
# maintainers
新思路Geek组成员某东，负责bug的修复,功能完善和添加算法

# contributing

- B站up主 [Minicking](https://space.bilibili.com/105229830)，贡献了最初的代码

# license

[新思路](许可证) © Geek

# Change log

## 2022.9.5 版本更新至1.1.0

- 修改了调倍速的模块和优化了倍速体验
- 添加了深度受限算法DLS、迭代加深算法IDS(开始默认depth为2，每次搜索depth+1)
- 添加了双向搜素BS、爬山搜素HCS、集束搜素BeamS(W = 3)、最佳优先搜素BFS、统一代价搜素UCS
- 添加了A*搜索,还想添加其他的，有感兴趣的来帮忙迭代呀！
- 显示搜素完成后的最短路径
