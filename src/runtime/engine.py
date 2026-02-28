import signal 
import cv2

from vision.camera import Camera
from vision.hands_task import HandsTask
from gestures.swipe_up import TwoFingerSwipeUpDetector
from actions.hs_socket import HammerSpoonBackend

running = True
def stop(*_):
    global running
    running = False

def run_swipe_up():
    global running
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    backend = HammerSpoonBackend(port=7777)
    detector = TwoFingerSwipeUpDetector(
        min_up_movement=0.10, 
        max_window_s= 0.45,
        cooldown_s=0.70
    )

    with Camera(0) as cam, HandsTask(num_hands=1) as hands:
        for frame in cam.frames():
            if not running:
                break
            res = hands.detect(frame)
            #use first hand if present
            hand_norm = res.hands[0].norm_landmarks if res.hands else None

            if detector.update(hand_norm):
                backend.scroll(dy=-220)
            
            #debug window
            cv2.imshow("debug", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()