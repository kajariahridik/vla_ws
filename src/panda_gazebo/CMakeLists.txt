cmake_minimum_required(VERSION 3.5)
project(panda_gazebo)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch config urdf
  DESTINATION share/${PROJECT_NAME})

ament_package()
