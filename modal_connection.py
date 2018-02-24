__author__ = 'Tarsier'
import os
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import simpledialog
from settings import Settings
import serial.tools.list_ports

class ConnectionDialog(simpledialog.Dialog):
    def body(self, master):        
        self.parent = master
        self.title('Device Connection')
        self.frame = tk.Frame(self.parent)
        self.resizable(width=False, height=False)
        self.init_classes()
        self.init_variables()
        self.init_ui()

        self.frame.pack(expand=1, fill=BOTH)
    
    def init_classes(self):
        self._settings = Settings()

    def init_variables(self):
        self.port_label = StringVar()
        self.port = StringVar()
        self.baud = StringVar()
        self.baud_rates = [1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200, 128000 , 256000]
        self.ports = list(serial.tools.list_ports.comports())

        self.port_label.set(self._settings.GetSetting('port_label'))
        self.port.set(self._settings.GetSetting('port'))
        self.baud.set(self._settings.GetSetting('baud'))

        self.OK = False ,self.port.get()

        pass

    def init_ui(self):
        self.dir_name = os.path.dirname(os.path.realpath(__file__))
        self.img_path = os.path.join(self.dir_name, "images","serial48.png")
        logo = PhotoImage(file=self.img_path )
        self.label_logo = Label(self.frame, image=logo)
        self.label_logo.image = logo
        self.label_logo.grid(row=0, column=0, rowspan =2, sticky='W', padx=1, pady=4)

        self.lbl_WFM = tk.Label(self.frame, text="Device port settings", font='Tahoma 8 bold', fg = 'gray')
        self.lbl_WFM.grid(row=0, column=1,  sticky='W', padx=1, pady=4)
        self.lbl_Note = tk.Label(self.frame, wraplength= 200, text="Please select port where your GPS device was connected and baud rate", fg ='darkgray')
        self.lbl_Note.grid(row=1, column=1,  sticky='W', padx=1, pady=1)

        self.lbl_ports = tk.Label(self.frame, text="Serial Port:")
        self.lbl_ports.grid(row=2, column=0, sticky='W', padx=10, pady=2)
        self.cbox_ports = ttk.Combobox(self.frame, textvariable=self.port_label, state="readonly", width = 50)
        self.cbox_ports.bind('<Return>')
        self.cbox_ports['values'] =self.ports
        self.cbox_ports.grid(row=2, column=1, sticky="W", pady=3)

        self.lbl_baud = tk.Label(self.frame, text="Baudrate:")
        self.lbl_baud.grid(row=3, column=0, sticky='W', padx=10, pady=2)
        self.cbox_baud = ttk.Combobox(self.frame, textvariable=self.baud, state="readonly", width = 30)
        self.cbox_baud.bind('<Return>')
        self.cbox_baud['values'] =  self.baud_rates
        #self.cbox_baud.current(2) # select index 2 (48000) by default
        self.cbox_baud.grid(row=3, column=1, sticky="W", pady=3)

        pass

    def ok(self):
        sel_port =  self.port_label.get().split(' ')[0].strip()
        print( sel_port)
        self._settings.SetSettings('port',sel_port)
        self._settings.SetSettings('port_label', self.port_label.get())
        self._settings.SetSettings('baud', self.baud.get())
        self.OK = True,self.port.get()
        self.destroy()