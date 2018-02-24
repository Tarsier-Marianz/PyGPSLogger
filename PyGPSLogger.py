__author__ = 'Tarsier'
try:
    from Tkinter import *
    import ttk
    import tkFileDialog
except:
    from tkinter import *
    from tkinter import ttk
    from tkinter import filedialog
    from tkinter import simpledialog
    from tkinter import messagebox

try:
    import configparser
except:
    from six.moves import configparser

import re
import os
import sys
import serial
import datetime
import parsenmea
from threading import Thread
from PIL import ImageTk
from goompy import GooMPy
from storage import StorageDB
from settings import Settings
from modal_connection import ConnectionDialog

WIDTH = 780
HEIGHT = 400

LATITUDE  =  14.5994
LONGITUDE = 121.0369
ZOOM = 15
MAPTYPE = 'roadmap'


'''
Create main window
'''
class Application(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.parent.protocol("WM_DELETE_WINDOW", self.onExit)
        self.parent.bind("<Destroy>", lambda e: self.onExit)

        self.init_settings()
        self.init_classes()
        self.init_variables()
        self.init_images()

        self.init_menubar()
        self.init_toolbar()
        self.init_tabs()
        self.init_statusbar()

        self.init_connections()

        self.pack()

    def init_settings(self):
        pass

    def init_classes(self):
        self.config_menus = configparser.ConfigParser()
        self.config_tools = configparser.ConfigParser()
        self.config_tabs  = configparser.ConfigParser()
        self.config_map  = configparser.ConfigParser()
        self._serial = serial.Serial()
        self._parser = parsenmea.ParseNmea()
        self._storage = StorageDB('gps.sqlite')
        self._settings = Settings()
        
        pass

    def init_variables(self):
        self.images_ui = {}
        self.toolbars ={}
        self.menus ={}

        self.lbl_status = StringVar()
        self.connection_status = StringVar()
        self.port_label = StringVar()
        self.port = StringVar()
        self.baud = StringVar()

        self.line_raw = IntVar()
        self.progress = IntVar()
        self.progress_maximum = IntVar()

        self.is_zoomIn = True
        
        # get current project root path
        self.dir_name = os.path.dirname(os.path.realpath(__file__))
        self.menu_file = os.path.join(self.dir_name, "configs/menus.ini")
        self.tool_file = os.path.join(self.dir_name, "configs/toolbars.ini")
        self.tabs_file = os.path.join(self.dir_name, "configs/tabs.ini")
        self.config_file = os.path.join(self.dir_name, "configs/global.ini")
        self.img_path = os.path.join(self.dir_name, "images")
        self.output_path = os.path.join(self.dir_name, "outputs")
        pass

    def init_images(self):
        for file in os.listdir(self.img_path):
            if file.endswith(".png"):   
                self.images_ui[file.replace(".png","")] =PhotoImage(file= str(os.path.join(self.img_path, file)))
        pass

    def init_menubar(self):
        # Load the menus configuration file
        self.config_menus.read(self.menu_file)
        # Initialize menus from configuration file
        self.menubar = Menu(self.parent)
        for section in self.config_menus.sections():
            topMenu = Menu(self.menubar, tearoff=0)
            for option in self.config_menus.options(section):
                if option.strip()== "-":
                    topMenu.add_separator()
                else:
                    topMenu.add_command(label=self.config_menus.get(section, option), compound=LEFT,
                                image=self.images_ui[option], command=lambda tag=option: self.doClickEvent(0, tag))
                    self.menus[option] =topMenu
            self.menubar.add_cascade(label=section, menu=topMenu)                
        self.parent.config(menu=self.menubar)
        #for entry in self.menus:
            #self.menus[entry].config(fg= 'green', image= self.images_ui['connect'])            
        pass

    def init_toolbar(self):
        # Load the toolbars configuration file
        self.config_tools.read(self.tool_file)
        # Initialize toolbars from configuration file
        
        self.toolbar = Frame(self.parent, bd=1, relief=RAISED)     
        for section in self.config_tools.sections():           
            for option in self.config_tools.options(section):
                self.btn_tool = Button(self.toolbar,  image=self.images_ui[option], text=option,relief=FLAT, justify=CENTER ,command=lambda tag=option :self.doClickEvent(0,tag))
                self.btn_tool.image =self.images_ui[option]               
                self.btn_tool.pack(side=LEFT, padx=2, pady=2)
                self.toolbars[option] =self.btn_tool
        self.toolbar.pack(side=TOP, fill=X)

        #for entry in self.toolbars:
        #    self.toolbars[entry]['state'] = DISABLED
        pass

    def init_tabs(self):
         # Load the tabs configuration file
        self.config_tabs.read(self.tabs_file)
        # Initialize tabs from configuration file
        self.tabs = ttk.Notebook(self.parent)
        for section in self.config_tabs.sections():           
            for tab in self.config_tabs.options(section):
                tabPage = ttk.Frame(self.tabs)   # first page, which would get widgets gridded into it            
                self.tabs.add(tabPage, text= self.config_tabs.get(section, tab), image =self.images_ui[tab], compound=LEFT)
                self.create_tabPages(tab, tabPage)
                pass
        self.tabs.pack(expand=1, fill="both")  # Pack to make visible

    def init_statusbar(self):
        self.status_frame = Frame(self.parent, bd=1, relief=GROOVE)
        self.status_frame.pack(fill=X)

        label_Status = Label(self.status_frame,textvariable=self.lbl_status, anchor=W)
        label_Status.pack(side=LEFT)
        label_Dummy = Label(self.status_frame,text='|  GPS Device:' , anchor=W)
        label_Dummy.pack(side=LEFT)
        lbl_Connection = Label(self.status_frame,textvariable=self.connection_status, anchor=E, fg = 'blue')
        lbl_Connection.pack(side=LEFT)        
        self.connection_status.set("Disconnected")
        label_lineDummy = Label(self.status_frame,text='|  Line:' , anchor=W)
        label_lineDummy.pack(side=LEFT)
        lbl_lineRaw = Label(self.status_frame,textvariable=self.line_raw, anchor=E, fg = 'green')
        lbl_lineRaw.pack(side=LEFT)        
        self.line_raw.set(0)

    def create_tabPages(self, tag, tabPage):
        if tag== 'parse':
            self.tree_parseDate = ttk.Treeview(tabPage, selectmode='browse')
            verticalScroll = ttk.Scrollbar(tabPage, orient='vertical', command=self.tree_parseDate.yview)
            verticalScroll.pack(side='right', fill='y')
            horScroll = ttk.Scrollbar(tabPage, orient='horizontal', command=self.tree_parseDate.xview)
            horScroll.pack(side='bottom', fill='x')
            
            self.tree_parseDate.configure(yscrollcommand=verticalScroll.set)
            self.tree_parseDate.configure(xscrollcommand=horScroll.set)

            self.tree_parseDate['columns'] = ('count', 'details')
            #self.tree_parseDate['show'] = 'headings'
            self.tree_parseDate.heading("#0", text='Name', anchor='w')
            #self.tree_parseDate.column("#0", anchor="w", width=40)
            self.tree_parseDate.heading('count', text='Count')
            self.tree_parseDate.column('count', stretch ='yes', anchor='center', width=14)
            self.tree_parseDate.heading('details', text='Details')
            self.tree_parseDate.column('details', anchor='center', width=20)

            #self.init_workspaces()
            self.tree_parseDate.pack(expand=1, fill='both')
        elif tag=='raw':
            self.txt_rawData = Text(tabPage)
            self.txt_rawData.pack(expand=1, fill='both')
            self.txt_rawData.insert(END, 'GPS Logger started...')
            pass
        elif tag=='summary':
            pass
        else:
            self.canvas = Canvas(tabPage)
            self.canvas.pack(expand=1, fill='both')
            self.label = Label(self.canvas)
            self.label.bind('<B1-Motion>', self.goompy_drag)
            self.label.bind('<Button-1>', self.goompy_click)
            self.label.bind("<Double-1>", lambda e:self.goompy_zoom(+1))      
            self.label.bind("<Double-3>", lambda e:self.goompy_zoom(-1))
            self.label.bind_all("<MouseWheel>", self.goompy_mousewheel)
            self.zoomlevel = ZOOM
            self.goompy = GooMPy(WIDTH, HEIGHT, LATITUDE, LONGITUDE, ZOOM, MAPTYPE)
            self.goompy_restart()
            pass
        pass
        
    def goompy_reload(self):
        self.coords = None
        self.goompy_redraw()
        self.parent['cursor']  = ''
        pass

    def goompy_restart(self):
        # A little trick to get a watch cursor along with loading
        self.parent['cursor']  = 'watch'
        self.after(1, self.goompy_reload)

    def goompy_redraw(self):
        self.image = self.goompy.getImage()
        self.image_tk = ImageTk.PhotoImage(self.image)
        self.label['image'] = self.image_tk
        self.label.pack(expand=1, fill='both')

    def goompy_zoom(self, sign):
        newlevel = self.zoomlevel + sign
        if newlevel > 0 and newlevel < 22:
            self.zoomlevel = newlevel
            self.goompy.useZoom(newlevel)
            self.goompy_restart()
    
    def goompy_mousewheel(self,event):
        if event.num == 5 or event.delta < 0:
            self.goompy_zoom(-1)
        else:
            self.goompy_zoom(+1)
        pass

    def goompy_drag(self, event):
        try:
            # Ignore NONE value 
            self.goompy.move(self.coords[0]-event.x, self.coords[1]-event.y)
        except:
            pass
        self.image = self.goompy.getImage()
        self.goompy_redraw()
        self.coords = event.x, event.y

    def goompy_click(self, event):
        self.coords = event.x, event.y

    def init_connections(self):
        self.port_label.set(self._settings.GetSetting('port_label'))
        self.port.set(self._settings.GetSetting('port'))
        self.baud.set(self._settings.GetSetting('baud'))
        self.lbl_status.set(('%s | %s'% (self.port_label.get(), self.baud.get())))
        
        self.port_old = self._settings.GetSetting('port_old')
        if self.port.get() != self.port_old:
            if self._serial.is_open == True:
                self._serial.close()            
                self.connection_status.set("Disconnected")
                self.toolbars['connect']['image'] = self.images_ui['connect']            
                self.menus['connect'].entryconfig(1,image= self.images_ui['connect'], label='Connect')
                
        self._serial.baudrate =self.baud.get()
        self._serial.port = self.port.get()
        
    def connect_device(self):
        if self._serial.is_open == False:
            try: 
                self._serial.open() # Open serial port
            except:
                pass
        else:
            self._serial.close()

        if self._serial.is_open == True:
            self.connection_status.set("Connected")
            self.toolbars['connect']['image'] = self.images_ui['disconnect']
            self.menus['connect'].entryconfig(1,image= self.images_ui['disconnect'], label='Disconnect')
            self.thread = Thread(target=self.read_serial, name = str(datetime.datetime.now()))
            self.thread.start()
        else:
            self.connection_status.set("Disconnected")
            self.toolbars['connect']['image'] = self.images_ui['connect']
            self.menus['connect'].entryconfig(1,image= self.images_ui['connect'], label='Connect')


    def read_serial(self):
        self.txt_rawData.insert(END, '\n') # add first line as line space
        self.line_raw.set(0)
        i =0
        while self._serial.is_open:
            reading = self._serial.read(self._serial.in_waiting)
            self.txt_rawData.insert(END, reading)
            self.txt_rawData.see("end")
            self.line_raw.set(i)
            i +=1
    
    def read_data(self, filename):
        self._parser.ParseGpsNmeaFile(filename)
        # If the gpsData is length zero the file was not in the
        # GPGGA, GPRMC pair format. Try the just GPRMC format
        if len(self._parser.gpsData) == 0:
            self._parser.ParseGpsNmeaGprmcFile(filename)
            if len(self._parser.gpsData) == 0:
                print("Error parsing data. Fix input file?")
                exit
        output_file =''.join(ch for ch in str(datetime.datetime.now()) if ch.isalnum())
        self._parser.SaveReducedGpsData('%s.txt' %  os.path.join(self.output_path, output_file))

        self.txt_rawData.delete('1.0', END)
        self.txt_rawData.insert(END, '\n') # add first line as line space
        with open(filename) as fp:
            self.line_raw.set(0)
            i =0
            for cnt, line in enumerate(fp):
                #print("Line {}: {}".format(cnt, line))
                if line.strip() is not '':
                    self.txt_rawData.insert(END, line)
                    self.txt_rawData.see("end")
                    self.line_raw.set(i)
                    i +=1

    '''
    This region starts with control events
    '''
    def doClickEvent(self, index, tag):
        if tag == 'zoom_out':
            self.is_zoomIn = False
            self.goompy_zoom(-1)
        elif tag == 'zoom_in':
            self.is_zoomIn = True
            self.goompy_zoom(+1)
        elif tag =='port':
            self._settings.SetSettings('port_old',self.port.get())
            cd = ConnectionDialog(self.parent)
            if cd.OK[0] == True:
                self.init_connections()                
        elif tag =='connect':
            self.connect_device()
            pass

        elif tag =='open':
            self.file_name = filedialog.askopenfilename()
            self.lbl_status.set(self.file_name)
            self.read_data(self.file_name)
            #self.thread = Thread(target=self.read_data, name = str(datetime.datetime.now()))
            #self.thread.start()
        else:
            print ((index,tag))
            pass
        pass

    def onExit(self):
        try:
            if messagebox.askokcancel('Quit', 'Do you want to quit?'):
                self.parent.destroy()
        except:
            pass


def main():
    root = Tk()
    style = ttk.Style()
    root.geometry("800x500+100+100")
    app = Application(root)
    app.master.title("Py GPS Logger")
    app.master.iconbitmap( os.path.join(os.path.dirname(os.path.realpath(__file__)), "gps.ico"))

    if 'win' not in sys.platform:
        style.theme_use('clam')

    root.mainloop()


if __name__ == '__main__':
    main()
