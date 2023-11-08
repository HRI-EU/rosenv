#include "ros/ros.h"

#include "adder/adder.h"
#include "adder_srvs/AddTwoInts.h"

bool add(adder_srvs::AddTwoInts::Request &req,
         adder_srvs::AddTwoInts::Response &res) {
  res.sum = add(req.a, req.b);
  ROS_INFO("request: x=%ld, y=%ld", (long int)req.a, (long int)req.b);
  ROS_INFO("sending back response: [%ld]", (long int)res.sum);
  return true;
}

int main(int argc, char **argv) {
  ros::init(argc, argv, "add_two_ints_server");
  ros::NodeHandle n;

  std::string service_name;
  ros::param::param<std::string>("/service_name", service_name, "add_two_ints");

  ros::ServiceServer service = n.advertiseService(service_name, add);
  ROS_INFO("Ready to add two ints.");
  ros::spin();

  return 0;
}
