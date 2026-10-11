FROM turing/base:humble
COPY src/turing_drive /ws/src/turing_drive
RUN /bin/bash -c "source /opt/ros/humble/setup.bash && cd /ws && colcon build"
ENV PARTICIPANT_CMD="ros2 run turing_drive drive_test"
