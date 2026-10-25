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

## Docker (work in progress)
Build the base image first, then the participant image, from the repo root:

    sudo docker build -t turing/base:humble docker/base
    sudo docker build -t turing/participant:dev -f docker/participant/Dockerfile .

The participant container runs the turing_drive test node. Testing it against the simulator is still in progress.


## Docker participant workflow

The Docker setup uses a reusable participant container template.
The selected participant image can be changed without editing the
Compose configuration.

### Start or switch the participant

    chmod +x scripts/swap-mode.sh
    ./scripts/swap-mode.sh turing/participant:dev

To select another participant image:

    ./scripts/swap-mode.sh team-a/planner:v1

The selected image must already be available locally or pulled from a registry.

### View logs and stop the participant

    docker compose logs -f participant
    docker compose down

Participant images must follow the agreed ROS 2 topic contract.
Only the selected planner should be active, and its commands must
pass through the approved safety interface before reaching the car.

Physical-car deployment requires separate hardware validation.

