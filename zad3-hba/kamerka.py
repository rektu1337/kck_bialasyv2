import cv2
import mediapipe as mp

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


def rozpoznaj_litere(landmarks):
    l_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    r_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    l_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    r_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
    l_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    r_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]

    tol = 0.15

    if l_hip.y < l_shoulder.y - 0.2 and r_hip.y < r_shoulder.y - 0.2:
        return "M"
    elif abs(l_wrist.y - l_shoulder.y) < tol and abs(r_wrist.y - r_shoulder.y) < tol:
        if l_wrist.x < l_shoulder.x - 0.1 and r_wrist.x > r_shoulder.x + 0.1:
            return "T"
    elif l_wrist.y < l_shoulder.y - 0.15 and r_wrist.y < r_shoulder.y - 0.15:
        return "Y"
    elif l_wrist.y > l_shoulder.y + 0.3 and r_wrist.y > r_shoulder.y + 0.3:
        if abs(l_wrist.x - l_hip.x) < 0.1 and abs(r_wrist.x - r_hip.x) < 0.1:
            return "I"
    elif r_wrist.y < r_shoulder.y - 0.15 and abs(l_wrist.y - l_shoulder.y) < tol:
        if abs(r_wrist.x - r_shoulder.x) < 0.1 and l_wrist.x < l_shoulder.x - 0.1:
            return "L"

    return "Inna / Brak"


def main():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break

            frame = cv2.flip(frame, 1)
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)

            litera = "Szukam..."
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                litera = rozpoznaj_litere(results.pose_landmarks.landmark)

            cv2.putText(frame, f"Litera: {litera}", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
            cv2.imshow('Rozpoznawanie Liter', frame)

            if cv2.waitKey(10) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()