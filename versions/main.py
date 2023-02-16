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

from tinydb import TinyDB, Query

TRANSLATED_TEXT_OPTIONS = [
    "en",
    "pt",
    "es",
]

VOICE_LANGUAGE_OPTIONS = [
    "en_US",
    "pt_BR",
    "es_ES",
]

VOICE_GENDER_OPTIONS = [
    "VoiceGenderMale",
    "VoiceGenderFemale",
    "None",  # When it is set to none, it shouldn't speak or show the button for it
]


class LanguagesSettingsDialog(tk.simpledialog.Dialog):
    def __init__(self, parent, title):
        languages_settings = read_settings("languages")[0]["details"]
        # print("languages_settings")
        # print(languages_settings)

        self.input_text = languages_settings["input_text"]
        self.translated_text = languages_settings["translated_text"]
        self.voice_language = languages_settings["voice_language"]
        self.voice_gender = languages_settings["voice_gender"]

        super().__init__(parent, title)

    def body(self, frame):
        self.input_text_label = tk.Label(frame, width=25, text="Input Text")
        self.input_text_label.pack()
        self.input_text_box = tk.Entry(frame, width=25)
        self.input_text_box.pack()
        self.input_text_box.insert(0, self.input_text)

        translated_text = tk.StringVar(frame)
        translated_text.set(self.translated_text)

        def translated_text_option_selected(selection):
            self.translated_text = selection

        self.translated_text_label = tk.Label(frame, width=21, text="Translated Text")
        self.translated_text_label.pack()
        self.translated_text_otpion_menu = tk.OptionMenu(
            frame,
            translated_text,
            *TRANSLATED_TEXT_OPTIONS,
            command=translated_text_option_selected,
        )
        self.translated_text_otpion_menu.config(width=21)
        self.translated_text_otpion_menu.pack()

        voice_language = tk.StringVar(frame)
        voice_language.set(self.voice_language)

        def voice_language_option_selected(selection):
            self.voice_language = selection

        self.voice_language_label = tk.Label(frame, width=21, text="Voice Language")
        self.voice_language_label.pack()
        self.voice_language_otpion_menu = tk.OptionMenu(
            frame,
            voice_language,
            *VOICE_LANGUAGE_OPTIONS,
            command=voice_language_option_selected,
        )
        self.voice_language_otpion_menu.config(width=21)
        self.voice_language_otpion_menu.pack()

        voice_gender = tk.StringVar(frame)
        voice_gender.set(self.voice_gender)

        def voice_gender_option_selected(selection):
            self.voice_gender = selection

        self.voice_gender_label = tk.Label(frame, width=21, text="Voice Gender")
        self.voice_gender_label.pack()
        self.voice_gender_otpion_menu = tk.OptionMenu(
            frame,
            voice_gender,
            *VOICE_GENDER_OPTIONS,
            command=voice_gender_option_selected,
        )
        self.voice_gender_otpion_menu.config(width=21)
        self.voice_gender_otpion_menu.pack()

        return frame

    def ok_pressed(self):
        upsert_settings(
            "languages",
            {
                "input_text": self.input_text_box.get(),
                "translated_text": self.translated_text,
                "voice_language": self.voice_language,
                "voice_gender": self.voice_gender,
            },
        )

        self.destroy()

    def cancel_pressed(self):
        self.destroy()

    def buttonbox(self):
        cancel_button = tk.Button(
            self, text="Cancel", width=5, command=self.cancel_pressed
        )
        cancel_button.pack(side="right", padx=(0, 5), pady=(0, 10))
        self.ok_button = tk.Button(self, text="OK", width=5, command=self.ok_pressed)
        self.ok_button.pack(side="right", pady=(0, 10))

        self.bind("<Return>", lambda event: self.ok_pressed())
        self.bind("<Escape>", lambda event: self.cancel_pressed())


def show_languages_settings_dialog():
    LanguagesSettingsDialog(title="Languages", parent=window)


# def languages_settings_dialog(parent):
#     dialog = LanguagesSettingsDialog(title="Languages", parent=parent)
#     return dialog.input_text, dialog.translated_text, dialog.translated_voice


# def show_languages_settings_dialog():
#     answer = languages_settings_dialog(window)
#     # print(type(answer)) # tuple
#     # Save it to the database?
#     print(answer)


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
                # print("data")
                # print(data)

                if data == "exit":
                    t_running = False
                else:
                    if self.change_voice(read_translated_voice_language()) == True:
                        # self.engine.setProperty('rate', 10)
                        self.engine.say(data)

        self.engine.endLoop()

    def change_voice(self, language):
        gender = read_translated_voice_gender()
        # print("gender")
        # print(gender)
        lang_correct = False
        gender_correct = False

        for voice in self.engine.getProperty("voices"):
            if language in voice.languages:
                lang_correct = True

                # print("voice")
                # print(voice)
                # print("language")
                # print(language)

                # print("gender")
                # print(gender)
                # print("voice.gender")
                # print(voice.gender)
                # print("gender == voice.gender")
                # print(gender == voice.gender)

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

        return lang_correct and gender_correct  # Both should be True to speak
        # for voice in self.engine.getProperty('voices'):
        #     if language in voice.languages and gender == voice.gender:
        #         print("gender")
        #         print(gender)
        #         print("voice")
        #         print(voice)

        #         self.engine.setProperty('voice', voice.id)
        #         return True

        # messagebox.showerror(message="Language '{}' for gender '{}' not found, update gender at languages settings if you don't want to see this error".format(language, gender))

        # raise RuntimeError(
        #     "Language '{}' for gender '{}' not found".format(language, gender))


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

        translated = GoogleTranslator(
            source=read_input_text_language(), target=read_translated_text_language()
        ).translate(text)

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

        translated = GoogleTranslator(
            source=read_input_text_language(), target=read_translated_text_language()
        ).translate(text)
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
            # TODO
            # Show an error at the desktop app with messagebox if it fails to read the audio file
            transcription = str(recognizer.recognize_google(audio, show_all=False))
            # transcription = str(recognizer.recognize_google(audio, language = "en-US", show_all = False)

            # print("transcription")
            # print(transcription)

            txt_edit.delete("1.0", tk.END)
            txt_translated.delete("1.0", tk.END)

            txt_edit.insert(tk.END, transcription)

            translated = GoogleTranslator(
                source=read_input_text_language(),
                target=read_translated_text_language(),
            ).translate(transcription)
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

        tts = gtts.gTTS(
            text=translated, lang=read_translated_text_language()
        )  # Include it for settings or input bar for text input or dropdown
        tts.save(filepath)  # mp3
        messagebox.showinfo(message=f"The file was saved")

        window.title(f"{APP_TITLE} - {filepath}")


def clear_input_text():
    txt_edit.delete("1.0", tk.END)


def save_input_text_to_clipboard():
    input = txt_edit.get("1.0", tk.END)
    window.clipboard_append(input)


def use_input_text_from_clipboard():
    input_text = window.clipboard_get()

    if len(txt_edit.get("1.0", tk.END)) > 0:
        txt_edit.insert(tk.END, f" {input_text}")
    else:
        txt_edit.insert(tk.END, f"{input_text}")


def speak_input_text():
    if read_translated_voice_gender() != "None":
        input_txt = txt_edit.get("1.0", tk.END)
        if len(input_txt) > 0:
            q.put(input_txt)
    else:
        messagebox.showinfo(
            message="Update Translated Voice Gender Option other than 'None' to use this"
        )


def clear_translated_text():
    txt_translated.config(state="normal")
    txt_translated.delete("1.0", tk.END)
    txt_translated.config(state="disabled")


def save_translated_text_to_clipboard():
    translated = txt_translated.get("1.0", tk.END)
    window.clipboard_append(translated)


def use_translated_text_from_clipboard():
    translated_text = window.clipboard_get()

    if len(txt_translated.get("1.0", tk.END)) > 0:
        txt_translated.insert(tk.END, f" {translated_text}")
    else:
        txt_translated.insert(tk.END, f"{translated_text}")


def speak_translated_text():
    if read_translated_voice_gender() != "None":
        translated = txt_translated.get("1.0", tk.END)
        if len(translated) > 0:
            q.put(translated)
    else:
        messagebox.showinfo(
            message="Update Translated Voice Gender Option other than 'None' to use this"
        )


window = tk.Tk()
window.title(APP_TITLE)

window.rowconfigure(0, weight=1)
window.columnconfigure(1, weight=1)

menubar = Menu(window)
window.config(menu=menubar)

file = Menu(menubar, tearoff=0)

# add menu items to the File menu
use_sub_menu = Menu(file, tearoff=0)
use_sub_menu.add_command(label="Mic for Input Text", command=use_mic_for_input_text)
use_sub_menu.add_command(
    label="Text File for Input Text", command=use_text_file_for_input_text
)
use_sub_menu.add_command(
    label="Audio File for Input Text", command=use_audio_file_for_input_text
)
file.add_cascade(label="Use", menu=use_sub_menu)

save_sub_menu = Menu(file, tearoff=0)
save_sub_menu.add_command(
    label="Translated Text to a text file", command=save_translated_text_to_text_file
)
save_sub_menu.add_command(
    label="Translated Text to an audio file", command=save_translated_text_to_audio_file
)
file.add_cascade(label="Save", menu=save_sub_menu)

file.add_separator()
file.add_command(label="Close", command=window.destroy)

menubar.add_cascade(label="File", menu=file, underline=0)

settings = Menu(menubar, tearoff=0)

settings.add_command(label="Languages", command=show_languages_settings_dialog)

# add the Help menu to the menubar
menubar.add_cascade(label="Settings", menu=settings)

# frm_buttons = tk.Frame(window, relief=tk.RAISED, bd=2)
# frm_buttons.grid(row=0, column=0, sticky="ns")
# btn_open_txt = tk.Button(frm_buttons, text="Settings")

# btn_open_txt.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

# frm_buttons = tk.Frame(window, relief=tk.RAISED, bd=2)
# frm_buttons.grid(row=0, column=0, sticky="ns")
# btn_open_txt = tk.Button(frm_buttons, text="Use a file for text input", command=use_file_for_input_text)
# btn_record_audio = tk.Button(frm_buttons, text="Use the mic for text input", command=use_mic_for_input_text)
# btn_save_txt = tk.Button(frm_buttons, text="Save a text file", command=save_translated_text_to_file)
# btn_save_audio = tk.Button(frm_buttons, text="Save an audio file", command=save_translated_text_to_audio_file)

# btn_open_txt.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
# # btn_open_audio.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
# btn_record_audio.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
# btn_save_txt.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
# btn_save_audio.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

frm_form = tk.Frame(window)
frm_form.grid(row=0, column=1, sticky="nsew")

txt_edit_label = tk.Label(
    frm_form, text="Input Text", anchor="w", font=LABEL_FONT, padx=10, pady=10
)
txt_edit_label.grid(row=0, column=1, sticky="ew")

txt_edit_buttons = tk.Frame(frm_form)
txt_edit_buttons.grid(row=1, column=1, sticky="ew")
btn_clear_txt_edit = tk.Button(txt_edit_buttons, text="Clear", command=clear_input_text)
btn_copy_to_clipboard_txt_edit = tk.Button(
    txt_edit_buttons, text="To Clipboard", command=save_input_text_to_clipboard
)
btn_from_clipboard_to_txt_edit = tk.Button(
    txt_edit_buttons, text="From Clipboard", command=use_input_text_from_clipboard
)
btn_speak_txt_edit = tk.Button(txt_edit_buttons, text="Speak", command=speak_input_text)
btn_clear_txt_edit.grid(row=0, column=0, sticky="ew", padx=(5, 0), pady=(0, 10))
btn_copy_to_clipboard_txt_edit.grid(
    row=0, column=1, sticky="ew", padx=(0, 0), pady=(0, 10)
)
btn_from_clipboard_to_txt_edit.grid(
    row=0, column=2, sticky="ew", padx=(0, 0), pady=(0, 10)
)
btn_speak_txt_edit.grid(row=0, column=3, sticky="ew", padx=(0, 0), pady=(0, 10))

txt_edit = tk.Text(frm_form, font=TEXT_FONT, height=15)
txt_edit.grid(row=2, column=1, sticky="ew")
txt_edit_value = tk.StringVar()

txt_translated_label = tk.Label(
    frm_form, text=f"Translated Text", anchor="w", font=LABEL_FONT, padx=10, pady=10
)
txt_translated_label.grid(row=3, column=1, sticky="ew")

txt_translated_buttons = tk.Frame(frm_form)
txt_translated_buttons.grid(row=4, column=1, sticky="ew")
btn_clear_txt_translated = tk.Button(
    txt_translated_buttons, text="Clear", command=clear_translated_text
)
btn_copy_to_clipboard_txt_translated = tk.Button(
    txt_translated_buttons,
    text="To Clipboard",
    command=save_translated_text_to_clipboard,
)
btn_from_clipboard_to_txt_translated = tk.Button(
    txt_translated_buttons,
    text="From Clipboard",
    command=use_translated_text_from_clipboard,
)
btn_clear_txt_translated.grid(row=0, column=0, sticky="ew", padx=(5, 0), pady=(0, 10))
btn_copy_to_clipboard_txt_translated.grid(
    row=0, column=1, sticky="ew", padx=(0, 0), pady=(0, 10)
)
btn_from_clipboard_to_txt_translated.grid(
    row=0, column=2, sticky="ew", padx=(0, 0), pady=(0, 10)
)

btn_speak_txt_translated = tk.Button(
    txt_translated_buttons, text="Speak", command=speak_translated_text
)
btn_speak_txt_translated.grid(row=0, column=3, sticky="ew", padx=(0, 0), pady=(0, 10))

txt_translated = tk.Text(frm_form, font=TEXT_FONT, height=15)
txt_translated.grid(row=5, column=1, sticky="ew")


@debounce(1)
def on_txt_edit_value_update(event):
    txt_edit_value.set(txt_edit.get("1.0", tk.END))
    # print(txt_edit_value.get())

    translated = GoogleTranslator(
        source=read_input_text_language(), target=read_translated_text_language()
    ).translate(txt_edit_value.get())

    # print("translated")
    # print(translated)

    if read_translated_voice_gender() != "None" and len(translated) != 0:
        q.put(translated)

    txt_translated.config(state="normal")
    txt_translated.replace("1.0", tk.END, translated)
    txt_translated.config(state="disabled")


txt_edit.bind("<KeyRelease>", on_txt_edit_value_update)

db = TinyDB("db.json")
query = Query()
settings = db.table("settings")


def read_settings(name):
    return settings.search(query.name == name)


def upsert_settings(name, details):
    settings.upsert({"name": name, "details": details}, query.name == name)


def read_input_text_language():
    return read_settings("languages")[0]["details"]["input_text"]


def read_translated_text_language():
    return read_settings("languages")[0]["details"]["translated_text"]


def read_translated_voice_language():
    return read_settings("languages")[0]["details"]["voice_language"]


def read_translated_voice_gender():
    return read_settings("languages")[0]["details"]["voice_gender"]


if __name__ == "__main__":
    if len(read_settings("languages")) == 0:
        # Separate it to form and voice or speaker?
        upsert_settings(
            "languages",
            {
                "input_text": "auto",
                "translated_text": "pt",  # en
                "voice_language": "pt_BR",  # en_US
                "voice_gender": "VoiceGenderFemale",  # "VoiceGenderMale"
            },
        )

    window.mainloop()
