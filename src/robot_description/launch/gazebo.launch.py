import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory("robot_description")
    with open(os.path.join(pkg, "urdf", "robot_description.urdf")) as f:
        robot_description = f.read()
    bridge_config = os.path.join(pkg, "config", "gz_bridge.yaml")
    gz_launch = os.path.join(get_package_share_directory("ros_gz_sim"), "launch", "gz_sim.launch.py")

    return LaunchDescription([
        # Para que Gazebo encuentre las mallas
        AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", os.path.dirname(pkg)),
        # Gazebo con mundo vacio
        IncludeLaunchDescription(PythonLaunchDescriptionSource(gz_launch),
                                 launch_arguments={"gz_args": "-r empty.sdf"}.items()),
        # Publica el URDF y calcula /tf
        Node(package="robot_state_publisher", executable="robot_state_publisher", output="screen",
             parameters=[{"robot_description": robot_description, "use_sim_time": True}]),
        # Mete el robot al mundo
        Node(package="ros_gz_sim", executable="create", output="screen",
             arguments=["-topic", "robot_description", "-name", "colmibot", "-z", "0.02"]),
        # Puente ROS 2 <-> Gazebo
        Node(package="ros_gz_bridge", executable="parameter_bridge", output="screen",
             parameters=[{"config_file": bridge_config, "use_sim_time": True}]),
        # Joystick
        Node(package="joy", executable="joy_node", output="screen"),
        # Nuestro nodo de Turtlesim, redirigido a /cmd_vel
        Node(package="colmibotbasics", executable="play_station_turtle_controller", output="screen",
             remappings=[("/turtle1/cmd_vel", "/cmd_vel")]),
    ])