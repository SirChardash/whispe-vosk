from threading import Thread
from time import sleep
from tkinter import filedialog, messagebox, StringVar

import customtkinter
from pvrecorder import PvRecorder

import config
import recognizer


class SettingsDialog(customtkinter.CTkInputDialog):

    def _create_widgets(self):
        # paddings between components, from edge of screen x, between x and y
        edge = 25
        mid = 10
        pad_y = (0, 20)

        # instantiate all ui components
        self._dummy_label = customtkinter.CTkLabel(self, text='', width=600)
        self._audio_input_label = customtkinter.CTkLabel(self, text='Mikrofon')
        self._audio_input_combobox = customtkinter.CTkComboBox(self, values=PvRecorder.get_audio_devices())
        self._model_dir_label = customtkinter.CTkLabel(self, text='Model')
        self._model_dir = StringVar(value=config.get(config.MODEL_PATH))
        self._model_dir_value = customtkinter.CTkEntry(self, textvariable=self._model_dir)
        self._model_dir_browse = customtkinter.CTkButton(self, width=28, text='📂', command=self._set_model_dir)
        self._dark_theme_checkbox = customtkinter.CTkCheckBox(self, text="Koristi tamnu temu")
        self._shuffle_words_checkbox = customtkinter.CTkCheckBox(self, text="Izmjesaj rijeci prije testa")
        self._save_recording_checkbox = customtkinter.CTkCheckBox(self, text="Sacuvaj audio snimak testa")

        if config.get(config.THEME) == 'Dark':
            self._dark_theme_checkbox.select()
        if config.get(config.SHUFFLE_WORDS):
            self._shuffle_words_checkbox.select()
        if config.get(config.SAVE_RECORDING):
            self._save_recording_checkbox.select()

        # configure arrangement
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=10)
        self.columnconfigure(2, weight=1)

        self._ok_button = customtkinter.CTkButton(self, width=100, text='U redu', command=self._ok_event)
        self._cancel_button = customtkinter.CTkButton(self, width=100, text='Otkazi', command=self._cancel_event)

        self.rowconfigure(0, weight=1)
        self._dummy_label.grid(row=0, column=0, columnspan=3)  # just to define full window width

        self.rowconfigure(1, weight=1)
        self._audio_input_label.grid(row=1, column=0, columnspan=1, padx=(edge, mid), pady=pad_y, sticky='w')
        self._audio_input_combobox.grid(row=1, column=1, columnspan=2, padx=(mid, edge), pady=pad_y, sticky='ew')

        self.rowconfigure(2, weight=1)
        self._model_dir_label.grid(row=2, column=0, columnspan=1, padx=(edge, mid), pady=pad_y, sticky='w')
        self._model_dir_value.grid(row=2, column=1, columnspan=1, padx=(mid, 0), pady=pad_y, sticky='ew')
        self._model_dir_browse.grid(row=2, column=2, columnspan=1, padx=(0, edge), pady=pad_y, sticky='e')

        self.rowconfigure(3, weight=1)
        self._dark_theme_checkbox.grid(row=3, column=1, columnspan=1, padx=(mid, mid), pady=pad_y, sticky='w')

        self.rowconfigure(4, weight=1)
        self._shuffle_words_checkbox.grid(row=4, column=1, columnspan=1, padx=(mid, mid), pady=pad_y, sticky='w')

        self.rowconfigure(5, weight=1)
        self._save_recording_checkbox.grid(row=5, column=1, columnspan=1, padx=(mid, mid), pady=pad_y, sticky='w')

        self.rowconfigure(6, weight=1)
        self._ok_button.grid(row=6, column=1, columnspan=3, padx=(mid, 2 * edge + 100), pady=(30, 20), sticky='e')
        self._cancel_button.grid(row=6, column=1, columnspan=3, padx=(mid, edge), pady=(30, 20), sticky='e')

        self._listen_to_device_change = True
        Thread(daemon=True, target=self._refresh_audio_input_devices).start()

    def _ok_event(self, event=None):
        try:
            recognizer.get_recognizer(self._model_dir.get())
        except:
            messagebox.showerror('Greska', 'Odabrani direktorij ne sadrzi model!')
            return
        config.put(config.AUDIO_INPUT, self._audio_input_combobox.get())
        config.put(config.MODEL_PATH, self._model_dir.get())
        config.put(config.THEME, 'Dark' if self._dark_theme_checkbox.get() else 'Light')
        config.put(config.SHUFFLE_WORDS, self._shuffle_words_checkbox.get())
        config.put(config.SAVE_RECORDING, self._save_recording_checkbox.get())
        customtkinter.set_appearance_mode(config.get(config.THEME))

        self._listen_to_device_change = False
        self.grab_release()
        self.destroy()

    def _cancel_event(self):
        self._listen_to_device_change = False
        self.grab_release()
        self.destroy()

    def _on_closing(self):
        self._listen_to_device_change = False
        self.grab_release()
        self.destroy()

    def _refresh_audio_input_devices(self):
        while self._listen_to_device_change:
            devices = PvRecorder.get_audio_devices()
            if self._audio_input_combobox.cget('values') != devices:
                self._audio_input_combobox.configure(values=devices)
            sleep(3)

    def _set_model_dir(self):
        model_dir = filedialog.askdirectory(parent=self)
        if model_dir:
            self._model_dir.set(model_dir)
