<p align="center" width="100%">
    <img height="300x" src="assets/robenv_white_background.png"/>
</p>

# Robenv - Lightweight ROS System Installation Tool

Welcome to Robenv, a lightweight Command-Line Interface (CLI) tool designed to
simplify the installation and management of ROS (Robot Operating System)
systems. With Robenv, you can effortlessly create and install ROS systems in a
virtual environment without requiring root privileges or relying on git
submodules. This tool empowers you to easily package and deploy ROS systems,
enhancing portability and enabling hassle-free development.

By encapsulating the ROS system within a virtual environment, Robenv isolates
the dependencies, ensuring that the installation remains self-contained. This
approach eliminates conflicts with existing ROS installations or other system
packages, enabling you to experiment with different ROS configurations or work
on multiple projects simultaneously without interference.

Robenv streamlines the process of setting up and managing ROS systems, making it
an ideal tool for researchers, roboticists, and ROS enthusiasts. Whether you are
exploring new algorithms, developing robotics applications, or working on
collaborative projects, Robenv provides a seamless environment for installing
and managing ROS systems.

[<img height="80px" src="assets/hri.png"/>](https://honda-ri.de)
[<img height="80px" src="assets/synyx.png"/>](https://synyx.de)

## Dependencies

- fakeroot
- debhelper
- dh-python

## Installation

At this moment there is no simple installation command yet.
Please follow the [Developer Setup](Developer Setup).

## Usage

Running `robenv` without any arguments will print helpful usage documentation.

Before running any command you have to initialize the virtual environment via

```bash
robenv init
```

Initializing the virtual environment requires a local installation of ROS.
For more information see `robenv help init`.

## Autocompletion

We ship with a basic autocompletion setup that you can easily enable yourself.
Take a look at `robenv help completions` for support on how to enable completion
for your specific shell.

## Developer Setup

Install [poetry](https://python-poetry.org/docs/) and install by running

```bash
poetry install
```

This will create a virtual environment for this project.
`poetry shell` will spawn a shell within the virtual environment.
The [poetry documentation](https://python-poetry.org/docs/basic-usage/#using-your-virtual-environment)
will provide more information about using the virtual environment.

### System-Site packages

When developing for ROS2 we probably need additional system dependencies as ROS2
apparently changed their internal handling of python-dependencies.

Potential errors that signify this are:

- Missing `lark` dependency
- Missing `numpy` dependency (esp. in connection with `rosidl`)

To fix this we need to enable an additional option in poetry so that we can use
those.

Two points to mention:

- Existing poetry envs will not change, so you need to recreate them
- This is a system-level change, so maybe only do that in containers or
    whereever you are fine with that constraint

```bash
poetry config virtualenvs.options.system-site-packages true
```

After that recreate your venv via:

```bash
rm -rf $(poetry env info --path) && poetry install
```

## Terminology

### General

- ROS package --> already defined in ROS space (the thing that has a package.xml)
- ROS Debian package --> the packed artifacts of a ROS package in .deb format
- ROS workspace --> a standard ROS workspace (the thing that contains the src
    folder including multiple packages and can be compiled with catkin)
- repository --> GIT repo
- robenv --> Our own virtual env for ROS (default path robenv)
- virtualenv --> Python virtual env (venv)

### Dependencies

The following terms are not mutually exclusive (except when they are). E.g.
there could be an internal ROS dependency, but no internal generic ROS dependency.

- Generic dependency --> Dependency that **is not** a ROS package
- ROS dependency --> Dependency that **is** a ROS package
- Internal dependency --> ROS dependency that **can** be resolved inside the
    ROS workspace
- External dependency --> Dependency that **cannot** be resolved inside the
    ROS workspace
- build dependency
- runtime dependency

## License
The project is licensed under the BSD 3-clause license - see the [LICENSE](LICENSE)
file for details.

The integration tests contain ROS workspaces with packages adopted from the ROS 1
and 2 wiki. They are licensed under [Creative Commons Attribution
3.0](https://creativecommons.org/licenses/by/3.0) and
[4.0](https://creativecommons.org/licenses/by/4.0) respectively. The licenses
are specified in the package.xml files.

# FAQ

## I did override ROS_HOME because $reason but robenv breaks this

Document #52 results

## Why is robenv a non-hidden folder? Shouldn't `.robenv` be more in line with python venvs?

Yes it should be and yes it would be.

Sadly it then would prevent autocompletion in most of the ros commands on the
file-level. `rosbash` filters everything from the completion results that is in
some hidden directory. Interestingly this only applies to files and not to
projects.

The reason for this is described also in:

<https://github.com/ros/ros/issues/295>
