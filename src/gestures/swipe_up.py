from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import time

import numpy as np

INDEX_TIP = 8
INDEX_PIP = 6
MIDDLE_TIP = 12
MIDDLE_PIP = 10

@dataclass
class TrackState:
    last_y: float
    last_t: float
    accum_up: float


class TwoFingerSwipeUpDetector:
    def __init__(
            self, 
            min_up_movement: float = 0.10,# normalized y movement [0,1]
            max_window_s: float = 0.45, 
            cooldown_s: float = 0.70,
    ) -> None:
        self.min_up_movement = min_up_movement
        self.max_window_s = max_window_s
        self.cooldown_s = cooldown_s

        self.state: Optional[TrackState] = None
        self.cooldown_until = 0.0
    
    @staticmethod
    def two_fingers_extended(hand_norm: np.ndarray) -> bool:
        # y decreases upward in image coords
        index_extended = hand_norm[INDEX_TIP,1] < hand_norm[INDEX_PIP, 1]
        middle_extended = hand_norm[MIDDLE_TIP,1] < hand_norm[MIDDLE_PIP,1]
        return bool(index_extended and middle_extended)
    
    @staticmethod
    def avg_two_tip_y(hand_norm: np.ndarray) -> float:
        return float((hand_norm[INDEX_TIP, 1] + hand_norm[MIDDLE_TIP,1]) / 2.0)
    
    def update(self, hand_norm: Optional[np.ndarray]) -> bool:
        
        now = time.monotonic()

        if now < self.cooldown_until:
            return False
        
        if hand_norm is None:
                self.state = None
                return False
        
        if not self.two_fingers_extended(hand_norm):
             self.state = None
             return False
        
        y = self.avg_two_tip_y(hand_norm)

        if self.state is None:
             self.state = TrackState(last_y=y, last_t=now, accum_up=0.0)
             return False
        
        dt = now - self.state.last_t
        if dt <= 0:
             return False
        
        #upward movement means y decreases
        dy = self.state.last_y - y          # y1 - y2 pos if moving up 
        self.state.accum_up += max(dy, 0.0)
        self.state.last_y = y
        self.state.last_t = now
        
        #reset if too slow
        if dt > self.max_window_s:
             self.state = TrackState(last_y=y, last_t=now, accum_up=0.0)
             return False
        
        if self.state.accum_up >= self.min_up_movement: # TODO: understand accum_up
             self.state = None
             self.cooldown_until = now + self.cooldown_s
             return True
        
        return False
             
