import cv2
import mediapipe as mp

# -----------------------------
# Load Pose Landmarker
# -----------------------------

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

options = PoseLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path="models/pose_landmarker_lite.task"
    ),
    running_mode=RunningMode.IMAGE,
    num_poses=1,
)

landmarker = PoseLandmarker.create_from_options(options)

# -----------------------------
# Start webcam
# -----------------------------

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Could not open webcam.")
    exit()

print("Camera started!")
print("Move in front of the camera.")
print("Press Q to quit.")

while True:

    success, frame = cap.read()

    if not success:
        print("Could not read frame.")
        break

    # OpenCV uses BGR
    # MediaPipe expects RGB
    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    # Convert to MediaPipe image
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    # Detect pose
    result = landmarker.detect(mp_image)

    # -----------------------------
    # Check if pose was detected
    # -----------------------------

    if result.pose_landmarks:

        print("POSE DETECTED!")

        # Get the first person's landmarks
        pose = result.pose_landmarks[0]

        # -----------------------------
        # Get shoulders and wrists
        # -----------------------------

        left_shoulder = pose[11]
        right_shoulder = pose[12]

        left_wrist = pose[15]
        right_wrist = pose[16]

        # -----------------------------
        # Check left hand
        # -----------------------------

        if left_wrist.y < left_shoulder.y:
            print("LEFT HAND RAISED!")

        # -----------------------------
        # Check right hand
        # -----------------------------

        if right_wrist.y < right_shoulder.y:
            print("RIGHT HAND RAISED!")

        # -----------------------------
        # Draw all landmarks
        # -----------------------------

        for landmark in pose:

            x = int(
                landmark.x * frame.shape[1]
            )

            y = int(
                landmark.y * frame.shape[0]
            )

            cv2.circle(
                frame,
                (x, y),
                5,
                (0, 255, 0),
                -1
            )

    else:

        print("No pose detected")

    # Show camera
    cv2.imshow(
        "CUT - Pose Detection",
        frame
    )

    # Press Q
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
cv2.destroyAllWindows()
landmarker.close()