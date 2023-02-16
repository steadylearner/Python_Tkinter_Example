from tkinter import messagebox, Frame, Button, END

from database import (
    read_voice_gender,
)


class TranslatedTextButtons(Frame):
    def __init__(self, master, translated_text, q):
        super().__init__(master)

        self.window = self.winfo_toplevel()
        self.translated_text = translated_text
        self.q = q

        self.grid(row=4, column=1, sticky="ew")

        btn_clear_translated_text = Button(
            self, text="Clear", command=self.clear_translated_text
        )
        btn_copy_to_clipboard_translated_text = Button(
            self, text="To Clipboard", command=self.save_translated_text_to_clipboard
        )
        btn_from_clipboard_to_translated_text = Button(
            self, text="From Clipboard", command=self.use_translated_text_from_clipboard
        )
        btn_clear_translated_text.grid(
            row=0, column=0, sticky="ew", padx=(5, 0), pady=(0, 10)
        )
        btn_copy_to_clipboard_translated_text.grid(
            row=0, column=1, sticky="ew", padx=(0, 0), pady=(0, 10)
        )
        btn_from_clipboard_to_translated_text.grid(
            row=0, column=2, sticky="ew", padx=(0, 0), pady=(0, 10)
        )
        btn_speak_translated_text = Button(
            self, text="Speak", command=self.speak_translated_text
        )
        btn_speak_translated_text.grid(
            row=0, column=3, sticky="ew", padx=(0, 0), pady=(0, 10)
        )

    def clear_translated_text(self):
        self.translated_text.config(state="normal")
        self.translated_text.delete("1.0", END)
        self.translated_text.config(state="disabled")

    def save_translated_text_to_clipboard(self):
        translated = self.translated_text.get("1.0", END)

        # Use winfo_toplevel instead
        self.window.clipboard_append(translated)

    def use_translated_text_from_clipboard(self):
        translated_text = self.window.clipboard_get()

        self.translated_text.config(state="normal")

        if len(self.translated_text.get("1.0", END)) > 0:
            self.translated_text.insert(END, f" {translated_text}")
        else:
            self.translated_text.insert(END, f"{translated_text}")

        self.translated_text.config(state="disabled")

    def speak_translated_text(self):
        if read_voice_gender() != "None":
            translated = self.translated_text.get("1.0", END)
            if len(translated) > 0:
                self.q.put(translated)
        else:
            messagebox.showinfo(
                message="Update Voice Gender Option other than 'None' to use this"
            )
