import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command

def generate_launch_description():
    gazebo_ros_pkg = get_package_share_directory('gazebo_ros')
    dobot_gazebo_pkg = get_package_share_directory('dobot_gazebo')
    mg400_desc_pkg = get_package_share_directory('mg400_description')

    models_path = os.path.abspath(os.path.join(mg400_desc_pkg, '..'))
    world_file = os.path.join(dobot_gazebo_pkg, 'worlds', 'cubes.world')
    xacro_file = os.path.join(mg400_desc_pkg, 'urdf', 'mg400.urdf.xacro')

    set_gazebo_model_path = SetEnvironmentVariable(
        name='GAZEBO_MODEL_PATH',
        value=models_path + ':' + os.environ.get('GAZEBO_MODEL_PATH', '')
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_pkg, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'world': world_file,
            'paused': 'true'
        }.items()
    )

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': Command(['xacro ', xacro_file])}]
    )

    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'mg400_robot'],
        output='screen'
    )

    dobot_main = Node(
        package='dobot_logic',
        executable='main',
        output='screen'
    )

    delayed_spawn = TimerAction(period=10.0, actions=[spawn_entity])
    delayed_main = TimerAction(period=12.0, actions=[dobot_main])

    dobot_bridge = Node(package='dobot_logic', executable='bridge', output='screen')
    delayed_bridge = TimerAction(period=13.0, actions=[dobot_bridge])

    return LaunchDescription([
        set_gazebo_model_path,
        gazebo,
        node_robot_state_publisher,
        delayed_spawn,
        delayed_main,
        delayed_bridge,
    ])