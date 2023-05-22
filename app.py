import wave
from datetime import datetime
import random
from threading import Thread
from tkinter import filedialog, END, messagebox
import re

import customtkinter

import config
import recognizer
import settings_dialog
from speech_test import SpeechTest
from state import State
from pvrecorder import PvRecorder

config.initialize()

# set global settings
customtkinter.set_appearance_mode(config.get(config.THEME))
app = customtkinter.CTk()
app.title('Vosk Recorder')
app.minsize(720, 520)
state = State(words=[], word_index=-1, speech_test=SpeechTest(), filename='')
rec = recognizer.Recognizer(0, lambda x: x, lambda: print(), 1.0, False)

# instantiate all components
settings_button = customtkinter.CTkButton(app, text='🛠', height=48, width=48, font=('Arial', 24))
open_button = customtkinter.CTkButton(app, text='Učitaj riječi')
start_button = customtkinter.CTkButton(app, text='Test govorom',
                                       state=customtkinter.DISABLED)
retry_word_button = customtkinter.CTkButton(app, text='Poništi riječ',
                                            state=customtkinter.DISABLED)
stop_test_button = customtkinter.CTkButton(app, text='Prekini test',
                                           state=customtkinter.DISABLED)
word_to_pronounce_label = customtkinter.CTkLabel(app, text='', font=('Arial', 42))
test_audio_file_button = customtkinter.CTkButton(app, text='Test fajlom',
                                                 state=customtkinter.DISABLED)
console_output = customtkinter.CTkTextbox(app)
console_output.bind('<Key>', lambda e: 'break')

# define ui grid
app.grid_columnconfigure(0, weight=1)
app.grid_rowconfigure(0, weight=2)
app.grid_rowconfigure(1, weight=2)
app.grid_rowconfigure(2, weight=2)
app.grid_rowconfigure(3, weight=3)

# arrange all components
open_button.grid(row=0, column=0, pady=25, padx=25, sticky='nw')
settings_button.grid(row=0, column=0, pady=25, padx=25, sticky='ne')

start_button.grid(row=0, column=0, pady=25, padx=(180, 0), sticky='nw')
retry_word_button.grid(row=2, column=0, pady=(25, 5), padx=180, sticky='ws')
stop_test_button.grid(row=2, column=0, pady=(25, 5), padx=25, sticky='ws')
test_audio_file_button.grid(row=0, column=0, pady=25, padx=(335, 0), sticky='nw')
word_to_pronounce_label.grid(row=1, pady=30, columnspan=2, sticky='ew')
console_output.grid(row=3, column=0, padx=25, pady=25, sticky='news')


def console_log(text):
    console_output.insert(END, text + '\n')


def set_ui_state(in_test, words_loaded):
    test_component_state = customtkinter.NORMAL if in_test else customtkinter.DISABLED
    config_component_state = customtkinter.DISABLED if in_test else customtkinter.NORMAL
    run_test_component_state = customtkinter.NORMAL if not in_test and words_loaded else customtkinter.DISABLED
    settings_button.configure(require_redraw=True, state=config_component_state)
    open_button.configure(require_redraw=True, state=config_component_state)
    start_button.configure(require_redraw=True, state=run_test_component_state)
    retry_word_button.configure(require_redraw=True, state=test_component_state)
    stop_test_button.configure(require_redraw=True, state=test_component_state)
    test_audio_file_button.configure(require_redraw=True, state=run_test_component_state)


def load_words():
    filename = filedialog.askopenfilename()
    if filename:
        words = list(map(lambda x: re.sub('\\s*$', '', x), open(filename, 'r').readlines()))
        if words:
            global state
            state.words = words
            state.filename = re.sub('(^.*[/\\\\])|(\\..{1,3}$)', '', filename)
            set_ui_state(in_test=False, words_loaded=state.words)
            console_log('učitao {0}, ukupno {1} riječi'.format(state.filename, len(state.words)))


def retry_word():
    if state.word_index < 1 or state.word_index == len(state.words):
        return
    state.word_index = state.word_index - 1
    word_to_pronounce_label.configure(require_redraw=True, text=state.words[state.word_index])
    ignored = state.speech_test.pop()
    console_log('[X]' + str(ignored))


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
    set_ui_state(in_test=False, words_loaded=state.words)


def check_word(recognized):
    recognized.expected = state.words[state.word_index] if state.word_index < len(state.words) else ''
    if recognized.confidence < config.get(config.THRESHOLD_UNK):
        recognized.word = '<UNK>'
    console_log(str(recognized))
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


def pre_test_validate():
    if not state.words:
        messagebox.showerror('Greška', 'Morate prvo učitati riječi za test!')
        return False
    if not recognizer.test_model(config.get(config.MODEL_PATH)):
        messagebox.showerror('Greška', 'Model nevalidan. Provjerite putanju.')
        return False
    return True


def start_test():
    if not pre_test_validate():
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
    set_ui_state(in_test=True, words_loaded=state.words)


def test_audio_file():
    if not pre_test_validate():
        return
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
settings_button.configure(command=lambda: settings_dialog.SettingsDialog(title='Podešavanja'))
open_button.configure(command=load_words)
start_button.configure(command=start_test)
retry_word_button.configure(command=retry_word)
stop_test_button.configure(command=lambda: end_test(finished=False))
test_audio_file_button.configure(command=test_audio_file)

app.mainloop()
