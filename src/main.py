import cv2
from pose_module import PoseDetector
from voice import VoiceController
from audio_module import AudioFeedback

def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    detector = PoseDetector()
    audio = AudioFeedback()
    voice = VoiceController()

    print("System Cyber Trener v0.1 uruchomiony. Naciśnij 'q', aby wyjść.")

    while cap.isOpened():
        success, img = cap.read()
        if not success:
            break

        # Mapowanie punktów charakterystycznych sylwetki (Landmarks)
        img = detector.find_pose(img)
        lm_list = detector.find_position(img, draw=False)

        cv2.imshow("Cyber Trener - Podglad OHP (v0.1)", img)

        # Zakończenie pracy programu po wciśnięciu klawisza 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()