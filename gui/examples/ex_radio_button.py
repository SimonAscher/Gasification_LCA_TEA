# # # # # # # # RADIO BUTTON EXAMPLE # # # # # # # # # #
# https://python-course.eu/tkinter/radio-buttons-in-tkinter.php#:~:text=A%20radio%20button%2C%20sometimes%20called,text%20in%20a%20single%20font.

import tkinter as tk

root = tk.Tk()

v = tk.IntVar()
v.set(1)  # initializing the choice, i.e. Python

languages = [("Python", 101),
   	     ("Perl", 102),
    	     ("Java", 103),
             ("C++", 104),
             ("C", 105)]

def ShowChoice():
    print(v.get())

tk.Label(root,
         text="""Choose your favourite programming language:""",
         justify = tk.LEFT,
         padx = 20).pack()

for language, val in languages:
    tk.Radiobutton(root,
                   text=language,
                   padx = 20,
                   variable=v,
                   command=ShowChoice,
                   value=val).pack(anchor=tk.W)


root.mainloop()
