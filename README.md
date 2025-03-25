# 头部姿势控制赛车游戏 | Head Pose Controlled Racing Game

[English](README_en.md)

![游戏演示](https://github.com/wangqiqi/interesting_assets/raw/main/images/head_racing_game.png)

## 中文

### 简介

头部姿势控制赛车游戏是一款结合计算机视觉与赛车游戏的互动项目。玩家通过摄像头捕捉的头部姿势来控制赛车的移动方向和速度。游戏屏幕分为两部分：左侧显示实时视频流和头部姿势跟踪，右侧显示赛车游戏。

### 特点

- 使用头部姿势控制赛车的移动
- 头部向左/右倾斜控制方向
- 头部向前倾斜（远离摄像头）加速
- 头部向后倾斜（靠近摄像头）减速
- 实时头部跟踪和姿势识别
- 动态曲线赛道，具有真实的透视效果
- 障碍物躲避和碰撞检测
- 基于时间的得分系统和奖励机制
- 加速和减速的视觉反馈
- 增强的游戏音效，对应不同游戏事件
- 分数为零时游戏结束
- 临时消息系统，显示游戏事件
- 半透明信息面板
- 可自定义显示选项（摄像头视图、调试信息）
- 暂停/继续功能
- 游戏过程中重新校准选项

### 游戏玩法

1. 将头部对准摄像头
2. 通过头部姿势控制赛车：
   - 头部向左倾斜：赛车向左移动
   - 头部向右倾斜：赛车向右移动
   - 头部向前倾斜（远离摄像头）：赛车加速
   - 头部向后倾斜（靠近摄像头）：赛车减速
3. 避开障碍物，在赛道上行驶
4. 通过生存时间和避开障碍物获得分数
5. 与障碍物碰撞或偏离赛道会扣分
6. 分数降至零时游戏结束

### 控制方式

- **头部姿势**：控制赛车的方向和速度
- **空格键**：暂停/继续游戏
- **R键**：重新校准头部位置
- **C键**：切换摄像头视图
- **D键**：切换调试信息
- **M键**：切换游戏模式
- **ESC键**：退出游戏

### 安装

1. 克隆仓库：
   ```
   git clone https://github.com/yourusername/head-racing-game.git
   cd head-racing-game
   ```

2. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

3. 运行游戏：
   ```
   python run.py
   ```

### 音效

游戏包含以下音效：
- `background.mp3`：持续播放的背景音乐
- `crash.mp3`：游戏结束时播放
- `collision.mp3`：赛车与障碍物碰撞或偏离赛道时播放
- `racing.mp3`：赛车加速时播放

将您的音效文件放在`sounds`目录中，使用上述文件名。

### 系统要求

- Python 3.7+
- 摄像头
- 查看 `requirements.txt` 获取Python包依赖

### 项目结构

```
head-racing-game/
├── sounds/              # 音效和音乐
├── src/                 # 源代码
│   ├── game/            # 赛车游戏逻辑
│   ├── head_tracking/   # 头部姿势检测
│   └── __init__.py
├── .gitignore           # Git忽略文件
├── LICENSE              # MIT许可证
├── README.md            # 本文件
├── README_en.md         # 英文说明
├── requirements.txt     # Python依赖
└── run.py               # 主入口点
```

### 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 微信：znzatop

![微信](https://github.com/wangqiqi/interesting_assets/raw/main/images/wechat.jpg)

## License | 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。