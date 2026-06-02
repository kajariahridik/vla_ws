import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():

    pkg = get_package_share_directory('vla_simulation')
    gazebo_ros = get_package_share_directory('gazebo_ros')

    world_file = os.path.join(pkg, 'worlds', 'vla_world.world')
    urdf_file = os.path.join(pkg, 'urdf', 'franka_with_camera.urdf')

    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    # Launch gzserver directly with world file
    gzserver = ExecuteProcess(
        cmd=['gzserver', '--verbose', world_file,
             '-s', 'libgazebo_ros_init.so',
             '-s', 'libgazebo_ros_factory.so'],
        output='screen'
    )

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}],
        output='screen'
    )

    # Spawn robot after delay
    spawn_robot = TimerAction(
        period=8.0,
        actions=[Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-entity', 'franka',
                '-file', urdf_file,
                '-x', '0', '-y', '0', '-z', '0'
            ],
            output='screen'
        )]
    )

    # Load controllers after spawn
    load_joint_state_broadcaster = TimerAction(
        period=15.0,
        actions=[ExecuteProcess(
            cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
                 'joint_state_broadcaster'],
            output='screen'
        )]
    )

    load_arm_controller = TimerAction(
        period=18.0,
        actions=[ExecuteProcess(
            cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
                 'panda_arm_controller'],
            output='screen'
        )]
    )

    return LaunchDescription([
        gzserver,
        robot_state_publisher,
        spawn_robot,
        load_joint_state_broadcaster,
        load_arm_controller,
    ])
