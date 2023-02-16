from tkinter import messagebox, Frame, Button, END

from database import (
    read_voice_gender,
)

class InputTextButtons(Frame):
    def __init__(
            self, master, 
            txt_edit, 
            q
        ):
        super().__init__(master)

        self.window = self.winfo_toplevel()

        self.txt_edit = txt_edit
        self.q = q

        self.grid(row=1, column=1, sticky="ew")

        btn_clear_txt_edit = Button(self, text="Clear", command=self.clear_input_text)
        btn_copy_to_clipboard_txt_edit = Button(
            self, text="To Clipboard", command=self.save_input_text_to_clipboard
        )
        btn_from_clipboard_to_txt_edit = Button(
            self, text="From Clipboard", command=self.use_input_text_from_clipboard
        )
        btn_clear_txt_edit.grid(row=0, column=0, sticky="ew", padx=(5, 0), pady=(0, 10))
        btn_copy_to_clipboard_txt_edit.grid(
            row=0, column=1, sticky="ew", padx=(0, 0), pady=(0, 10)
        )
        btn_from_clipboard_to_txt_edit.grid(
            row=0, column=2, sticky="ew", padx=(0, 0), pady=(0, 10)
        )
        btn_speak_txt_edit = Button(self, text="Speak", command=self.speak_input_text)
        btn_speak_txt_edit.grid(row=0, column=3, sticky="ew", padx=(0, 0), pady=(0, 10))

    def clear_input_text(self):
        self.txt_edit.delete("1.0", END)

    def save_input_text_to_clipboard(self):
        input = self.txt_edit.get("1.0", END)
        self.window.clipboard_append(input)
        # self.winfo_toplevel().clipboard_append(input)

    def use_input_text_from_clipboard(self):
        # input_text = self.winfo_toplevel().clipboard_get()
        input_text = self.window.clipboard_get()

        if len(self.txt_edit.get("1.0", END)) > 0:
            self.txt_edit.insert(END, f" {input_text}")
        else:
            self.txt_edit.insert(END, f"{input_text}")

    def speak_input_text(self):
        if read_voice_gender() != "None":
            input_txt = self.txt_edit.get("1.0", END)
            if len(input_txt) > 0:
                self.q.put(input_txt)
        else:
            messagebox.showinfo(
                message="Update Voice Gender Option other than 'None' to use this"
            )
