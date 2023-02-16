# $brew install python-tk
# https://realpython.com/python-gui-tkinter/#building-a-text-editor-example-app
# https://tkdocs.com/tutorial/index.html
# https://www.pythontutorial.net/tkinter/tkinter-menu/

# You need to include ffmpeg
# $brew install ffmpeg --force
# $brew link ffmpeg
# from pydub import AudioSegment

import tkinter as tk
from tkinter import Menu

from deep_translator import GoogleTranslator

import speech_recognition as sr
from components.filemenu import FileMenu
from components.input_text_buttons import InputTextButtons
from components.translated_text_buttons import TranslatedTextButtons

from thread import (
    q,
)

from database import (
    read_settings,
    upsert_settings,
    read_input_text_language,
    read_translated_text_language,
    read_voice_gender,
)

from functions import (
    debounce,
)

from settings import (
    APP_TITLE,
    LABEL_FONT,
    TEXT_FONT,
)

from components.languages_settings_dialog import show_form_settings_dialog

recognizer = sr.Recognizer()
microphone = sr.Microphone()

window = tk.Tk()
window.title(APP_TITLE)

window.rowconfigure(0, weight=1)
window.columnconfigure(1, weight=1)

menubar = Menu(window)
window.config(menu=menubar)

translation_form = tk.Frame(window)
translation_form.grid(row=0, column=1, sticky="nsew")

input_text_label = tk.Label(
    translation_form, text="Input Text", anchor="w", font=LABEL_FONT, padx=10, pady=10
)
input_text_label.grid(row=0, column=1, sticky="ew")

input_text = tk.Text(translation_form, font=TEXT_FONT, height=15)
input_text.grid(row=2, column=1, sticky="ew")

input_text_value = tk.StringVar()


@debounce(1)
def on_input_text_value_update(event):
    input_text_value.set(input_text.get("1.0", tk.END))

    translated = GoogleTranslator(
        source=read_input_text_language(), target=read_translated_text_language()
    ).translate(input_text_value.get())

    if read_voice_gender() != "None" and len(translated) != 0:
        q.put(translated)

    translated_text.config(state="normal")
    translated_text.replace("1.0", tk.END, translated)
    translated_text.config(state="disabled")


input_text.bind("<KeyRelease>", on_input_text_value_update)

input_text_buttons = InputTextButtons(translation_form, input_text, q)

translated_text_label = tk.Label(
    translation_form,
    text=f"Translated Text",
    anchor="w",
    font=LABEL_FONT,
    padx=10,
    pady=10,
)
translated_text_label.grid(row=3, column=1, sticky="ew")

translated_text = tk.Text(translation_form, font=TEXT_FONT, height=15)
translated_text.grid(row=5, column=1, sticky="ew")
translated_text_buttons = TranslatedTextButtons(
    translation_form, translated_text, q
)

menubar.add_cascade(
    label="File",
    menu=FileMenu(window, q, input_text, translated_text, recognizer, microphone),
    underline=0,
)

settings = Menu(menubar, tearoff=0)
settings.add_command(label="Form", command=lambda: show_form_settings_dialog(window))

menubar.add_cascade(label="Settings", menu=settings)

if __name__ == "__main__":
    if len(read_settings("form")) == 0:
        upsert_settings(
            "form",
            {
                "input_text": "auto",
                "translated_text": "pt",  # en
                "voice_language": "pt_BR",  # en_US
                "voice_gender": "VoiceGenderFemale",  # "VoiceGenderMale"
            },
        )

    window.mainloop()
