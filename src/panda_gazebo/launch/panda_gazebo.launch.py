from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    pkg = get_package_share_directory("panda_gazebo")

    urdf_path = os.path.join(pkg, "urdf", "panda.urdf")
    robot_desc = open(urdf_path).read()

    return LaunchDescription([

        # Gazebo
        ExecuteProcess(
            cmd=["gazebo", "--verbose", "-s", "libgazebo_ros_factory.so"],
            output="screen"
        ),

        # controller manager WITH robot_description (CRITICAL FIX)
        Node(
            package="controller_manager",
            executable="ros2_control_node",
            parameters=[{
                "robot_description": robot_desc,
            }],
            output="screen"
        ),

        # controllers
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=["joint_state_broadcaster"]
        ),

        Node(
            package="controller_manager",
            executable="spawner",
            arguments=["panda_arm_controller"]
        ),
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            parameters=[{"robot_description": robot_desc}]
        ),
    ])
