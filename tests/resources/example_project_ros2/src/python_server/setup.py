from setuptools import setup

package_name = "python_server"

setup(
    name=package_name,
    version="0.0.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="hri",
    maintainer_email="hri@todo.todo",
    description="The python_server package",
    license="TODO",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "python_server = python_server.python_server:main",
        ],
    },
)
