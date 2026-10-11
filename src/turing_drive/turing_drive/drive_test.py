import math
import rclpy
from rclpy.node import Node
from ackermann_msgs.msg import AckermannDriveStamped
from sensor_msgs.msg import LaserScan

V_MAX = 1.5
V_MIN = 0.6
STEER_MAX = 0.4
KP = 0.25
KD = 0.06
STALE_S = 0.2


def clean(r, cap=4.0):
    if math.isnan(r) or math.isinf(r):
        return cap
    return min(r, cap)


class DriveTest(Node):
    def __init__(self):
        super().__init__('drive_test')
        self.pub = self.create_publisher(AckermannDriveStamped, '/drive', 10)
        self.create_subscription(LaserScan, '/scan_d500', self.on_scan, 10)
        self.speed = 0.0
        self.steer = 0.0
        self.prev_err = 0.0
        self.prev_t = None
        self.last_scan = None
        self.create_timer(0.05, self.tick)

    def now_s(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def range_at(self, msg, deg):
        i = int((math.radians(deg) - msg.angle_min) / msg.angle_increment)
        i = max(0, min(len(msg.ranges) - 1, i))
        return clean(msg.ranges[i])

    def avg(self, msg, lo, hi):
        vals = [self.range_at(msg, d) for d in range(lo, hi + 1, 5)]
        return sum(vals) / len(vals)

    def on_scan(self, msg):
        t = self.now_s()
        front = min(self.range_at(msg, d) for d in range(-15, 16, 5))
        side_err = self.avg(msg, 60, 90) - self.avg(msg, -90, -60)
        diag_err = self.avg(msg, 30, 50) - self.avg(msg, -50, -30)
        err = 0.6 * side_err + 0.4 * diag_err

        dt = (t - self.prev_t) if self.prev_t else 0.1
        deriv = (err - self.prev_err) / dt if dt > 0.01 else 0.0
        self.prev_err, self.prev_t = err, t

        steer = KP * err + KD * deriv
        self.steer = max(-STEER_MAX, min(STEER_MAX, steer))

        speed = V_MAX - (V_MAX - V_MIN) * abs(self.steer) / STEER_MAX
        if front < 0.6:
            speed = 0.0
        elif front < 2.0:
            speed = min(speed, 0.4 + 0.5 * (front - 0.6))
        self.speed = speed
        self.last_scan = t

    def tick(self):
        cmd = AckermannDriveStamped()
        stale = self.last_scan is None or self.now_s() - self.last_scan > STALE_S
        cmd.drive.speed = 0.0 if stale else self.speed
        cmd.drive.steering_angle = self.steer
        self.pub.publish(cmd)


def main():
    rclpy.init()
    rclpy.spin(DriveTest())
