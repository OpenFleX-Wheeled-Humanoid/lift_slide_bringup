# lift_slide_bringup

English | [中文](./README-CN.md)

---

![Cover](./image/cover.gif)

Top-level bringup package that launches the complete lift-slide system, including robot_state_publisher, controller_manager, all controllers, and optionally RViz.

## Features

- Single launch file to bring up the full lift-slide stack
- Configurable simulation or real hardware mode
- Timed controller spawning with configurable delays
- Graceful shutdown on controller_manager exit
- Loads defaults from `config/ros2_controllers.yaml` with launch argument overrides

## Package Contents

| Path | Description |
|------|-------------|
| `launch/lift_slide_bringup.launch.py` | Main system launch file |
| `config/ros2_controllers.yaml` | Controller manager and hardware default parameters |
| `rviz/bringup.rviz` | RViz configuration with panel plugin |

## Launch

```bash
# Simulation mode (default)

---
ros2 launch lift_slide_bringup lift_slide_bringup.launch.py

# Real hardware

---
ros2 launch lift_slide_bringup lift_slide_bringup.launch.py use_fake_hardware:=false can_interface:=can3 node_id:=16
```

## Key Launch Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `use_fake_hardware` | `true` | Enable simulation mode |
| `can_interface` | `can3` | SocketCAN interface name |
| `node_id` | `16` | CANopen node ID |
| `min_height` | `-0.650` | Minimum travel position (m) |
| `max_height` | `0.300` | Maximum travel position (m) |
| `max_velocity_mps` | `0.10` | Maximum velocity (m/s) |
| `start_rviz` | `true` | Launch RViz with panel |
| `homing_method` | `27` | CANopen homing method (CiA402 6098h) |
| `invert_command` | `true` | Invert command direction |
| `invert_feedback` | `true` | Invert feedback direction |

## Controllers Spawned

- `joint_state_broadcaster` - Standard joint state broadcaster
- `lift_velocity_controller` - Velocity command forwarding (spawned inactive)
- `lift_position_controller` - Position command forwarding (spawned inactive)
- `lift_manual_position_controller` - Manual step/jog position controller (active)
- `lift_state_controller` - Status bridge between hardware interface and ROS topics/services

## Build

```bash
colcon build --packages-select lift_slide_bringup
source install/setup.bash
```

## Prerequisites

- ROS 2 (Humble/Iron)
- lift_slide_description, lift_slide_driver, lift_slide_panel packages
- robot_state_publisher, controller_manager, joint_state_broadcaster
- xacro, rviz2

## License

This package is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0).

Copyright (c) 2026 Chengdu Changshu Robot Co., Ltd.

For details, please refer to the [LICENSE](LICENSE) file or visit: http://creativecommons.org/licenses/by-nc-sa/4.0/

## Acknowledgments

This package is part of the OpenFlex full-body humanoid robot platform ecosystem, developed specifically for research and industrial applications in the humanoid robotics field.

---

## 📞 Contact Us

### Chengdu Changshu Robot Co., Ltd.
**Chengdu Changshu Robotics Co., Ltd.**

| Contact | Information |
|---------|-------------|
| 📧 Email | openarmrobot@gmail.com |
| 📱 Phone/WeChat | +86-17746530375 |
| 🌐 Website | https://openarmx.com/ |
| 🌐 Docs | http://docs.openarmx.com/ |
| 📍 Address | Tianjin Xiqing District · Daochao Robot Experience Base (City of Tomorrow) · Tianjin Humanoid Robot Center |
| 👤 Contact Person | Mr. Wang |
