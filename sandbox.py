from tkinter import *


def read_input_field():
    current_input = input_field.get()
    print(current_input)


window = Tk()
window.title("Mail")

input_field = Entry(window)
ok_button = Button(text='prüfen', command=read_input_field)

input_field.pack()
ok_button.pack()

window.mainloop()