#
#  Copyright (c) Honda Research Institute Europe GmbH
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  1. Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived from
#     this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#
from __future__ import annotations

from pathlib import Path

import pytest

from rosenv.catkin_profile import CatkinProfile
from rosenv.ros_package.package import PackageName
from rosenv.ros_package.workspace import ROSWorkspace
from tests.conftest import ROS_1_PROJECT_LIST
from tests.conftest import ROS_2_PROJECT_LIST


@pytest.fixture(params=["example_project_ros1", "example_project_ros2"])
def workspace(request: pytest.FixtureRequest) -> ROSWorkspace:
    return ROSWorkspace.from_workspace(
        request.getfixturevalue(request.param),
        CatkinProfile.with_no_blacklist(),
    )


@pytest.fixture()
def project_list(workspace: ROSWorkspace) -> list[str]:
    if workspace.path.name.endswith("ros1"):
        return ROS_1_PROJECT_LIST

    return ROS_2_PROJECT_LIST


@pytest.fixture()
def expected_external_dependencies(workspace: ROSWorkspace) -> list[str]:
    if workspace.path.name.endswith("ros1"):
        return [
            "message_generation",
            "message_runtime",
            "roscpp",
            "rospy",
            "std_msgs",
        ]

    return [
        "rclcpp",
        "rclpy",
        "rosidl_default_generators",
        "rosidl_default_runtime",
    ]


def test_ros_workspace(
    workspace: ROSWorkspace,
    project_list: list[str],
    expected_external_dependencies: list[str],
) -> None:
    package_names = {p.name for p in workspace.ros_packages}
    external_dependencies = {p.name for p in workspace.external_dependencies}
    assert package_names == set(project_list)  # order is not specified
    assert external_dependencies == {*expected_external_dependencies}


@pytest.fixture()
def external_required_by(workspace: ROSWorkspace) -> dict[str, list[str]]:
    if workspace.path.name.endswith("ros1"):
        return {
            "message_generation": ["adder_srvs"],
            "message_runtime": ["adder_srvs"],
            "roscpp": ["adder", "adder_srvs", "client", "server"],
            "rospy": ["adder", "adder_srvs", "client", "python_server", "server"],
            "std_msgs": ["adder_srvs"],
        }

    return {
        "rclcpp": ["client", "server"],
        "rclpy": ["python_server"],
        "rosidl_default_generators": ["adder_srvs"],
        "rosidl_default_runtime": ["adder_srvs"],
    }


def test_ros_workspace_should_create_correct_external_dependencies_for_ros_1(
    workspace: ROSWorkspace,
    external_required_by: dict[str, list[str]],
) -> None:
    def get_required_by_names(project: str) -> list[PackageName]:
        for dep in workspace.external_dependencies:
            if dep.name == project:
                return [p.name for p in dep.required_by]

        pytest.fail(reason=f"ExternalDependency for {project=} not found")

    assert len(workspace.external_dependencies) == len(external_required_by)
    assert all(get_required_by_names(name) == external_required_by[name] for name in external_required_by)


def test_ros_workspace_sort_ros_packages_for_installation(
    workspace: ROSWorkspace,
    project_list: list[str],
) -> None:
    workspace.ros_packages.reverse()
    sorted_list = workspace.sort_ros_packages_for_installation()
    package_names = {p.name for p in sorted_list}
    assert package_names == set(project_list)


def test_ros_workspace_should_filter_blacklisted_packages(example_project: Path) -> None:
    profile = CatkinProfile.with_no_blacklist()
    profile.blacklist = ["adder", "server"]

    workspace = ROSWorkspace.from_workspace(example_project, profile)

    assert "adder" not in [p.name for p in workspace.ros_packages]
    assert "server" not in [p.name for p in workspace.ros_packages]


def test_ros_workspace_should_give_correct_build_tree(workspace: ROSWorkspace) -> None:
    expected_tree_levels = 2

    first_level = (
        [
            "adder",
            "adder_meta",
            "adder_srvs",
        ]
        if workspace.path.name.endswith("ros1")
        else [
            "adder",
            "adder_srvs",
        ]
    )

    tree = workspace.get_install_tree()

    assert len(tree) == expected_tree_levels
    assert [item.name for item in tree[0]] == first_level
    assert [item.name for item in tree[1]] == ["client", "python_server", "server"]
