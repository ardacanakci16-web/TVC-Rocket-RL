"""
Failure-Mode-Driven Reward Shaping & Handoff Gate Evaluation Engine
Implements Section III-E (Reward Redesign) and Table III (Handoff Gates)
from the Acta Astronautica paper.
"""
import numpy as np

class TVCRewardShaper:
    """
    Computes reward terms for TVC rocket climb, supporting both the baseline
    (defective) formulation and the redesigned multi-scale formulation.
    """
    @staticmethod
    def compute_center_attraction(lateral_dist, mode="redesigned"):
        d = lateral_dist
        if mode == "defective":
            # Decays to ~0.001 at 4m, producing dead gradient
            return float(np.exp(- (d / 1.5)**2))
        else:
            # Two-scale Gaussian preserving sharpness and extending gradient to boundary
            return float(0.6 * np.exp(- (d / 1.5)**2) + 0.4 * np.exp(- (d / 4.5)**2))

    @staticmethod
    def compute_drift_penalty(lateral_dist, mode="redesigned"):
        d = lateral_dist
        if mode == "defective":
            # Saturates beyond 3m
            return float(d / (d + 2.0))
        else:
            # Linear component restoring constant slope up to termination boundary
            return float(0.5 * (d / (d + 2.0)) + 0.5 * min(d / 4.0, 1.5))

    @staticmethod
    def compute_directional_velocity_bonus(v_closing):
        # Additive signed bonus for motion toward target, penalizing motion away
        return float(np.tanh(v_closing / 2.0))

    @classmethod
    def evaluate_step_reward(cls, lateral_dist, v_closing, altitude, target_alt=10.4, mode="redesigned"):
        attract = cls.compute_center_attraction(lateral_dist, mode=mode)
        drift = cls.compute_drift_penalty(lateral_dist, mode=mode)
        v_bonus = cls.compute_directional_velocity_bonus(v_closing) if mode == "redesigned" else 0.0

        # Altitude tracking reward
        alt_err = abs(altitude - target_alt)
        alt_reward = float(np.exp(- (alt_err / 2.0)**2))

        total = 3.0 * attract - 2.5 * drift + 1.5 * v_bonus + 2.0 * alt_reward
        return {
            "total_reward": total,
            "center_attraction": attract,
            "drift_penalty": drift,
            "directional_bonus": v_bonus,
            "altitude_reward": alt_reward
        }


class HandoffGateEvaluator:
    """
    Evaluates the 9-condition handoff gate window (Table III in paper).
    """
    def __init__(self, mode="calibrated"):
        self.mode = mode
        if mode == "original":
            self.alt_min = 10.0
            self.upright_min = 0.97
            self.dist_max = 1.0
            self.speed_max = 2.0
            self.horiz_speed_max = 2.0
            self.vert_speed_range = (-2.0, 2.0)
            self.ang_speed_max = 0.50
            self.tvc_deflection_max = 0.10  # ~5.7 deg (infeasible under hover)
            self.tvc_joint_speed_max = 0.80 # infeasible under active servo (meas. 16 rad/s)
        else:  # calibrated
            self.alt_min = 10.0
            self.upright_min = 0.97
            self.dist_max = 1.0
            self.speed_max = 2.0
            self.horiz_speed_max = 2.0
            self.vert_speed_range = (-2.0, 2.0)
            self.ang_speed_max = 1.00
            self.tvc_deflection_max = 0.30  # ~17.2 deg
            self.tvc_joint_speed_max = 6.00 # rad/s

    def evaluate(self, state_dict):
        """
        state_dict contains:
          altitude, upright, distance, speed, horiz_speed, vert_speed,
          ang_speed, tvc_deflection, tvc_joint_speed
        """
        conditions = {
            "altitude": state_dict["altitude"] >= self.alt_min,
            "upright": state_dict["upright"] > self.upright_min,
            "distance": state_dict["distance"] <= self.dist_max,
            "speed": state_dict["speed"] <= self.speed_max,
            "horiz_speed": state_dict["horiz_speed"] <= self.horiz_speed_max,
            "vert_speed": (self.vert_speed_range[0] <= state_dict["vert_speed"] <= self.vert_speed_range[1]),
            "ang_speed": state_dict["ang_speed"] <= self.ang_speed_max,
            "tvc_deflection": state_dict["tvc_deflection"] <= self.tvc_deflection_max,
            "tvc_joint_speed": state_dict["tvc_joint_speed"] <= self.tvc_joint_speed_max,
        }
        all_passed = all(conditions.values())
        return all_passed, conditions
