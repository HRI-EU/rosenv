cmake_minimum_required(VERSION 3.0.2)
project(launch_success)
find_package(catkin REQUIRED)

catkin_package()
install(DIRECTORY launch/
    DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/launch
)
