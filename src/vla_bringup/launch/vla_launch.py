from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription([

        Node(
            package='vla_perception',
            executable='perception',
            output='screen'
        ),

        Node(
            package='vla_reasoning',
            executable='reasoning_node',
            output='screen'
        ),

        Node(
            package='vla_executor',
            executable='vla_executor',
            output='screen'
        ),
    ])
