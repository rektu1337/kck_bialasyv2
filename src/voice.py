import speech_recognition as sr

class VoiceController:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        print("Moduł mowy zainicjalizowany (Szkielet)")

    def listen_command(self):
        with self.microphone as source:
            print("Słucham...")
            audio = self.recognizer.listen(source)
        try:
            command = self.recognizer.recognize_google(audio, language='pl-PL')
            return command.lower()
        except:
            return ""