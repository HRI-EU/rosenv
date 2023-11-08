cmake_minimum_required(VERSION 3.0.2)

project(server)

find_package(catkin REQUIRED COMPONENTS
  roscpp
  adder
  adder_srvs
)

catkin_package()

include_directories(
  ${catkin_INCLUDE_DIRS}
)

add_executable(server src/server.cpp)
target_link_libraries(server ${catkin_LIBRARIES})

install(TARGETS ${PROJECT_NAME}
    RUNTIME DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/bin
)

install(DIRECTORY launch/
    DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/launch
)
