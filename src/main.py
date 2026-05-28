import cv2
import numpy as np
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

    # Zmienne dla ćwiczenia Overhead Press (OHP)
    count = 0
    dir = 0  # 0 = faza ruchu w górę, 1 = faza ruchu w dół
    feedback_msg = "Przygotuj sie"
    color = (0, 0, 255)

    while cap.isOpened():
        success, img = cap.read()
        if not success:
            break

        # Mapowanie punktów charakterystycznych sylwetki (Landmarks)
        img = detector.find_pose(img)
        lm_list = detector.find_position(img, draw=False)

        if len(lm_list) != 0:
            # Punkty dla lewego ramienia (11-bark, 13-łokieć, 15-nadgarstek)
            angle_left = detector.find_angle(img, 11, 13, 15, draw=True)
            # Punkty dla prawego ramienia (12-bark, 14-łokieć, 16-nadgarstek)
            angle_right = detector.find_angle(img, 12, 14, 16, draw=True)

            # Uśredniony kąt z obu rąk dla płynności
            avg_angle = (angle_left + angle_right) / 2

            # Obliczenie procentu i paska postępu
            # Kąt około 70 stopni to pozycja startowa, 160 stopni to pełne wyprostowanie
            per = np.interp(avg_angle, (70, 160), (0, 100))
            bar = np.interp(avg_angle, (70, 160), (600, 100))

            # Sprawdzenie asymetrii i biomechaniki (prawidłowość ćwiczenia)
            
            # Pobranie koordynatów X i Y dla łokci, nadgarstków i barków w celu sprawdzania techniki
            x_sh_l, y_sh_l = lm_list[11][1:]
            x_sh_r, y_sh_r = lm_list[12][1:]
            x_el_l, y_el_l = lm_list[13][1:]
            x_el_r, y_el_r = lm_list[14][1:]
            x_wr_l, y_wr_l = lm_list[15][1:]
            x_wr_r, y_wr_r = lm_list[16][1:]

            # Różnica w osi X między nadgarstkiem a łokciem mówi nam, jak bardzo przedramię odchyla się od pionu
            forearm_tilt_l = abs(x_wr_l - x_el_l)
            forearm_tilt_r = abs(x_wr_r - x_el_r)
            tilt_threshold = 80  # Dozwolone odchylenie w pikselach dla przedramion

            if abs(angle_left - angle_right) > 35:
                feedback_msg = "Wyrownaj ramiona!"
                color = (0, 0, 255)
            elif forearm_tilt_l > tilt_threshold or forearm_tilt_r > tilt_threshold:
                feedback_msg = "Pionuj przedramiona!"
                color = (0, 165, 255)  # Pomarańczowy kolor (BGR) dla błędu technicznego
            elif (y_el_l > y_sh_l + 70) or (y_el_r > y_sh_r + 70):
                feedback_msg = "Lokcie za nisko!"
                color = (0, 165, 255)
            else:
                feedback_msg = "Dobra forma"
                color = (0, 255, 0)
                
            # Zliczanie powtórzeń na podstawie fazy ruchu
            if per == 100:  # Ramiona w pełni w górze
                if dir == 0:
                    count += 0.5
                    dir = 1
            if per == 0:    # Ramiona w dół (pozycja startowa)
                if dir == 1:
                    count += 0.5
                    dir = 0
                    # Zliczaj i sygnalizuj powtórzenie
                    audio.play_notification("rep_done")

            # Rysowanie interfejsu (pasek postępu)
            cv2.rectangle(img, (1100, 100), (1175, 600), color, 3)
            cv2.rectangle(img, (1100, int(bar)), (1175, 600), color, cv2.FILLED)
            cv2.putText(img, f'{int(per)} %', (1100, 75), cv2.FONT_HERSHEY_PLAIN, 4, color, 4)

            # Rysowanie informacji tekstowych
            cv2.rectangle(img, (0, 0), (450, 150), (255, 255, 255), cv2.FILLED)
            cv2.putText(img, f'Powt: {int(count)}', (20, 70), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 5)
            cv2.putText(img, feedback_msg, (20, 130), cv2.FONT_HERSHEY_PLAIN, 2, color, 3)

        cv2.imshow("Cyber Trener - Podglad OHP (v0.1)", img)

        # Zakończenie pracy programu po wciśnięciu klawisza 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()