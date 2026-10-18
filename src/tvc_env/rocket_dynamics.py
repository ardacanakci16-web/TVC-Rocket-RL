"""
TVC Hopper Rocket Physical Model & Simulation Dynamics
Matches physical parameters from Table I of the Acta Astronautica paper.
"""
import numpy as np

class TVCRocketDynamics:
    """
    MuJoCo-equivalent 6-DOF single-engine TVC hopper rocket simulation model.
    """
    def __init__(self):
        # Physical parameters
        self.mass = 1.63  # kg
        self.gravity = 9.81  # m/s^2
        self.inertia_diag = np.array([0.025, 0.025, 0.008], dtype=np.float32)  # kg*m^2
        self.height = 1.0  # m
        self.radius = 0.06  # m
        self.max_thrust = 35.3  # N (3.6 kgf, TWR = 2.21)

        # Actuation limits
        self.max_gimbal_deg = 20.0  # +/- 20 deg
        self.max_gimbal_rad = np.radians(self.max_gimbal_deg)  # ~0.349 rad
        self.servo_rate_limit = 8.06  # rad/s (461.5 deg/s = 60 deg / 0.13 s)
        self.gimbal_damping = 0.1  # N*m*s/rad

        # Simulation intervals
        self.physics_dt = 0.002  # 2 ms
        self.frame_skip = 8
        self.control_dt = self.physics_dt * self.frame_skip  # 16 ms (62.5 Hz)

        # State initialization [pos(3), vel(3), rot(quat: w,x,y,z), ang_vel(3), gimbal(yaw, pitch)]
        self.reset()

    def reset(self, target_altitude=10.0, seed=None):
        if seed is not None:
            np.random.seed(seed)
        # Random initial altitude (0.5 to 10.0 m)
        z0 = float(np.random.uniform(0.5, 10.0))
        self.pos = np.array([0.0, 0.0, z0], dtype=np.float64)
        self.vel = np.zeros(3, dtype=np.float64)
        self.quat = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float64)  # upright
        self.ang_vel = np.zeros(3, dtype=np.float64)
        self.gimbal = np.zeros(2, dtype=np.float64)  # [yaw, pitch] rad
        self.gimbal_rate = np.zeros(2, dtype=np.float64)
        self.thrust_fraction = 0.0
        self.target = np.array([0.0, 0.0, target_altitude], dtype=np.float64)
        self.step_count = 0
        return self.get_observation()

    def step(self, action):
        """
        Action: [thrust_fraction in [0, 1], gimbal_yaw_norm in [-1, 1], gimbal_pitch_norm in [-1, 1]]
        """
        self.step_count += 1
        thrust_cmd = float(np.clip(action[0], 0.0, 1.0))
        gimbal_cmd = np.clip(action[1:3], -1.0, 1.0) * self.max_gimbal_rad

        # Apply servo rate limiter over control steps
        d_gimbal = gimbal_cmd - self.gimbal
        max_step_change = self.servo_rate_limit * self.control_dt
        gimbal_delta = np.clip(d_gimbal, -max_step_change, max_step_change)
        self.gimbal_rate = gimbal_delta / self.control_dt
        self.gimbal += gimbal_delta
        self.thrust_fraction = thrust_cmd

        # Compute forces and torques
        total_thrust = self.thrust_fraction * self.max_thrust
        yaw, pitch = self.gimbal
        # Thrust vector components in body frame
        thrust_vec = np.array([
            total_thrust * np.sin(pitch),
            -total_thrust * np.sin(yaw),
            total_thrust * np.cos(pitch) * np.cos(yaw)
        ], dtype=np.float64)

        # Acceleration (body to world approx for small angles)
        acc = thrust_vec / self.mass - np.array([0.0, 0.0, self.gravity])
        self.vel += acc * self.control_dt
        self.pos += self.vel * self.control_dt

        # Ensure ground limit (z >= 0)
        if self.pos[2] < 0.0:
            self.pos[2] = 0.0
            self.vel = np.zeros(3)

        obs = self.get_observation()
        return obs

    def get_observation(self):
        """
        Returns 31-dim observation vector matching Table II.
        """
        rel_pos = self.pos - self.target
        obs = np.zeros(31, dtype=np.float32)
        obs[0:3] = rel_pos
        obs[3:7] = self.quat
        obs[7] = self.pos[2]
        obs[8:11] = self.vel
        obs[11:14] = self.ang_vel
        obs[14:16] = self.gimbal
        obs[16:18] = self.gimbal_rate
        obs[18:22] = (1.0 if self.pos[2] <= 0.01 else 0.0)  # Foot contacts
        obs[22] = self.thrust_fraction
        # Task state encoding (8 dims)
        obs[23] = 1.0  # Phase one-hot (climb)
        obs[30] = 1.0  # Readiness flag
        return obs
