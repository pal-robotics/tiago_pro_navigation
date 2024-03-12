cmake_minimum_required(VERSION 3.8)
project(tiago_pro_laser_sensors)

find_package(ament_cmake_auto REQUIRED)
ament_auto_find_build_dependencies()

if(pal_module_cmake_FOUND)
  pal_register_modules(module/10_laser.yaml
                      module/10_laser_w_composition.yaml)
endif()

if(BUILD_TESTING)
  ament_auto_find_test_dependencies()
  ament_lint_auto_find_test_dependencies()
endif()

ament_auto_package(INSTALL_TO_SHARE params)

