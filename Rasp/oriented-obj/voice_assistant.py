import speech_recognition as sr
import pyttsx3
import openai
import threading
import subprocess
import time
import os
import pyaudio
from sound_effects import Sound_FX

play = Sound_FX()
flag_init_sys = 0
#Initializing pyttsx3
engine = pyttsx3.init()

#Set your openai api key and customizing the chatgpt role
openai.api_key = "xyz"
messages = [{"role": "system", "content": "Your name is Jarvis and give answers in 2 lines"}]

#Customizing The output voice
voices = engine.getProperty('voices')
rate = engine.getProperty('rate')
volume = engine.getProperty('volume')

engine.setProperty('rate', 120)
engine.setProperty('volume', volume)
engine.setProperty('voice', 'brazil')


class Voice_Assistant():
    def __init__(self):
        """Class Builder"""
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.run()

    def start_jack_server(self):
        subprocess.run(['jackd', '-d', 'alsa'])

    def get_response(self, user_input):
        messages.append({"role": "user", "content": user_input})
        query = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages = messages
            )
        ChatGPT_reply = query["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": ChatGPT_reply})
        print(f"Robô: \"{ChatGPT_reply}\"") 
        return ChatGPT_reply


    def waiting_hotword(self):
        #global flag_init_sys
        #if flag_init_sys == 0:
        #print('entrou no if') 
        #with sr.Microphone() as source:
        #   recognizer = sr.Recognizer()
        #   recognizer.adjust_for_ambient_noise(source)
        #   recognizer.dynamic_energy_threshold = 3000
            #flag_init_sys = 1
        with self.microphone as source:  
            self.recognizer.adjust_for_ambient_noise(source)
            self.recognizer.dynamic_energy_threshold = 3000
            print('Waiting for wakeword \"robô\"')
           
            while True:
                audio = self.recognizer.listen(source)
        
                try: 
                    text = self.recognizer.recognize_google(audio, language='pt-BR')
                    print(text)
                    if 'robô' in text.lower():
                        print('Wake word detected')
                        play.wake()
                        engine.runAndWait()
                        self.provide_info(source)
                        break

                except sr.UnknownValueError:
                    print('Diga \"Robô\" para me chamar')
                    pass
        #else:
         #   print('Waiting for wakeword again')
          #  while True:
           #     audio = recognizer.liste(source)

            #    try:
             #       text = recognizer.recognize_google(audio, language='pt-BR')
              #      print(text)
               #     if 'robô' in text.lower():
                #        print('Wake word detected')
                 #       play.wake()
                  #      self.provide_info(source, recognizer)
                   #     break
                #except sr.UnknownValueError:
                 #   print('Diga \"Robô\" para me chamar')
                  #  pass


    def provide_info(self,source):
        #while True:
        #audio = recognizer.listen(source)
        #with sr.Microphone() as source:
           # recognizer = sr.Recognizer()
           # recognizer.adjust_for_ambient_noise(source)
           # recognizer.dynamic_energy_threshold = 3000
        while True:
            try:
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=5.0)
                print("Recognizing...")
                query = self.recognizer.recognize_google(audio,language='pt-BR')
                print(query)

                if 'me trazer' in query:
                #engine.setProperty('rate', 120)
                #engine.setProperty('volume', volume)
                #engine.setProperty('voice', 'brazil')
                    print("Robô: \"Ok, irei levar à você\"")
                    engine.say('Ok, irei levar à voce')
                    engine.runAndWait()

                elif 'siga-me' in query:
                    print("Robô: \"Ok, irei te seguir\"")
                    engine.say("Ok, irei te seguir")
                    engine.runAndWait()

                elif 'obrigado' in query:
                    print("Robô: Sem problemas")
                        #play.end()
                    engine.say("Sem problemas")
                    engine.runAndWait()
                    exit()
                
                elif 'parar' in query:
                    play.end()

                    self.waiting_hotword()

                else:
                    response_from_openai = self.get_response(query)
                        #engine.setProperty('rate', 120)
                        #engine.setProperty('volume', volume)
                        #engine.setProperty('voice', 'brazil')
                    engine.say(response_from_openai)
                    engine.runAndWait()
                        #play.end()

            except sr.UnknownValueError:
                print("Mensagem desconhecida")
                engine.say("Não entendi, poderia repetir por favor?")

    def kill_jackd_server(self):
        pid_jackd = subprocess.run(['pidof', 'jackd'], capture_output=True)
        pid = pid_jackd.stdout.decode()
        kill_cmd = "kill -9 " + pid
        os.system(kill_cmd)
        time.sleep(2)
        print("Program closed")

    def run(self):
        #Starts jack server in a thread:
        jackd_thread = threading.Thread(target=self.start_jack_server, daemon=True)
        jackd_thread.start()

        #Wait 4 seconds to jack server intialize:
        time.sleep(3)

        #Starts provide-information loop:
        info_thread = threading.Thread(target=self.waiting_hotword, daemon=True)
        info_thread.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Closing Program...")
            self.kill_jackd_server()

