import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque

mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5,
    model_complexity=1
)

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

class EnhancedCrosshair:
    def __init__(self):
        self.size = 150
        self.min_size = 25
        self.shrink_speed = 8
        self.active = False
        self.position = (0, 0)
        self.pulse_phase = 0
        self.lock_time = 0
        self.locked = False
        
    def start(self, pos):
        self.position = pos
        self.size = 150
        self.active = True
        self.pulse_phase = 0
        self.lock_time = time.time()
        self.locked = False
        
    def deactivate(self):
        self.active = False
        self.locked = False
        self.size = self.min_size
    

    def update_and_draw(self, frame):
        if self.active:
            x, y = self.position
            current_time = time.time()
            
            if current_time - self.lock_time > 2.0 and not self.locked:
                self.locked = True
            
            if self.locked:
                pulse = 10 * np.sin(self.pulse_phase)
                display_size = self.min_size + pulse
                color = (0, 255, 255)
                self.pulse_phase += 0.3
            else:
                display_size = self.size
                color = (0, 0, 255)
            
            thickness = 3 if self.locked else 2
            
            cv2.line(frame, (int(x - display_size), y), (int(x + display_size), y), color, thickness)
            cv2.line(frame, (x, int(y - display_size)), (x, int(y + display_size)), color, thickness)
            cv2.circle(frame, (x, y), int(display_size), color, thickness)
            
            bracket_size = int(display_size * 0.3)
            cv2.line(frame, (x - bracket_size, y - bracket_size), (x - bracket_size + 15, y - bracket_size), color, thickness)
            cv2.line(frame, (x - bracket_size, y - bracket_size), (x - bracket_size, y - bracket_size + 15), color, thickness)
            cv2.line(frame, (x + bracket_size, y - bracket_size), (x + bracket_size - 15, y - bracket_size), color, thickness)
            cv2.line(frame, (x + bracket_size, y - bracket_size), (x + bracket_size, y - bracket_size + 15), color, thickness)
            cv2.line(frame, (x - bracket_size, y + bracket_size), (x - bracket_size + 15, y + bracket_size), color, thickness)
            cv2.line(frame, (x - bracket_size, y + bracket_size), (x - bracket_size, y + bracket_size - 15), color, thickness)
            cv2.line(frame, (x + bracket_size, y + bracket_size), (x + bracket_size - 15, y + bracket_size), color, thickness)
            cv2.line(frame, (x + bracket_size, y + bracket_size), (x + bracket_size, y + bracket_size - 15), color, thickness)
            
            if self.size > self.min_size and not self.locked:
                self.size -= self.shrink_speed
            
            return self.locked
        return False

class GestureDetector:
    def __init__(self, smoothing_window=5):
        self.detection_history = deque(maxlen=smoothing_window)
        
    def is_middle_finger_only_up(self, landmarks):
        finger_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        finger_pips = [3, 6, 10, 14, 18]
        
        fingers_up = []
        
        if landmarks[finger_tips[0]].x > landmarks[finger_pips[0]].x:
            fingers_up.append(1)
        else:
            fingers_up.append(0)
            
        for i in range(1, 5):
            if landmarks[finger_tips[i]].y < landmarks[finger_pips[i]].y:
                fingers_up.append(1)
            else:
                fingers_up.append(0)
        return fingers_up == [0, 0, 1, 0, 0]
    
    def detect_gesture(self, hand_landmarks):
        """Smoothed gesture detection"""
        is_middle_up = self.is_middle_finger_only_up(hand_landmarks.landmark)
        self.detection_history.append(is_middle_up)
        
        return sum(self.detection_history) > len(self.detection_history) // 2

class TargetSystem:
    def __init__(self):
        self.crosshair = EnhancedCrosshair()

        self.gesture_detector = GestureDetector()
        self.target_locked = False
        self.fps_counter = deque(maxlen=30)
        
    def get_forehead_position(self, face_landmarks, frame_shape):
        h, w, _ = frame_shape

        forehead_indices = [10, 151, 9, 10]
        
        avg_x = sum(face_landmarks[i].x for i in forehead_indices) / len(forehead_indices)
        avg_y = sum(face_landmarks[i].y for i in forehead_indices) / len(forehead_indices)
        
        return (int(avg_x * w), int(avg_y * h - 40))
    
    def draw_ui(self, frame, target_detected, fps):
        """Scary UI drawing"""
        h, w, _ = frame.shape
        
        if target_detected:
            if self.target_locked:
                status_text = 'Over'
                status_color = (0, 0, 200)
                shake_x = int(5 * np.sin(time.time() * 20))
                shake_y = int(3 * np.cos(time.time() * 15))
            else:
                status_text = 'Bad Guy Detected'
                status_color = (0, 0, 255)
                shake_x = shake_y = 0
        else:
            status_text = 'Good Guy'
            status_color = (0, 255, 0)
            shake_x = shake_y = 0
        
        text_x = 20 + shake_x
        text_y = 50 + shake_y
        
        cv2.putText(frame, status_text, (text_x + 2, text_y + 2), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 0), 4)  # Shadow
        cv2.putText(frame, status_text, (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX, 1.2, status_color, 3)
        
        cv2.putText(frame, f'FPS: {fps:.0f}', (w - 100, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)
        
        cv2.putText(frame, 'Middle finger to target | Q to quit', (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
        
        if target_detected:
            threat_text = "THREAT LEVEL: MAXIMUM"
            cv2.putText(frame, threat_text, (text_x, text_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    target_system = TargetSystem()
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read from camera")
            break
        
        frame_start = time.time()
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        hand_results = hands.process(rgb)
        face_results = face_mesh.process(rgb)
        
        hostile_detected = False
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                if target_system.gesture_detector.detect_gesture(hand_landmarks):
                    hostile_detected = True
                    break
        
        if face_results.multi_face_landmarks and hostile_detected:
            face_landmarks = face_results.multi_face_landmarks[0].landmark
            forehead_pos = target_system.get_forehead_position(face_landmarks, frame.shape)
            target_system.crosshair.start(forehead_pos)
        elif not hostile_detected:
            target_system.crosshair.deactivate()
        
        target_system.target_locked = target_system.crosshair.update_and_draw(frame)
        
        frame_end = time.time()
        frame_time = frame_end - frame_start
        fps = 1.0 / frame_time if frame_time > 0 else 0
        target_system.fps_counter.append(fps)
        avg_fps = sum(target_system.fps_counter) / len(target_system.fps_counter)
        
        target_system.draw_ui(frame, hostile_detected, avg_fps)
        
        cv2.imshow('Good Guy, Bad Guy Detector', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break
        
        frame_count += 1
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()