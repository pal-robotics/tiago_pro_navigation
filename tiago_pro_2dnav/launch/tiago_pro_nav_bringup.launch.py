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

from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    DeclareLaunchArgument,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():

    declare_slam_arg = DeclareLaunchArgument(
        "slam",
        default_value="false",
        description="Whether or not you are using SLAM",
    )

    pal_nav2_bringup = get_package_share_directory("pal_nav2_bringup")

    nav_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                pal_nav2_bringup,
                "launch",
                "nav_bringup.launch.py",
            )
        ),
        launch_arguments={
            "params_pkg": "tiago_pro_2dnav",
            "params_file": "tiago_pro_nav.yaml",
            "robot_name": "tiago_pro",
            "remappings_file": os.path.join(
                get_package_share_directory("tiago_pro_2dnav"),
                "params",
                "tiago_pro_remappings_sim.yaml"),
            "rviz": "true"
        }.items()
    )

    slam_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                pal_nav2_bringup,
                "launch",
                "nav_bringup.launch.py",
            )
        ),
        launch_arguments={
            "params_pkg": "tiago_pro_2dnav",
            "params_file": "tiago_pro_slam.yaml",
            "robot_name": "tiago_pro",
            "rviz": "false"
        }.items(),
        condition=IfCondition(LaunchConfiguration('slam')),
    )

    loc_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                pal_nav2_bringup,
                "launch",
                "nav_bringup.launch.py",
            )
        ),
        launch_arguments={
            "params_pkg": "tiago_pro_2dnav",
            "params_file": "tiago_pro_loc.yaml",
            "robot_name": "tiago_pro",
            "rviz": "false"
        }.items(),
        condition=UnlessCondition(LaunchConfiguration('slam')),
    )
    # Create the launch description and populate
    ld = LaunchDescription()
    ld.add_action(declare_slam_arg)
    ld.add_action(nav_bringup_launch)
    ld.add_action(slam_bringup_launch)
    ld.add_action(loc_bringup_launch)

    return ld
