from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    return LaunchDescription([

        Node(
            package='turtlesim',
            executable='turtlesim_node',
            output='screen'
        ),

        Node(
            package='joy',
            executable='joy_node',
            output='screen'
        ),

        Node(
            package='colmibotbasics',
            executable='play_station_turtle_controller',
            output='screen'
        ),

    ])
