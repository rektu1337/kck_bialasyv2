import cv2
import numpy as np
import time
from pose_module import PoseDetector
from voice import VoiceController
from audio_module import AudioFeedback
from user_profile import UserProfileManager

class CyberTrainerApp:
    def __init__(self, username):
        self.username = username
        self.profile_mgr = UserProfileManager()
        self.user_data = self.profile_mgr.load_user(username)
        
        # Moduły Audio & Voice
        self.audio = AudioFeedback()
        self.voice = VoiceController()
        
        # Zmienne stanu aplikacji
        self.state = "WARMUP"
        self.warmup_start = None
        
        self.count = 0
        self.dir = 0
        self.feedback_msg = "Rozgrzewka: Unies rece by zaczac!"
        self.color = (0, 255, 255)
        self.current_rep_flawed = False
        self.per = 0
        self.bar = 600
        
        # Zmienne sesji do historii treningowej
        self.session_reps = 0
        self.session_perfect = 0
        
        self.init_cameras()
        
    def init_cameras(self):
        """Inicjalizacja kamery głównej oraz bocznej, jeśli dostępna."""
        self.cap_front = cv2.VideoCapture(0)
        self.cap_front.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap_front.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.detector_front = PoseDetector()
        
        self.cap_side = cv2.VideoCapture(1)
        self.has_side_cam = self.cap_side.isOpened()
        if self.has_side_cam:
            success, _ = self.cap_side.read()
            if not success:
                self.has_side_cam = False
            else:
                self.cap_side.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap_side.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                print("Wykryto i podlaczono kamere boczna.")
        
        if not self.has_side_cam:
            print("Nie wykryto kamery bocznej. Analiza boczna wylaczona.")
            
        self.detector_side = PoseDetector() if self.has_side_cam else None
        
    def run(self):
        """Główna pętla programu."""
        while self.cap_front.isOpened():
            success, img_front = self.cap_front.read()
            if not success:
                break
                
            img_side = None
            if self.has_side_cam:
                s_side, img_side = self.cap_side.read()
                if not s_side:
                    self.has_side_cam = False
            
            # Przetwarzanie obrazu
            img_front, lm_list_front = self.process_frame(img_front, self.detector_front)
            lm_list_side = []
            if self.has_side_cam and img_side is not None:
                img_side, lm_list_side = self.process_frame(img_side, self.detector_side)
                
            # Logika analizy, jeśli wykryto postać
            if len(lm_list_front) != 0:
                self.analyze_pose(img_front, lm_list_front, lm_list_side)
                self.draw_ui(img_front)
                
            # Wyświetlanie okien
            cv2.imshow("Cyber Trener - Podglad OHP (v0.1)", img_front)
            if self.has_side_cam and img_side is not None:
                cv2.imshow("Cyber Trener - Profil Boczny", img_side)
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        self.cleanup()
        
    def process_frame(self, img, detector):
        """Wykrywanie punktów kluczowych sylwetki na pojedynczej klatce."""
        img = detector.find_pose(img)
        lm_list = detector.find_position(img, draw=False)
        return img, lm_list

    def analyze_pose(self, img_front, lm_list_front, lm_list_side):
        """Obliczanie kątów i delegowanie do odpowiedniego stanu (rozgrzewka / ćwiczenie)."""
        angle_left = self.detector_front.find_angle(img_front, 11, 13, 15, draw=True)
        angle_right = self.detector_front.find_angle(img_front, 12, 14, 16, draw=True)
        avg_angle = (angle_left + angle_right) / 2
        
        self.per = np.interp(avg_angle, (70, 160), (0, 100))
        self.bar = np.interp(avg_angle, (70, 160), (600, 100))
        
        if self.state == "WARMUP":
            self.handle_warmup()
        elif self.state == "EXERCISE":
            self.handle_exercise(angle_left, angle_right, lm_list_front, lm_list_side)

    def handle_warmup(self):
        """Mechanika 5-sekundowej rozgrzewki."""
        if self.per > 90:
            if self.warmup_start is None:
                self.warmup_start = time.time()
            elapsed = time.time() - self.warmup_start
            remaining = 5 - int(elapsed)
            self.feedback_msg = f"Rozciaganie: Trzymaj! ({remaining}s)"
            self.color = (0, 255, 255)
            
            if elapsed >= 5:
                self.state = "EXERCISE"
                self.audio.play_notification("rep_done")
                self.feedback_msg = "Rozgrzewka OK! Zaczynamy OHP"
                self.color = (0, 255, 0)
        else:
            self.warmup_start = None
            self.feedback_msg = "Rozgrzewka: Unies rece by zaczac!"
            self.color = (0, 165, 255)

    def handle_exercise(self, angle_left, angle_right, lm_front, lm_side):
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
            self.feedback_msg = "Wyrownaj ramiona!"
            self.color = (0, 0, 255)
        elif forearm_tilt_l > tilt_threshold or forearm_tilt_r > tilt_threshold:
            self.feedback_msg = "Pionuj przedramiona!"
            self.color = (0, 165, 255)
        elif (y_el_l > y_sh_l + 70) or (y_el_r > y_sh_r + 70):
            self.feedback_msg = "Lokcie za nisko!"
            self.color = (0, 165, 255)
        else:
            front_error = False

        # Weryfikacja boku
        side_error = False
        if self.has_side_cam and len(lm_side) != 0:
            try:
                x_sh_side = lm_side[12][1]
                x_wr_side = lm_side[16][1]
                if self.per > 50 and abs(x_wr_side - x_sh_side) > 70:
                    side_error = True
                    self.feedback_msg = "Wyciskaj w pionie (bok)!"
                    self.color = (0, 0, 255)
            except IndexError:
                pass

        if front_error or side_error:
            self.current_rep_flawed = True
        elif not front_error and not side_error:
            self.feedback_msg = "Dobra forma"
            self.color = (0, 255, 0)
            
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

    def draw_ui(self, img_front):
        """Generowanie interfejsu wizualnego na obrazie."""
        cv2.rectangle(img_front, (1100, 100), (1175, 600), self.color, 3)
        cv2.rectangle(img_front, (1100, int(self.bar)), (1175, 600), self.color, cv2.FILLED)
        cv2.putText(img_front, f'{int(self.per)} %', (1100, 75), cv2.FONT_HERSHEY_PLAIN, 4, self.color, 4)

        cv2.rectangle(img_front, (0, 0), (700, 150), (255, 255, 255), cv2.FILLED)
        cv2.putText(img_front, f'Powt(sesja): {int(self.count)}', (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
        
        user_data = self.profile_mgr.get_user(self.username)
        total = user_data['total_reps']
        perf = user_data['perfect_reps']
        acc = (perf / total * 100) if total > 0 else 0
        cv2.putText(img_front, f'Suma OHP: {total} | Dokladnosc: {int(acc)}%', (20, 90), cv2.FONT_HERSHEY_PLAIN, 2, (0, 100, 0), 2)
        cv2.putText(img_front, self.feedback_msg, (20, 135), cv2.FONT_HERSHEY_PLAIN, 2, self.color, 3)

    def cleanup(self):
        """Sprzątanie na koniec działania programu i zapis logów sesji."""
        self.profile_mgr.save_session(self.username, self.session_reps, self.session_perfect)
        self.cap_front.release()
        if self.has_side_cam:
            self.cap_side.release()
        cv2.destroyAllWindows()


def main():
    print("--- System Cyber Trener ---")
    username = input("Podaj nazwe uzytkownika: ").strip() or "Gosc"
    app = CyberTrainerApp(username)
    print(f"Zalogowano jako: {username}. Suma powtorzen: {app.user_data['total_reps']}")
    print("System uruchomiony. Naciśnij 'q', aby wyjść.")
    app.run()

if __name__ == "__main__":
    main()