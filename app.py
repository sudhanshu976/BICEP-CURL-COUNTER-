# Importing Libraries and dependencies
import cv2
import mediapipe as mp
import numpy as np

# Storing main utilities
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Function for calculating angles
def calculateAngle(a, b, c):
    a = np.array(a)  # First Point
    b = np.array(b)  # Second Point
    c = np.array(c)  # Last Point
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle
    return angle

# Counter
counter = 0
stage = None

cap = cv2.VideoCapture(0)

# Setup Mediapipe
with mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7) as pose:
    while cap.isOpened():
        ret, frame = cap.read()

        # Flip the frame horizontally
        frame = cv2.flip(frame, 1)

        # Recolour image as mediapipe accepts RGB only
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Make detection
        results = pose.process(image_rgb)

        # Extract landmarks
        try:
            landmarks = results.pose_landmarks.landmark
            #print(len(landmarks))
            #print(landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value])
            # there are 33 landmarks that specify each body part : here we want 11,13 and 15

            # Our main three Landmarks
            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]

            elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]

            wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

            # print("SHOULDER : ",shoulder)
            # print("ELBOW : ",elbow)
            # print("WRIST : ",wrist)

            angle = calculateAngle(shoulder, elbow, wrist)
            #print("ANGLE : ",angle)

            if angle > 155:
                stage = "DOWN"
            elif angle < 20 and stage == "DOWN":
                stage = "UP"
                counter = counter + 1
                #print(counter)

        except:
            pass

        # Rendering landmarks
        # 1st drawingSpec : for dots and 2nd DrawingSpec for connections
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color=(255, 0, 255), thickness=2, circle_radius=2),
                                      mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2))

        # Displaying Counter and Stage on the screen
        cv2.putText(frame, f"Counter: {counter}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, f"Stage: {stage}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow("Image FEED", frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
