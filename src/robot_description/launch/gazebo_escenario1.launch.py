import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg = get_package_share_directory("robot_description")
    urdf_path = os.path.join(pkg, "urdf", "robot_description.urdf")
    with open(urdf_path) as f:
        robot_description = f.read().replace("package://robot_description", f"file://{pkg}")

    bridge_config = os.path.join(pkg, "config", "gz_bridge.yaml")
    world_path = os.path.join(pkg, "worlds", "escenario1.sdf")
    gz_launch = os.path.join(get_package_share_directory("ros_gz_sim"), "launch", "gz_sim.launch.py")

    return LaunchDescription([
        AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", os.path.dirname(pkg)),
        AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", os.path.join(pkg, "models")),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gz_launch),
            launch_arguments={"gz_args": f"-r {world_path}"}.items(),
        ),
        Node(package="robot_state_publisher", executable="robot_state_publisher", output="screen",
             parameters=[{"robot_description": robot_description, "use_sim_time": True}]),
        Node(package="ros_gz_sim", executable="create", output="screen",
             arguments=[
                 "-topic", "robot_description",
                 "-name", "colmibot",
                 "-x", "6.5",
                 "-y", "4.5",
                 "-z", "0.1",
                 "-Y", "-1.5708"
             ]),
        Node(package="ros_gz_bridge", executable="parameter_bridge", output="screen",
             parameters=[{"config_file": bridge_config, "use_sim_time": True}]),
        Node(package="joy", executable="joy_node", output="screen"),
        Node(package="colmibotbasics", executable="play_station_turtle_controller", output="screen",
             remappings=[("/turtle1/cmd_vel", "/cmd_vel")]),
    ])