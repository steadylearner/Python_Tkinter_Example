# $brew install python-tk
# https://realpython.com/python-gui-tkinter/#building-a-text-editor-example-app
# https://tkdocs.com/tutorial/index.html

from time import sleep
import pyttsx3
import threading
import queue

import tkinter as tk
from tkinter import messagebox

from tkinter.filedialog import askopenfilename, asksaveasfilename
from deep_translator import GoogleTranslator
import gtts

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


def use_file_for_input_text():
    """Open a file for editing."""

    filepath = askopenfilename(
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if not filepath:
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


def use_mic_for_input_text():
    """Record a voice with mic and use it for input text"""

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


def save_translated_text_to_file():
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

    window.title(f"{APP_TITLE} - {filepath}")


def save_translated_text_to_audio_file():
    """Save the translated_text as a new file."""

    filepath = asksaveasfilename(
        defaultextension=".mp3",
        filetypes=[("Audio Files", "*.mp3"), ("All Files", "*.*")],
    )
    if not filepath:
        return

    with open(filepath, mode="w", encoding="utf-8") as output_file:
        translated = txt_translated.get("1.0", tk.END)

        tts = gtts.gTTS(text=translated, lang=TARGET_LANG, slow=False)
        tts.save(filepath)

    window.title(f"{APP_TITLE} - {filepath}")


window = tk.Tk()
window.title(APP_TITLE)

window.rowconfigure(0, weight=1)
window.columnconfigure(1, weight=1)

frm_buttons = tk.Frame(window, relief=tk.RAISED, bd=2)
frm_buttons.grid(row=0, column=0, sticky="ns")
btn_open_txt = tk.Button(
    frm_buttons, text="Use a file for text input", command=use_file_for_input_text
)
btn_record_audio = tk.Button(
    frm_buttons, text="Use the mic for text input", command=use_mic_for_input_text
)
btn_save_txt = tk.Button(
    frm_buttons, text="Save a text file", command=save_translated_text_to_file
)
btn_save_audio = tk.Button(
    frm_buttons, text="Save an audio file", command=save_translated_text_to_audio_file
)

btn_open_txt.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
# btn_open_audio.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
btn_record_audio.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
btn_save_txt.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
btn_save_audio.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

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
