import cv2
import mediapipe as mp

# Inicjalizacja narzędzi MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Inicjalizacja detektora póz
# min_detection_confidence i min_tracking_confidence pomagają w stabilności
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Otwarcie pliku wideo lub kamerki (zmień "film.mp4" na 0, aby użyć kamery na żywo)
video_source = "film.mp4" # do testów na żywo wpisz: 0
cap = cv2.VideoCapture(video_source)

def check_letter(landmarks):
    """
    Funkcja sprawdza wzajemne położenie stawów i zwraca rozpoznaną literę.
    Współrzędne (x, y) w MediaPipe są znormalizowane i przyjmują wartości od 0.0 do 1.0.
    """
    # Pobranie interesujących nas punktów
    ls = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    rs = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    lw = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    rw = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
    
    # Tolerancja błędu (zależy od odległości osoby od kamery)
    tol = 0.15 
    
    # 1. Warunek dla litery T
    # Obie ręce w poziomie, szeroko rozstawione
    if abs(lw.y - ls.y) < tol and abs(rw.y - rs.y) < tol and abs(lw.x - rw.x) > 0.5:
        return "T"
        
    # 2. Warunek dla litery I
    # Obie ręce w górze (y nadgarstka < y barku), nadgarstki blisko siebie w poziomie
    elif lw.y < (ls.y - tol) and rw.y < (rs.y - tol) and abs(lw.x - rw.x) < 0.25:
        return "I"
        
    # 3. Warunek dla litery Y
    # Obie ręce w górze, ale nadgarstki daleko od siebie
    elif lw.y < (ls.y - tol) and rw.y < (rs.y - tol) and abs(lw.x - rw.x) > 0.35:
        return "Y"
        
    # 4. Warunek dla litery L (Opcja A: Lewa w bok, Prawa w górę)
    elif abs(lw.y - ls.y) < tol and rw.y < (rs.y - tol) and abs(rw.x - rs.x) < tol:
        return "L"
        
    # 4. Warunek dla litery L (Opcja B: Prawa w bok, Lewa w górę - lustrzane odbicie)
    elif abs(rw.y - rs.y) < tol and lw.y < (ls.y - tol) and abs(lw.x - ls.x) < tol:
        return "L"
        
    # Zwraca znak zapytania, jeśli układ ciała nie pasuje do żadnej z liter
    return "?"

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Koniec filmu lub błąd kamery.")
        break
        
    # Konwersja kolorów BGR (OpenCV) na RGB (wymagane przez MediaPipe)
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Przetwarzanie klatki obrazu w poszukiwaniu szkieletu
    results = pose.process(image_rgb)
    
    letter = "?"
    
    # Jeśli znaleziono sylwetkę człowieka
    if results.pose_landmarks:
        # Narysowanie szkieletu na oryginalnym obrazie (frame)
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        # Analiza ułożenia ciała (wywołanie naszej funkcji)
        landmarks = results.pose_landmarks.landmark
        letter = check_letter(landmarks)
        
    # Nałożenie tekstu z rozpoznaną literą na obraz
    cv2.putText(frame, f"Litera: {letter}", (50, 80), 
                cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 255, 0), 4)
    
    # Wyświetlenie okna z filmem
    cv2.imshow('Rozpoznawanie Liter - Projekt PSIO', frame)
    
    # Przerwanie pętli po naciśnięciu klawisza 'q'
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# Sprzątanie po zakończeniu
cap.release()
cv2.destroyAllWindows()