from datetime import datetime
from threading import Thread
from tkinter import filedialog, END
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
app.geometry("720x360")
app.minsize(720, 360)
state = State(words=[], word_index=-1, audio_input_index=0, speech_test=SpeechTest(), filename='')
rec = recognizer.Recognizer(0, lambda x: x, lambda: print(), 1.0)

# instantiate all components
audio_input_combobox = customtkinter.CTkComboBox(app, values=PvRecorder.get_audio_devices())
theme_button = customtkinter.CTkButton(app, text="Tema")
open_button = customtkinter.CTkButton(app, text="Otvori")
start_button = customtkinter.CTkButton(app, text="Zapocni")
word_to_pronounce_label = customtkinter.CTkLabel(app, text='', font=('Arial', 36))
console_output = customtkinter.CTkTextbox(app)
console_output.bind("<Key>", lambda e: "break")

# define ui grid
app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=5)

# arrange all components
audio_input_combobox.grid(row=0, column=0, pady=5)
theme_button.grid(row=1, column=0, pady=5)
open_button.grid(row=2, column=0, pady=5)
start_button.grid(row=3, column=0, pady=5)
word_to_pronounce_label.grid(row=0, column=1, pady=30)
console_output.grid(row=1, column=1, rowspan=4)


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


def end_test(finished):
    word_to_pronounce_label.configure(require_redraw=True, text='')
    global rec
    rec.stop()
    if finished:
        state.speech_test.save('{0}{1}-{2}.csv'.format(config.get(config.RESULT_SAVE_DIR),
                                                       state.filename,
                                                       datetime.now().strftime('%Y%m%d%H%M%S')))
    print('done')


def check_word(recognized):
    recognized.expected = state.words[state.word_index]
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
    state.word_index = 0
    word_to_pronounce_label.configure(require_redraw=True, text=state.words[state.word_index])
    rec = recognizer.Recognizer(audio_input_index=state.audio_input_index, on_recognize=check_word,
                                on_ready=lambda: print('heh'),
                                threshold_ignore=config.get(config.THRESHOLD_IGNORE))
    Thread(target=rec.start).start()
    console_output.delete('1.0', END)


def toggle_theme():
    config.put(config.THEME, 'Light' if customtkinter.get_appearance_mode() == 'Dark' else 'Dark')
    customtkinter.set_appearance_mode(config.get(config.THEME))


# assign commands to ui components
audio_input_combobox.configure(command=change_audio_input)
theme_button.configure(command=toggle_theme)
open_button.configure(command=load_words)
start_button.configure(command=start_test)

app.mainloop()
