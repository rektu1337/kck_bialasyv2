import pygame
import pyttsx3
import threading
import queue


class AudioFeedback:
    def __init__(self):
        pygame.mixer.init()

        self._queue = queue.Queue()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

        print("Moduł powiadomień dźwiękowych Pygame gotowy.")
        print("Moduł TTS gotowy.")

    def _worker(self):
        """Jeden wątek obsługuje TTS kolejno — bez kolizji."""
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        while True:
            text = self._queue.get()
            if text is None:
                break
            engine.say(text)
            engine.runAndWait()
            self._queue.task_done()

    def play_notification(self, sound_type="beep"):
        print(f"Odtwarzanie dźwięku: {sound_type}")

    def say(self, text):
        """Wrzuca tekst do kolejki — nigdy nie gubi powtórzeń."""
        self._queue.put(text)

    def stop(self):
        """Zatrzymuje wątek TTS przy zamknięciu aplikacji."""
        self._queue.put(None)
