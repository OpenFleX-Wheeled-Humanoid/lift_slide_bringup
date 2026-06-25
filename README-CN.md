# lift_slide_bringup

[English](./README.md) | 中文

---

![封面](./image/cover.gif)

升降滑台模组的顶层启动包，启动完整系统，包括 robot_state_publisher、controller_manager、所有控制器，以及可选的 RViz。

## 功能

- 单一启动文件启动完整的升降滑台系统
- 可切换仿真或真实硬件模式
- 控制器定时启动，延迟可配置
- controller_manager 退出时优雅关闭整个系统
- 从 `config/ros2_controllers.yaml` 加载默认值，启动参数可覆盖

## 包内容

| 路径 | 说明 |
|------|------|
| `launch/lift_slide_bringup.launch.py` | 主系统启动文件 |
| `config/ros2_controllers.yaml` | 控制器管理器与硬件默认参数 |
| `rviz/bringup.rviz` | 带控制面板的 RViz 配置 |

## 启动

```bash
# 仿真模式（默认）

---
ros2 launch lift_slide_bringup lift_slide_bringup.launch.py

# 真实硬件

---
ros2 launch lift_slide_bringup lift_slide_bringup.launch.py use_fake_hardware:=false can_interface:=can3 node_id:=16
```

## 主要启动参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `use_fake_hardware` | `true` | 是否启用仿真模式 |
| `can_interface` | `can3` | SocketCAN 接口名称 |
| `node_id` | `16` | CANopen 节点 ID |
| `min_height` | `-0.650` | 最小行程位置（米） |
| `max_height` | `0.300` | 最大行程位置（米） |
| `max_velocity_mps` | `0.10` | 最大速度（米/秒） |
| `start_rviz` | `true` | 是否启动 RViz |
| `homing_method` | `27` | CANopen 回零方法（CiA402 6098h） |
| `invert_command` | `true` | 是否反向控制指令 |
| `invert_feedback` | `true` | 是否反向反馈方向 |

## 启动的控制器

- `joint_state_broadcaster` - 标准关节状态广播器
- `lift_velocity_controller` - 速度指令转发控制器（启动时为非活跃状态）
- `lift_position_controller` - 位置指令转发控制器（启动时为非活跃状态）
- `lift_manual_position_controller` - 手动步进/点动位置控制器（活跃状态）
- `lift_state_controller` - 硬件状态到 ROS 话题/服务的桥接控制器

## 编译

```bash
colcon build --packages-select lift_slide_bringup
source install/setup.bash
```

## 前置依赖

- ROS 2（Humble/Iron）
- lift_slide_description、lift_slide_driver、lift_slide_panel 功能包
- robot_state_publisher、controller_manager、joint_state_broadcaster
- xacro、rviz2

## 许可证

本包通过 知识共享 署名-非商业性使用-相同方式共享 4.0 国际许可协议 (CC BY-NC-SA 4.0) 进行许可。

版权所有 (c) 2026 成都长数机器人有限公司 (Chengdu Changshu Robot Co., Ltd.)

详情请参阅 [LICENSE](LICENSE) 文件或访问：http://creativecommons.org/licenses/by-nc-sa/4.0/

## 致谢

本包是 OpenFlex 全身人形机器人平台生态系统的一部分，专为人形机器人领域的研究和工业应用而开发。

---

## 📞 联系我们

### 成都长数机器人有限公司
**Chengdu Changshu Robotics Co., Ltd.**

| 联系方式 | 信息 |
|---------|------|
| 📧 邮箱 | openarmrobot@gmail.com |
| 📱 电话/微信 | +86-17746530375 |
| 🌐 官网 | https://openarmx.com/ |
| 🌐 文档 | http://docs.openarmx.com/ |
| 📍 地址 | 天津市西青区・稻潮机器人体验基地（明日之城）・天津市人形机器人中心 |
| 👤 联系人 | 王先生 |
