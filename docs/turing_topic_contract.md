# Turing Track: ROS 2 Topic Contract (Draft v0.1)

ROS 2 distribution: Humble. Conventions follow F1TENTH.

## Topics

| Topic | Message type | Rate | QoS | Publisher | Subscriber |
|---|---|---|---|---|---|
| /scan | sensor_msgs/LaserScan | 10 Hz | Best effort, volatile, depth 5 | D500 LiDAR driver | Planner, localisation |
| /odom | nav_msgs/Odometry | 20 to 50 Hz | Best effort, volatile, depth 5 | Odometry node (VESC ERPM + steering + IMU yaw) | Planner, localisation |
| /imu | sensor_msgs/Imu | about 50 Hz | Best effort, volatile, depth 5 | IMU driver | Odometry node |
| /camera/image_raw | sensor_msgs/Image | 15 to 30 Hz | Best effort, volatile, depth 1 | Pi camera driver | Planner (optional) |
| /drive_raw | ackermann_msgs/AckermannDriveStamped | 20 Hz or better | Reliable, depth 1 | Planner / participant model | Command gate |
| /drive_gated | ackermann_msgs/AckermannDriveStamped | 20 Hz or better | Reliable, depth 1 | Command gate | Watchdog |
| /drive | ackermann_msgs/AckermannDriveStamped | 20 Hz or better | Reliable, depth 1 | Watchdog | VESC driver |
| /mode | std_msgs/String | On change | Reliable, transient local | Mode manager | Command gate |

Participant containers publish only to /drive_raw. They never publish to /drive directly.

## Frames

- map: fixed world frame from the pre-made map
- odom: odometry frame
- base_link: center of the car (rear axle)
- laser: LiDAR frame

## Safety rules

- Hardware E-Stop relay in the battery line. Software never acts as the E-Stop.
- Watchdog: if no fresh /drive_gated arrives within 200 ms, output zero speed.
- Command gate: clamps speed, steering angle and steering rate. Initial speed cap is 1.5 m/s, raised only after validation.
- Modes: STANDBY, ARMED, RUN, STOPPED. RUN starts only from ARMED, on the official start signal, from zero speed.
- Manual drive is allowed in practice mode only and is locked out in race mode.
- All processing is onboard. No network dependence during timed runs, wireless interface down in race mode.

## Performance targets

- Control loop at 20 Hz or better
- Sensor to command latency within one scan period (100 ms)

## Sim LiDAR model (for F1TENTH Gym)

- 10 Hz, plus or minus 30 mm noise, effective range capped near 4 m, added latency

## Open items

- Is the VESC motor sensored? (affects low speed odometry)
- Start signal mechanism (button on car or RC channel) needs an organizer ruling
- Exact JetPack version on the Jetson
- Lap length and number of finals laps are undefined
