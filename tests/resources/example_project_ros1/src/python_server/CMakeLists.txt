cmake_minimum_required(VERSION 3.0.2)

project(python_server)

find_package(catkin REQUIRED COMPONENTS
  adder
  adder_srvs
)

catkin_package()
catkin_python_setup()

catkin_install_python(PROGRAMS
    src/python_server.py
    DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY launch/
    DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/launch
)
