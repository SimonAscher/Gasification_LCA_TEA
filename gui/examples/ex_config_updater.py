# # # # # # # CONFIG UPDATER EXAMPLE # # # # # # # #
import tkinter as tk
import tkinter.ttk as ttk


import os
from configupdater import ConfigUpdater

appPath=os.path.dirname(os.path.abspath(__file__))
configPath=os.path.join(appPath,"settings.ini")

updater=ConfigUpdater()
updater.read(configPath)#settings.inimustexists,otherwiseexception

root=tk.Tk()
ttk.Label(root,text='Howmuchdoyoulikecars(from1-10)?').grid(row=0,column=0)

rating= tk.StringVar()
rating_opt=ttk.OptionMenu(root,rating,*range(1,11))#dropdownwithvalues1to10
rating_opt.config(width=5)
rating_opt.grid(row=0,column=1)

def update():
    value=rating.get()
    #updateinifileonlywhenuserhasselectedarating
    if value:
        updater['TradingSettings']['maximum_value_gain'].value=rating.get()
        updater.update_file()

tk.Button(root,text='Update',command=update).grid(row=2,column=0,columnspan=2)

root.mainloop()