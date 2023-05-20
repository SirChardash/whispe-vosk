import wave
from datetime import datetime
import random
from threading import Thread
from time import sleep
from tkinter import filedialog, END, messagebox
import re

import customtkinter

import config
import recognizer
from speech_test import SpeechTest
from state import State
from pvrecorder import PvRecorder

# get config and apply initial settings
config.initialize()
customtkinter.set_appearance_mode(config.get(config.THEME))

# set global settings
app = customtkinter.CTk()
app.title("my app")
app.geometry("720x520")
app.minsize(720, 360)
state = State(words=[], word_index=-1, audio_input_index=0, speech_test=SpeechTest(), filename='')
rec = recognizer.Recognizer(0, lambda x: x, lambda: print(), 1.0, False)

# instantiate all components
audio_input_combobox = customtkinter.CTkComboBox(app, values=PvRecorder.get_audio_devices())
theme_button = customtkinter.CTkButton(app, text="Tema")
open_button = customtkinter.CTkButton(app, text="Otvori")
start_button = customtkinter.CTkButton(app, text="Zapocni")
retry_word_button = customtkinter.CTkButton(app, text="Ponisti zadnje", state=customtkinter.DISABLED)
stop_test_button = customtkinter.CTkButton(app, text="Prekini", state=customtkinter.DISABLED)
shuffle_words_checkbox = customtkinter.CTkCheckBox(app, text="Nasumican poredak")
save_recording_checkbox = customtkinter.CTkCheckBox(app, text="Sacuvaj audio")
word_to_pronounce_label = customtkinter.CTkLabel(app, text='', font=('Arial', 36))
test_audio_file_button = customtkinter.CTkButton(app, text="Test preko fajla")
load_model_button = customtkinter.CTkButton(app, text="Ucitaj model")
console_output = customtkinter.CTkTextbox(app, width=400)
console_output.bind("<Key>", lambda e: "break")

if config.get(config.SHUFFLE_WORDS):
    shuffle_words_checkbox.select()
if config.get(config.SAVE_RECORDING):
    save_recording_checkbox.select()

# define ui grid
app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=5)

# arrange all components
audio_input_combobox.grid(row=0, column=0, pady=5)
theme_button.grid(row=1, column=0, pady=5)
open_button.grid(row=2, column=0, pady=5)
start_button.grid(row=3, column=0, pady=5)
retry_word_button.grid(row=4, column=0, pady=5)
stop_test_button.grid(row=5, column=0, pady=5)
shuffle_words_checkbox.grid(row=6, column=0, pady=5)
save_recording_checkbox.grid(row=7, column=0, pady=5)
test_audio_file_button.grid(row=8, column=0, pady=5)
load_model_button.grid(row=9, column=0, pady=5)
word_to_pronounce_label.grid(row=0, column=1, pady=30)
console_output.grid(row=1, column=1, rowspan=4)


def set_ui_state(in_test):
    test_component_state = customtkinter.NORMAL if in_test else customtkinter.DISABLED
    config_component_state = customtkinter.DISABLED if in_test else customtkinter.NORMAL
    audio_input_combobox.configure(require_redraw=True, state=config_component_state)
    open_button.configure(require_redraw=True, state=config_component_state)
    start_button.configure(require_redraw=True, state=config_component_state)
    retry_word_button.configure(require_redraw=True, state=test_component_state)
    stop_test_button.configure(require_redraw=True, state=test_component_state)
    shuffle_words_checkbox.configure(require_redraw=True, state=config_component_state)
    test_audio_file_button.configure(require_redraw=True, state=config_component_state)
    save_recording_checkbox.configure(require_redraw=True, state=config_component_state)
    load_model_button.configure(require_redraw=True, state=config_component_state)


def change_audio_input(selected):
    for index, device in enumerate(PvRecorder.get_audio_devices()):
        if selected == device:
            state.audio_input_index = index


def load_words():
    filename = filedialog.askopenfilename()
    if filename:
        words = list(map(lambda x: re.sub('\\s*$', '', x), open(filename, 'r').readlines()))
        if words:
            global state
            state.words = words
            state.filename = re.sub('(^.*[/\\\\])|(\\..{1,3}$)', '', filename)


def retry_word():
    if state.word_index < 1 or state.word_index == len(state.words):
        return
    state.word_index = state.word_index - 1
    word_to_pronounce_label.configure(require_redraw=True, text=state.words[state.word_index])
    ignored = state.speech_test.pop()
    console_output.insert(END, '[X]' + str(ignored) + '\n')


def end_test(finished):
    word_to_pronounce_label.configure(require_redraw=True, text='')
    global rec
    rec.stop()
    if finished:
        save_file = '{0}{1}-{2}'.format(config.get(config.RESULT_SAVE_DIR),
                                        state.filename,
                                        datetime.now().strftime('%Y%m%d%H%M%S'))
        state.speech_test.save('{0}.csv'.format(save_file))
        if save_recording_checkbox.get() and not rec.audio_stream:
            rec.save_last_recording('{0}.wav'.format(save_file))
    state.speech_test = SpeechTest()
    print('done')
    set_ui_state(in_test=False)


def check_word(recognized):
    recognized.expected = state.words[state.word_index] if state.word_index < len(state.words) else ''
    if recognized.confidence < config.get(config.THRESHOLD_UNK):
        recognized.word = '<UNK>'
    console_output.insert(END, str(recognized) + '\n')
    state.speech_test.add(recognized)
    print(recognized)
    state.word_index = state.word_index + 1
    if state.word_index < len(state.words):
        word_to_pronounce_label.configure(require_redraw=True, text=state.words[state.word_index])
    else:
        end_test(finished=True)


def start_test():
    if not state.words:
        return
    global rec
    rec.stop()
    if shuffle_words_checkbox.get():
        random.shuffle(state.words)
    state.word_index = 0
    word_to_pronounce_label.configure(require_redraw=True, text=state.words[state.word_index])
    rec = recognizer.Recognizer(audio_input_index=state.audio_input_index,
                                on_recognize=check_word,
                                on_ready=lambda: print('heh'),
                                model_path=config.get(config.MODEL_PATH),
                                threshold_ignore=config.get(config.THRESHOLD_IGNORE),
                                save_recording=save_recording_checkbox.get())
    Thread(daemon=True, target=rec.start).start()
    console_output.delete('1.0', END)
    set_ui_state(in_test=True)


def toggle_theme():
    config.put(config.THEME, 'Light' if customtkinter.get_appearance_mode() == 'Dark' else 'Dark')
    customtkinter.set_appearance_mode(config.get(config.THEME))


def test_audio_file():
    filename = filedialog.askopenfilename()
    if not filename or not state.words:
        return
    global rec
    rec.stop()
    state.word_index = 0
    word_to_pronounce_label.configure(require_redraw=True, text=state.words[state.word_index])
    rec = recognizer.Recognizer(on_recognize=check_word,
                                on_ready=lambda: print('heh'),
                                threshold_ignore=config.get(config.THRESHOLD_IGNORE),
                                model_path=config.get(config.MODEL_PATH),
                                save_recording=0,
                                audio_stream=wave.open(filename))
    Thread(target=rec.start).start()
    console_output.delete('1.0', END)


def refresh_audio_input_devices():
    while True:
        devices = PvRecorder.get_audio_devices()
        if audio_input_combobox.cget('values') != devices:
            audio_input_combobox.configure(values=devices)
            if audio_input_combobox.get() not in devices:
                new_device = devices[0] if devices else None
                audio_input_combobox.set(new_device)
                change_audio_input(new_device)
        sleep(3)


def set_model_path():
    model_dir = filedialog.askdirectory()
    if model_dir:
        try:
            recognizer.get_recognizer(model_dir)
            config.put(config.MODEL_PATH, model_dir)
        except:
            messagebox.showerror('Greska', 'Odabrani direktorij ne sadrzi model!')


# assign commands to ui components
audio_input_combobox.configure(command=change_audio_input)
theme_button.configure(command=toggle_theme)
open_button.configure(command=load_words)
start_button.configure(command=start_test)
retry_word_button.configure(command=retry_word)
stop_test_button.configure(command=lambda: end_test(finished=False))
test_audio_file_button.configure(command=test_audio_file)
shuffle_words_checkbox.configure(command=lambda: config.put(config.SHUFFLE_WORDS, shuffle_words_checkbox.get()))
save_recording_checkbox.configure(command=lambda: config.put(config.SAVE_RECORDING, save_recording_checkbox.get()))
load_model_button.configure(command=set_model_path)

Thread(daemon=True, target=refresh_audio_input_devices).start()

app.mainloop()
