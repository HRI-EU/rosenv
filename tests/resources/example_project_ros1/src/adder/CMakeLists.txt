cmake_minimum_required(VERSION 3.0.2)

project(adder)

find_package(catkin REQUIRED COMPONENTS
  roscpp
)

catkin_package(
  INCLUDE_DIRS include
  LIBRARIES adder
  CATKIN_DEPENDS roscpp
)

include_directories(
  include
  ${catkin_INCLUDE_DIRS}
)

add_library(${PROJECT_NAME}
  src/${PROJECT_NAME}/adder.cpp
)

install(TARGETS ${PROJECT_NAME}
  LIBRARY DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
)

install(DIRECTORY include/${PROJECT_NAME}/
  DESTINATION ${CATKIN_PACKAGE_INCLUDE_DESTINATION}
  FILES_MATCHING PATTERN "*.h"
)
