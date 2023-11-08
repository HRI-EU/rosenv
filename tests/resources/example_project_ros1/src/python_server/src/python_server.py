#!/usr/bin/env python

from rospy import spin, init_node, Service, loginfo, get_param

from adder_srvs.srv import AddTwoInts, AddTwoIntsResponse, AddTwoIntsRequest


class PythonServer:
    def __init__(self) -> None:
        service_name = get_param("/service_name", "add_two_ints")
        Service(service_name, AddTwoInts, self.add)

        loginfo("Ready to receive ints")

    @staticmethod
    def add(request: AddTwoIntsRequest) -> None:
        result = AddTwoIntsResponse(request.a + request.b)

        loginfo(f"{request=} {result=}")
        return result


if __name__ == "__main__":
    init_node("python_server")
    PythonServer()

    spin()
