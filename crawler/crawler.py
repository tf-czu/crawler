"""
  Crawler - tracked vehicle
"""
import math

from pymavlink import mavutil

from osgar.node import Node


class Crawler(Node):

    def __init__(self, config, bus):
        super().__init__(config, bus)
        bus.register('pose2d', 'msg')
        self.max_speed = config.get('max_speed', 0.1)
        self.pose = 0, 0, 0
        self.desired_speed = 0  # m/s
        self.desired_angular_speed = 0.0  # rad/s

        self.master = mavutil.mavlink_connection('/dev/serial/by-id/usb-CubePilot_CubeOrange+_32002C001951333230363332-if00', baud=115200)
        self.master.wait_heartbeat()

    def on_desired_speed(self, data):
        self.desired_speed, self.desired_angular_speed = data[0]/1000, math.radians(data[1]/100)

    def on_tick(self, data):
        msg = self.master.recv_match(blocking=True)
        self.publish('msg', msg)

        # 1900 - max dopredu, 1100 - max dozadu
        levy_mix, pravy_mix = self.max_speed, self.max_speed
        pwm_levy = int(1500 + (levy_mix * 500))
        pwm_pravy = int(1500 + (pravy_mix * 500))

        self.master.mav.rc_channels_override_send(
            self.master.target_system, self.master.target_component,
            pwm_levy, pwm_pravy, 0, 0, 0, 0, 0, 0
        )
