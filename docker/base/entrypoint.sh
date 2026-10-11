#!/bin/bash
set -e
source /opt/ros/humble/setup.bash
if [ -f /ws/install/setup.bash ]; then source /ws/install/setup.bash; fi
exec bash -c "${PARTICIPANT_CMD:?PARTICIPANT_CMD is not set}"
