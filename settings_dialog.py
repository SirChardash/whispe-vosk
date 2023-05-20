from threading import Thread
from time import sleep
from tkinter import filedialog, messagebox, StringVar, DoubleVar

import customtkinter
from pvrecorder import PvRecorder

import config
import recognizer


def is_zero_one_decimal(data):
    if data == '':
        return True
    try:
        rv = float(data)
        if rv < 0 or rv > 1:
            return False
    except ValueError:
        return False
    return True


class SettingsDialog(customtkinter.CTkInputDialog):

    def _create_widgets(self):
        # paddings between components, from edge of screen x, between x and y
        edge = 25
        mid = 10
        pad_y = (0, 20)

        validate = self.register(is_zero_one_decimal)

        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=10)
        self.columnconfigure(2, weight=1)

        self._ok_button = customtkinter.CTkButton(self, width=100, text='U redu', command=self._ok_event)
        self._cancel_button = customtkinter.CTkButton(self, width=100, text='Otkazi', command=self._cancel_event)

        row = 0
        self._dummy_label = customtkinter.CTkLabel(self, text='', width=600)
        self.rowconfigure(row, weight=1)
        self._dummy_label.grid(row=row, column=0, columnspan=3)  # just to define full window width

        row = 1
        self._audio_input_label = customtkinter.CTkLabel(self, text='Mikrofon')
        self._audio_input_combobox = customtkinter.CTkComboBox(self, values=PvRecorder.get_audio_devices())
        self.rowconfigure(row, weight=1)
        self._audio_input_label.grid(row=row, column=0, columnspan=1, padx=(edge, mid), pady=pad_y, sticky='w')
        self._audio_input_combobox.grid(row=row, column=1, columnspan=2, padx=(mid, edge), pady=pad_y, sticky='ew')

        row = 2
        self._model_dir_label = customtkinter.CTkLabel(self, text='Model')
        self._model_dir = StringVar(value=config.get(config.MODEL_PATH))
        self._model_dir_value = customtkinter.CTkEntry(self, textvariable=self._model_dir)
        self._model_dir_browse = customtkinter.CTkButton(self, width=28, text='📂',
                                                         command=lambda: self._set_dir(self._model_dir))
        self.rowconfigure(row, weight=1)
        self._model_dir_label.grid(row=row, column=0, columnspan=1, padx=(edge, mid), pady=pad_y, sticky='w')
        self._model_dir_value.grid(row=row, column=1, columnspan=1, padx=(mid, 0), pady=pad_y, sticky='ew')
        self._model_dir_browse.grid(row=row, column=2, columnspan=1, padx=(0, edge), pady=pad_y, sticky='e')

        row = 3
        self._result_dir_label = customtkinter.CTkLabel(self, text='Cuvaj rezultate u')
        self._result_dir = StringVar(value=config.get(config.RESULT_SAVE_DIR))
        self._result_dir_value = customtkinter.CTkEntry(self, textvariable=self._result_dir)
        self._result_dir_browse = customtkinter.CTkButton(self, width=28, text='📂',
                                                          command=lambda: self._set_dir(self._result_dir))
        self.rowconfigure(row, weight=1)
        self._result_dir_label.grid(row=row, column=0, columnspan=1, padx=(edge, mid), pady=pad_y, sticky='w')
        self._result_dir_value.grid(row=row, column=1, columnspan=1, padx=(mid, 0), pady=pad_y, sticky='ew')
        self._result_dir_browse.grid(row=row, column=2, columnspan=1, padx=(0, edge), pady=pad_y, sticky='e')

        row = 4
        self.rowconfigure(row, weight=1)
        self._ignore_threshold_label = customtkinter.CTkLabel(self, text="Prag ignorisanja izgovora")
        self._ignore_threshold = StringVar(value=config.get(config.THRESHOLD_IGNORE))
        self._ignore_threshold_value = customtkinter.CTkEntry(self, textvariable=self._ignore_threshold,
                                                              validate='key', validatecommand=(validate, '%P'))
        self._ignore_threshold_label.grid(row=row, column=0, columnspan=1, padx=(edge, mid), pady=pad_y, sticky='w')
        self._ignore_threshold_value.grid(row=row, column=1, columnspan=1, padx=(mid, 0), pady=pad_y, sticky='w')

        row = 5
        self.rowconfigure(row, weight=1)
        self._unk_threshold_label = customtkinter.CTkLabel(self, text="Prag pokusaja prepoznavanja")
        self._unk_threshold = StringVar(value=config.get(config.THRESHOLD_UNK))
        self._unk_threshold_value = customtkinter.CTkEntry(self, textvariable=self._unk_threshold,
                                                           validate='key', validatecommand=(validate, '%P'))
        self._unk_threshold_label.grid(row=row, column=0, columnspan=1, padx=(edge, mid), pady=pad_y, sticky='w')
        self._unk_threshold_value.grid(row=row, column=1, columnspan=1, padx=(mid, 0), pady=pad_y, sticky='w')

        row = 6
        self._dark_theme_checkbox = customtkinter.CTkCheckBox(self, text="Koristi tamnu temu")
        if config.get(config.THEME) == 'Dark':
            self._dark_theme_checkbox.select()
        self.rowconfigure(row, weight=1)
        self._dark_theme_checkbox.grid(row=row, column=1, columnspan=1, padx=(mid, mid), pady=pad_y, sticky='w')

        row = 7
        self._shuffle_words_checkbox = customtkinter.CTkCheckBox(self, text="Izmjesaj rijeci prije testa")
        if config.get(config.SHUFFLE_WORDS):
            self._shuffle_words_checkbox.select()
        self.rowconfigure(row, weight=1)
        self._shuffle_words_checkbox.grid(row=row, column=1, columnspan=1, padx=(mid, mid), pady=pad_y, sticky='w')

        row = 8
        self._save_recording_checkbox = customtkinter.CTkCheckBox(self, text="Sacuvaj audio snimak testa")
        if config.get(config.SAVE_RECORDING):
            self._save_recording_checkbox.select()
        self.rowconfigure(row, weight=1)
        self._save_recording_checkbox.grid(row=row, column=1, columnspan=1, padx=(mid, mid), pady=pad_y, sticky='w')

        row = 9
        self.rowconfigure(row, weight=1)
        self._ok_button.grid(row=row, column=1, columnspan=3, padx=(mid, 2 * edge + 100), pady=(30, 20), sticky='e')
        self._cancel_button.grid(row=row, column=1, columnspan=3, padx=(mid, edge), pady=(30, 20), sticky='e')

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
        config.put(config.RESULT_SAVE_DIR, self._result_dir.get())
        config.put(config.THEME, 'Dark' if self._dark_theme_checkbox.get() else 'Light')
        config.put(config.SHUFFLE_WORDS, self._shuffle_words_checkbox.get())
        config.put(config.SAVE_RECORDING, self._save_recording_checkbox.get())
        config.put(config.THRESHOLD_IGNORE, float(self._ignore_threshold.get()))
        config.put(config.THRESHOLD_UNK, float(self._unk_threshold.get()))
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

    def _set_dir(self, dir_var):
        model_dir = filedialog.askdirectory(parent=self)
        if model_dir:
            dir_var.set(model_dir)
