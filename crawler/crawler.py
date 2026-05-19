"""
  Crawler - tracked vehicle
"""
import math
from datetime import timedelta

from pymavlink import mavutil

from osgar.node import Node


class Crawler(Node):

    RPM2MPS = 1.0  # scale RPM to distance traveled in maters

    def __init__(self, config, bus):
        super().__init__(config, bus)
        bus.register('pose2d', 'msg', 'rpm')
        self.max_speed = config.get('max_speed', 0.1)
        self.pose = 0, 0, 0
        self.desired_speed = 0  # m/s
        self.desired_angular_speed = 0.0  # rad/s
        self.distance_traveled = 0.0  # meters
        self.last_distance_update_time = timedelta()

        self.master = mavutil.mavlink_connection('/dev/serial/by-id/usb-CubePilot_CubeOrange+_32002C001951333230363332-if00', baud=115200)
        self.master.wait_heartbeat()

    def publish_pose2d(self, dt, speed, angular_speed):
        x, y, heading = self.pose
        dist = speed * dt

        # advance robot by given distance and angle
        if abs(angular_speed) < 0.0000001:  # EPS
            # Straight movement - a special case
            x += dist * math.cos(heading)
            y += dist * math.sin(heading)
            # Not needed: heading += angle
        else:
            # Arc
            x += dist * math.cos(heading)
            y += dist * math.sin(heading)
            heading += angular_speed * dt  # not normalized
        self.pose = (x, y, heading)
        self.publish('pose2d', [round(x*1000), round(y*1000), round(math.degrees(heading)*100)])

    def on_desired_speed(self, data):
        self.desired_speed, self.desired_angular_speed = data[0]/1000, math.radians(data[1]/100)

    def on_tick(self, data):
        msg = self.master.recv_match(blocking=True)
        self.publish('msg', str(msg))

        msg_type = msg.get_type()
        if msg_type == 'ESC_TELEMETRY_1_TO_4':
            self.publish('rpm', [msg.rpm[0], msg.rpm[1]])
            self.distance_traveled += msg.rpm[0] * RPM2MPS
            self.publish_pose2d(self.time - self.last_distance_update_time, msg.rpm[0] * RPM2MPS, 0.0)

        # 1900 - max dopredu, 1100 - max dozadu
        # ignore angular speed at the moment
        levy_mix, pravy_mix = self.desired_speed, self.desired_speed
        pwm_levy = int(1500 + (levy_mix * 100))  # was 500
        pwm_pravy = int(1500 + (pravy_mix * 100))

        self.master.mav.rc_channels_override_send(
            self.master.target_system, self.master.target_component,
            pwm_levy, pwm_pravy, 0, 0, 0, 0, 0, 0
        )
