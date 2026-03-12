import speech_recognition as sr
from translate import Translator
import pyttsx3

engine = pyttsx3.init()
recognizer = sr.Recognizer()

translator_pl_en = Translator(from_lang="pl", to_lang="en")
translator_en_pl = Translator(from_lang="en", to_lang="pl")

def speak(text):
    print(f"Tłumacz: {text}")
    engine.say(text)
    engine.runAndWait()


def listen(language="pl-PL"):

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print(f"[Nasłuchuję w języku: {language}] ...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            text = recognizer.recognize_google(audio, language=language)
            print(f"Ty: {text}")
            return text.lower()
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            print("⚠Błąd połączenia.")
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
            if current_lang == "en":
                speak("I don't understand. Say again please.")
            else:
                speak("Nie rozumiem. Proszę powtórz.")
            continue


        if "bywaj" in text:
            speak("Do widzenia. Zamykam program.")
            break

        if "goodbye" in text or "good bye" in text or "bye" in text:
            speak("Good bye, closing the program.")


        if "angielski" in text or "english" in text:
            current_lang = "en"
            speak("Zmieniono język na angielski.")
            continue

        if "polski" in text or "polish" in text:
            current_lang = "pl"
            speak("Changed language to Polish.")
            continue


        if current_lang == "pl":
            translated_text = translator_pl_en.translate(text)
            speak(translated_text)
        elif current_lang == "en":
            translated_text = translator_en_pl.translate(text)
            speak(translated_text)
        else:

            speak("Proszę, najpierw wybierz język mówiąc 'polski' lub 'angielski'.")


if __name__ == "__main__":
    main()