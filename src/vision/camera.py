import cv2
from typing import Iterator
import mediapipe as mp

class Camera:
    def __init__(self, index: int = 0):
        self.index = 0
        self.cap: cv2.VideoCapture | None = None

    def __enter__(self) -> "Camera":
        self.cap = cv2.VideoCapture(self.index)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open Camera")
        return self
    
    def __exit__(self, exc_type, exc, tb) -> None:
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def frames(self) -> Iterator:
        assert self.cap is not None
        while True:
                ok, frame = self.cap.read()
                if ok: 
                    yield frame
    
