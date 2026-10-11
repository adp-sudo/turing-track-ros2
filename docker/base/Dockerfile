FROM ros:humble-ros-base
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-colcon-common-extensions \
    ros-humble-ackermann-msgs \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /ws
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
