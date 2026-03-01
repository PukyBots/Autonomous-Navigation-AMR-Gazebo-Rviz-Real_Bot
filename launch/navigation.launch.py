import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.actions import TimerAction


def generate_launch_description():

    package_name = 'diff_drive_robot'
    pkg_share = get_package_share_directory(package_name)
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')

    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')
    map_yaml_file = LaunchConfiguration('map')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true'
    )

    declare_params_file = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(pkg_share, 'config', 'nav2_params.yaml')
    )

    declare_map_yaml = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(pkg_share, 'maps', 'my_map.yaml')
    )

    # --- NAV2 ---
    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'params_file': params_file,
            'map': map_yaml_file,
            'autostart': 'true',
            'use_composition': 'False'
        }.items()
    )

    # --- RVIZ ---
    rviz_node = TimerAction(
        period=5.0,   # wait 5 seconds before launching RViz
        actions=[
            Node(
                package='rviz2',
                executable='rviz2',
                name='rviz2',
                arguments=[
                    '-d',
                    os.path.join(nav2_bringup_dir, 'rviz', 'nav2_default_view.rviz')

                ],
                parameters=[{'use_sim_time': use_sim_time}],
                output='screen'
            )
        ]
)

    robot_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, 'launch', 'robot.launch.py')
        ),
        launch_arguments={'use_sim_time': 'true'}.items()
)

    # --- NAV2 (delay start so robot TF is ready) ---
    nav2_launch = TimerAction(
        period=5.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')
                ),
                launch_arguments={
                    'use_sim_time': use_sim_time,
                    'params_file': params_file,
                    'map': map_yaml_file,
                    'autostart': 'true',
                    'use_composition': 'False'
                }.items()
            )
        ]
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_params_file,
        declare_map_yaml,
        robot_launch,
        nav2_launch,
        rviz_node
    ])


