from tkinter import Menu, messagebox, END
from tkinter.filedialog import askopenfilename, asksaveasfilename

from deep_translator import GoogleTranslator
import gtts
import speech_recognition as sr

from database import (
    read_input_text_language,
    read_translated_text_language,
)

from functions import (
    recognize_speech_from_mic,
)

from settings import APP_TITLE

import os
import subprocess


class FileMenu(Menu):
    def __init__(self, master, q, input_text, translated_text, recognizer, microphone):
        super().__init__(master)

        self.q = q
        self.input_text = input_text
        self.translated_text = translated_text
        self.recognizer = recognizer
        self.microphone = microphone

        use_sub_menu = Menu(self, tearoff=0)
        use_sub_menu.add_command(
            label="Mic for Input Text", command=self.use_mic_for_input_text
        )
        use_sub_menu.add_command(
            label="Text File for Input Text", command=self.use_text_file_for_input_text
        )
        use_sub_menu.add_command(
            label="Audio File for Input Text",
            command=self.use_audio_file_for_input_text,
        )
        self.add_cascade(label="Use", menu=use_sub_menu)

        save_sub_menu = Menu(self, tearoff=0)
        save_sub_menu.add_command(
            label="Translated Text to a text file",
            command=self.save_translated_text_to_text_file,
        )
        save_sub_menu.add_command(
            label="Translated Text to an audio file",
            command=self.save_translated_text_to_audio_file,
        )
        self.add_cascade(label="Save", menu=save_sub_menu)

        self.add_separator()
        self.add_command(label="Close", command=self.master.destroy)

    def use_mic_for_input_text(self):
        """Use a mic for input text"""

        what_you_said = recognize_speech_from_mic(self.recognizer, self.microphone)

        if what_you_said["error"]:
            messagebox.showerror(title="Error", message=what_you_said["error"])
            return

        if not what_you_said["success"]:
            messagebox.showerror(
                title="Error", message="I couldn't read that. What did you say?"
            )
            return

        if what_you_said["transcription"] == None:
            messagebox.showerror(
                title="Error", message="Please, say something next time."
            )
        else:
            text = what_you_said["transcription"]

            translated = GoogleTranslator(
                source=read_input_text_language(),
                target=read_translated_text_language(),
            ).translate(text)

            self.q.put(translated)

            if len(self.input_text.get("1.0", END)) > 0:
                self.input_text.insert(END, f" {text}")
                self.translated_text.insert(END, f" {translated}")
            else:
                self.input_text.insert(END, f"{text}")
                self.translated_text.insert(END, f"{translated}")

    def use_text_file_for_input_text(self):
        """Use a text file for input text."""

        filepath = askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not filepath:
            # messagebox.showerror(title="Error", message="Use the correct filepath for the text file")
            return

        self.input_text.delete("1.0", END)
        self.translated_text.delete("1.0", END)
        with open(filepath, mode="r", encoding="utf-8") as input_file:
            text = input_file.read()
            self.input_text.insert(END, text)

            translated = GoogleTranslator(
                source=read_input_text_language(),
                target=read_translated_text_language(),
            ).translate(text)
            self.q.put(translated)

            self.translated_text.config(state="normal")
            self.translated_text.replace("1.0", END, translated)
            self.translated_text.config(state="disabled")

            self.master.title(f"{APP_TITLE} - {filepath}")

            # self.winfo_toplevel().title(f"{APP_TITLE} - {filepath}")

    def use_audio_file_for_input_text(self):
        """Use an audio file for input text."""

        filepath = askopenfilename(
            filetypes=[("Audio Files", "*.mp3"), ("Audio Files", "*.wav")],
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
            filepath_without_ext = filepath.split(".")[0]
            new_wav_filepath = f"{filepath_without_ext}.wav"

            subprocess.call(["ffmpeg", "-y", "-i", filepath, new_wav_filepath])

            audio = sr.AudioFile(new_wav_filepath)

            response = messagebox.askquestion(
                title=None,
                message="To use the mp3 file for the app, we had to make the file with .wav extension, do you want to remove the original mp3 file?",
            )
            if response == "yes":
                os.remove(filepath)
                messagebox.showinfo(message=f"The mp3 file at {filepath} was removed")

        else:
            audio = sr.AudioFile(filepath)

        with audio as source:
            # This doesn't work here.
            # recognizer.adjust_for_ambient_noise(source)

            audio = self.recognizer.record(source)

            try:
                transcription = str(
                    self.recognizer.recognize_google(audio, show_all=False)
                )

                self.input_text.delete("1.0", END)
                self.translated_text.delete("1.0", END)

                self.input_text.insert(END, transcription)

                translated = GoogleTranslator(
                    source=read_input_text_language(),
                    target=read_translated_text_language(),
                ).translate(transcription)
                self.q.put(translated)

                self.translated_text.config(state="normal")
                self.translated_text.replace("1.0", END, translated)
                self.translated_text.config(state="disabled")

                self.master.title(f"{APP_TITLE} - {filepath}")
                # self.winfo_toplevel().title(f"{APP_TITLE} - {filepath}")
            except:
                messagebox.showinfo("Something went wrong while reading the audio file")

    def save_translated_text_to_text_file(self):
        """Save the translated_text as a new file."""

        filepath = asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if not filepath:
            return

        with open(filepath, mode="w", encoding="utf-8") as output_file:
            translated = self.translated_text.get("1.0", END)
            output_file.write(translated)
            messagebox.showinfo(message=f"The file was saved")

            self.master.title(f"{APP_TITLE} - {filepath}")
            # self.winfo_toplevel().title(f"{APP_TITLE} - {filepath}")

    def save_translated_text_to_audio_file(self):
        """Save the translated_text as a new file."""

        # Should be wav instead of mp3
        filepath = asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("Audio Files", "*.mp3"), ("All Files", "*.*")],
        )
        if not filepath:
            return

        with open(filepath, mode="w", encoding="utf-8") as output_file:
            translated = self.translated_text.get("1.0", END)

            tts = gtts.gTTS(
                text=translated, lang=read_translated_text_language()
            )  # Include it for settings or input bar for text input or dropdown
            tts.save(filepath)  # mp3
            messagebox.showinfo(message=f"The file was saved")

            self.master.title(f"{APP_TITLE} - {filepath}")
            # self.winfo_toplevel().title(f"{APP_TITLE} - {filepath}")
