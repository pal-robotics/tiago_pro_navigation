# Copyright (c) 2025 PAL Robotics S.L. All rights reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited,
# unless it was supplied under the terms of a license agreement or
# nondisclosure agreement with PAL Robotics SL. In this case it may not be
# copied or disclosed except in accordance with the terms of that agreement.

import os

from ament_index_python import get_package_share_directory

import rclpy
from rclpy.node import Node as RclpyNode
from launch import LaunchDescription
from launch_ros.actions import LoadComposableNodes, Node
from launch_ros.descriptions import ComposableNode
from launch_pal import get_pal_configuration


def generate_launch_description():

    ld = LaunchDescription()
    head_front_camera_node = 'head_front_camera'
    head_front_camera_config = get_pal_configuration(
        pkg='realsense_camera_cfg', node=head_front_camera_node, ld=ld, cmdline_args=False)

    # If the container node already exists, just load the component
    rclpy.init()
    node = RclpyNode('node_checker')
    rclpy.spin_once(node, timeout_sec=1.0)
    if 'rgbd_container' not in node.get_node_names():
        rgbd_container = Node(
            name='rgbd_container',
            package='rclcpp_components',
            executable='component_container',
            emulate_tty=True,
            output='screen',
        )
        ld.add_action(rgbd_container)
    rclpy.shutdown()

    camera_components = LoadComposableNodes(
        target_container='rgbd_container',
        composable_node_descriptions=[
            # Head Front Camera Driver
            ComposableNode(
                package='realsense2_camera',
                plugin='realsense2_camera::RealSenseNodeFactory',
                name=head_front_camera_node,
                namespace='head_front_camera',
                parameters=head_front_camera_config["parameters"],
                remappings=head_front_camera_config["remappings"],
            ),
        ],
    )

    ld.add_action(camera_components)

    rgbd_analyzer = Node(
        package='diagnostic_aggregator',
        executable='add_analyzer',
        namespace='tiago_pro_rgbd_sensors',
        output='screen',
        emulate_tty=True,
        parameters=[
            os.path.join(
                get_package_share_directory('tiago_pro_rgbd_sensors'),
                'config', 'rgbd_analyzers.yaml')],
    )
    ld.add_action(rgbd_analyzer)

    return ld
