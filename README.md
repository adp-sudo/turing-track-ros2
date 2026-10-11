# Turing Track ROS 2

ROS 2 infrastructure for the Turing Track autonomous car race (Charter A).

## Contents
- src/turing_drive: ROS 2 package with the D500 sensor model (d500_relay) and a test driving node (drive_test)
- config/sim.yaml: F1TENTH Gym config with the map path fix
- docker/: base image and participant container template (added later)
- docs/: topic contract, setup guide and status document

## Quick start
Clone this repo into ~/sim_ws/src, then build with colcon:

    cd ~/sim_ws/src
    git clone git@github.com:adp-sudo/turing-track-ros2.git
    cd ~/sim_ws
    colcon build --packages-select turing_drive
    source install/setup.bash

The full setup and run commands are in the command reference in docs/.
