import mediapipe as mp
import cv2
import numpy as np
import pyautogui
import time
import sys

# Initialization safety settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

def init_camera():
    """Initialize camera with multiple attempts and different backends"""
    backends = [cv2.CAP_AVFOUNDATION]  # MacOS-specific backend
    
    for backend in backends:
        print(f"Trying camera with backend {backend}")
        cap = cv2.VideoCapture(0, backend)
        
        if cap is None or not cap.isOpened():
            print(f"Failed to open camera with backend {backend}")
            continue
            
        # Try to read a test frame
        ret, frame = cap.read()
        if ret and frame is not None:
            print("Successfully initialized camera")
            return cap
            
        cap.release()
    
    raise RuntimeError("Failed to initialize camera with any backend")

def calculate_distance(point1, point2, frame_width, frame_height):
    """Calculate distance between two points"""
    x1 = int(point1.x * frame_width)
    y1 = int(point1.y * frame_height)
    x2 = int(point2.x * frame_width)
    y2 = int(point2.y * frame_height)
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def main():
    try:
        # Get screen dimensions
        screen_width, screen_height = pyautogui.size()
        print(f"Screen dimensions: {screen_width}x{screen_height}")
        
        # Initialize MediaPipe
        mp_hands = mp.solutions.hands
        mp_drawing = mp.solutions.drawing_utils
        
        print("Initializing camera...")
        cap = init_camera()
        
        # Read one frame to get dimensions
        ret, frame = cap.read()
        if not ret:
            raise RuntimeError("Could not read initial frame")
            
        # Set frame size
        frame_height, frame_width = frame.shape[:2]
        fsize = (frame_height, frame_width)
        print(f"Frame size: {fsize}")
        
        # Define ROI (Region of Interest)
        left = int(frame_width * 0.2)
        right = int(frame_width * 0.8)
        top = int(frame_height * 0.2)
        bottom = int(frame_height * 0.8)
        
        # Initialize hand detection
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        print("Starting main loop...")
        last_event = None
        check_cnt = 0
        check_every = 10  # Reduced for faster response
        
        # Add help text
        help_text = [
            "Gestures:",
            "- Pinch index & thumb: Left Click",
            "- Pinch middle & thumb: Right Click",
            "- Pinch index & middle: Double Click",
            "Press ESC to exit"
        ]
        
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("Failed to read frame")
                break
                
            # Basic frame processing
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process hands
            results = hands.process(rgb_frame)
            
            # Draw ROI
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            
            # Display help text
            y = 30
            for text in help_text:
                cv2.putText(frame, text, (10, y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                y += 25
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks
                    mp_drawing.draw_landmarks(
                        frame, 
                        hand_landmarks, 
                        mp_hands.HAND_CONNECTIONS
                    )
                    
                    # Get landmarks
                    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                    
                    # Convert index tip to pixel coordinates for cursor
                    index_x = int(index_tip.x * frame_width)
                    index_y = int(index_tip.y * frame_height)
                    
                    # Map to screen coordinates for cursor movement
                    if left <= index_x <= right and top <= index_y <= bottom:
                        screen_x = (index_x - left) / (right - left) * screen_width
                        screen_y = (index_y - top) / (bottom - top) * screen_height
                        
                        # Smooth mouse movement
                        try:
                            pyautogui.moveTo(
                                int(screen_x),
                                int(screen_y),
                                duration=0.1,
                                _pause=False
                            )
                        except pyautogui.FailSafeException:
                            print("FailSafe triggered - mouse in corner")
                    
                    # Gesture detection
                    if check_cnt >= check_every:
                        # Calculate distances for different gestures
                        thumb_index_dist = calculate_distance(thumb_tip, index_tip, frame_width, frame_height)
                        thumb_middle_dist = calculate_distance(thumb_tip, middle_tip, frame_width, frame_height)
                        index_middle_dist = calculate_distance(index_tip, middle_tip, frame_width, frame_height)
                        
                        # Left click - thumb and index pinch
                        if thumb_index_dist < 30:
                            if last_event != "left_click":
                                pyautogui.click(button='left')
                                last_event = "left_click"
                                cv2.putText(frame, "Left Click!", (50, frame_height - 50), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        
                        # Right click - thumb and middle pinch
                        elif thumb_middle_dist < 30:
                            if last_event != "right_click":
                                pyautogui.click(button='right')
                                last_event = "right_click"
                                cv2.putText(frame, "Right Click!", (50, frame_height - 50), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        
                        # Double click - index and middle pinch
                        elif index_middle_dist < 30:
                            if last_event != "double_click":
                                pyautogui.doubleClick()
                                last_event = "double_click"
                                cv2.putText(frame, "Double Click!", (50, frame_height - 50), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                        
                        else:
                            last_event = None
                            
                        check_cnt = 0
                    
                    check_cnt += 1
            
            # Display frame
            cv2.imshow('Hand Gesture Control', frame)
            
            # Check for exit
            if cv2.waitKey(1) & 0xFF == 27:  # ESC
                print("ESC pressed, exiting...")
                break
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("Cleaning up...")
        try:
            cap.release()
            cv2.destroyAllWindows()
            print("Cleanup completed")
        except Exception as e:
            print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    print(f"OpenCV version: {cv2.__version__}")
    print(f"Python version: {sys.version}")
    main()