import pyttsx3
import threading
import queue

from tkinter import messagebox

from database import (
    read_voice_language,
    read_voice_gender,
)


class TTSThread(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.daemon = True
        self.engine = pyttsx3.init()
        self.start()

    def run(self):
        self.engine.startLoop(False)
        t_running = True

        while t_running:
            if self.queue.empty():
                self.engine.iterate()
            else:
                data = self.queue.get()
                # print("data")
                # print(data)

                if data == "exit":
                    t_running = False
                else:
                    if self.change_voice(read_voice_language()) == True:
                        # self.engine.setProperty('rate', 10)
                        self.engine.say(data)

        self.engine.endLoop()

    def change_voice(self, language):
        gender = read_voice_gender()
        # print("gender")
        # print(gender)
        lang_correct = False
        gender_correct = False

        for voice in self.engine.getProperty("voices"):
            if language in voice.languages:
                lang_correct = True

                if gender == voice.gender:
                    gender_correct = True
                    self.engine.setProperty("voice", voice.id)
                    break
                else:
                    gender_correct = False
                    messagebox.showerror(
                        message="Gender '{}' not found for {}, update it at languages settings if you don't want to see this error".format(
                            gender, language
                        )
                    )
                    break
        # print("")
        if lang_correct == False and gender_correct == False:
            messagebox.showerror(
                message="Language '{}' not found, update Translated Voice if you don't want to see this error".format(
                    language, gender
                )
            )

        # Both should be True to speak
        return lang_correct and gender_correct


# create a queue to send commands from the main thread
q = queue.Queue()
tts_thread = TTSThread(q)  # note: thread is auto-starting
