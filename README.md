# 🏋️‍♂️ System Cyber Trener (v0.1)

Inteligentny asystent treningowy wykorzystujący wizję komputerową do monitorowania i korygowania techniki ćwiczeń w czasie rzeczywistym. Obecnie zoptymalizowany pod kątem ćwiczenia **Overhead Press (Wyciskanie Żołnierskie)**.

## ✨ Główne funkcje

System wykorzystuje biblioteki takie jak OpenCV oraz MediaPipe do precyzyjnego śledzenia punktów kluczowych ciała (landmarks) na obrazie z kamery.

* **👀 Detekcja Postawy w Czasie Rzeczywistym:** Błyskawiczna identyfikacja sylwetki przy pomocy MediaPipe Pose.
* **📐 Zaawansowana Analiza Biomechaniki (Overhead Press):**
  * **Asymetria rąk:** Ostrzega, gdy ramiona nie są wyciskane równomiernie (`Wyrównaj ramiona!`).
  * **Pionowanie przedramion:** Monitoruje odchylenie przedramion od pionu, chroniąc stawy barkowe (`Pionuj przedramiona!`).
  * **Pozycja łokci:** Zapobiega zbyt niskiemu opuszczaniu łokci względem barków w dolnej fazie ruchu (`Łokcie za nisko!`).
* **💯 Automatyczne Liczenie Powtórzeń:** Zlicza poprawnie wykonane powtórzenia na podstawie fazy ugięcia i wyprostu ramion, chroniąc przed tzw. "oszukanymi powtórzeniami".
* **🔊 Powiadomienia Dźwiękowe:** Sygnalizacja dźwiękowa przy pełnym i poprawnie zakończonym powtórzeniu.
* **📊 Interfejs Wizualny (HUD):** Dynamiczny pasek postępu (0-100%) oraz wizualne wskaźniki błędów technicznych (zmiana kolorów ostrzeżeń).

## 🛠️ Wymagania

Do uruchomienia projektu wymagany jest Python w wersji 3.8 lub nowszej, a także kamera internetowa. 

Zależności:
* `opencv-python`
* `mediapipe`
* `numpy`
* *(pozostałe biblioteki wymienione w `requirements.txt` dla modułów audio i głosowych)*

## 🚀 Instalacja

1. Sklonuj repozytorium:
   ```bash
   git clone <url_repozytorium>
   cd kck_bialasyv2
   ```

2. (Opcjonalnie, zalecane) Utwórz środowisko wirtualne:
   ```bash
   python -m venv venv
   # Aktywacja na Windows:
   venv\Scripts\activate
   # Aktywacja na Linux/Mac:
   source venv/bin/activate
   ```

3. Zainstaluj wymagane pakiety:
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Uruchamianie

Aby rozpocząć korzystanie z Cyber Trenera, uruchom plik główny:

```bash
python src/main.py
```

* System automatycznie spróbuje uzyskać dostęp do Twojej domyślnej kamery (indeks `0`). 
* Stanowisko powinno być dobrze oświetlone, a sylwetka od pasa w górę (w tym ramiona przy maksymalnym wyproście) w pełni widoczna w kadrze.
* Aby zamknąć program, naciśnij klawisz `q` podczas aktywnego okna podglądu.

## 📂 Struktura projektu

```text
kck_bialasyv2/
├── src/
│   ├── main.py            # Główna pętla programu i interfejs wizualny HUD
│   ├── pose_module.py     # Klasa PoseDetector (wykrywanie sylwetki i liczenie kątów)
│   ├── audio_module.py    # Obsługa efektów dźwiękowych (powiadomienia)
│   └── voice.py           # Obsługa komend głosowych / feedbacku audio
├── requirements.txt       # Lista zależności projektu
└── README.md              # Dokumentacja projektu
```

---
*Projekt stworzony w celach edukacyjnych, jako wsparcie przy treningu oporowym. Przed rozpoczęciem nowej aktywności fizycznej skonsultuj się z trenerem lub lekarzem.*