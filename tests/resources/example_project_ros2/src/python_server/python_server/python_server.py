#!/usr/bin/env python

import rclpy
from rclpy.node import Node

from adder_srvs.srv import AddTwoInts


class PythonServer(Node):
    def __init__(self) -> None:
        super().__init__("python_server")
        self.create_service(AddTwoInts, "add_two_ints", self.add)

        self.get_logger().info("Ready to receive ints")

    def add(self, request, response) -> None:
        response.sum = request.a + request.b

        self.get_logger().info(f"{request=} {response=}")
        return response


def main():
    rclpy.init()
    python_server = PythonServer()

    rclpy.spin(python_server)

    rclpy.shutdown()


if __name__ == "__main__":
    main()
