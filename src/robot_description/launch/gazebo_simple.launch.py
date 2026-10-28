
import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    ExecuteProcess,
    SetEnvironmentVariable,
    AppendEnvironmentVariable,
    TimerAction,
)
from launch_ros.actions import Node


def generate_launch_description():

    pkg = get_package_share_directory("robot_description")

    robot_file = os.path.join(
        pkg, "urdf", "colmibot_gazebo.urdf"
    )

    bridge_config = os.path.join(
        pkg, "config", "gz_bridge.yaml"
    )

    return LaunchDescription([

        # 1. Configuracion para Parallels
        AppendEnvironmentVariable(
            "GZ_SIM_RESOURCE_PATH",
            os.path.dirname(pkg)
        ),

        SetEnvironmentVariable(
            "LIBGL_ALWAYS_SOFTWARE", "1"
        ),

        SetEnvironmentVariable(
            "QT_QPA_PLATFORM", "xcb"
        ),

        # 2. Servidor de Gazebo
        ExecuteProcess(
            cmd=[
                "gz", "sim", "-s", "-r",
                "-v", "4", "empty.sdf"
            ],
            output="screen"
        ),

        # 3. GUI con OGRE 1
        TimerAction(
            period=3.0,
            actions=[
                ExecuteProcess(
                    cmd=[
                        "gz", "sim", "-g",
                        "-v", "4",
                        "--render-engine", "ogre"
                    ],
                    output="screen"
                )
            ]
        ),

        # 4. Descripcion del robot
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            parameters=[{
                "robot_description": open(robot_file).read(),
                "use_sim_time": True
            }],
            output="screen"
        ),

        # 5. Insertar Colmibot simplificado
        TimerAction(
            period=6.0,
            actions=[
                Node(
                    package="ros_gz_sim",
                    executable="create",
                    arguments=[
                        "-file", robot_file,
                        "-name", "colmibot",
                        "-z", "0.2"
                    ],
                    output="screen"
                )
            ]
        ),

        # 6. Puente ROS 2 - Gazebo
        Node(
            package="ros_gz_bridge",
            executable="parameter_bridge",
            parameters=[{
                "config_file": bridge_config,
                "use_sim_time": True
            }],
            output="screen"
        ),

        # 7. Joystick PlayStation
        Node(
            package="joy",
            executable="joy_node",
            output="screen"
        ),

        # 8. Controlador Colmibot
        Node(
            package="colmibotbasics",
            executable="colmibot_controller",
            output="screen"
        ),
    ])
