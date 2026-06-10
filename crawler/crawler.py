"""
  Crawler - tracked vehicle
"""
import math
from datetime import timedelta

from pymavlink import mavutil
from pymavlink.dialects.v20 import ardupilotmega as mavlink  # hmm

from osgar.node import Node


RPM2MPS = 0.0001  # scale RPM to distance traveled in maters


class Crawler(Node):

    def __init__(self, config, bus):
        super().__init__(config, bus)
        bus.register('pose2d', 'msg', 'rpm', 'raw_serial')
        self.max_speed = config.get('max_speed', 0.2)
        self.pose = 0, 0, 0
        self.desired_speed = 0  # m/s
        self.desired_angular_speed = 0.0  # rad/s
        self.distance_traveled = 0.0  # meters
        self.last_distance_update_time = timedelta()

        # Track distances for odometry estimation
        self.last_dist_L = None
        self.last_dist_R = None
        self.delta_L = 0.0
        self.delta_R = 0.0
        self.wheel_track = config.get('wheel_track', 0.5)  # track width in meters

#        self.master = mavutil.mavlink_connection('', baud=115200)
#        self.master.wait_heartbeat()
        self.master = mavlink.MAVLink(None)
        self.master.srcSystem = 255
        self.master.srcComponent = 0
        self.target_system, self.target_component = None, None
        self.verbose = False   # TO BE REMOVED! (after osgar update)

    def update_pose2d(self, dL, dR):
        x, y, heading = self.pose
        dist = (dL + dR) / 2.0
        d_heading = (dR - dL) / self.wheel_track

        # advance robot by given distance and angle
        if abs(d_heading) < 0.000001:  # EPS
            # Straight movement - a special case
            x += dist * math.cos(heading)
            y += dist * math.sin(heading)
        else:
            # Arc approximation
            x += dist * math.cos(heading + d_heading / 2.0)
            y += dist * math.sin(heading + d_heading / 2.0)
            heading += d_heading

        self.pose = (x, y, heading)
        self.publish('pose2d', [round(x*1000), round(y*1000), round(math.degrees(heading)*100)])

    def on_desired_speed(self, data):
        self.desired_speed, self.desired_angular_speed = data[0]/1000, math.radians(data[1]/100)

    def on_raw_serial(self, data):
        for b in data:
            try:
                msg = self.master.parse_char(bytes([b]))
            except mavlink.MAVError:
                print(f'skipping {hex(b)}')
                msg = None
            if msg:
                if self.verbose:
                    print(msg)
                self.publish('msg', str(msg))

                msg_type = msg.get_type()
                if msg_type == 'HEARTBEAT' and msg.type == 10:
                    header = msg.get_header()
                    self.target_system = header.srcSystem
                    self.target_component = header.srcComponent

                elif msg_type == 'NAMED_VALUE_FLOAT':
                    if msg.name == 'Dist_L':
                        if self.last_dist_L is not None:
                            diff = msg.value - self.last_dist_L
                            if abs(diff) < 10.0:  # protect against resets/glitches
                                self.delta_L += diff
                        self.last_dist_L = msg.value
                    elif msg.name == 'Dist_R':
                        if self.last_dist_R is not None:
                            diff = msg.value - self.last_dist_R
                            if abs(diff) < 10.0:  # protect against resets/glitches
                                self.delta_R += diff
                        self.last_dist_R = msg.value

                elif msg_type == 'ESC_TELEMETRY_1_TO_4':
                    self.publish('rpm', [msg.rpm[0], msg.rpm[1]])

    def on_tick(self, data):
        # Update pose based on accumulated deltas since the last tick
        dL = self.delta_L
        dR = self.delta_R
        self.delta_L = 0.0
        self.delta_R = 0.0
        self.update_pose2d(dL, dR)

        if self.target_system is None:
            return  # not identified yet

        # 1900 - max dopredu, 1100 - max dozadu (for speed scaled by 500)
        # Ch1 = Steering (zataceni), Ch2 = Throttle (plyn)
        # Scale desired_speed (m/s) and desired_angular_speed (rad/s) to PWM.
        # Scale factors: 1.0 m/s -> 500 PWM, 1.0 rad/s -> 500 PWM
        pwm_steering = int(1500 + (self.desired_angular_speed * 500))
        pwm_throttle = int(1500 + (self.desired_speed * 500))

        # Clamp values to safe limits [1100, 1900]
        pwm_steering = max(1100, min(1900, pwm_steering))
        pwm_throttle = max(1100, min(1900, pwm_throttle))

        # We must use 65535 for unused channels (no override) instead of 0,
        # otherwise we might override critical channels (mode, safety, arming)
        # to invalid/low values, triggering failsafes or disarming on ArduPilot.
        msg = self.master.rc_channels_override_encode(
            self.target_system, self.target_component,
            pwm_steering, pwm_throttle, 65535, 65535, 65535, 65535, 65535, 65535
        )
        print(self.desired_speed, self.desired_angular_speed, pwm_steering, pwm_throttle)
        self.publish('raw_serial', msg.pack(self.master))
        self.master.seq += 1
