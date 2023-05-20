import wave
from datetime import datetime
import random
from threading import Thread
from tkinter import filedialog, END
import re

import customtkinter

import config
import recognizer
import settings_dialog
from speech_test import SpeechTest
from state import State
from pvrecorder import PvRecorder

# get config and apply initial settings
config.initialize()
customtkinter.set_appearance_mode(config.get(config.THEME))

# set global settings
app = customtkinter.CTk()
app.title('my app')
app.geometry('720x520')
app.minsize(720, 360)
state = State(words=[], word_index=-1, audio_input_index=0, speech_test=SpeechTest(), filename='')
rec = recognizer.Recognizer(0, lambda x: x, lambda: print(), 1.0, False)

# instantiate all components
settings_button = customtkinter.CTkButton(app, text='Postavke')
open_button = customtkinter.CTkButton(app, text='Otvori')
start_button = customtkinter.CTkButton(app, text='Zapocni')
retry_word_button = customtkinter.CTkButton(app, text='Ponisti zadnje', state=customtkinter.DISABLED)
stop_test_button = customtkinter.CTkButton(app, text='Prekini', state=customtkinter.DISABLED)
word_to_pronounce_label = customtkinter.CTkLabel(app, text='', font=('Arial', 36))
test_audio_file_button = customtkinter.CTkButton(app, text='Test preko fajla')
console_output = customtkinter.CTkTextbox(app, width=400)
console_output.bind('<Key>', lambda e: 'break')

# define ui grid
app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=5)

# arrange all components
settings_button.grid(row=1, column=0, pady=5)
open_button.grid(row=2, column=0, pady=5)
start_button.grid(row=3, column=0, pady=5)
retry_word_button.grid(row=4, column=0, pady=5)
stop_test_button.grid(row=5, column=0, pady=5)
test_audio_file_button.grid(row=8, column=0, pady=5)
word_to_pronounce_label.grid(row=0, column=1, pady=30)
console_output.grid(row=1, column=1, rowspan=4)


def set_ui_state(in_test):
    test_component_state = customtkinter.NORMAL if in_test else customtkinter.DISABLED
    config_component_state = customtkinter.DISABLED if in_test else customtkinter.NORMAL
    settings_button.configure(require_redraw=True, state=config_component_state)
    open_button.configure(require_redraw=True, state=config_component_state)
    start_button.configure(require_redraw=True, state=config_component_state)
    retry_word_button.configure(require_redraw=True, state=test_component_state)
    stop_test_button.configure(require_redraw=True, state=test_component_state)
    test_audio_file_button.configure(require_redraw=True, state=config_component_state)


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
        if config.get(config.SAVE_RECORDING) and not rec.audio_stream:
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


def get_audio_input_index():
    device_name = config.get(config.AUDIO_INPUT)
    for index, device in enumerate(PvRecorder.get_audio_devices()):
        if device_name == device:
            return index
    return 0


def start_test():
    if not state.words:
        return
    global rec
    rec.stop()
    if config.get(config.SHUFFLE_WORDS):
        random.shuffle(state.words)
    state.word_index = 0
    word_to_pronounce_label.configure(require_redraw=True, text=state.words[state.word_index])
    rec = recognizer.Recognizer(audio_input_index=get_audio_input_index(),
                                on_recognize=check_word,
                                on_ready=lambda: print('heh'),
                                model_path=config.get(config.MODEL_PATH),
                                threshold_ignore=config.get(config.THRESHOLD_IGNORE),
                                save_recording=config.get(config.SAVE_RECORDING))
    Thread(daemon=True, target=rec.start).start()
    console_output.delete('1.0', END)
    set_ui_state(in_test=True)


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


# assign commands to ui components
settings_button.configure(command=lambda: settings_dialog.SettingsDialog())
open_button.configure(command=load_words)
start_button.configure(command=start_test)
retry_word_button.configure(command=retry_word)
stop_test_button.configure(command=lambda: end_test(finished=False))
test_audio_file_button.configure(command=test_audio_file)

app.mainloop()
