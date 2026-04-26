from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    pkg_share = get_package_share_directory('xr_hand_pipeline')
    default_rviz_config = os.path.join(pkg_share, 'rviz', 'hand_pose.rviz')

    rviz_arg = DeclareLaunchArgument(
        'rviz_config',
        default_value=default_rviz_config,
        description='Full path to the RViz config file',
    )

    ws_publisher = Node(
        package='xr_hand_pipeline',
        executable='hand_ws_publisher',
        name='hand_ws_publisher',
        output='screen',
    )

    pose_subscriber = Node(
        package='xr_hand_pipeline',
        executable='hand_pose_subscriber',
        name='hand_pose_subscriber',
        output='screen',
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', LaunchConfiguration('rviz_config')],
        output='screen',
    )

    return LaunchDescription([
        rviz_arg,
        ws_publisher,
        pose_subscriber,
        rviz,
    ])
