"""
TVC Rocket Reinforcement Learning Environment & Dynamics Engine
Acta Astronautica Paper: Failure-Mode-Driven Reward Shaping and Handoff-Gate Calibration
"""
from .rocket_dynamics import TVCRocketDynamics
from .reward_shaping import TVCRewardShaper, HandoffGateEvaluator

__all__ = ["TVCRocketDynamics", "TVCRewardShaper", "HandoffGateEvaluator"]
