cmake_minimum_required(VERSION 3.0.2)

project(client)

find_package(catkin REQUIRED COMPONENTS
  roscpp
  adder_srvs
)

catkin_package()

include_directories(
  ${catkin_INCLUDE_DIRS}
)

add_executable(client src/client.cpp)
target_link_libraries(client ${catkin_LIBRARIES})

install(TARGETS ${PROJECT_NAME}
    RUNTIME DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/bin
)
