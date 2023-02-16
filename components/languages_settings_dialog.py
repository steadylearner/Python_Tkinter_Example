import tkinter as tk

from settings import (
    TRANSLATED_TEXT_OPTIONS,
    VOICE_LANGUAGE_OPTIONS,
    VOICE_GENDER_OPTIONS,
)

from database import (
    upsert_settings,
    read_input_text_language,
    read_translated_text_language,
    read_voice_language,
    read_voice_gender,
)

class FormSettingsDialog(tk.simpledialog.Dialog):
    def __init__(self, parent, title):
        self.input_text = read_input_text_language()
        self.translated_text = read_translated_text_language()
        self.voice_language = read_voice_language()
        self.voice_gender = read_voice_gender()

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
            command=translated_text_option_selected
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
            command=voice_language_option_selected
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
            command=voice_gender_option_selected
        )
        self.voice_gender_otpion_menu.config(width=21)
        self.voice_gender_otpion_menu.pack()

        return frame

    def ok_pressed(self):
        upsert_settings(
            "form",
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


def show_form_settings_dialog(parent):
    FormSettingsDialog(title="Form", parent=parent)
