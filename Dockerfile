FROM ros:humble-ros-base-jammy

SHELL ["/bin/bash", "-c"]

WORKDIR /ros2_ws

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-colcon-common-extensions \
    ros-humble-rclpy \
    ros-humble-geometry-msgs \
    ros-humble-launch \
    ros-humble-launch-ros \
    && rm -rf /var/lib/apt/lists/*

COPY ros2_ws/src/ /ros2_ws/src/

RUN source /opt/ros/humble/setup.bash && colcon build

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]

CMD ["ros2", "launch", "route_patrol", "patrol.launch.py", "mode:=point", "start:=8", "end:=4"]