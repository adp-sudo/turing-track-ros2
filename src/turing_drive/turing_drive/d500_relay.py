import collections
import math
import random

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class D500Relay(Node):
    def __init__(self):
        super().__init__('d500_relay')
        self.declare_parameter('range_max', 4.0)
        self.declare_parameter('noise_std', 0.03)
        self.declare_parameter('delay_ms', 50.0)
        self.declare_parameter('rate_hz', 10.0)
        self.declare_parameter('stride', 3)

        self.range_max = self.get_parameter('range_max').value
        self.noise_std = self.get_parameter('noise_std').value
        self.delay_ns = int(self.get_parameter('delay_ms').value * 1e6)
        self.rate = self.get_parameter('rate_hz').value
        self.stride = int(self.get_parameter('stride').value)

        self.buffer = collections.deque()
        self.pub = self.create_publisher(LaserScan, '/scan_d500', 10)
        self.create_subscription(LaserScan, '/scan', self.on_scan, 10)
        self.create_timer(1.0 / self.rate, self.tick)

    def on_scan(self, msg):
        now = self.get_clock().now().nanoseconds
        self.buffer.append((now, msg))
        while self.buffer and now - self.buffer[0][0] > self.delay_ns + 1_000_000_000:
            self.buffer.popleft()

    def tick(self):
        target = self.get_clock().now().nanoseconds - self.delay_ns
        chosen = None
        for t, m in self.buffer:
            if t <= target:
                chosen = m
            else:
                break
        if chosen is None:
            return

        out = LaserScan()
        out.header = chosen.header
        out.angle_min = chosen.angle_min
        out.angle_increment = chosen.angle_increment * self.stride
        out.range_min = chosen.range_min
        out.range_max = self.range_max
        out.scan_time = 1.0 / self.rate
        out.time_increment = 0.0

        ranges = []
        for r in chosen.ranges[::self.stride]:
            if math.isnan(r) or math.isinf(r):
                ranges.append(float('inf'))
                continue
            r = r + random.gauss(0.0, self.noise_std)
            if r > self.range_max or r < out.range_min:
                ranges.append(float('inf'))
            else:
                ranges.append(r)
        out.ranges = ranges
        out.angle_max = out.angle_min + out.angle_increment * (len(ranges) - 1)
        self.pub.publish(out)


def main():
    rclpy.init()
    rclpy.spin(D500Relay())
