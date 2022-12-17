import customtkinter
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os
import time


class MainUi(customtkinter.CTk):
    def __init__(self, background_job, title_name):
        super().__init__()
        self.geometry("450x400")
        self.title(title_name)
        self.background_job = background_job
        self.peer_list = ["No online user"]
        self.resizable(0, 0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.bind('<Return>', self.send_handler)
        self.bind('<Control-l>', self.clear_screen)
        self.current_peer_name = customtkinter.StringVar()

        self.income_message = customtkinter.CTkTextbox(
            master=self, state="disabled", height=280, width=110, font=customtkinter.CTkFont(size=16))

        self.income_message.grid(
            row=1, column=0, columnspan=3, padx=20, pady=(0, 0), sticky="nsew")

        self.peer_chooser = customtkinter.CTkOptionMenu(
            master=self, corner_radius=0, values=self.peer_list, font=customtkinter.CTkFont(size=14))

        self.peer_chooser.grid(
            row=0, column=0, columnspan=2, padx=(20, 5), pady=(20, 10), sticky="ew")

        self.reload_button = customtkinter.CTkButton(
            master=self, command=self.reload_handler, text="Reload", corner_radius=0, font=customtkinter.CTkFont(size=14))

        self.reload_button.grid(
            row=0, column=2, padx=(5, 20), pady=(20, 10), sticky="e")

        self.input_message = customtkinter.CTkEntry(
            master=self, placeholder_text="Input message", width=400, corner_radius=0, font=customtkinter.CTkFont(size=16))

        self.input_message.grid(
            row=2, column=0, columnspan=2, padx=(20, 5), pady=(15, 20), sticky="ew")

        self.send_file_button = customtkinter.CTkButton(
            master=self, command=self.send_file_handler, text="File", corner_radius=0, font=customtkinter.CTkFont(size=16))

        self.send_file_button.grid(
            row=2, column=2, padx=(5, 20), pady=(15, 20), sticky="e")

    def show_mesage(self):
        self.income_message.configure(state="normal")
        self.income_message.delete("0.0", "end")
        for message in self.background_job.message_history:
            self.income_message.insert("end", message)
        self.income_message.configure(state="disabled")
        self.after(500, self.show_mesage)

    def clear_screen(self, event):
        self.background_job.message_history = []

    def reload_handler(self):
        self.background_job.server_interact("online?")
        self.peer_list = []
        for item in self.background_job.online_user:
            self.peer_list.append(item[0])
        if self.peer_list == []:
            self.peer_list = ["No online user"]
        self.peer_chooser.configure(values=self.peer_list)
        return

    def send_handler(self, event):
        name_to_sent = self.peer_chooser.get()
        content = self.input_message.get()
        connected = self.background_job.connect_if_not(name_to_sent)
        if connected:
            self.background_job.send_to_peer(
                name_to_sent, content, type="text")
            self.input_message.delete("0", "end")
            sent_report = "[ -> " + name_to_sent + " ]    " + content + "\n\n"
            self.background_job.message_history.append(sent_report)
        return

    
    def get_file_name(self, str):
        for i in range(-1, 0 - len(str) - 1, -1):
            if (str[i] == "/"):
                return str[i + 1:]

    def send_file_handler(self):
        name_to_sent = self.peer_chooser.get()
        connected = self.background_job.connect_if_not(name_to_sent)
        file_path = askopenfilename()
        print(self.get_file_name(file_path))
        if file_path:
            if connected:
                self.background_job.send_to_peer(
                    name_to_sent, "<START>", type="text")
                if file_path:
                    self.background_job.send_to_peer(
                        name_to_sent, bytes(self.get_file_name(file_path), 'utf-8'), type="file")
                    time.sleep(1)
                    file = open(file_path, "rb")
                    data = file.read()
                    self.background_job.send_to_peer(
                        name_to_sent, data, type="file")

                self.background_job.send_to_peer(
                    name_to_sent, "<END>", type="text")
            else:
                return
            # self.background_job.send_to_peer(name_to_sent, "FILE", type="text")
            # self.background_job.send_to_peer(name_to_sent, "FILE", type="text")
            self.input_message.delete("0", "end")
            sent_report = "[ -> " + name_to_sent + " ]    " + "FILE" + "\n\n"
            self.background_job.message_history.append(sent_report)
        return
