# -----------------------------------------------------------------------------
# Copyright 2022 Bernd Pfrommer <bernd.pfrommer@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#

import launch
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode
from launch.substitutions import LaunchConfiguration as LaunchConfig
from launch.actions import DeclareLaunchArgument as LaunchArg
from ament_index_python.packages import get_package_share_directory

camera_params_left = {
    'debug': False,
    'compute_brightness': True,
    'dump_node_map': False,
    'adjust_timestamp': True,
    'frame_rate_auto': 'Off',
    'frame_rate': 1.0,
    'gain_auto': 'Off',
    'gain': 0,
    'exposure_auto': 'Off',
    'exposure_time': 9000,
    'trigger_mode': 'Off',
    'line_selector': 'Line2',
    'line_mode': 'Output',
    'line_source': 'ExposureActive',
    }

camera_params_right = {
    'debug': False,
    'compute_brightness': True,
    'dump_node_map': False,
    'adjust_timestamp': True,
    'gain_auto': 'Off',
    'gain': 0,
    'exposure_auto': 'Off',
    'exposure_time': 9000,
    'trigger_selector': 'FrameStart',
    'trigger_mode': 'On',
    'trigger_source': 'Line3',
    'trigger_delay': 9,
    }


def generate_launch_description():
    """Create synchronized stereo camera."""
    flir_dir = get_package_share_directory('flir_spinnaker_ros2')
    config_dir = flir_dir + '/config/'
    container = ComposableNodeContainer(
            name='stereo_camera_container',
            namespace='',
            package='rclcpp_components',
            executable='component_container',
            composable_node_descriptions=[
                ComposableNode(
                    package='flir_spinnaker_ros2',
                    plugin='flir_spinnaker_ros2::CameraDriver',
                    name=LaunchConfig('cam_0_name'),
                    parameters=[camera_params_left,
                                {'parameter_file': config_dir + 'flea.cfg',
                                 'serial_number': '16362337'}],
                    remappings=[('~/control', '/exposure_control/control'), ],
                    extra_arguments=[{'use_intra_process_comms': True}],
                ),
                ComposableNode(
                    package='flir_spinnaker_ros2',
                    plugin='flir_spinnaker_ros2::CameraDriver',
                    name=LaunchConfig('cam_1_name'),
                    parameters=[camera_params_right,
                                {'parameter_file':
                                 config_dir + 'flea.cfg',
                                 'serial_number': '17476603'}],
                    remappings=[('~/control', '/exposure_control/control'), ],
                    extra_arguments=[{'use_intra_process_comms': True}],
                ),
                ComposableNode(
                    package='cam_sync_ros2',
                    plugin='cam_sync_ros2::CamSync',
                    name='sync',
                    parameters=[],
                    extra_arguments=[{'use_intra_process_comms': True}],
                ),
                ComposableNode(
                    package='exposure_control_ros2',
                    plugin='exposure_control_ros2::ExposureControl',
                    name='exposure_control',
                    parameters=[{'cam_name': LaunchConfig('cam_0_name'),
                                 'max_gain': 20.0,
                                 'gain_priority': False,
                                 'brightness_target': 100,
                                 'max_exposure_time': 9500.0,
                                 'min_exposure_time': 1000.0}],
                    remappings=[('~/meta', ['/', LaunchConfig('cam_0_name'),
                                            '/meta']), ],
                    extra_arguments=[{'use_intra_process_comms': True}],
                ),
            ],
            output='screen',
    )
    name_0_arg = LaunchArg('cam_0_name', default_value=['cam_0'],
                           description='name of camera 0')
    name_1_arg = LaunchArg('cam_1_name', default_value=['cam_1'],
                           description='name of camera 1')
    return launch.LaunchDescription([name_0_arg, name_1_arg, container])
