import cv2
import numpy as np
import mediapipe as mp
import pygame
import time
import math

class HeadTracker:
    def __init__(self):
        """Initialize head tracker"""
        # Initialize MediaPipe face detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        
        # Try other cameras if the first one fails
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(1)
        
        # Use simulated data if camera still fails
        if not self.cap.isOpened():
            print("Warning: Camera not available, using simulated data")
            self.cap = None
        
        # Calibration parameters
        self.calibration_samples = []
        self.calibration_count = 30  # Collect 30 samples for calibration
        self.is_calibrated = False
        self.neutral_angle = 0.0
        self.neutral_tilt = 0.0
        
        # Sensitivity parameters
        self.angle_sensitivity = 2.0  # Left/right turning sensitivity
        self.tilt_sensitivity = 2.0   # Forward/backward tilt sensitivity
        
        # Smoothing parameters
        self.smoothing_factor = 0.3  # Lower value means stronger smoothing
        self.last_angle = 0.0
        self.last_tilt = 0.0
        
        # Timeout detection
        self.last_detection_time = time.time()
        self.detection_timeout = 1.0  # 1 second without detection is considered face loss
        
        # Current frame and face detection results
        self.frame = None
        self.results = None
        self.face_detected = False
        
        # Store recent head angles and tilts for smoothing
        self.recent_angles = [0.0] * 5
        self.recent_tilts = [0.0] * 5
        
        # Current frame and processed frame
        self.current_frame = None
        self.processed_frame = None
        
        # Current head angle and tilt
        self.current_angle = 0.0
        self.current_tilt = 0.0
        
        # Control indicator parameters
        self.indicator_radius = 50
        self.indicator_center = (80, 80)  # Top-left position
        
        # Initialize pygame surface
        self.surface = None
        self.frame_surface = None
        
        # Last time face was detected
        self.last_face_time = time.time()
        self.face_timeout = 0.5  # Face timeout in seconds
        
        print("Head tracker initialized")
    
    def calibrate(self):
        """Calibrate head position"""
        print("Starting head position calibration...")
        print("Please keep your head in neutral position, facing the camera...")
        
        self.calibration_samples = []
        self.is_calibrated = False
        
        # Collect calibration samples
        calibration_start = time.time()
        while len(self.calibration_samples) < self.calibration_count:
            # Check for timeout
            if time.time() - calibration_start > 10:  # 10 seconds timeout
                print("Calibration timeout, using default values")
                self.neutral_angle = 0.0
                self.neutral_tilt = 0.0
                self.is_calibrated = True
                return False
            
            # Update head tracking
            if not self.update(calibration_mode=True):
                continue
            
            # Get current head angle and tilt
            angle, tilt = self._calculate_head_pose()
            
            if angle is not None and tilt is not None:
                self.calibration_samples.append((angle, tilt))
                print(f"Collecting calibration sample: {len(self.calibration_samples)}/{self.calibration_count}")
                time.sleep(0.1)  # Short delay
        
        # Calculate neutral position
        if self.calibration_samples:
            angles, tilts = zip(*self.calibration_samples)
            self.neutral_angle = sum(angles) / len(angles)
            self.neutral_tilt = sum(tilts) / len(tilts)
            self.is_calibrated = True
            print(f"Calibration complete: neutral angle={self.neutral_angle:.2f}, neutral tilt={self.neutral_tilt:.2f}")
            return True
        else:
            print("Calibration failed, using default values")
            self.neutral_angle = 0.0
            self.neutral_tilt = 0.0
            self.is_calibrated = True
            return False
    
    def update(self, calibration_mode=False):
        """Update head tracking"""
        # Read camera frame
        ret, self.frame = self.cap.read()
        if not ret or self.frame is None:
            print("Cannot read from camera")
            return False
        
        # Flip image horizontally (mirror effect)
        self.frame = cv2.flip(self.frame, 1)
        
        # Convert to RGB
        rgb_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        
        # Process image
        self.results = self.face_mesh.process(rgb_frame)
        
        # Check if face is detected
        if self.results.multi_face_landmarks:
            self.face_detected = True
            self.last_detection_time = time.time()
            
            # Don't draw in calibration mode
            if not calibration_mode:
                self._draw_face_mesh()
                self._draw_control_indicators()
                self._draw_acceleration_status()
        else:
            # Check for timeout
            if time.time() - self.last_detection_time > self.detection_timeout:
                self.face_detected = False
                
                # Display hint on image
                cv2.putText(
                    self.frame, 
                    "No face detected", 
                    (50, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1, 
                    (0, 0, 255), 
                    2
                )
        
        return self.face_detected
    
    def get_head_angle(self):
        """Get head left/right angle, range [-1, 1]"""
        if not self.face_detected:
            return 0.0
        
        angle, _ = self._calculate_head_pose()
        
        if angle is None:
            return 0.0
        
        # Apply calibration
        if self.is_calibrated:
            angle = angle - self.neutral_angle
        
        # Apply sensitivity
        angle = angle * self.angle_sensitivity
        
        # Limit range
        angle = max(-1.0, min(1.0, angle))
        
        # Smooth processing
        angle = self.last_angle * (1 - self.smoothing_factor) + angle * self.smoothing_factor
        self.last_angle = angle
        
        return angle
    
    def get_head_tilt(self):
        """Get head forward/backward tilt, range [-1, 1]"""
        if not self.face_detected:
            return 0.0
        
        _, tilt = self._calculate_head_pose()
        
        if tilt is None:
            return 0.0
        
        # Apply calibration
        if self.is_calibrated:
            tilt = tilt - self.neutral_tilt
        
        # Apply sensitivity
        tilt = tilt * self.tilt_sensitivity
        
        # Limit range
        tilt = max(-1.0, min(1.0, tilt))
        
        # Smooth processing
        tilt = self.last_tilt * (1 - self.smoothing_factor) + tilt * self.smoothing_factor
        self.last_tilt = tilt
        
        # Save current tilt for display
        self.current_tilt = tilt
        
        return tilt
    
    def _calculate_head_pose(self):
        """Calculate head pose"""
        if not self.results.multi_face_landmarks:
            return None, None
        
        face_landmarks = self.results.multi_face_landmarks[0]
        
        # Get key points
        nose_tip = face_landmarks.landmark[4]
        left_eye = face_landmarks.landmark[33]
        right_eye = face_landmarks.landmark[263]
        mouth_left = face_landmarks.landmark[61]
        mouth_right = face_landmarks.landmark[291]
        
        # Calculate head left/right angle (based on eye horizontal line)
        dx_eyes = right_eye.x - left_eye.x
        dy_eyes = right_eye.y - left_eye.y
        angle = math.atan2(dy_eyes, dx_eyes)
        
        # Calculate head forward/backward tilt (based on vertical distance between nose tip and mouth center)
        mouth_center_y = (mouth_left.y + mouth_right.y) / 2
        tilt = nose_tip.z  # Use nose tip z-coordinate to represent forward/backward tilt
        
        return angle, tilt
    
    def _draw_face_mesh(self):
        """Draw face mesh"""
        if not self.results.multi_face_landmarks:
            return
        
        h, w, c = self.frame.shape
        face_landmarks = self.results.multi_face_landmarks[0]
        
        # Draw key points
        for idx, landmark in enumerate(face_landmarks.landmark):
            x, y = int(landmark.x * w), int(landmark.y * h)
            
            # Only draw some key points to avoid overcrowding
            if idx % 5 == 0:
                cv2.circle(self.frame, (x, y), 1, (0, 255, 0), -1)
        
        # Draw eyes
        left_eye = [(33, 160), (160, 158), (158, 133), (133, 153), (153, 144), (144, 33)]
        right_eye = [(263, 387), (387, 385), (385, 362), (362, 382), (382, 381), (381, 263)]
        
        for connections in [left_eye, right_eye]:
            for start_idx, end_idx in connections:
                start_point = face_landmarks.landmark[start_idx]
                end_point = face_landmarks.landmark[end_idx]
                
                start_x, start_y = int(start_point.x * w), int(start_point.y * h)
                end_x, end_y = int(end_point.x * w), int(end_point.y * h)
                
                cv2.line(self.frame, (start_x, start_y), (end_x, end_y), (0, 255, 255), 1)
        
        # Draw mouth outline
        mouth_outline = [(61, 146), (146, 91), (91, 181), (181, 84), (84, 17), 
                         (17, 314), (314, 405), (405, 321), (321, 375), (375, 291)]
        
        for start_idx, end_idx in mouth_outline:
            start_point = face_landmarks.landmark[start_idx]
            end_point = face_landmarks.landmark[end_idx]
            
            start_x, start_y = int(start_point.x * w), int(start_point.y * h)
            end_x, end_y = int(end_point.x * w), int(end_point.y * h)
            
            cv2.line(self.frame, (start_x, start_y), (end_x, end_y), (0, 255, 255), 1)
    
    def _draw_control_indicators(self):
        """Draw control indicators"""
        if not self.results.multi_face_landmarks:
            return
        
        h, w, c = self.frame.shape
        
        # Get head angle and tilt
        angle = self.get_head_angle()
        tilt = self.get_head_tilt()
        
        # Draw left/right turning indicator
        cv2.rectangle(self.frame, (w//2 - 100, h - 60), (w//2 + 100, h - 40), (255, 255, 255), 1)
        indicator_x = int(w//2 + angle * 100)
        cv2.rectangle(self.frame, (indicator_x - 5, h - 60), (indicator_x + 5, h - 40), (0, 255, 0), -1)
        cv2.putText(self.frame, "Left/Right", (w//2 - 40, h - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Draw forward/backward tilt indicator
        cv2.rectangle(self.frame, (w - 60, h//2 - 100), (w - 40, h//2 + 100), (255, 255, 255), 1)
        indicator_y = int(h//2 + tilt * 100)
        cv2.rectangle(self.frame, (w - 60, indicator_y - 5), (w - 40, indicator_y + 5), (0, 255, 0), -1)
        cv2.putText(self.frame, "Closer=Brake, Away=Accel", (w - 200, h//2 - 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Draw calibration status
        if self.is_calibrated:
            status_text = "Calibrated"
            color = (0, 255, 0)
        else:
            status_text = "Not Calibrated"
            color = (0, 0, 255)
        
        cv2.putText(self.frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Draw sensitivity information
        cv2.putText(
            self.frame, 
            f"Sensitivity: Angle={self.angle_sensitivity:.1f}, Tilt={self.tilt_sensitivity:.1f}", 
            (10, h - 10), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.5, 
            (255, 255, 255), 
            1
        )
        
        # Draw current angle and tilt
        cv2.putText(
            self.frame, 
            f"Angle: {angle:.2f}, Tilt: {tilt:.2f}", 
            (10, 60), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.5, 
            (255, 255, 255), 
            1
        )
    
    def _draw_acceleration_status(self):
        """Draw acceleration status"""
        if not hasattr(self, 'current_tilt'):
            return
        
        h, w, c = self.frame.shape
        tilt = self.current_tilt
        
        # Create status area
        status_area = np.zeros((80, 200, 3), dtype=np.uint8)
        
        # Display different status based on tilt
        if tilt < -0.1:  # Accelerating
            cv2.putText(
                self.frame, 
                "Accelerating", 
                (w//2 - 60, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.8, 
                (0, 255, 0), 
                2
            )
            # Draw acceleration arrow
            cv2.arrowedLine(
                self.frame,
                (w//2, 60),
                (w//2, 100),
                (0, 255, 0),
                2,
                tipLength=0.3
            )
        elif tilt > 0.1:  # Braking
            cv2.putText(
                self.frame, 
                "Braking", 
                (w//2 - 40, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.8, 
                (0, 0, 255), 
                2
            )
            # Draw braking arrow
            cv2.arrowedLine(
                self.frame,
                (w//2, 100),
                (w//2, 60),
                (0, 0, 255),
                2,
                tipLength=0.3
            )
        else:  # Constant speed
            cv2.putText(
                self.frame, 
                "Steady", 
                (w//2 - 30, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.8, 
                (255, 255, 0), 
                2
            )
            # Draw steady line
            cv2.line(
                self.frame,
                (w//2 - 30, 80),
                (w//2 + 30, 80),
                (255, 255, 0),
                2
            )
    
    def get_video_frame(self):
        """
        Get processed video frame
        
        Returns:
            numpy.ndarray: Processed video frame
        """
        return self.processed_frame
    
    def get_frame_surface(self, width=None, height=None):
        """Get current frame as pygame surface"""
        if self.frame is None:
            # Create a black image
            img = np.zeros((height or 480, width or 640, 3), dtype=np.uint8)
            cv2.putText(img, "Camera not available", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        else:
            img = self.frame.copy()
        
        # Resize
        if width is not None and height is not None:
            img = cv2.resize(img, (width, height))
        
        # Convert to pygame surface - fix rotation issue
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Create Surface directly, without rotation
        surface = pygame.surfarray.make_surface(img.swapaxes(0, 1))
        
        return surface
    
    def __del__(self):
        """Release resources"""
        if self.cap is not None:
            self.cap.release()
        self.face_mesh.close()
        cv2.destroyAllWindows() 