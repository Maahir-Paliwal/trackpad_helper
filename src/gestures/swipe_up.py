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
    last_dy: float

class TwoFingerSwipeUpDetector:
    def __init__(
            self, 
            deadband_px: int = 5,           # ignore tiny jitters
            sensitivity: float = 1.6,       # higher is faster scrolls
            max_step_px: int = 80           # clamp to avoid misreads and spikes           
    ) -> None:
        self.deadband_px = deadband_px
        self.sensitivity = sensitivity
        self.max_step_px = max_step_px
        self.state: Optional[TrackState] = None
    
    
    @staticmethod
    def two_fingers_extended(hand_norm: np.ndarray) -> bool:
        # y decreases upward in image coords
        index_extended = hand_norm[INDEX_TIP,1] < hand_norm[INDEX_PIP, 1]
        middle_extended = hand_norm[MIDDLE_TIP,1] < hand_norm[MIDDLE_PIP,1]
        return bool(index_extended and middle_extended)
    
    
    @staticmethod
    def avg_two_tip_y(hand_norm: np.ndarray) -> float:
        return float((hand_norm[INDEX_TIP, 1] + hand_norm[MIDDLE_TIP,1]) / 2.0)
    
    def update(self, hand_norm: Optional[np.ndarray], frame_h: int) -> Optional[int]:
        
        now = time.monotonic()

        if hand_norm is None:
                self.state = None
                return None
        
        
        if not self.two_fingers_extended(hand_norm):
             self.state = None
             return None
        

        y = self.avg_two_tip_y(hand_norm)

        # if it is the first frame which recognizes the movement
        if self.state is None:
             self.state = TrackState(last_y=y, last_t=now, last_dy=0.0)
             return None
        
        #upward movement means y decreases
        dy_now = self.state.last_y - y          # y1 - y2 pos if moving up 
        self.state.last_y = y
        self.state.last_t = now


        #smooth with last reading
        dy_smooth = 0.8 * self.state.last_dy + 0.2 * dy_now
        self.state.last_dy = dy_now             # update last_dy after usage

        dy_px = int(dy_smooth * frame_h * self.sensitivity)


        # deadbacd to kill jitter
        if abs(dy_px) < self.deadband_px:
             return None

        
        if dy_px > self.max_step_px:
            dy_px = self.max_step_px
        elif dy_px < -self.max_step_px:
            dy_px = -self.max_step_px
        
        return dy_px
             
