# $brew install python-tk
# https://realpython.com/python-gui-tkinter/#building-a-text-editor-example-app
# https://tkdocs.com/tutorial/index.html
# https://www.pythontutorial.net/tkinter/tkinter-menu/

from time import sleep
import pyttsx3
import threading
import queue
import os

import tkinter as tk
from tkinter import messagebox, Menu

from tkinter.filedialog import askopenfilename, asksaveasfilename
from deep_translator import GoogleTranslator
import gtts
import numpy as np
from playsound import playsound

# You need to include ffmpeg
# $brew install ffmpeg --force
# $brew link ffmpeg
# from pydub import AudioSegment
import subprocess

import speech_recognition as sr
from speech_recognition import Recognizer, Microphone


def recognize_speech_from_mic(recognizer: Recognizer, microphone: Microphone):
    """Transcribe speech recorded from `microphone`.

    Returns a dictionary with three keys:
    "success": a boolean indicating whether or not the API request was
               successful
    "error":   `None` if no error occured, otherwise a string containing
               an error message if the API could not be reached or
               speech was unrecognizable
    "transcription": `None` if speech could not be transcribed,
               otherwise a string containing the transcribed text
    """

    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # set up the response object
    response = {"success": True, "error": None, "transcription": None}

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #     update the response object accordingly
    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response


recognizer = sr.Recognizer()
microphone = sr.Microphone()

APP_TITLE = "Tkinter Translator"
LABEL_FONT = ("Helvetica", 20, "bold")
TEXT_FONT = (None, 16)
TARGET_LANG = "pt"


# Thread for Text to Speech Engine


# https://stackoverflow.com/questions/63892455/running-pyttsx3-inside-a-game-loop
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
                if data == "exit":
                    t_running = False
                else:
                    self.change_voice("pt_BR")
                    self.engine.setProperty("rate", 10)

                    self.engine.say(data)

        self.engine.endLoop()

    def change_voice(self, language, gender="VoiceGenderFemale"):
        for voice in self.engine.getProperty("voices"):
            if language in voice.languages and gender == voice.gender:
                self.engine.setProperty("voice", voice.id)
                return True

        raise RuntimeError(
            "Language '{}' for gender '{}' not found".format(language, gender)
        )


# create a queue to send commands from the main thread
q = queue.Queue()
tts_thread = TTSThread(q)  # note: thread is auto-starting

# engine = pyttsx3.init()
# change_voice(engine, "en_US")
# rate = engine.getProperty('rate')
# engine.setProperty('rate', 10)

# https://github.com/salesforce/decorator-operations/tree/master/decoratorOperations


def debounce(interval: float):
    """
    Decorator that will debounce a function so that it is called after wait_time seconds
    If it is called multiple times, will wait for the last call to be debounced and run only this one.
    See the test_debounce.py file for examples
    """

    def debounce_decorator(function):
        def debounced_function(*args, **kwargs):
            def call_decorated_function():
                debounced_function._timer = None
                return function(*args, **kwargs)

            if debounced_function._timer is not None:
                debounced_function._timer.cancel()

            debounced_function._timer = threading.Timer(
                interval, call_decorated_function
            )
            debounced_function._timer.start()

        debounced_function._timer = None
        return debounced_function

    return debounce_decorator


def use_mic_for_input_text():
    """Use a mic for input text"""

    # print("use_mic_for_input_text")
    what_you_said = recognize_speech_from_mic(recognizer, microphone)
    # print("what_you_said")
    # print(what_you_said)

    if what_you_said["error"]:
        # print("ERROR: {}".format(what_you_said["error"]))
        messagebox.showerror(title="Error", message=what_you_said["error"])
        return

    if not what_you_said["success"]:
        # print("I couldn't read that. What did you say?\n")
        messagebox.showerror(
            title="Error", message="I couldn't read that. What did you say?"
        )
        return

    if what_you_said["transcription"] == None:
        # print("Please, say something next time.")
        messagebox.showerror(title="Error", message="Please, say something next time.")
    else:
        text = what_you_said["transcription"]

        translated = GoogleTranslator(source="auto", target="pt").translate(text)

        q.put(translated)

        if len(txt_edit.get("1.0", tk.END)) > 0:
            txt_edit.insert(tk.END, f" {text}")
            txt_translated.insert(tk.END, f" {translated}")
        else:
            txt_edit.insert(tk.END, f"{text}")
            txt_translated.insert(tk.END, f"{translated}")


def use_text_file_for_input_text():
    """Use a text file for input text."""

    filepath = askopenfilename(
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if not filepath:
        # messagebox.showerror(title="Error", message="Use the correct filepath for the text file")
        return

    txt_edit.delete("1.0", tk.END)
    txt_translated.delete("1.0", tk.END)
    with open(filepath, mode="r", encoding="utf-8") as input_file:
        text = input_file.read()
        txt_edit.insert(tk.END, text)

        translated = GoogleTranslator(source="auto", target="pt").translate(text)
        q.put(translated)

        txt_translated.config(state="normal")
        txt_translated.replace("1.0", tk.END, translated)
        txt_translated.config(state="disabled")

        window.title(f"{APP_TITLE} - {filepath}")


def use_audio_file_for_input_text():
    """Use an audio file for input text."""

    filepath = askopenfilename(
        filetypes=[("Audio Files", "*.mp3"), ("Audio Files", "*.wav")],
        # filetypes=[("Audio Files", "*.mp3"), ("All Files", "*.*")],
    )
    if not filepath:
        # messagebox.showerror(
        #     title="Error", message="Use the correct filepath for the audio file")
        return

    # mp3
    # print("filepath")
    # print(filepath)
    # to wav file to use sr.AudioFile

    if filepath.endswith("mp3"):
        # sound = AudioSegment.from_mp3(filepath)
        # sound.export(filepath, format="wav")

        filepath_without_ext = filepath.split(".")[0]
        new_wav_filepath = f"{filepath_without_ext}.wav"

        subprocess.call(["ffmpeg", "-y", "-i", filepath, new_wav_filepath])

        # playsound(new_wav_filepath)
        audio = sr.AudioFile(new_wav_filepath)

        response = messagebox.askquestion(
            title=None,
            message="To use the mp3 file we for the app, we had to make the file with .wav extension, do you want to remove the original mp3 file?",
        )
        if response == "yes":
            os.remove(filepath)
            messagebox.showinfo(message=f"The mp3 file at {filepath} was removed")

    else:
        # playsound(filepath)
        audio = sr.AudioFile(filepath)

    with audio as source:
        # This doesn't work here.
        # recognizer.adjust_for_ambient_noise(source)

        audio = recognizer.record(source)
        # print(audio)

        try:
            transcription = str(recognizer.recognize_google(audio, show_all=False))
            # transcription = str(recognizer.recognize_google(audio, language = "en-US", show_all = False)

            # print("transcription")
            # print(transcription)

            txt_edit.delete("1.0", tk.END)
            txt_translated.delete("1.0", tk.END)

            txt_edit.insert(tk.END, transcription)

            translated = GoogleTranslator(source="auto", target="pt").translate(
                transcription
            )
            q.put(translated)

            txt_translated.config(state="normal")
            txt_translated.replace("1.0", tk.END, translated)
            txt_translated.config(state="disabled")

            window.title(f"{APP_TITLE} - {filepath}")
        except:
            messagebox.showinfo("Something went wrong while reading the audio file")


def save_translated_text_to_text_file():
    """Save the translated_text as a new file."""

    filepath = asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
    )
    if not filepath:
        return

    with open(filepath, mode="w", encoding="utf-8") as output_file:
        # text = txt_edit.get("1.0", tk.END)
        translated = txt_translated.get("1.0", tk.END)
        output_file.write(translated)
        messagebox.showinfo(message=f"The file was saved")

        window.title(f"{APP_TITLE} - {filepath}")


def save_translated_text_to_audio_file():
    """Save the translated_text as a new file."""

    # Should be wav instead of mp3
    filepath = asksaveasfilename(
        defaultextension=".mp3",
        filetypes=[("Audio Files", "*.mp3"), ("All Files", "*.*")],
    )
    if not filepath:
        return

    with open(filepath, mode="w", encoding="utf-8") as output_file:
        translated = txt_translated.get("1.0", tk.END)

        tts = gtts.gTTS(text=translated)
        tts.save(filepath)  # mp3
        messagebox.showinfo(message=f"The file was saved")

        window.title(f"{APP_TITLE} - {filepath}")


window = tk.Tk()
window.title(APP_TITLE)

window.rowconfigure(0, weight=1)
window.columnconfigure(1, weight=1)

menubar = Menu(window)
window.config(menu=menubar)

file_menu = Menu(menubar, tearoff=0)

# add menu items to the File menu
use_sub_menu = Menu(file_menu, tearoff=0)
use_sub_menu.add_command(label="Mic for Input Text", command=use_mic_for_input_text)
use_sub_menu.add_command(
    label="Text File for Input Text", command=use_text_file_for_input_text
)
use_sub_menu.add_command(
    label="Audio File for Input Text", command=use_audio_file_for_input_text
)
file_menu.add_cascade(label="Use", menu=use_sub_menu)

save_sub_menu = Menu(file_menu, tearoff=0)
save_sub_menu.add_command(
    label="Translated Text to a text file", command=save_translated_text_to_text_file
)
save_sub_menu.add_command(
    label="Translated Text to an audio file", command=save_translated_text_to_audio_file
)
file_menu.add_cascade(label="Save", menu=save_sub_menu)

file_menu.add_separator()
file_menu.add_command(label="Close", command=window.destroy)

menubar.add_cascade(label="File", menu=file_menu, underline=0)

frm_form = tk.Frame(window)
frm_form.grid(row=0, column=1, sticky="nsew")

txt_edit_label = tk.Label(
    frm_form, text="Input Text", anchor="w", font=LABEL_FONT, padx=5, pady=8
)
txt_edit_label.grid(row=0, column=1, sticky="ew")
txt_edit = tk.Text(frm_form, font=TEXT_FONT, height=15)
txt_edit.grid(row=1, column=1, sticky="ew")

txt_translated_label = tk.Label(
    frm_form, text=f"Translated Text", anchor="w", font=LABEL_FONT, padx=5, pady=8
)
txt_translated_label.grid(row=2, column=1, sticky="ew")
txt_translated = tk.Text(frm_form, font=TEXT_FONT, height=15)
txt_translated.grid(row=3, column=1, sticky="ew")

txt_edit_value = tk.StringVar()


@debounce(2)
def on_txt_edit_value_update(event):
    txt_edit_value.set(txt_edit.get("1.0", tk.END))
    # print(txt_edit_value.get())

    translated = GoogleTranslator(source="auto", target="pt").translate(
        txt_edit_value.get()
    )
    q.put(translated)

    txt_translated.config(state="normal")
    txt_translated.replace("1.0", tk.END, translated)
    txt_translated.config(state="disabled")


txt_edit.bind("<KeyRelease>", on_txt_edit_value_update)

window.mainloop()
