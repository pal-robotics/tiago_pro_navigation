cmake_minimum_required(VERSION 3.8)
project(tiago_pro)

find_package(ament_cmake_auto REQUIRED)

# PAL Robotics stricter build flags, other developers should not worry about this
find_package(ament_cmake_pal QUIET)

ament_auto_find_build_dependencies()

ament_auto_package(INSTALL_TO_SHARE
#     @TODO: Define building system
#     buildings
    config
    configurations
)
