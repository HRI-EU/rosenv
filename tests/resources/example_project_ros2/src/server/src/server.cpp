#include "rclcpp/rclcpp.hpp"

#include "adder/adder.h"
#include "adder_srvs/srv/add_two_ints.hpp"

#include <memory>

void add_service(const std::shared_ptr<adder_srvs::srv::AddTwoInts::Request> request,
         std::shared_ptr<adder_srvs::srv::AddTwoInts::Response> response) {
  response->sum = add(request->a, request->b);
  RCLCPP_INFO(rclcpp::get_logger("rclcpp"),
              "Incoming request\na: %ld"
              " b: %ld",
              request->a, request->b);
  RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "sending back response: [%ld]",
              (long int)response->sum);
}

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);

  std::shared_ptr<rclcpp::Node> node =
      rclcpp::Node::make_shared("add_two_ints_server");

  rclcpp::Service<adder_srvs::srv::AddTwoInts>::SharedPtr service =
      node->create_service<adder_srvs::srv::AddTwoInts>("add_two_ints", &add_service);

  RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "Ready to add two ints.");

  rclcpp::spin(node);
  rclcpp::shutdown();
}
