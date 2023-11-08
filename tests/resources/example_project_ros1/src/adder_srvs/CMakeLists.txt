cmake_minimum_required(VERSION 3.0.2)

project(adder_srvs)

find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  std_msgs
  message_generation
)
add_service_files(
  FILES
  AddTwoInts.srv
)
generate_messages(
  DEPENDENCIES
  std_msgs
)
catkin_package(
)
include_directories(
  ${catkin_INCLUDE_DIRS}
)
