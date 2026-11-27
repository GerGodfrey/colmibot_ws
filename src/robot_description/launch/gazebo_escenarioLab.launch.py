import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    AppendEnvironmentVariable,
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory("robot_description")
    urdf_path = os.path.join(pkg, "urdf", "robot_description.urdf")
    with open(urdf_path) as f:
        robot_description = f.read().replace("package://robot_description", f"file://{pkg}")

    bridge_config = os.path.join(pkg, "config", "gz_bridge.yaml")
    world_path = os.path.join(pkg, "worlds", "escenarioLab.sdf")
    persona_sdf = os.path.join(pkg, "worlds", "persona_geometrica.sdf")
    obstaculo_sdf = os.path.join(pkg, "worlds", "obstaculo_regreso.sdf")
    gz_launch = os.path.join(get_package_share_directory("ros_gz_sim"), "launch", "gz_sim.launch.py")

    obstaculos_arg = DeclareLaunchArgument(
        "obstaculos",
        default_value="true",
        description="Activa (true) o desactiva (false) la persona y el obstaculo de regreso",
    )
    usar_obstaculos = IfCondition(LaunchConfiguration("obstaculos"))

    crear_persona = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=["-file", persona_sdf, "-name", "persona_geometrica"],
    )

    detener_persona_centro = ExecuteProcess(
        cmd=[
            "gz", "topic",
            "-t", "/model/persona_geometrica/cmd_vel",
            "-m", "gz.msgs.Twist",
            "-p", "linear: {y: 0.0}",
        ],
        output="screen",
    )

    regresar_persona = ExecuteProcess(
        cmd=[
            "gz", "topic",
            "-t", "/model/persona_geometrica/cmd_vel",
            "-m", "gz.msgs.Twist",
            "-p", "linear: {y: -0.15}",
        ],
        output="screen",
    )

    detener_persona_origen = ExecuteProcess(
        cmd=[
            "gz", "topic",
            "-t", "/model/persona_geometrica/cmd_vel",
            "-m", "gz.msgs.Twist",
            "-p", "linear: {y: 0.0}",
        ],
        output="screen",
    )

    eliminar_persona = Node(
        package="ros_gz_sim",
        executable="remove",
        output="screen",
        parameters=[{
            "world_name": "escenarioLab",
            "entity_name": "persona_geometrica",
            "entity_type": "MODEL",
        }],
    )

    crear_obstaculo = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=["-file", obstaculo_sdf, "-name", "obstaculo_regreso"],
    )

    return LaunchDescription([
        obstaculos_arg,
        AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", os.path.dirname(pkg)),
        AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", os.path.join(pkg, "models")),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gz_launch),
            launch_arguments={"gz_args": f"-r {world_path}"}.items(),
        ),
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            output="screen",
            parameters=[{"robot_description": robot_description, "use_sim_time": True}],
        ),
        Node(
            package="ros_gz_sim",
            executable="create",
            output="screen",
            arguments=[
                "-topic", "robot_description",
                "-name", "colmibot",
                "-x", "5.5",
                "-y", "0.25",
                "-z", "0.1",
                "-Y", "-1.5708",
            ],
        ),
        # Secuencia sincronizada tras apertura de GUI
        TimerAction(period=15.0, actions=[crear_persona], condition=usar_obstaculos),
        TimerAction(period=19.5, actions=[detener_persona_centro], condition=usar_obstaculos),
        TimerAction(period=25.0, actions=[regresar_persona], condition=usar_obstaculos),
        TimerAction(period=29.5, actions=[detener_persona_origen], condition=usar_obstaculos),
        TimerAction(period=30.0, actions=[eliminar_persona], condition=usar_obstaculos),
        TimerAction(period=35.0, actions=[crear_obstaculo], condition=usar_obstaculos),

        Node(
            package="ros_gz_bridge",
            executable="parameter_bridge",
            output="screen",
            parameters=[{"config_file": bridge_config, "use_sim_time": True}],
        ),
        Node(package="joy", executable="joy_node", output="screen"),
        Node(
            package="colmibotbasics",
            executable="play_station_turtle_controller",
            output="screen",
            remappings=[("/turtle1/cmd_vel", "/cmd_vel")],
        ),
    ])