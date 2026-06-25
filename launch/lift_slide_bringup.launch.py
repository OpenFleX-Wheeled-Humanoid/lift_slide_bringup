#!/usr/bin/env python3

import os
import yaml

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler, Shutdown
from launch.actions import TimerAction
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory


def _load_lift_defaults():
    defaults = {
        'can_interface': 'can3',
        'node_id': 16,
        'min_position_m': -0.650,
        'max_position_m': 0.300,
        'max_velocity_mps': 0.10,
        'lower_switch_position_m': 0.000,
        'home_switch_position_m': 0.650,
        'upper_switch_position_m': 0.950,
        'switch_position_tolerance_m': 0.008,
        'counts_per_meter': 2000000.0,
        'counts_per_revolution': 10000.0,
        'profile_acceleration': 50000,
        'profile_deceleration': 50000,
        'homing_method': 27,
        'homing_speed_mps': 0.010,
        'homing_low_speed_ratio': 0.2,
        'homing_acceleration': 50000,
        'homing_timeout_sec': 60.0,
        'homing_configure_di': True,
        'di_active_low': True,
        'di6_not_func': 2,
        'di4_homing_func': 22,
        'di5_pot_func': 1,
        'home_di_channel': 4,
        'pot_di_channel': 5,
        'not_di_channel': 6,
        'invert_command': True,
        'invert_feedback': True,
        'command_timeout_sec': 0.5,
        'sdo_timeout_sec': 0.20,
        'feedback_poll_rate_hz': 20.0,
        'joint_state_broadcaster_delay': 2.0,
        'velocity_controller_delay': 3.0,
        'position_controller_delay': 3.5,
        'manual_position_controller_delay': 3.8,
        'state_controller_delay': 2.5,
        'start_rviz': True,
        'rviz_delay': 4.0,
    }
    config_path = os.path.join(
        get_package_share_directory('lift_slide_bringup'),
        'config',
        'ros2_controllers.yaml',
    )
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        joint = data.get('lift_slide_defaults', {}).get('ros__parameters', {})
        for key in defaults:
            if key in joint:
                defaults[key] = joint[key]
    except Exception as exc:
        print(f'[lift_slide_bringup] Failed to load {config_path}, using built-in defaults: {exc}')
    def launch_value(value):
        if isinstance(value, bool):
            return 'true' if value else 'false'
        return str(value)

    return {key: launch_value(value) for key, value in defaults.items()}


def generate_launch_description():
    lift_defaults = _load_lift_defaults()

    default_controllers_path = PathJoinSubstitution(
        [FindPackageShare('lift_slide_bringup'), 'config', 'ros2_controllers.yaml']
    )
    default_rviz_path = PathJoinSubstitution(
        [FindPackageShare('lift_slide_bringup'), 'rviz', 'bringup.rviz']
    )
    model_path = PathJoinSubstitution(
        [FindPackageShare('lift_slide_description'), 'urdf', 'lift_slide_module.urdf.xacro']
    )

    controllers_file_arg = DeclareLaunchArgument(
        'controllers_file',
        default_value=default_controllers_path,
        description='ros2_control 控制器管理器配置文件'
    )
    can_interface_arg = DeclareLaunchArgument(
        'can_interface',
        default_value=lift_defaults['can_interface'],
        description='CAN 接口名'
    )
    node_id_arg = DeclareLaunchArgument(
        'node_id',
        default_value=lift_defaults['node_id'],
        description='CANopen 节点ID'
    )
    use_fake_hardware_arg = DeclareLaunchArgument(
        'use_fake_hardware',
        default_value='true',
        description='是否启用仿真模式'
    )
    min_height_arg = DeclareLaunchArgument(
        'min_height',
        default_value=lift_defaults['min_position_m'],
        description='升降最小位移（米）'
    )
    max_height_arg = DeclareLaunchArgument(
        'max_height',
        default_value=lift_defaults['max_position_m'],
        description='升降最大位移（米）'
    )
    max_velocity_mps_arg = DeclareLaunchArgument(
        'max_velocity_mps',
        default_value=lift_defaults['max_velocity_mps'],
        description='升降最大速度（米每秒）'
    )
    counts_per_meter_arg = DeclareLaunchArgument(
        'counts_per_meter',
        default_value=lift_defaults['counts_per_meter'],
        description='编码器计数到米换算系数'
    )
    counts_per_revolution_arg = DeclareLaunchArgument(
        'counts_per_revolution',
        default_value=lift_defaults['counts_per_revolution'],
        description='编码器每转计数'
    )
    profile_acceleration_arg = DeclareLaunchArgument(
        'profile_acceleration',
        default_value=lift_defaults['profile_acceleration'],
        description='CANopen 6083 加速度 (pulses/s²)'
    )
    profile_deceleration_arg = DeclareLaunchArgument(
        'profile_deceleration',
        default_value=lift_defaults['profile_deceleration'],
        description='CANopen 6084 减速度 (pulses/s²)'
    )
    homing_method_arg = DeclareLaunchArgument(
        'homing_method',
        default_value=lift_defaults['homing_method'],
        description='CANopen 6098 寻零方法'
    )
    homing_speed_mps_arg = DeclareLaunchArgument(
        'homing_speed_mps',
        default_value=lift_defaults['homing_speed_mps'],
        description='硬件回零速度（米每秒）'
    )
    homing_low_speed_ratio_arg = DeclareLaunchArgument(
        'homing_low_speed_ratio',
        default_value=lift_defaults['homing_low_speed_ratio'],
        description='硬件回零低速比例（相对 homing_speed_mps）'
    )
    homing_acceleration_arg = DeclareLaunchArgument(
        'homing_acceleration',
        default_value=lift_defaults['homing_acceleration'],
        description='CANopen 609A 寻零加速度 (pulses/s²)'
    )
    homing_timeout_sec_arg = DeclareLaunchArgument(
        'homing_timeout_sec',
        default_value=lift_defaults['homing_timeout_sec'],
        description='硬件回零超时（秒）'
    )
    homing_configure_di_arg = DeclareLaunchArgument(
        'homing_configure_di',
        default_value=lift_defaults['homing_configure_di'],
        description='是否在回零前配置 DI4/5/6 功能'
    )
    lower_switch_position_arg = DeclareLaunchArgument(
        'lower_switch_position_m',
        default_value=lift_defaults['lower_switch_position_m'],
        description='下限位在滑台物理坐标中的位置（米）'
    )
    home_switch_position_arg = DeclareLaunchArgument(
        'home_switch_position_m',
        default_value=lift_defaults['home_switch_position_m'],
        description='零点开关在滑台物理坐标中的位置（米）'
    )
    upper_switch_position_arg = DeclareLaunchArgument(
        'upper_switch_position_m',
        default_value=lift_defaults['upper_switch_position_m'],
        description='上限位在滑台物理坐标中的位置（米）'
    )
    switch_position_tolerance_arg = DeclareLaunchArgument(
        'switch_position_tolerance_m',
        default_value=lift_defaults['switch_position_tolerance_m'],
        description='软件回零开关位置容差（米）'
    )
    di_active_low_arg = DeclareLaunchArgument(
        'di_active_low',
        default_value=lift_defaults['di_active_low'],
        description='DI 物理输入是否低电平触发（NPN 常闭 b 接法为 true）'
    )
    di6_not_func_arg = DeclareLaunchArgument(
        'di6_not_func',
        default_value=lift_defaults['di6_not_func'],
        description='DI6 功能码（默认 NOT=0x02）'
    )
    di4_homing_func_arg = DeclareLaunchArgument(
        'di4_homing_func',
        default_value=lift_defaults['di4_homing_func'],
        description='DI4 功能码（默认 HOME=0x16）'
    )
    di5_pot_func_arg = DeclareLaunchArgument(
        'di5_pot_func',
        default_value=lift_defaults['di5_pot_func'],
        description='DI5 功能码（默认 POT=0x01）'
    )
    home_di_channel_arg = DeclareLaunchArgument(
        'home_di_channel',
        default_value=lift_defaults['home_di_channel'],
        description='HOME 传感器接入的 DI 通道号'
    )
    pot_di_channel_arg = DeclareLaunchArgument(
        'pot_di_channel',
        default_value=lift_defaults['pot_di_channel'],
        description='下限位传感器接入的 DI 通道号'
    )
    not_di_channel_arg = DeclareLaunchArgument(
        'not_di_channel',
        default_value=lift_defaults['not_di_channel'],
        description='上限位传感器接入的 DI 通道号'
    )
    invert_command_arg = DeclareLaunchArgument(
        'invert_command',
        default_value=lift_defaults['invert_command'],
        description='是否反向控制指令'
    )
    invert_feedback_arg = DeclareLaunchArgument(
        'invert_feedback',
        default_value=lift_defaults['invert_feedback'],
        description='是否反向位置速度反馈'
    )
    command_timeout_sec_arg = DeclareLaunchArgument(
        'command_timeout_sec',
        default_value=lift_defaults['command_timeout_sec'],
        description='指令超时（秒）'
    )
    sdo_timeout_sec_arg = DeclareLaunchArgument(
        'sdo_timeout_sec',
        default_value=lift_defaults['sdo_timeout_sec'],
        description='SDO超时（秒）'
    )
    feedback_poll_rate_hz_arg = DeclareLaunchArgument(
        'feedback_poll_rate_hz',
        default_value=lift_defaults['feedback_poll_rate_hz'],
        description='反馈轮询频率（Hz）'
    )
    start_rviz_arg = DeclareLaunchArgument(
        'start_rviz',
        default_value=lift_defaults['start_rviz'],
        description='是否启动 RViz'
    )
    rviz_config_arg = DeclareLaunchArgument(
        'rviz_config',
        default_value=default_rviz_path,
        description='RViz 配置文件'
    )

    robot_description_content = ParameterValue(
        Command(
            [
                'xacro ',
                model_path,
                ' min_height:=',
                LaunchConfiguration('min_height'),
                ' max_height:=',
                LaunchConfiguration('max_height'),
                ' ros2_control:=true',
                ' use_fake_hardware:=',
                LaunchConfiguration('use_fake_hardware'),
                ' can_interface:=',
                LaunchConfiguration('can_interface'),
                ' node_id:=',
                LaunchConfiguration('node_id'),
                ' counts_per_meter:=',
                LaunchConfiguration('counts_per_meter'),
                ' counts_per_revolution:=',
                LaunchConfiguration('counts_per_revolution'),
                ' profile_acceleration:=',
                LaunchConfiguration('profile_acceleration'),
                ' profile_deceleration:=',
                LaunchConfiguration('profile_deceleration'),
                ' homing_method:=',
                LaunchConfiguration('homing_method'),
                ' homing_speed_mps:=',
                LaunchConfiguration('homing_speed_mps'),
                ' homing_low_speed_ratio:=',
                LaunchConfiguration('homing_low_speed_ratio'),
                ' homing_acceleration:=',
                LaunchConfiguration('homing_acceleration'),
                ' homing_timeout_sec:=',
                LaunchConfiguration('homing_timeout_sec'),
                ' homing_configure_di:=',
                LaunchConfiguration('homing_configure_di'),
                ' lower_switch_position_m:=',
                LaunchConfiguration('lower_switch_position_m'),
                ' home_switch_position_m:=',
                LaunchConfiguration('home_switch_position_m'),
                ' upper_switch_position_m:=',
                LaunchConfiguration('upper_switch_position_m'),
                ' switch_position_tolerance_m:=',
                LaunchConfiguration('switch_position_tolerance_m'),
                ' di_active_low:=',
                LaunchConfiguration('di_active_low'),
                ' di6_not_func:=',
                LaunchConfiguration('di6_not_func'),
                ' di4_homing_func:=',
                LaunchConfiguration('di4_homing_func'),
                ' di5_pot_func:=',
                LaunchConfiguration('di5_pot_func'),
                ' home_di_channel:=',
                LaunchConfiguration('home_di_channel'),
                ' pot_di_channel:=',
                LaunchConfiguration('pot_di_channel'),
                ' not_di_channel:=',
                LaunchConfiguration('not_di_channel'),
                ' invert_command:=',
                LaunchConfiguration('invert_command'),
                ' invert_feedback:=',
                LaunchConfiguration('invert_feedback'),
                ' max_velocity_mps:=',
                LaunchConfiguration('max_velocity_mps'),
                ' command_timeout_sec:=',
                LaunchConfiguration('command_timeout_sec'),
                ' sdo_timeout_sec:=',
                LaunchConfiguration('sdo_timeout_sec'),
                ' feedback_poll_rate_hz:=',
                LaunchConfiguration('feedback_poll_rate_hz'),
            ]
        ),
        value_type=str,
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='lift_slide_robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_content}],
    )

    ros2_control_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        name='controller_manager',
        output='screen',
        parameters=[
            LaunchConfiguration('controllers_file'),
            {
                'lift_manual_position_controller': {
                    'ros__parameters': {
                        'min_position_m': LaunchConfiguration('min_height'),
                        'max_position_m': LaunchConfiguration('max_height'),
                        'lower_switch_position_m': LaunchConfiguration('lower_switch_position_m'),
                        'home_switch_position_m': LaunchConfiguration('home_switch_position_m'),
                        'upper_switch_position_m': LaunchConfiguration('upper_switch_position_m'),
                    }
                }
            },
            {'robot_description': robot_description_content},
        ],
    )

    joint_state_broadcaster_spawner = TimerAction(
        period=float(lift_defaults['joint_state_broadcaster_delay']),
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=['joint_state_broadcaster', '-c', '/controller_manager'],
                output='screen',
            )
        ]
    )

    lift_velocity_controller_spawner = TimerAction(
        period=float(lift_defaults['velocity_controller_delay']),
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=[
                    'lift_velocity_controller',
                    '-c',
                    '/controller_manager',
                    '--inactive',
                ],
                output='screen',
            )
        ]
    )

    lift_position_controller_spawner = TimerAction(
        period=float(lift_defaults['position_controller_delay']),
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=[
                    'lift_position_controller',
                    '-c',
                    '/controller_manager',
                    '--inactive',
                ],
                output='screen',
            )
        ]
    )

    lift_manual_position_controller_spawner = TimerAction(
        period=float(lift_defaults['manual_position_controller_delay']),
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=[
                    'lift_manual_position_controller',
                    '-c',
                    '/controller_manager',
                ],
                output='screen',
            )
        ]
    )

    lift_state_controller_spawner = TimerAction(
        period=float(lift_defaults['state_controller_delay']),
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=[
                    'lift_state_controller',
                    '-c',
                    '/controller_manager',
                ],
                output='screen',
            )
        ]
    )

    # Graceful shutdown: when controller_manager exits, shut down everything
    shutdown_on_cm_exit = RegisterEventHandler(
        OnProcessExit(
            target_action=ros2_control_node,
            on_exit=[Shutdown(reason='controller_manager exited')],
        )
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='lift_slide_rviz',
        output='screen',
        arguments=[
            '-d', LaunchConfiguration('rviz_config'),
            '--ros-args',
            '-p', ['pos_min:=', LaunchConfiguration('min_height')],
            '-p', ['pos_max:=', LaunchConfiguration('max_height')],
            '-p', 'position_command_topic:=/lift_position_controller/commands',
        ],
        condition=IfCondition(LaunchConfiguration('start_rviz')),
    )

    delayed_rviz_node = TimerAction(
        period=float(lift_defaults['rviz_delay']),
        actions=[rviz_node],
    )

    return LaunchDescription(
        [
            controllers_file_arg,
            use_fake_hardware_arg,
            can_interface_arg,
            node_id_arg,
            min_height_arg,
            max_height_arg,
            max_velocity_mps_arg,
            counts_per_meter_arg,
            counts_per_revolution_arg,
            profile_acceleration_arg,
            profile_deceleration_arg,
            homing_method_arg,
            homing_speed_mps_arg,
            homing_low_speed_ratio_arg,
            homing_acceleration_arg,
            homing_timeout_sec_arg,
            homing_configure_di_arg,
            lower_switch_position_arg,
            home_switch_position_arg,
            upper_switch_position_arg,
            switch_position_tolerance_arg,
            di_active_low_arg,
            di6_not_func_arg,
            di4_homing_func_arg,
            di5_pot_func_arg,
            home_di_channel_arg,
            pot_di_channel_arg,
            not_di_channel_arg,
            invert_command_arg,
            invert_feedback_arg,
            command_timeout_sec_arg,
            sdo_timeout_sec_arg,
            feedback_poll_rate_hz_arg,
            start_rviz_arg,
            rviz_config_arg,
            robot_state_publisher_node,
            ros2_control_node,
            joint_state_broadcaster_spawner,
            lift_velocity_controller_spawner,
            lift_position_controller_spawner,
            lift_manual_position_controller_spawner,
            lift_state_controller_spawner,
            shutdown_on_cm_exit,
            delayed_rviz_node,
        ]
    )
