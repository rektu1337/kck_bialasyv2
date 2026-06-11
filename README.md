# 🏋️‍♂️ System Cyber Trener (v0.1)

Inteligentny asystent treningowy wykorzystujący wizję komputerową do monitorowania i korygowania techniki ćwiczeń w czasie rzeczywistym. Obecnie zoptymalizowany pod kątem ćwiczenia **Overhead Press (Wyciskanie Żołnierskie)**.

## ✨ Główne funkcje

System wykorzystuje biblioteki takie jak OpenCV oraz MediaPipe do precyzyjnego śledzenia punktów kluczowych ciała (landmarks) na obrazie z kamery. Program został ostatnio mocno rozbudowany o nowe mechanizmy:

* **👀 Detekcja z Dwóch Kamer:** Równoczesna analiza postawy z przodu i z boku (przy użyciu drugiej kamery). System weryfikuje m.in. czy wyciskanie w płaszczyźnie bocznej przebiega w linii pionowej.
* **👤 Profile Użytkownika:** Zapisywanie postępów dla różnych użytkowników. Aplikacja przechowuje sumę powtórzeń i analizuje historyczną **dokładność (accuracy)** Twoich ćwiczeń w oparciu o poprawność każdego powtórzenia.
* **🌐 Web Dashboard (Nowość!):** Zintegrowana lokalna strona internetowa pozwalająca na przeglądanie wyników i interaktywnych wykresów pokazujących Twoje postępy na osi czasu.
* **🔥 Rozgrzewka:** Zanim zaczniesz ćwiczenie właściwe, system wymusza fazę 5-sekundowego rozciągania i wstępnego pobudzenia mięśni w pozycji wyprostowanych ramion.
* **📐 Zaawansowana Analiza Biomechaniki (Overhead Press):**
  * **Asymetria rąk:** Ostrzega, gdy ramiona nie są wyciskane równomiernie (`Wyrównaj ramiona!`).
  * **Pionowanie przedramion:** Monitoruje odchylenie przedramion od pionu, chroniąc stawy barkowe (`Pionuj przedramiona!`).
  * **Pozycja łokci:** Zapobiega zbyt niskiemu opuszczaniu łokci względem barków w dolnej fazie ruchu (`Łokcie za nisko!`).
  * **Linia wyciskania (Bok):** Weryfikuje tor prowadzenia ciężaru od strony profilu ciała.
* **💯 Automatyczne Liczenie Powtórzeń:** Zlicza poprawnie wykonane powtórzenia na podstawie fazy ugięcia i wyprostu ramion, chroniąc przed tzw. "oszukanymi powtórzeniami".
* **🔊 Powiadomienia Dźwiękowe:** Sygnalizacja dźwiękowa przy pełnym i poprawnie zakończonym powtórzeniu oraz zakończeniu rozgrzewki.
* **📊 Interfejs Wizualny (HUD):** Dynamiczny pasek postępu (0-100%), wizualne wskaźniki błędów technicznych oraz stały podgląd na statystyki profilu i powtórzenia podczas sesji.

## 🛠️ Wymagania

Do uruchomienia projektu wymagany jest Python w wersji 3.8 lub nowszej, a także jedna lub dwie kamery internetowe. 

Zależności:
* `opencv-python`
* `mediapipe`
* `numpy`
* `flask`
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

### 1. Moduł Treningowy (Cyber Trener)

Aby rozpocząć korzystanie z systemu kamer, uruchom plik główny:

```bash
python src/main.py
```

* Na wstępie zostaniesz zapytany w terminalu o **Nazwę użytkownika**, aby załadować Twój profil z poprzednich sesji.
* System automatycznie spróbuje uzyskać dostęp do Twojej domyślnej kamery (przód) oraz kamery o indeksie 1 (bok). 
* Zostaniesz poprowadzony przez fazę rozgrzewki. Zastosuj się do instrukcji na ekranie.
* Aby zamknąć program i zapisać dane treningowe, naciśnij klawisz `q` podczas aktywnego okna podglądu.

### 2. Panel Przeglądarkowy (Web Dashboard)

Aby podejrzeć swoje statystyki na czytelnych wykresach, uruchom serwer lokalny:

```bash
python src/web/app.py
```

* Po uruchomieniu komendy otwórz w przeglądarce adres: `http://127.0.0.1:5000/`.
* Na stronie możesz przełączać się między zapisanymi użytkownikami i weryfikować dokładność z poszczególnych dni.

## 📂 Struktura projektu

```text
kck_bialasyv2/
├── src/
│   ├── main.py            # Główna pętla i interfejs wideo
│   ├── pose_module.py     # Klasa PoseDetector (wykrywanie sylwetki)
│   ├── user_profile.py    # Moduł obsługujący bazę JSON profili
│   ├── audio_module.py    # Obsługa powiadomień dźwiękowych
│   ├── voice.py           # Moduł analizy głosu
│   └── web/               # Moduł strony internetowej
│       ├── app.py             # Aplikacja i API we Flasku
│       ├── templates/         # Pliki HTML (index.html)
│       └── static/            # Zasoby CSS oraz skrypty JS
├── profiles.json          # Baza danych statystyk treningowych
├── requirements.txt       # Lista zależności projektu (w tym Flask)
└── README.md              # Dokumentacja projektu
```

---
*Projekt stworzony w celach edukacyjnych, jako wsparcie przy treningu oporowym. Przed rozpoczęciem nowej aktywności fizycznej skonsultuj się z trenerem lub lekarzem.*