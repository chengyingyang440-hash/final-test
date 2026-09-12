from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    mode = LaunchConfiguration('mode')
    start = LaunchConfiguration('start')
    end = LaunchConfiguration('end')

    return LaunchDescription([
        DeclareLaunchArgument('mode', default_value='point'),
        DeclareLaunchArgument('start', default_value='1'),
        DeclareLaunchArgument('end', default_value='5'),
        Node(
            package='route_patrol',
            executable='chassis_node',
            output='screen',
            parameters=[{
                'start': ParameterValue(start, value_type=int),
            }],
        ),

        Node(
            package='route_patrol',
            executable='controller_node',
            output='screen',
            parameters=[{
                'mode': ParameterValue(mode, value_type=str),
                'start': ParameterValue(start, value_type=int),
                'end': ParameterValue(end, value_type=int),
            }],
        ),
    ])