# ROS2 环形路线巡检

基于 ROS2 Humble 和 Python 的二维机器人运动模拟。通过主控制节点发布速度，底盘节点对速度积分得到位置，并将位置反馈给主控制节点，实现指定起终点运动和完整环路巡检。

本项目不依赖实体底盘或额外位置传感器，未接入 Gazebo；位置来自程序内的速度积分。

## 功能

- `point`：从指定起点沿规定方向到达终点；起终点相同时保持静止。
- `patrol`：从指定起点出发，沿环运动一整圈，返回起点后停止。
- x、y 方向速度分别限制在 `[-2, 2] m/s`。
- 根据积分位置判断到达，距离目标不超过 `0.01 m` 时切换目标或结束任务。
- 支持独立启动节点、Launch 统一启动、Docker 和 Docker Compose。
- 输出初始位置、规划路线、经过点、最终位置和任务完成状态；底盘约每秒输出一条位置与速度状态。

## 场地与路线

| 点编号 | x / m | y / m |
| --- | ---: | ---: |
| 1 | 0 | 0 |
| 2 | 2 | 0 |
| 3 | 4 | 1 |
| 4 | 4 | 3 |
| 5 | 2 | 4 |
| 6 | 0 | 4 |
| 7 | -1 | 2 |
| 8 | -1 | 1 |

运动顺序固定为：

```text
1 → 4 → 7 → 2 → 5 → 8 → 3 → 6 → 1
```

相邻点之间按直线目标控制。例如 `8 → 4` 的路线为 `[8, 3, 6, 1, 4]`；从 7 出发巡检的路线为 `[7, 2, 5, 8, 3, 6, 1, 4, 7]`。

## 项目结构

```text
.
├── README.md
├── Dockerfile
├── docker-entrypoint.sh
├── compose.yml
├── .dockerignore
├── .gitignore
└── ros2_ws/
    └── src/route_patrol/
        ├── package.xml
        ├── setup.py
        ├── setup.cfg
        ├── LICENSE
        ├── launch/patrol.launch.py
        ├── route_patrol/
        │   ├── __init__.py
        │   ├── chassis_node.py
        │   ├── controller_node.py
        │   └── route_data.py
        ├── resource/
        └── test/
```

## 节点与控制原理

| 节点 | 订阅 | 发布 | 职责 |
| --- | --- | --- | --- |
| `controller_node` | `/position`，`geometry_msgs/msg/Point` | `/cmd_vel`，`geometry_msgs/msg/Twist` | 路线生成、目标切换、速度控制、到达判断 |
| `chassis_node` | `/cmd_vel`，`geometry_msgs/msg/Twist` | `/position`，`geometry_msgs/msg/Point` | 速度限幅、位置积分、位置反馈 |

底盘使用 `time.monotonic()` 计算实际时间差，执行：

```text
x = x + vx × dt
y = y + vy × dt
```

位置更新定时器和主控制定时器的周期均为 `0.05 s`。底盘在接收新速度时，先用旧速度积分到当前时刻，再采用新的限幅速度。

主控制采用比例控制：`vx = 0.5 × dx`、`vy = 0.5 × dy`。如果任一速度分量的绝对值超过 `2 m/s`，则将速度沿目标方向归一化为合速度 `2 m/s`，保持方向。接近目标时逐渐减速，到达容差内后发送零速度。

## 本机运行

已在 Ubuntu 22.04、ROS2 Humble 环境中进行人工运行验证。需要 ROS2 Humble、Python 3、colcon，以及 `rclpy`、`geometry_msgs`、`launch`、`launch_ros`。

以下构建命令从仓库根目录执行：

```bash
source /opt/ros/humble/setup.bash
cd ros2_ws
colcon build
source install/setup.bash
```

构建应在 `ros2_ws` 中执行。使用普通 `colcon build` 时，修改源码后需要重新构建并重启节点。

### Launch 统一启动

在已加载工作空间环境的终端执行指定终点任务：

```bash
ros2 launch route_patrol patrol.launch.py mode:=point start:=8 end:=4
```

或巡检一圈：

```bash
ros2 launch route_patrol patrol.launch.py mode:=patrol start:=7
```

两条命令分别运行，每次测试结束后按 `Ctrl+C` 停止上一轮。Launch 会把同一个起点传给两个节点。

| 参数 | 类型 | Launch/节点默认值 | 说明 |
| --- | --- | --- | --- |
| `mode` | 字符串 | `point` | `point` 或 `patrol`；仅主控制使用 |
| `start` | 整数 | `1` | 起点编号，两个节点必须一致 |
| `end` | 整数 | `5` | 终点编号，仅 `point` 模式使用 |

路径点编号为 1～8。非法模式或非法点编号会引发错误；`patrol` 模式不使用 `end`。

### 使用 ros2 run 分别启动

每个终端都需加载 ROS2 和工作空间环境。终端一启动底盘：

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run route_patrol chassis_node --ros-args -p start:=8
```

终端二在同一个 `ros2_ws` 目录中启动主控制：

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run route_patrol controller_node --ros-args -p mode:=point -p start:=8 -p end:=4
```

需要详细日志时，可在节点命令末尾增加 `--log-level debug`，例如：

```bash
ros2 run route_patrol controller_node --ros-args -p start:=8 -p end:=4 --log-level debug
```

## Docker 运行

需要已运行的 Docker Engine，且能够访问 Docker Hub 和软件包仓库。基础镜像为 `ros:humble-ros-base-jammy`。

以下命令从仓库根目录执行：

```bash
docker build -t route-patrol:humble .
docker run --rm -it --name route-patrol-test route-patrol:humble
```

默认执行 `point` 模式的 `8 → 4` 任务。容器入口脚本自动加载 ROS2 和容器内工作空间环境，无需在宿主机执行 `source`。

覆盖默认命令，执行巡检：

```bash
docker run --rm -it --name route-patrol-test route-patrol:humble ros2 launch route_patrol patrol.launch.py mode:=patrol start:=7
```

完成后按 `Ctrl+C` 停止。`--rm` 会删除退出的容器，但保留镜像。

## Docker Compose 一键启动

Compose 启动一个容器，由容器内的 Launch 同时启动主控制和底盘节点。

首次构建或修改源码后，从仓库根目录执行：

```bash
docker compose up --build
```

已有镜像且源码未改时：

```bash
docker compose up
```

默认执行 `mode=point、start=8、end=4`。可通过环境变量指定任务：

```bash
MODE=point START=8 END=4 docker compose up
```

```bash
MODE=patrol START=7 docker compose up
```

这些命令分别运行。切换任务前先按 `Ctrl+C`，再执行：

```bash
docker compose down
```

该命令移除本项目的 Compose 容器与网络，保留镜像。仅修改模式和起终点不需要重新构建；修改 Python 源码、场地坐标或 Dockerfile 后，使用 `docker compose up --build`。

## 日志与验证

指定终点任务的关键日志应依次包含：

```text
Initial position: start=8, x=-1.0, y=1.0
Route: [8, 3, 6, 1, 4]
Reached waypoint: 3
Next waypoint: 6
Reached waypoint: 6
Next waypoint: 1
Reached waypoint: 1
Next waypoint: 4
Reached waypoint: 4
Task completed: end = 4 | Final position: x=..., y=...
```

两个节点的启动日志顺序可能不同，运行过程中还会穿插每秒一次的底盘状态日志。

开发过程中已人工验证速度限幅、零速度保持位置、单段运动、多点运动、起终点相同、非默认起点、完整巡检，以及 Launch、Docker、Compose 启动。以下为部分实测输出，最终值可能因调度时序略有差异：

| 场景 | 路线 | 实测最终位置 / m |
| --- | --- | --- |
| 指定终点 | `8 → 3 → 6 → 1 → 4` | `(3.992, 2.994)` |
| 完整巡检 | `7 → 2 → 5 → 8 → 3 → 6 → 1 → 4 → 7` | `(-0.990, 2.002)` |
| 起终点相同 | `[7]` | `(-1.000, 2.000)`，保持静止 |

日志坐标保留三位小数；到达判断使用未舍入的内部数值。用显示值重新计算距离可能略大于 `0.01 m`。

如需保存完整 Compose 输出，可在仓库根目录执行：

```bash
mkdir -p results
MODE=point START=8 END=4 docker compose up 2>&1 | tee results/point_8_to_4.txt
```

任务结束后按 `Ctrl+C` 并执行 `docker compose down`，再记录巡检任务：

```bash
MODE=patrol START=7 docker compose up 2>&1 | tee results/patrol_from_7.txt
```

同名结果文件会被覆盖。README 中的示例不能替代完整运行记录；提交时请另外保留日志或截图。

## 当前实现的约定与限制

- 运动模型假设 x、y 速度位于同一个固定坐标系，不模拟朝向、加速度或真实硬件误差。
- 使用真实经过的时间积分，未支持 ROS2 `/clock` 仿真时间。
- 采用 1 厘米到达容差，不会将积分位置强行改成路径点坐标；切换后的下一段从实际估计位置开始，可能与理想线段存在厘米级偏差。
- 任务完成后持续发布零速度，节点保持运行，使用 `Ctrl+C` 结束进程。
- 底盘没有速度指令超时保护。若只停止主控制节点，底盘可能继续使用最后的非零速度；测试结束应停止整组节点。
- 独立启动时需自行确保两个节点的 `start` 一致；建议使用 Launch 或 Compose。
- 本文记录的是人工运行验证；仓库中的模板测试不代表已经通过完整的自动化验收。

## Git 与许可证

项目使用 Git 记录各开发阶段，`.gitignore` 排除 `build/`、`install/`、`log/` 及 Python 缓存，`.dockerignore` 排除不需要的构建上下文内容。

ROS2 功能包声明采用 Apache-2.0 许可证，详见 [LICENSE](ros2_ws/src/route_patrol/LICENSE)。
