# Turing Track: F1TENTH Gym Setup Guide

This guide gets the F1TENTH Gym simulator running with ROS 2 Humble inside Docker on a Linux Mint host, with RViz showing on the host desktop. It also covers the small test node that drives the sim car. Every command here was run and checked on the reference setup.

Setup used: Linux Mint host, Docker container named `ros-humble-gui`, ROS 2 Humble (Ubuntu 22.04 inside the container).

## 1. Start the container with display access

On the host, allow the container to draw windows on the desktop. This has to be repeated after every host reboot.

```
xhost +local:docker
```

If `xhost` is missing: `sudo apt install x11-xserver-utils`.

The container needs the display passed in when it is created. A working example:

```
docker run -it --name ros-humble-gui --net=host \
  -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix \
  osrf/ros:humble-desktop bash
```

To get back into an existing container later:

```
sudo docker start ros-humble-gui
sudo docker exec -it ros-humble-gui bash
```

Inside the container, check the display is visible:

```
echo $DISPLAY
ls /tmp/.X11-unix
```

You should see `:0` and a file named `X0`.

## 2. Make ROS load automatically

Run once inside the container so every new terminal has ROS ready:

```
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
echo "source ~/sim_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

## 3. Install tools

```
sudo apt update
sudo apt install -y git python3-pip ros-humble-rviz2 ros-humble-ackermann-msgs python3-colcon-common-extensions python3-rosdep
sudo rosdep init
rosdep update
```

If `rosdep init` says the file already exists, ignore it.

## 4. Install the simulator physics (f1tenth_gym)

```
cd ~
git clone https://github.com/f1tenth/f1tenth_gym
cd f1tenth_gym
pip3 install -e .
```

Run these one at a time. If pip complains about the old `gym` package, run `pip3 install "setuptools<66" "wheel<0.40"` and try the install again. Keep the `f1tenth_gym` folder where it is, because the install points to it.

## 5. Install the ROS bridge (f1tenth_gym_ros)

```
mkdir -p ~/sim_ws/src
cd ~/sim_ws/src
git clone https://github.com/f1tenth/f1tenth_gym_ros
cd ~/sim_ws
rosdep install -i --from-path src --rosdistro humble -y
colcon build
source install/setup.bash
```

`rosdep` installs the extra packages the bridge needs (xacro, nav2 map server, nav2 lifecycle manager). Build warnings are fine, red errors are not.

## 6. Fix the map path

The shipped config points to `/sim_ws/src/...`, which is the path used inside the official F1TENTH Docker image. In this setup the workspace lives at `/root/sim_ws`, so the sim crashes with `FileNotFoundError ... levine.png` until the path is corrected.

Check the current value:

```
grep map_path ~/sim_ws/src/f1tenth_gym_ros/config/sim.yaml
```

If it starts with `/sim_ws/src`, fix it once (running it twice breaks the path):

```
sed -i 's#/sim_ws/src#/root/sim_ws/src#' ~/sim_ws/src/f1tenth_gym_ros/config/sim.yaml
```

Rebuild, because the config is copied at build time:

```
cd ~/sim_ws
colcon build
source install/setup.bash
```

To use the track team's map later, set `map_path` in the same file to the full path of the map without the file extension, and set `map_img_ext` to match the image type (for example `.png`). Then rebuild.

## 7. Launch the simulator

```
cd ~/sim_ws
source install/setup.bash
ros2 launch f1tenth_gym_ros gym_bridge_launch.py
```

RViz opens on the host desktop with the map and the car. The long `UserWarning` lines about parameters are harmless. Leave this terminal running.

If RViz does not open, rerun `xhost +local:docker` on the host and relaunch. If RViz opens but crashes with an OpenGL error, run `export LIBGL_ALWAYS_SOFTWARE=1` and launch again.

## 8. Check the topics

Open a second host terminal and enter the container with `sudo docker exec -it ros-humble-gui bash`, then:

```
ros2 topic list
ros2 topic hz /scan
```

Expected topics include `/scan`, `/drive` and `/ego_racecar/odom`.

## 9. Drive the car with a test node

This is a small package that reads `/scan` and publishes `/drive`. It drives at 1 m/s, steers away from the nearer side wall, and stops if something is within 1 m straight ahead.

Create the package:

```
cd ~/sim_ws/src
ros2 pkg create --build-type ament_python turing_drive --dependencies rclpy ackermann_msgs sensor_msgs
```

Write the node:

```
cat > ~/sim_ws/src/turing_drive/turing_drive/drive_test.py << 'EOF'
import math
import rclpy
from rclpy.node import Node
from ackermann_msgs.msg import AckermannDriveStamped
from sensor_msgs.msg import LaserScan


def clean(r, cap=4.0):
    if math.isnan(r) or math.isinf(r):
        return cap
    return min(r, cap)


class DriveTest(Node):
    def __init__(self):
        super().__init__('drive_test')
        self.pub = self.create_publisher(AckermannDriveStamped, '/drive', 10)
        self.sub = self.create_subscription(LaserScan, '/scan', self.on_scan, 10)
        self.front = 4.0
        self.left = 4.0
        self.right = 4.0
        self.create_timer(0.05, self.tick)

    def range_at(self, msg, deg):
        angle = math.radians(deg)
        i = int((angle - msg.angle_min) / msg.angle_increment)
        i = max(0, min(len(msg.ranges) - 1, i))
        return clean(msg.ranges[i])

    def on_scan(self, msg):
        self.front = min(self.range_at(msg, d) for d in range(-10, 11, 5))
        self.left = self.range_at(msg, 80)
        self.right = self.range_at(msg, -80)

    def tick(self):
        cmd = AckermannDriveStamped()
        cmd.drive.speed = 0.0 if self.front < 1.0 else 1.0
        steer = 0.3 * (self.left - self.right)
        cmd.drive.steering_angle = max(-0.4, min(0.4, steer))
        self.pub.publish(cmd)


def main():
    rclpy.init()
    rclpy.spin(DriveTest())
EOF
```

Register it as a runnable program (run once):

```
sed -i "s/'console_scripts': \[/'console_scripts': ['drive_test = turing_drive.drive_test:main',/" ~/sim_ws/src/turing_drive/setup.py
```

Build and run:

```
cd ~/sim_ws
colcon build --packages-select turing_drive
source install/setup.bash
ros2 run turing_drive drive_test
```

The car should roll forward and nudge away from the nearer wall. If it steers into the wall instead, flip the sign of the `0.3` in the steering line, rebuild and run again. To reposition the car, use **2D Pose Estimate** in the RViz toolbar, or relaunch the sim.

## 10. Save your work

On the host, save the container state as an image so nothing is lost if the container is removed:

```
sudo docker commit ros-humble-gui turing-ros:v2
```

## Quick start for a new session

Host:

```
xhost +local:docker
sudo docker start ros-humble-gui
sudo docker exec -it ros-humble-gui bash
```

Terminal 1, inside the container:

```
ros2 launch f1tenth_gym_ros gym_bridge_launch.py
```

Terminal 2, a new host terminal, then inside the container:

```
sudo docker exec -it ros-humble-gui bash
ros2 run turing_drive drive_test
```

## Common problems

| Problem | Fix |
|---|---|
| `ros2: command not found` | Run `source /opt/ros/humble/setup.bash` in that terminal |
| RViz says it cannot connect to display :0 | Run `xhost +local:docker` on the host, and make sure the container was started with `-e DISPLAY` and the X11 socket |
| `FileNotFoundError ... levine.png` | Map path is wrong, see section 6 |
| Car does not move | Check the sim is still running, then `ros2 topic echo /drive` to see whether the node is publishing |
| Pasted commands run together | Paste one command at a time and wait for the prompt |

## Status and next steps

- Done: Gym running in Docker with RViz, test node driving the sim car.
- Not yet done: realistic D500 LiDAR model (10 Hz, plus or minus 30 mm noise, range capped near 4 m, added latency), the real track map from the track team, safety nodes (watchdog, command gate, mode manager), multi-arch Docker base image.
