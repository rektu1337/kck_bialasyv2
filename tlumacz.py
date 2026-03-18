import speech_recognition as sr
from translate import Translator
import pyttsx3
import time

recognizer = sr.Recognizer()

translator_pl_en = Translator(from_lang="pl", to_lang="en")
translator_en_pl = Translator(from_lang="en", to_lang="pl")


def speak(text):
    print(f"Tłumacz: {text}")
    engine = pyttsx3.init()   # <-- świeża instancja za każdym razem
    engine.say(text)
    engine.runAndWait()
    del engine                 # <-- zwolnij zasoby


def listen(language="pl-PL"):
    with sr.Microphone() as source:
        time.sleep(0.2)
        print(f"[Nasłuchuję w języku: {language}] ... (MÓW TERAZ)")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            text = recognizer.recognize_google(audio, language=language)
            print(f"Ty: {text}")
            return text.lower()
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            print("Błąd połączenia z Google.")
            return None
        except sr.WaitTimeoutError:
            return None


def main():
    current_lang = None
    speak("Witaj. Powiedz 'polski' lub 'angielski', aby wybrać język.")

    while True:
        listen_lang = "en-US" if current_lang == "en" else "pl-PL"

        if current_lang == "pl":
            speak("Powiedz coś po polsku.")
        elif current_lang == "en":
            speak("Say something in English.")

        text = listen(listen_lang)

        if not text:
            speak("I don't understand. Say again." if current_lang == "en" else "Nie rozumiem. Proszę powtórz.")
            continue

        if "bywaj" in text:
            speak("Do widzenia. Zamykam program.")
            break

        if any(w in text for w in ["goodbye", "good bye", "bye"]):
            speak("Good bye, closing the program.")
            break

        if "angielski" in text or "english" in text:
            current_lang = "en"
            speak("Zmieniono język na angielski.")
            continue

        if "polski" in text or "polish" in text:
            current_lang = "pl"
            speak("Changed language to Polish.")
            continue

        if current_lang == "pl":
            speak(translator_pl_en.translate(text))
        elif current_lang == "en":
            speak(translator_en_pl.translate(text))
        else:
            speak("Proszę, najpierw wybierz język mówiąc 'polski' lub 'angielski'.")


if __name__ == "__main__":
    main()