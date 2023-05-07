import customtkinter

import config


def button_callback():
    print(customtkinter.get_appearance_mode())
    config.put(config.THEME, 'Light' if customtkinter.get_appearance_mode() == 'Dark' else 'Dark')
    customtkinter.set_appearance_mode(config.get(config.THEME))


def combobox_callback(choice):
    print("combobox dropdown clicked:", choice)


config.initialize()
customtkinter.set_appearance_mode(config.get(config.THEME))

app = customtkinter.CTk()
app.title("my app")
app.geometry("720x360")
app.minsize(720, 360)

combobox = customtkinter.CTkComboBox(app, values=["option 1", "option 2"],
                                     command=combobox_callback)
combobox.set("option 2")
combobox.grid(row=0, column=0, padx=20, pady=20)

button = customtkinter.CTkButton(app, text="⛭", font=('Arial', 25), command=button_callback)
button.grid(row=0, column=1, padx=20, pady=20)

button2 = customtkinter.CTkButton(app, text="my button", command=button_callback)
button2.grid(row=1, column=2, padx=20, pady=20)

app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=10)
app.grid_columnconfigure(2, weight=1)

app.mainloop()
