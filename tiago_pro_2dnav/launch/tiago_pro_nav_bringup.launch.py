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
)
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_pal.robot_arguments import CommonArgs
from launch_pal.arg_utils import LaunchArgumentsBase
from launch_pal.include_utils import include_scoped_launch_py_description


@dataclass(frozen=True)
class LaunchArguments(LaunchArgumentsBase):

    slam: DeclareLaunchArgument = CommonArgs.slam
    advanced_navigation: DeclareLaunchArgument = CommonArgs.advanced_navigation


def generate_launch_description():

    # Create the launch description and populate
    ld = LaunchDescription()
    launch_arguments = LaunchArguments()

    launch_arguments.add_to_launch_description(ld)

    declare_actions(ld, launch_arguments)

    return ld


def declare_actions(launch_description: LaunchDescription, launch_args: LaunchArguments):

    tiago_pro_2dnav = get_package_share_directory("tiago_pro_2dnav")
    remmaping_file = os.path.join(tiago_pro_2dnav, "params", "tiago_pro_remappings_sim.yaml")

    laser_bringup_launch = include_scoped_launch_py_description(
        pkg_name="pal_nav2_bringup",
        paths=["launch", "nav_bringup.launch.py"],
        launch_arguments={
            "params_pkg": "tiago_pro_laser_sensors",
            "params_file": "laser_pipeline_sim_multi.yaml",
            "robot_name": "tiago_pro",
            "remappings_file": remmaping_file,
        }
    )

    nav_bringup_launch = include_scoped_launch_py_description(
        pkg_name="pal_nav2_bringup",
        paths=["launch", "nav_bringup.launch.py"],
        launch_arguments={
            "params_pkg": "tiago_pro_2dnav",
            "params_file": "tiago_pro_nav.yaml",
            "robot_name": "tiago_pro",
            "remappings_file": remmaping_file,
        }
    )

    slam_bringup_launch = include_scoped_launch_py_description(
        pkg_name="pal_nav2_bringup",
        paths=["launch", "nav_bringup.launch.py"],
        launch_arguments={
            "params_pkg": "tiago_pro_2dnav",
            "params_file": "tiago_pro_slam.yaml",
            "robot_name": "tiago_pro",
        },
        condition=IfCondition(LaunchConfiguration("slam"))
    )

    loc_bringup_launch = include_scoped_launch_py_description(
        pkg_name="pal_nav2_bringup",
        paths=["launch", "nav_bringup.launch.py"],
        launch_arguments={
            "params_pkg": "tiago_pro_2dnav",
            "params_file": "tiago_pro_loc.yaml",
            "robot_name": "tiago_pro",
        },
        condition=UnlessCondition(LaunchConfiguration("slam"))
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

    # Create the launch description and populate
    launch_description.add_action(laser_bringup_launch)
    launch_description.add_action(slam_bringup_launch)
    launch_description.add_action(nav_bringup_launch)
    launch_description.add_action(loc_bringup_launch)
    launch_description.add_action(rviz_node)
