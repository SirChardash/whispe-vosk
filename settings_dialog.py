from threading import Thread
from time import sleep
from tkinter import filedialog, messagebox, StringVar

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
        mid = 0
        pad_y = (0, 20)

        validate = self.register(is_zero_one_decimal)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=8)
        self.columnconfigure(2, weight=1)

        row = 0
        self._dummy_label = customtkinter.CTkLabel(self, text='', width=640)
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
        self._result_dir_label = customtkinter.CTkLabel(self, text='Čuvaj rezultate u')
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
        self._unk_threshold_label = customtkinter.CTkLabel(self, text="Prag pokušaja prepoznavanja")
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
        self._shuffle_words_checkbox = customtkinter.CTkCheckBox(self, text="Izmješaj riječi prije testa")
        if config.get(config.SHUFFLE_WORDS):
            self._shuffle_words_checkbox.select()
        self.rowconfigure(row, weight=1)
        self._shuffle_words_checkbox.grid(row=row, column=1, columnspan=1, padx=(mid, mid), pady=pad_y, sticky='w')

        row = 8
        self._save_recording_checkbox = customtkinter.CTkCheckBox(self, text="Sačuvaj audio snimak testa")
        if config.get(config.SAVE_RECORDING):
            self._save_recording_checkbox.select()
        self.rowconfigure(row, weight=1)
        self._save_recording_checkbox.grid(row=row, column=1, columnspan=1, padx=(mid, mid), pady=pad_y, sticky='w')

        row = 9
        self._result_format_label = customtkinter.CTkLabel(self, text='Format rezultata')
        self.rowconfigure(row, weight=1)
        self._result_format = StringVar(value=config.get(config.RESULT_FORMAT))
        self._result_format_value = customtkinter.CTkEntry(self, textvariable=self._result_format)
        self._result_format_label.grid(row=row, column=0, columnspan=1, padx=(edge, mid), pady=pad_y, sticky='w')
        self._result_format_value.grid(row=row, column=1, columnspan=1, padx=(mid, 0), pady=pad_y, sticky='ew')

        row = 10
        self.rowconfigure(row, weight=5)
        self._result_format_hint1 = customtkinter.CTkLabel(self, text='{expected} očekivana riječ')
        self._result_format_hint1.grid(row=row, column=1, columnspan=1, padx=(mid, 0), pady=(0, 10), sticky='w')

        row = 11
        self.rowconfigure(row, weight=1)
        self._result_format_hint2 = customtkinter.CTkLabel(self, text='{detected} prepoznata riječ')
        self._result_format_hint2.grid(row=row, column=1, columnspan=1, padx=(mid, 0), pady=(0, 10), sticky='w')

        row = 12
        self.rowconfigure(row, weight=1)
        self._result_format_hint3 = customtkinter.CTkLabel(self, text='{confidence} pouzdanost')
        self._result_format_hint3.grid(row=row, column=1, columnspan=1, padx=(mid, 0), pady=(0, 10), sticky='w')

        row = 13
        self.rowconfigure(row, weight=1)
        self._result_format_example = customtkinter.CTkLabel(self, text=self._show_example_result_format())
        self._result_format_example.grid(row=row, column=1, columnspan=1, padx=(mid, 0), pady=(0, 10), sticky='w')
        self._result_format.trace_add("write", lambda x, y, z: self._result_format_example.configure(
            text=self._show_example_result_format()))

        row = 14
        self._ok_button = customtkinter.CTkButton(self, width=100, text='U redu', command=self._ok_event)
        self._cancel_button = customtkinter.CTkButton(self, width=100, text='Otkaži', command=self._cancel_event)
        self.rowconfigure(row, weight=1)
        self._ok_button.grid(row=row, column=1, columnspan=3, padx=(mid, 2 * edge + 100), pady=(30, 20), sticky='e')
        self._cancel_button.grid(row=row, column=1, columnspan=3, padx=(mid, edge), pady=(30, 20), sticky='e')

        self._listen_to_device_change = True
        Thread(daemon=True, target=self._refresh_audio_input_devices).start()

    def _ok_event(self, event=None):
        if not recognizer.test_model(self._model_dir.get()):
            messagebox.showerror('Greška', 'Odabrani direktorij ne sadrži model!')
            return

        config.put(config.AUDIO_INPUT, self._audio_input_combobox.get())
        config.put(config.MODEL_PATH, self._model_dir.get())
        config.put(config.RESULT_SAVE_DIR, self._result_dir.get())
        config.put(config.THEME, 'Dark' if self._dark_theme_checkbox.get() else 'Light')
        config.put(config.SHUFFLE_WORDS, self._shuffle_words_checkbox.get())
        config.put(config.SAVE_RECORDING, self._save_recording_checkbox.get())
        config.put(config.THRESHOLD_IGNORE, float(self._ignore_threshold.get()))
        config.put(config.THRESHOLD_UNK, float(self._unk_threshold.get()))
        config.put(config.RESULT_FORMAT, self._result_format.get())
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

    def _show_example_result_format(self):
        try:
            return 'Primjer: {}'.format(self._result_format.get().format(detected='izgovoreno',
                                                                         expected='ocekivano',
                                                                         confidence='0.997'))
        except:
            return ''
