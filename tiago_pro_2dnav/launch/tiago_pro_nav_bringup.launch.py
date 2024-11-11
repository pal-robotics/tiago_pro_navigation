# Copyright (c) 2024 PAL Robotics S.L. All rights reserved.
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

import os

from ament_index_python.packages import get_package_share_directory
from dataclasses import dataclass

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    OpaqueFunction,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_pal.robot_arguments import CommonArgs
from launch_pal.arg_utils import LaunchArgumentsBase
from launch_pal.arg_utils import read_launch_argument
from launch_pal.include_utils import include_scoped_launch_py_description
from tiago_pro_description.launch_arguments import TiagoProArgs


@dataclass(frozen=True)
class LaunchArguments(LaunchArgumentsBase):

    base_type: DeclareLaunchArgument = TiagoProArgs.base_type
    slam: DeclareLaunchArgument = CommonArgs.slam
    advanced_navigation: DeclareLaunchArgument = CommonArgs.advanced_navigation


def generate_launch_description():

    # Create the launch description and populate
    ld = LaunchDescription()
    launch_arguments = LaunchArguments()

    launch_arguments.add_to_launch_description(ld)

    declare_actions(ld, launch_arguments)

    return ld


def private_nav_function(context, *args, **kwargs):

    base_type = read_launch_argument("base_type", context)
    actions = []
    tiago_pro_2dnav = get_package_share_directory("tiago_pro_2dnav")

    nav_bringup_launch = include_scoped_launch_py_description(
        pkg_name="pal_navigation_cfg_utils",
        paths=["launch", "pipeline_executor.launch.py"],
        launch_arguments={
            "pipeline": "navigation",
            "robot_name": base_type,
        },
    )

    slam_bringup_launch = include_scoped_launch_py_description(
        pkg_name="pal_navigation_cfg_utils",
        paths=["launch", "pipeline_executor.launch.py"],
        launch_arguments={
            "pipeline": "slam",
            "robot_name": base_type,
        },
        condition=IfCondition(LaunchConfiguration("slam"))
    )

    loc_bringup_launch = include_scoped_launch_py_description(
        pkg_name="pal_navigation_cfg_utils",
        paths=["launch", "pipeline_executor.launch.py"],
        launch_arguments={
            "pipeline": "localization",
            "robot_name": base_type,
        },
        condition=UnlessCondition(LaunchConfiguration("slam"))
    )

    laser_bringup_launch = include_scoped_launch_py_description(
        pkg_name="pal_navigation_cfg_utils",
        paths=["launch", "pipeline_executor.launch.py"],
        launch_arguments={
            "pipeline": "laser_sim",
            "robot_name": base_type,
        },
    )

    rviz_node = Node(
        condition=UnlessCondition(LaunchConfiguration("advanced_navigation")),
        package="rviz2",
        executable="rviz2",
        arguments=["-d", os.path.join(
            tiago_pro_2dnav,
            "config",
            "rviz",
            "navigation.rviz",
        )],
        output="screen",
    )

    actions.append(laser_bringup_launch)
    actions.append(slam_bringup_launch)
    actions.append(nav_bringup_launch)
    actions.append(loc_bringup_launch)
    actions.append(rviz_node)

    return actions


def declare_actions(launch_description: LaunchDescription, launch_args: LaunchArguments):

    launch_description.add_action(
        OpaqueFunction(
            function=private_nav_function,
        )
    )
