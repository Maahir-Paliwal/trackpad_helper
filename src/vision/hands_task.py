from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple
import time

import cv2
import numpy as np
import mediapipe as mp

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

@dataclass(frozen=True)
class HandLandmarks:
    norm_landmarks: np.ndarray  # **how does this data actually look?

@dataclass(frozen=True)
class HandsResult:
    image_size: Tuple[int, int]    #(w,h)
    hands: List[HandLandmarks]

class HandsTask:
    def __init__(self, num_hands: int = 2) -> None:
        model_path = str(Path(__file__).resolve().parent.parent.parent / "model" / "hand_landmarker.task")
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.VIDEO,
            num_hands=num_hands,
        )
        self.landmarker = HandLandmarker.create_from_options(options)
        self.t0 = time.monotonic()

    def close(self) -> None:
        self.landmarker.close()

    def __enter__(self) -> "HandsTask":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def detect(self, frame_bgr : np.ndarray) -> HandsResult:
        h,w = frame_bgr.shape[:2]
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

        timestamp_ms = int((time.monotonic() - self.t0) * 1000)
        result = self.landmarker.detect_for_video(mp_image, timestamp_ms)

        hands: List[HandLandmarks] = []
        if result.hand_landmarks:
            for hand in result.hand_landmarks:
                    norm = np.array([[lm.x, lm.y, lm.z] for lm in hand], dtype=np.float32)
                    hands.append(HandLandmarks(norm_landmarks=norm)) # [(21,3), (21,3)]

        return HandsResult(image_size=(w,h), hands=hands)

        
