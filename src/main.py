import cv2
import numpy as np
import time
from pose_module import PoseDetector
from voice import VoiceController
from audio_module import AudioFeedback
from user_profile import UserProfileManager


class CyberTrainerApp:
    def __init__(self, username, ip_webcam=""):
        self.username = username
        self.ip_webcam = ip_webcam
        self.profile_mgr = UserProfileManager()
        self.user_data = self.profile_mgr.load_user(username)

        # Moduły Audio & Voice
        self.audio = AudioFeedback()
        self.voice = VoiceController()

        # Słownik liczebników po polsku
        self.NUMBERS_PL = {
            1: "jeden", 2: "dwa", 3: "trzy", 4: "cztery", 5: "pięć",
            6: "sześć", 7: "siedem", 8: "osiem", 9: "dziewięć", 10: "dziesięć",
            11: "jedenaście", 12: "dwanaście", 13: "trzynaście", 14: "czternaście",
            15: "piętnaście", 16: "szesnaście", 17: "siedemnaście", 18: "osiemnaście",
            19: "dziewiętnaście", 20: "dwadzieścia",
        }

        # Zmienne stanu aplikacji
        self.state = "WARMUP"
        self.warmup_start = None

        self.count = 0
        self.dir = 0

        # Osobne komunikaty dla przodu i boku
        self.feedback_warmup = "Rozgrzewka: Unies rece by zaczac!"
        self.feedback_front = "Dobra forma"
        self.feedback_side = ""
        self.color_front = (0, 255, 0)
        self.color_side = (0, 255, 0)
        self.color_warmup = (0, 165, 255)

        self.current_rep_flawed = False
        self.per = 0
        self.bar = 600

        # Zmienne sesji do historii treningowej
        self.session_reps = 0
        self.session_perfect = 0

        self.init_cameras(ip_webcam)

    def init_cameras(self, ip_webcam=""):
        """Inicjalizacja kamery głównej oraz bocznej przez IP Webcam."""
        self.cap_front = cv2.VideoCapture(0)
        self.cap_front.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap_front.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.detector_front = PoseDetector(complexity=1)

        if ip_webcam:
            url = f"http://{ip_webcam}/video"
            cap = cv2.VideoCapture(url)
            if cap.isOpened():
                success, _ = cap.read()
                if success:
                    self.cap_side = cap
                    self.cap_side.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.cap_side.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    self.has_side_cam = True
                    print(f"Połączono z kamerą boczną: {url}")
                else:
                    cap.release()
                    self.has_side_cam = False
                    print("Nie udało się odczytać obrazu z IP Webcam.")
            else:
                self.has_side_cam = False
                print("Nie można połączyć z IP Webcam. Sprawdź IP i czy aplikacja działa.")
        else:
            self.has_side_cam = False
            print("Nie podano IP kamery bocznej. Analiza boczna wyłączona.")

    
        self.detector_side = PoseDetector(complexity=2) if self.has_side_cam else None

    def run(self):
        """Główna pętla programu."""
        while self.cap_front.isOpened():
            success, img_front = self.cap_front.read()
            if not success:
                break

            img_side = None
            if self.has_side_cam:
                self.cap_side.grab()
                self.cap_side.grab()
                self.cap_side.grab()
                s_side, img_side = self.cap_side.retrieve()
                if not s_side:
                    self.has_side_cam = False

            # Przetwarzanie obrazu
            img_front, lm_list_front = self.process_frame(img_front, self.detector_front, draw=True)
            lm_list_side = []
            if self.has_side_cam and img_side is not None:
                img_side, lm_list_side = self.process_frame(img_side, self.detector_side, draw=True)

            # Logika analizy, jeśli wykryto postać
            if len(lm_list_front) != 0:
                self.analyze_pose(img_front, img_side, lm_list_front, lm_list_side)
                self.draw_ui(img_front)

            # Wyświetlanie okien
            cv2.imshow("Cyber Trener - Podglad OHP (v0.1)", img_front)
            if self.has_side_cam and img_side is not None:
                cv2.imshow("Cyber Trener - Profil Boczny", img_side)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cleanup()

    def process_frame(self, img, detector, draw=False):
        """Wykrywanie punktów kluczowych sylwetki na pojedynczej klatce."""
        img = detector.find_pose(img, draw=draw)
        lm_list = detector.find_position(img, draw=draw)
        return img, lm_list

    def analyze_pose(self, img_front, img_side, lm_list_front, lm_list_side):
        """Obliczanie kątów i delegowanie do odpowiedniego stanu (rozgrzewka / ćwiczenie)."""
        angle_left = self.detector_front.find_angle(img_front, 11, 13, 15, draw=True)
        angle_right = self.detector_front.find_angle(img_front, 12, 14, 16, draw=True)
        avg_angle = (angle_left + angle_right) / 2

        self.per = np.interp(avg_angle, (70, 160), (0, 100))
        self.bar = np.interp(avg_angle, (70, 160), (600, 100))

        if self.state == "WARMUP":
            self.handle_warmup()
        elif self.state == "EXERCISE":
            self.handle_exercise(img_front, img_side, angle_left, angle_right, lm_list_front, lm_list_side)

    def handle_warmup(self):
        """Mechanika 3-sekundowej rozgrzewki."""
        if self.per > 90:
            if self.warmup_start is None:
                self.warmup_start = time.time()
            elapsed = time.time() - self.warmup_start
            remaining = 3 - int(elapsed)
            self.feedback_warmup = f"Rozciaganie: Trzymaj! ({remaining}s)"
            self.color_warmup = (0, 235, 255)

            if elapsed >= 3:
                self.state = "EXERCISE"
                self.audio.play_notification("rep_done")
                self.feedback_warmup = "Rozgrzewka OK! Zaczynamy OHP"
                self.color_warmup = (0, 255, 0)
        else:
            self.warmup_start = None
            self.feedback_warmup = "Rozgrzewka: Unies rece by zaczac!"
            self.color_warmup = (0, 165, 255)

    def handle_exercise(self, img_front, img_side, angle_left, angle_right, lm_front, lm_side):
        """Sprawdzanie poprawnej formy ćwiczenia (OHP) na podstawie dwóch widoków."""
        x_sh_l, y_sh_l = lm_front[11][1:]
        x_sh_r, y_sh_r = lm_front[12][1:]
        x_el_l, y_el_l = lm_front[13][1:]
        x_el_r, y_el_r = lm_front[14][1:]
        x_wr_l, y_wr_l = lm_front[15][1:]
        x_wr_r, y_wr_r = lm_front[16][1:]

        forearm_tilt_l = abs(x_wr_l - x_el_l)
        forearm_tilt_r = abs(x_wr_r - x_el_r)
        tilt_threshold = 80

        # Weryfikacja przodu
        front_error = True
        if abs(angle_left - angle_right) > 35:
            self.feedback_front = "Wyrownaj ramiona!"
            self.color_front = (0, 0, 255)
        elif forearm_tilt_l > tilt_threshold or forearm_tilt_r > tilt_threshold:
            self.feedback_front = "Pionuj przedramiona!"
            self.color_front = (0, 165, 255)
        elif (y_el_l > y_sh_l + 70) or (y_el_r > y_sh_r + 70):
            self.feedback_front = "Lokcie za nisko!"
            self.color_front = (0, 165, 255)
        else:
            front_error = False
            self.feedback_front = "Dobra forma"
            self.color_front = (0, 255, 0)

        # Weryfikacja boku - kąt tułowia przez nos->bark->biodro
        
        side_error = False
        if self.has_side_cam and img_side is not None and len(lm_side) != 0:
            try:
                
                angle_torso = self.detector_side.find_angle(
                    img_side, 8, 12, 24, draw=True
                )
                # Wyprostowana sylwetka: kąt ~170-180 stopni
                # Garbienie/wygięcie do tyłu: kąt spada poniżej 155
                if self.per > 30 and angle_torso < 155:
                    side_error = True
                    self.feedback_side = "Nie wyginaj plecow!"
                    self.color_side = (0, 0, 255)
                else:
                    self.feedback_side = "Plecy OK"
                    self.color_side = (0, 255, 0)
            except (IndexError, TypeError):
                self.feedback_side = ""
        elif not self.has_side_cam:
            self.feedback_side = ""

        if front_error or side_error:
            self.current_rep_flawed = True

        self.update_reps()

    def update_reps(self):
        """Aktualizacja ilości powtórzeń i statystyk w profilu użytkownika."""
        if self.per == 100 and self.dir == 0:
            self.count += 0.5
            self.dir = 1
        if self.per == 0 and self.dir == 1:
            self.count += 0.5
            self.dir = 0

            is_perfect = not self.current_rep_flawed

            # Zliczanie do historii aktualnej sesji
            self.session_reps += 1
            if is_perfect:
                self.session_perfect += 1

            self.profile_mgr.update_user(self.username, 1, 1 if is_perfect else 0)
            self.current_rep_flawed = False
            self.audio.play_notification("rep_done")

            # Głosowe odliczanie po każdym powtórzeniu
            rep_number = int(self.count)
            spoken = self.NUMBERS_PL.get(rep_number, str(rep_number))
            self.audio.say(spoken)

    def draw_ui(self, img_front):
        """Generowanie interfejsu wizualnego na obrazie."""
        # Pasek postępu
        cv2.rectangle(img_front, (1100, 100), (1175, 600), self.color_front, 3)
        cv2.rectangle(img_front, (1100, int(self.bar)), (1175, 600), self.color_front, cv2.FILLED)
        cv2.putText(img_front, f'{int(self.per)} %', (1100, 75), cv2.FONT_HERSHEY_PLAIN, 4, self.color_front, 4)

        # Panel informacyjny
        cv2.rectangle(img_front, (0, 0), (900, 200), (255, 255, 255), cv2.FILLED)
        cv2.putText(img_front, f'Powt(sesja): {int(self.count)}', (20, 45), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

        user_data = self.profile_mgr.get_user(self.username)
        total = user_data['total_reps']
        perf = user_data['perfect_reps']
        acc = (perf / total * 100) if total > 0 else 0
        cv2.putText(img_front, f'Suma OHP: {total} | Dokladnosc: {int(acc)}%', (20, 85), cv2.FONT_HERSHEY_PLAIN, 2,
                    (0, 100, 0), 2)

        if self.state == "WARMUP":
            # Podczas rozgrzewki jeden komunikat
            cv2.putText(img_front, self.feedback_warmup, (20, 130), cv2.FONT_HERSHEY_PLAIN, 2, self.color_warmup, 3)
        else:
            # Podczas ćwiczenia dwa osobne komunikaty
            cv2.putText(img_front, f'Przod: {self.feedback_front}', (20, 130), cv2.FONT_HERSHEY_PLAIN, 2,
                        self.color_front, 2)
            if self.has_side_cam and self.feedback_side:
                cv2.putText(img_front, f'Bok:   {self.feedback_side}', (20, 170), cv2.FONT_HERSHEY_PLAIN, 2,
                            self.color_side, 2)

    def cleanup(self):
        """Sprzątanie na koniec działania programu i zapis logów sesji."""
        self.profile_mgr.save_session(self.username, self.session_reps, self.session_perfect)
        self.audio.stop()
        self.cap_front.release()
        if self.has_side_cam:
            self.cap_side.release()
        cv2.destroyAllWindows()


def main():
    print("--- System Cyber Trener ---")
    username = input("Podaj nazwe uzytkownika: ").strip() or "Gosc"
    ip = input("Podaj IP kamery bocznej np. 192.168.1.100:8080 (Enter = pomiń): ").strip()

    # Import i uruchomienie serwera web w osobnym wątku
    import threading
    from web.app import app as flask_app
    flask_thread = threading.Thread(
        target=lambda: flask_app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False), 
        daemon=True
    )
    flask_thread.start()
    print("Serwer web (Flask) został uruchomiony na http://127.0.0.1:5000 w tle.")

    app = CyberTrainerApp(username, ip_webcam=ip)
    print(f"Zalogowano jako: {username}. Suma powtorzen: {app.user_data['total_reps']}")
    print("System uruchomiony. Naciśnij 'q', aby wyjść.")
    app.run()


if __name__ == "__main__":
    main()
