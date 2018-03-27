from Tkinter import *
import ttk
import matplotlib.animation as anim
import threading
import thread
import time
import timeit
import numpy as np
import serial
import sys
import subprocess
import struct
from  __builtin__ import any as b_any
from random import randint
import datetime as stampTime
import datetime as stampDate
import datetime as dt
import datetime as DT
import decimal
import csv

#from Pillow import Image,ImageTk
#import Pillow
import os
import random
#from pyorbital import orbital
#from orbital import tlefile
from datetime import datetime
import matplotlib
#from matplotlib import style
from serial.serialutil import SerialException
#style.use('ggplot')
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler
import math
#from matplotlib import style
LARGE_FONT= ("Verdana", 12)



class menu: #this class creates and displays the preferences menu
    def __init__(self,root): #here the default option menu values are defined, to be overwritten when the user changes the settings
        self.root = root
        self.baudSelection = StringVar() #the variable which will be in the optionmenu for the radio settings
        self.paritySelection = StringVar()
        self.databitsSelection = StringVar()
        self.stopbitsSelection = StringVar()
        self.HFCSelection = StringVar()
        self.path = StringVar() #stores the path to the TLE file
        self.wPath = StringVar() #stores the write to file path
        self.write = IntVar() #stores whether the write to file radio button is 'yes' or 'no'
        self.extendedTele = IntVar() #stores whether the extended telemetry radio button is 'yes' or 'no'
        self.baudSelection.set('9600') #set the default value for the optionmenu
        self.paritySelection.set('None')
        self.databitsSelection.set('8')
        self.stopbitsSelection.set('1')
        self.HFCSelection.set('False')
        #self.path.set('/users/gregstewart96/Desktop/unisat6.txt')
        self.path.set('C:\Users\Alex\GUI\unisat6.txt')
        #self.wPath.set('/users/gregstewart96/desktop') #default write path
        self.wPath.set("C:\\Users\\Alex\\GUI\\")
        self.TLEPath = self.path.get() #stores the stringVar() in a variable
        self.writePathVar = self.wPath.get() #stores the stringVar() in a variable
        self.write.set('1')
        self.extendedTele.set('2')
        self.baud='9600'
        self.par=serial.PARITY_NONE #here the actual default values which correspond to the optionmenu default values are defined
        self.data=serial.EIGHTBITS
        self.stop=serial.STOPBITS_ONE
        #self.HFC='False'
        self.HFC = 0
  
        
        menubar = Menu(root) #create the menu
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Preferences", command=self.preferences_window) #when preferences is selected, the preferences_window is called
        filemenu.add_command(label="Quit", command=self.quit)
        menubar.add_cascade(label="GSI", menu=filemenu)
        root.config(menu=menubar)

    def quit(self): #when the quit menu item is selected this method is called
        os._exit(1) #a hard exit is required as there will be multiple threads running.

    def preferences_window(self): #this method creates preferences widgets and labels, and allows the user to set new settings values 
        window = Toplevel(self.root) #creates a new smaller window on top of the existing one
        window.title("Preferences") #title of the window
    
        close_button = Button(window, text="Close", command=lambda: self.close_window(window)) #call the close_window method when the button is pressed
        close_button.grid(row=30, column=0,columnspan=2)
        
        self.listbox = Listbox(window) #creates the listbox for port selection
        self.listbox['height'] = 10
        self.listbox['width'] = 30
        self.listbox.grid(row=1,rowspan=20, columnspan=5) #given a big row and column span to stop the listbox stretching columns
        self.listbox.bind('<<ListboxSelect>>',self.CurSelet) #listbox attached to teh self.CurSelet event handler
        port_list = subprocess.check_output([sys.executable, "list_ports.py"]) #runs the script that lists the ports as a subprocess and stores what it returns in a variable
        port_list = port_list.split() #breaks each port into a seperate lines
        for port in port_list: #loops through each port
            global port_selection
            self.listbox.insert(0, port) #adds each port to the listbox

        baudrateLabel = Label(window) #create the label that displays which setting this is
        baudrateLabel["text"] = "Baudrate"
        baudrateLabel.grid(row=21, column=0, sticky="W")
        baudOptions={'115200','57600','19200','14400','9600','4800'} #various options for the optionmenu
        baudDropdown = OptionMenu(window, self.baudSelection, *baudOptions, command=self.baud_selection) #create the optionmenu sending the chosen item to self.baud_selection
        baudDropdown.grid(row=21, column=1, sticky="W")

        parityLabel = Label(window)
        parityLabel["text"] = "Parity"
        parityLabel.grid(row=22, column=0, sticky="W")
        parityOptions={'None','Even','Odd','Mark','Space'}
        parityDropdown = OptionMenu(window, self.paritySelection, *parityOptions, command=self.parity_selection)
        parityDropdown.grid(row=22, column=1, sticky="W")

        databitsLabel = Label(window)
        databitsLabel["text"] = "Data Bits"
        databitsLabel.grid(row=23, column=0, sticky="W")
        databitsOptions={'5','6','7','8'}
        databitsDropdown = OptionMenu(window, self.databitsSelection, *databitsOptions, command=self.databits_selection)
        databitsDropdown.grid(row=23, column=1, sticky="W")

        stopbitsLabel = Label(window)
        stopbitsLabel["text"] = "Stop Bits"
        stopbitsLabel.grid(row=24, column=0, sticky="W") 
        stopbitsOptions={'1','1.5','2'}
        stopbitsDropdown = OptionMenu(window, self.stopbitsSelection, *stopbitsOptions, command=self.stopbits_selection)
        stopbitsDropdown.grid(row=24, column=1, sticky="W")

        HFCLabel = Label(window)
        HFCLabel["text"] = "Hardware Flow Control"
        HFCLabel.grid(row=25, column=0, sticky="W")
        HFCOptions={'True','False'}
        HFCDropdown = OptionMenu(window, self.HFCSelection, *HFCOptions, command=self.HFC_selection)
        HFCDropdown.grid(row=25, column=1, sticky="W")

        writePathLabel = Label(window)
        writePathLabel["text"] = "File Write Path"
        writePathLabel.grid(row=26,column=0,sticky="W")
        writePath = Entry(window,textvariable=self.wPath,width=10)
        writePath.grid(row=26,column=1,sticky="W")
        self.wPath.trace("w",self.entryCallback)

        writeFrame = Frame(window) #a new small frame is placed on the grid just so that multiple buttons can be placed in one grid
        writeFrame.grid(row=27,column=1, sticky="nsew")
        writeLabel = Label(window, text="Write timestamps to file").grid(row=27, column=0, sticky="W")
        writeYes = Radiobutton(writeFrame, text="Yes", variable=self.write, value=1).grid(row=0,column=0)
        writeNo = Radiobutton(writeFrame, text="No", variable=self.write, value=2).grid(row=0,column=1)

        extendedTeleFrame = Frame(window)
        extendedTeleFrame.grid(row=28,column=1, sticky="nsew")
        extendedTeleLabel = Label(window, text="Extended Telemetry").grid(row=28, column=0, sticky="W")
        extendedTeleYes = Radiobutton(extendedTeleFrame, text="On", variable=self.extendedTele, value=1).grid(row=0,column=0)
        extendedTeleNo = Radiobutton(extendedTeleFrame, text="Off", variable=self.extendedTele, value=2).grid(row=0,column=1)

        TLEPathLabel = Label(window)
        TLEPathLabel["text"] = "TLE Path"
        TLEPathLabel.grid(row=29, column=0,sticky="W")
        TLEPath = Entry(window, textvariable=self.path,width=10)
        TLEPath.grid(row=29,column=1,sticky="W")
        self.path.trace("w",self.entryCallback) #attaches the entry box to a callback method so that a variable is updated whenever the entry box is edited

    def getTLEPath(self): #one of many getter methods that allow other classes to access menu variables
        return self.TLEPath

    def getWritePath(self):
        return self.writePathVar

    def entryCallback(self,*args): #this method is automatically called when a user edits an entry box
        self.TLEPath = self.path.get() #as the entry box content is stored in a StringVar() we need to call get() on that
        self.writePathVar = self.wPath.get()
        
    def close_window(self,window):
        window.withdraw() #closes the preferences window
        
    def CurSelet(self,evt): #event handler called when a user changes the selection in the listbox
        global port_selection
        port_selection = self.listbox.get(self.listbox.curselection()) #get what the user has selected and store it in port_selection

    def get_port_selection(self): #allows other classes to see which port has been selected
        return port_selection
    
    def set_port_selection(self,selection): #allows other classes to change which port has been selected
        port_selection = selection

    def baud_selection(self,selection):
        self.baudSelection.set(selection) #stores the users selection in the optionmenu StringVar() so when the preferences window is reopened the last choice will still be there
        self.baud=selection #sets the user selection to a variable that isn't a StringVar() for use in the rest of the system

    def get_baud_selection(self): #allows other parts of the system to see which baudrate value has been selected
        return self.baud

    def parity_selection(self,selection):
        self.paritySelection.set(selection)
        if selection=='None': #in this case if statements are required as the options in the optionmenu don't directly correspond with exactly what should be sent to the radio
            self.par=serial.PARITY_NONE
        elif selection=='Even':
            self.par=serial.PARITY_EVEN
        elif selection=='Odd':
            self.par=serial.PARITY_ODD
        elif selection=='Mark':
            self.par=serial.PARITY_MARK
        elif selection=='Space':
            self.par=serial.PARITY_SPACE

    def get_parity_selection(self):
        return self.par

    def databits_selection(self,selection):
        self.databitsSelection.set(selection)
        if selection=='5':
            self.data=serial.FIVEBITS
        elif selection=='6':
            self.data=serial.SIXBITS
        elif selection=='7':
            self.data=serial.SEVENBITS
        elif selection=='8':
            self.data=serial.EIGHTBITS

    def get_databits_selection(self):
        return self.data

    def stopbits_selection(self,selection):
        self.stopbitsSelection.set(selection)
        if selection=='1':
            self.stop=serial.STOPBITS_ONE
        elif selection=='1.5':
            self.stop=serial.STOPBITS_ONE_POINT_FIVE
        elif selection=='2':
            self.stop=serial.STOPBITS_TWO

    def get_stopbits_selection(self):
        return self.stop

    def HFC_selection(self,selection):
        self.HFCSelection.set(selection)
        self.HFC = selection

    def get_HFC_selection(self):
        return self.HFC

    def getWriteSelection(self):
        if self.write.get()==1:
            return True
        else:
            return False

    def getExtendedSelection(self):
        if self.extendedTele.get()==1:
            return True
        else:
            return False

    
class setup(Frame): #this class deals with showing both radio and satellite telemetry, sending commands to the radio and fetching new telemetry
    
    def __init__(self,master,menuClass,stamps,radio):
    
        self.hex_values=0
        self.root = master
        self.radio = radio
        self.menuClass = menuClass #this ensures the same instance of the menu class is used in this class
        self.showStamps = stamps #again, we want the same instance of showStamps to be used
        self.byte_value = 'Battery Voltage' #default user selection value
        self.satellitePacket = []
        self.stamplist=[] #list of created stamps which will be passed into show stamps
        self.selectedBytes = [] #list contains the elements that the user has selected
        self.satelliteBytes = []
        self.labellist = [] #list contains all the labels currently displayed on the grid
        self.deletebuttonlist = [] #list contains all the delete buttons currently displayed on the grid
        Frame.__init__(self, master)
        self.configure(height=master.winfo_screenheight(), width=master.winfo_screenwidth()) #size of the setup frame
        self.grid_propagate(0) #force the size of the frame
        self.grid() #.grid() is used throughout the program as opposed to .pad()
        self.create_widgets() # calls the create_widgets method
 		
    

    def add_whitespace(self, string, length): # function which returns a string with spaces in it when given the input string and after how many characters there should be a space, as parameters
        return ' '.join(string[i:i+length] for i in xrange(0,len(string),length))

 
    def create_widgets(self): #This method creates the widgets that are always displayed

         
        self.telemetryTextbox = Text(self,width=self.root.winfo_screenwidth()/13,height=self.root.winfo_screenheight()/32,font=('Helvetica')) #textbox displays the latest telemetry packet
        self.telemetryTextbox.insert(INSERT, "Telemetry Received")
        self.telemetryTextbox.grid(row=6,column=0,rowspan=15,columnspan=4,sticky="W")
        scrollbar = Scrollbar(self,command=self.telemetryTextbox.yview)
        scrollbar.grid(row=6,column=4,sticky='nsew')
        self.telemetryTextbox['yscrollcommand'] = scrollbar.set
        
        required_width= self.root.winfo_screenwidth()/4.615
        required_height= self.root.winfo_screenheight()/3.6
        """
        img = Image.open('C:\Users\Alex\GUI\logo.gif')
        img = img.resize((int(round(required_width)),int(round(required_height))),Image.ANTIALIAS)
        """
        img = PhotoImage(file='/Users/gregstewart96/Documents/LaTex/Images/Alba.gif')
        
        img = img.zoom(3)
        img = img.subsample(10)
        logo = Label(self,image=img)
        logo.image = img
        logo.grid(row=0,column=0,rowspan=6)
        
        buttonFrame1 = Frame(self)
        buttonFrame1.grid(sticky="W",row=0,column=1)
        portLabel=Label(buttonFrame1,text="Ports")
        portLabel.grid(row=0,sticky="W")        
        self.openPort = Button(buttonFrame1, text="Open Port", command=self.openPort)
        self.openPort.grid(row=1)
        
        self.closePort = Button(self, text="Close Port", command=self.closePort)
        self.closePort.grid(sticky="W",row=1,column=1)
        self.closePort['state'] = 'disabled'
        
        self.startButton = Button(self) #button to begin reading packets
        self.startButton["text"] = "Start Listening"
        self.startButton["command"] = self.fetchTelemetry #self.fetchTelemetry is called upon the button being clicked
        self.startButton.grid(sticky="W",row=2,column=1)
        
        self.endButton=Button(self,text='End Listening',command=self.endListening,state=DISABLED)
        self.endButton.grid(sticky="W",row=3,column=1)
        
        testFrame=Frame(self)
        testFrame.grid(sticky="W",row=0,column=3)
        testLabel=Label(testFrame,text="Test Buttons")
        testLabel.grid(row=0,sticky="W")
        self.send_button = Button(testFrame) # creates the send hello world button
        self.send_button["text"] = "Send Hello World" #text on the button
        self.send_button["command"] = self.send_command # when clicked, the send_command method is called
        self.send_button.grid(sticky="W",row=1)
        
        self.send_t_command_button = Button(self) # send :T command
        self.send_t_command_button["text"] = "Send :T Command"
        self.send_t_command_button["command"] = self.send_t_command
        self.send_t_command_button.grid(sticky="W",row=5,column=2)
        
        commandFrame=Frame(self)
        commandFrame.grid(sticky="W",row=0,column=2)
        commandLabel=Label(commandFrame,text="Send Commands")
        commandLabel.grid(row=0,sticky="W")
        self.get_housekeeping_button = Button(commandFrame) # send housekeeping request
        self.get_housekeeping_button["text"] = "Get GS Housekeeping Data"
        self.get_housekeeping_button["command"] = self.send_housekeeping_command
        self.get_housekeeping_button.grid(sticky="W",row=1)
        
        sat_housekeeping_button = Button(self,text="Get Satellite Housekeeping Data")
        sat_housekeeping_button.grid(sticky="W",row=1,column=2)
        
        echo_button = Button(self,text="Send Echo Command")
        echo_button.grid(sticky="W",row=2,column=2)
        
        id_button = Button(self,text="Send ID Command")
        id_button.grid(sticky="W",row=3,column=2)
        
        r_button = Button(self,text="Send :S Command",command=self.send_s_command)
        r_button.grid(sticky="W",row=4,column=2)

        self.timestamps_button=Button(self, text="View Timestamps", command=lambda: self.showStamps.showWindow()) #when button pressed, calls the showWindow method inside showStamps passing in the stampList
        self.timestamps_button.grid(row=1, column=3,sticky="W")
        
        self.auto_on=Button(self, text="Satellite Track On",command=self.trackOn)
        self.auto_on.grid(row=2,column=3,sticky="W")
        
        self.auto_off=Button(self, text="Satellite Track Off",command=self.trackOff)
        self.auto_off['state'] = 'disabled'
        self.auto_off.grid(row=2,column=4,sticky="W")
        
        
        self.label1 = Label(self) #this label will display the hex value
        self.label1.grid(sticky="W", row=4, columnspan=10) # as it is long it has to have a columnspan so that it won't make the other grids unnecessarily big
        
        optionsFrame=Frame(self)
        optionsFrame.grid(row=0,column=5, sticky="W")
        optionsLabel=Label(optionsFrame,text="View Byte")
        optionsLabel.grid(row=0,sticky="W")
        self.options = ['Radio Telemetry','Temperature','Supply Voltage','MCU Voltage','Power Amplifier','Phase of Transmission Procedure','Phase of Receive Initialization','Phase of Receive Procedure','RSSI (dBm)','RSSI (Watts)', 'Carriage Return', 'Line Feed',
                   'Satellite Telemetry','Battery Voltage','No of Resets','OBC T1','OBC T2','EPS T1','Solar T1','Solar T2','Solar T3','Solar T4','Solar T5','Solar T6','Solar T7','Solar T8','RSSI (Sat)','3v3 OBC Current','3v3 BRO Current','3v6 Payload Current','3v3 GEO Current',
                   '5V GEO Current','3v3 OBC Voltage','3v3 BRO Voltage','3v6 Payload Voltage','3v3 GEO Voltage','5V GEO Voltage','Extended Telemetry','Gyro X','Gyro Y','Gyro Z','Accel X','Accel Z','Mag X','Mag Y','Mag Z','PA Enabled/Disable','Sband Enable/Disable','OBC Resets',
                   'RadioBro Resets','EPS Resets','Internal OBC I2C Errors','OBC-EPS I2C Errors'] #the byte options in the drop down menu
        selection = StringVar() #Contains the value the user selects 
        selection.set('Battery Voltage') #default drop down menu value
        self.info_dropdown = OptionMenu(optionsFrame, selection, *self.options, command=self.user_selection) #user selection is passed to the user_selection method
        self.info_dropdown['menu'].entryconfigure(0, state = "disabled") #disable the labels in the optionmenu
        self.info_dropdown['menu'].entryconfigure(12, state = "disabled")
        self.info_dropdown['menu'].entryconfigure(37, state = "disabled")
        self.info_dropdown.grid(row=1,sticky="ew",column=0)
        
        self.add_button = Button(optionsFrame, text = "Add", command = lambda: self.updateBytes(True, self.byte_value)) #when the button is clicked the radio will get the updated hex value and find the bits of it the user wants
        self.add_button.grid(sticky="W",row=1,column=1)

        self.addall_button = Button(self, text="Add All Satellite Telemetry", command = lambda: self.add_all_satellite(self.options)) #when pressed, calls the add_all method, passing in the list of available options(MCU, RSSI etc)
        #self.addall_button.grid(sticky="W", row=4, column=2)
    
    def send_s_command(self):
        self.radio.send(":S\r\n")
        
    def trackOn(self):
        self.track_flag = True
        self.auto_on['state'] = 'disabled'
        self.auto_off['state'] = 'normal'
        
    def trackOff(self):
        self.track_flag = False
        self.auto_on['state'] = 'normal'
        self.auto_off['state'] = 'disabled'
    
    def openPort(self):
        if self.radio.openPort(self.menuClass.get_port_selection(), self.menuClass.get_baud_selection(), self.menuClass.get_parity_selection(), self.menuClass.get_databits_selection(), self.menuClass.get_stopbits_selection(), self.menuClass.get_HFC_selection()) == True:
            self.openPort['state'] = 'disabled'
            self.closePort['state'] = 'normal'
            
    def closePort(self):
        if self.radio.closePort() == True:
            self.closePort['state'] = 'disabled'
            self.openPort['state'] = 'normal'
    
    
    def user_selection(self,byte): #method is called when an optionmenu item is selected
        self.byte_value = byte #saves user byte selection to a variable
        self.updateBytes(False, byte) #calls the housekeeping method but passes in a False, as we don't want the selection to be processed until the button is pressed

    def add_all_satellite(self,options): #this method adds all possible byte options to the list of added items
        for i,items in enumerate(self.options): #loop through the byte options in the optionmenu
            if i>12 and items!='Extended Telemetry': #skip the first 12 (as they are radio items) and greyed out items in the optionmenu
                if i>36 and self.menuClass.getExtendedSelection()==False: break #break if we don't want to add extended telemetry
                self.selectedBytes.append(items) #add the bytes to the selectedBytes list
        self.updateBytes(True,None) #calls housekeeping method but passed in null as the byte value as we don't want to add any more bytes

 
    def send_command(self): #creates a new instance of the radio class and sends helloworld to it
        self.radio.send(":helloworld\r\n")
        self.label1["text"] = "SENT"
         
    def send_t_command(self): #creates a new instance of the radio class and sends :T to it 
        #self.radio.send(":T\r\n")
        print('T command sent')
        self.label1["text"] = "SENT"
         
    def send_housekeeping_command(self):
        print("about to call updateBytes")
        self.updateBytes(True,"Temperature") #make call of updateBytes with "Temperature" - any housekeeping element can be used, so just choose Temperature.
        print("updateBytes call has returned")
         
    def updates(self,queue):
        while True:
            print('GSI Here')
            name = queue.get()
            endTime = queue.get()
            print('name',name)
            print('endTime',endTime)
        if name=='XW-2A':
            self.send_t_command()
    
    def fetchTelemetry(self): #this methods checks to see if the interface has all the packets the have been created on the satellite. If some are missing, fetch them.    
        self.endListeningFlag=False
        self.startButton['state']='disabled'
        self.endButton['state']='normal'
        thread.start_new_thread(self.readThread,())
      
    
    def endListening(self): #change the flag changed by the read thread so it ends after the next read
        self.endListeningFlag=True
        self.startButton['state']='normal'
        self.endButton['state']='disabled'
            
    def readThread(self):
        hex_values=[]
        packet_count = 0
        while self.endListeningFlag==False:
            gx=[]
            gy=[]
            gz=[]
           
            hex_string = self.radio.readBytes(1) #read one byte to check preamble
            print(hex_string)
            
            if hex_string=='0d' or hex_string =='0a': #if the first byte if a carriage return, skip to the next iteration of loop
                continue
            
            elif hex_string=='53': #preamble S
                hex_string_2 = self.radio.readBytes(3) # read remaining bytes
                hex_string = "".join([hex_string,hex_string_2]) #join first byte with remaining bytes
                hex_values.append(hex_string) #add this to the array for it to be displayed
                
            elif hex_string=='54': #preamble T
                hex_string_2 = self.radio.readBytes(48) #read remaining bytes
                hex_string = "".join([hex_string,hex_string_2])
                print(hex_string)
                hex_values.append(hex_string) #this line stores the hex values (in ASCII) received to hex_values
                csv_array = [hex_string[i:i + 2] for i in range(0, len(hex_string), 2)]
                self.setLatestSatellitePacket(csv_array)
                """
                tempArray=[] # temp array for concatenating bytes
                csv_array=[]
                for i in range(0, len(hex_string), 2):
                    if i>=52 and i<=74: #for gx,gy,gx
                        tempArray.append(hex_string[i:i+2])
                        if len(tempArray)==12:
                            for j in range(0,len(tempArray), 4):
                                joiner = "".join(tempArray[j:j+4])
                                print(joiner)
                                csv_array.append(struct.unpack('!f',joiner.decode('hex'))[0])
                            tempArray=[]
                    
                    elif i>=2 and i<=6: # for seconds,minutes,hours
                        csv_array.append(int(hex_string[i:i+2],16))
                    else:
                        csv_array.append(hex_string[i:i+2])
                """            
                time_seconds=csv_array[1]
                time_seconds=int(time_seconds,16)
                csv_array[1] = time_seconds
                print("SECONDS %s"%(time_seconds))
                time_minutes=csv_array[2]
                time_minutes=int(time_minutes,16)
                csv_array[2] = time_minutes
                print("MINUTES %s" % (time_minutes))
                time_hours=csv_array[3]
                time_hours=int(time_hours,16)
                csv_array[3] = time_hours
                print("HOURS %s"%(time_hours))
                
                temp1 = csv_array[4]
                temp1 = bin(int(temp1, 16))[2:].zfill(8)
                temp1 = self.twos_comp(int(temp1,2), len(temp1))
                csv_array[4] = temp1
                
                temp2 = csv_array[5]
                temp2 = bin(int(temp2, 16))[2:].zfill(8)
                temp2 = self.twos_comp(int(temp2,2), len(temp2))
                csv_array[5] = temp2
                
                
                #freeze_detect=hex_string[10:12]
                #freeze_detect=int(freeze_detect,16)
                #print("FREEZE DETECT %s" % (freeze_detect))
             
                gx.append(csv_array[29])
                gx.append(csv_array[28])
                gx.append(csv_array[27])
                gx.append(csv_array[26])
                gxTempString="".join(gx)
                print(gxTempString)
                gyroX=struct.unpack('!f',gxTempString.decode('hex'))[0]
                csv_array[26:29] = ''
                csv_array[26] = gyroX
              
                gy.append(csv_array[30])
                gy.append(csv_array[29])
                gy.append(csv_array[28])
                gy.append(csv_array[27])
                gyTempString="".join(gy)           
                gyroY=struct.unpack('!f',gyTempString.decode('hex'))[0]
                csv_array[27:30] = ''
                csv_array[27] = gyroY
                
                gz.append(csv_array[31])
                gz.append(csv_array[30])
                gz.append(csv_array[29])
                gz.append(csv_array[28])
                gzTempString="".join(gz)
                gyroZ=struct.unpack('!f',gzTempString.decode('hex'))[0]
                csv_array[28:31] = ''
                csv_array[28] = gyroZ 
                
                csvFile=open('C:\Users\Alex\GUI\guiOutput.csv','ab')
                with csvFile:
                    writer = csv.writer(csvFile)
                    writer.writerow(csv_array)
                
                print("GYRO X %s" % (gyroX))
                print("GYRO Y %s" % (gyroY))
                print("GYRO Z %s" % (gyroZ))
                
                label = Label(self)
                packet_count+=1
                #print("NUMBER OF PACKETS %s" % (packet_count))
                print
                label["text"] = "%s packets received" %(packet_count) #display the number of packets received based on the length of the array
                #label.grid(row=21,column=2,columnspan=5,sticky="W")
                
                stamp = self.create_stamp(hex_string, None) #create a timestamp for each item
                self.showStamps.addToList(stamp) #add it to the list of stamps
                if self.menuClass.getWriteSelection() == True: #write the stamp to a file if we require
                    self.showStamps.writeFile(stamp)
                    
                self.updateBytes(True,None) #display the changes
            
            elif hex_string=='42': 
                hex_string_2 = self.radio.readBytes(7) #check for beacon
                hex_string = "".join([hex_string,hex_string_2])
                if '426561636f6e' in hex_string:
                    hex_values.append('BEACON')
                    print('BEACON') 
                else: #assume housekeeping packet
                    hex_string_2 = self.radio.readBytes(9)
                    hex_string = "".join([hex_string,hex_string_2])
                    self.hex_values=hex_string
            
            for item in hex_values: #add items in the array to the textbox
                self.telemetryTextbox.insert(END, '\n' + item)
                self.telemetryTextbox.see(END) #scroll to the bottom of the textbox
            hex_values=[]
        

    def setLatestSatellitePacket(self,packet): #getter for the classes which graph the data
        self.satellitePacket = packet
        

    def updateBytes(self,button_pressed, byte): #this method fetches the hex string and finds out the information that the user wants. button_pressed is there to avoid the method proceeding if it has been called just by an optionmenu selection
        radioItem = False #variable to check if the packet is a radio packet or not
        if button_pressed==True: #only proceed if the housekeeping butto has been pressed
            for i,items in enumerate(self.options): #loop radio options to check if the item is a radio item
                #print("check for radio options")
                if i>11: break #only loop through radio elements
                print(items)
                if byte==items or self.in_list(byte,self.selectedBytes):
                    radioItem = True
                    
            if radioItem==False:
                for i,item in enumerate(self.options):
                    if i<13: continue #if there is no extended telemetry don't continue to avoid index out of bounds
                    if i>=37: #take into account disabled labels
                        i-=1 #to take into account the disabled label
                    j = i-12
                    if self.satellitePacket==[]:
                        if item==byte and self.in_list(item,self.satelliteBytes)==False:
                            self.satelliteBytes.append("%s"%(item))
                            break
                    elif item==byte or self.in_list(item,self.satelliteBytes):
                        if self.in_list(item,self.satelliteBytes):
                            self.empty_elements("%s"%(item,self.satelliteBytes)) 
                        self.satelliteBytes.append("%s - %s"%(item,self.satellitePacket[j]))

            else: #if it is a radio item
                try:
                    print("about to send radioCommand")
                    self.radio.send("h\r\n") #sends the h command, passes in False as we don't want to close the connection
                    time.sleep(3) #wait before reading to give the radio time
                    self.hex_values = self.add_whitespace(self.hex_values,2)       #adds whitespace every 2 characters

                except serial.SerialException:
                    print("exception")
                    self.hex_values = []          

                if len(self.hex_values)==50: # was 50: #  little bit of error checking as we know what length the returned hex string should be
                    #self.label1["text"] = hex_values #displays hex values on the GUI
                    pass
                else:
                    print(self.hex_values)
                    self.label1["text"] = "Error fetching housekeeping packet"

           
                if byte=='Temperature' or self.in_list('Temperature',self.selectedBytes): #if the user has chosen to add temperature, or temperature has already been added and we just want to refresh it
                    self.empty_elements('Temperature',self.selectedBytes) #remove the old temperature data from the list
                    Temp = self.hex_values[6:11] #parse the hex string to get the value we want
                    Temp = Temp.replace(" ","") #delete the space between the two hex values
                    Temp = int(Temp,16) #converts hex to decimal
                    Temp = Temp/100
                    Temp_C = Temp - 273.15
                    self.selectedBytes.append("Temperature - %s Kelvin (%s Celsius)" % (Temp, Temp_C)) #adds the finalised string to the list of added data
                
                if byte=='Supply Voltage' or self.in_list('Supply Voltage',self.selectedBytes):
                    self.empty_elements('Supply Voltage',self.selectedBytes)
                    SV = self.hex_values[12:17]
                    SV = SV.replace(" ","")
                    SV = int(SV,16)
                    self.selectedBytes.append("Supply Voltage - %s mV" % (SV))
    
                if byte=='MCU Voltage' or self.in_list('MCU Voltage',self.selectedBytes):
                    self.empty_elements('MCU Voltage',self.selectedBytes)
                    MCU = self.hex_values[18:23]
                    MCU = MCU.replace(" ","")
                    MCU = int(MCU,16)
                    self.selectedBytes.append("MCU Voltage - %s mV" % (MCU))
    
                if byte=='Power Amplifier' or self.in_list('Power Amplifier',self.selectedBytes):
                    self.empty_elements('Power Amplifier',self.satelliteBytes)
                    PA = self.hex_values[24:29]
                    PA = PA.replace(" ","")
                    PA = int(PA,16)
                    self.selectedBytes.append("Power Amplifier - %s mV" % (PA))
    
                if byte == 'Phase of Transmission Procedure' or self.in_list('Phase of Transmission Procedure',self.selectedBytes): #only proceed if it is the byte the user has just selected or has been previously selected
                    self.empty_elements('Phase of Transmission Procedure',self.selectedBytes) #every time the housekeeping button is pressed we refresh the values so empty the list of bytes first
                    PTP = self.hex_values[33:35] #parses the hex string to get the required hex value. In this case it is byte 11
                    if PTP=='00':
                        self.selectedBytes.append("Phase of Transmission Procedure - Stand by") #if this is the correct result, add it to the list
                    if PTP=='01':
                        self.selectedBytes.append("Phase of Transmission Procedure - Radio being configured, begin key-up")
                    if PTP=='02':
                        self.selectedBytes.append("Phase of Transmission Procedure - Preparing data")
                    if PTP=='03':
                        self.selectedBytes.append("Phase of Transmission Procedure - Data is ready to be sent")
                    if PTP=='04':
                        self.selectedBytes.append("Phase of Transmission Procedure - Sending data")
                    if PTP=='05':
                        self.selectedBytes.append("Phase of Transmission Procedure - Clearing old packet from buffer")
                    PTP = int(PTP, 16) #convert to decimal to check if greater than 0xCA (200)
                    if PTP>=200:
                        self.selectedBytes.append("Phase of Transmission Procedure - Data whitening is active")
    
                if byte=='Phase of Receive Initialization' or self.in_list('Phase of Receive Initialization',self.selectedBytes):
                    self.empty_elements('Phase of Receive Initialization',self.selectedBytes)
                    PRI = self.hex_values[36:38]
                    if PRI=='00':
                        self.selectedBytes.append("Phase of Receive Initialization - Default set to RX disabled")
                    if PRI=='01':
                        self.selectedBytes.append("Phase of Receive Initialization - Default set to RX enabled")
                        
                if byte=='Phase of Receive Procedure' or self.in_list('Phase of Receive Procedure',self.selectedBytes):
                    self.empty_elements('Phase of Receive Procedure',self.selectedBytes)
                    PRP = self.hex_values[39:41]
                    if PRP=='00':
                        self.selectedBytes.append("Phase of Receive Procedure - Off")
                    if PRP=='01':
                        self.selectedBytes.append("Phase of Receive Procedure - No data clocking yet")
                    if PRP=='02':
                        self.selectedBytes.append("Phase of Receive Procedure - On and waiting for preamble")
                    if PRP=='03':
                        self.selectedBytes.append("Phase Receive Procedure - On, preamble discovered, waiting on sync word")
                    if PRP=='04':
                        self.selectedBytes.append("Phase of Receive Procedure - Data being collected, waiting on end flag")
                    if PRP=='05':
                        self.selectedBytes.append("Phase of Receive Procedure - Processing Data")
                
                
                if byte == 'RSSI (dBm)' or self.in_list('dBm',self.selectedBytes):
                    self.empty_elements('dBm',self.selectedBytes)
                    RSSI_value = self.hex_values[42:44]
                    RSSI_value = bin(int(RSSI_value, 16))[2:].zfill(8) #as it is signed we need to convert to binary first
                    RSSI_value = self.twos_comp(int(RSSI_value,2), len(RSSI_value)) #then convert signed binary to int
                    self.selectedBytes.append("RSSI value is %s dBm" % (RSSI_value))
                
    
                if byte=='RSSI (Watts)' or self.in_list('Watts',self.selectedBytes):
                    self.empty_elements('Watts',self.selectedBytes)
                    RSSI_value_power = self.hex_values[42:44]
                    RSSI_value_power = bin(int(RSSI_value_power, 16))[2:].zfill(8)
                    RSSI_value_power = self.twos_comp(int(RSSI_value_power,2), len(RSSI_value_power))
                    RSSI_value_power = 10**((RSSI_value_power-30)/10) #we need to do a final calculation this time
                    self.selectedBytes.append("RSSI value is %s Watts" % (RSSI_value_power))
    
                if byte=='Carriage Return' or self.in_list('Carriage Return',self.selectedBytes):
                    self.empty_elements('Carriage Return',self.selectedBytes)
                    CR = self.hex_values[45:47]
                    if CR=='0d':
                        self.selectedBytes.append("Carriage Return - True")
                    else:
                        self.selectedBytes.append("Carriage Return - False")
    
                if byte=='Line Feed' or self.in_list('Line Feed',self.selectedBytes):
                    self.empty_elements('Line Feed',self.selectedBytes)
                    LF = self.hex_values[48:50]
                    if LF=='0a':
                        self.selectedBytes.append("Line Feed - True")
                    else:
                        self.selectedBytes.append("Line Feed - False")
                      
                
                for item in self.selectedBytes: #create a stamp for each item in the list of added data
                    stamp = self.create_stamp(self.hex_values,item)  
                    self.showStamps.addToList(stamp) #add the stamp to the show stamp array
                    if self.menuClass.getWriteSelection() == True:
                        self.showStamps.writeFile(stamp) #write to file


            self.refresh_list() #call the refresh_list method
            

    def create_stamp(self, hex_values,item): #creates an instance of the createStamp class
        if item==None:
            date_time = 'Telemetry packet collected at {:%H:%M:%S on %d-%m-%Y}'.format(DT.datetime.now()) #defines what teh data and time should look like
        else:
            date_time = 'Radio housekeeping packet collected at {:%H:%M:%S on %d-%m-%Y}'.format(DT.datetime.now()) #defines what teh data and time should look like
        stamp = createStamp(date_time, hex_values, item) #creates a stamp object
        return stamp #returns the stamp object
                
    def print_list(self):
        combinedList=[]
        printFrame=(self)
        printFrame.grid(row=2,column=5,sticky="W")
        Column = 5
        Row = 2     
        for item in self.selectedBytes:
            combinedList.append(item)
        for item in self.satelliteBytes:
            combinedList.append(item)
        for selections in combinedList: #loop through the list of selected bytes, need an iterator to use as the row value
            self.label = Label(self)
            self.label["text"] = selections #create new label for each item in the list of bytes
            self.label.grid(row = Row,  column=Column, sticky="W")
            self.labellist.append(self.label) #add this new label to the list of labels
            self.delete_button = Button(self,text="Delete", command=lambda j=selections : self.delete_element(j)) #create new delete button for each item in the list of bytes. When the button is pressed delete_element is called
            self.delete_button.grid(row = Row, column=Column+1, sticky="W")
            self.deletebuttonlist.append(self.delete_button) #add this new button to the list of buttons
            Row+=1
            
            
        

    def delete_element(self,element):
        if element in self.selectedBytes:
            self.selectedBytes.remove(element) #remove the element from the list
        elif element in self.satelliteBytes:
            self.satelliteBytes.remove(element) #remove the element from the list
        self.refresh_list() #refresh the list again

    def in_list(self, string,array): #checks to see if a particular byte has already been selected by the user so we know if it should be added when the list is refreshed or not
        if b_any(string in x for x in array):
            return True
        else:
            return False
        

    def refresh_list(self): #clears everything
        for selections in self.labellist:
            selections.destroy() #destroy every label previously created
        for selections in self.deletebuttonlist:
            selections.destroy() #destroy every button previously created
        self.print_list() #call the method that creates new labels and buttons

    def empty_elements(self,string,array): #This method matches a string with a smaller substring. Eg. 'dBm' finds 'RSSI (dBm)'
        keywordFilter = set([string])
        self.selectedBytes = [str for str in array if not any(i in str for i in keywordFilter)] #new list doesn't contain any strings that contain the keyword
    
    def twos_comp(self,val, bits): #twos complement conversion
        if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)        # compute negative value
        return val # return positive value as is



     
        
    	 

class temperature(Frame): #class to display the temperature telemetry

    def __init__(self,temperatureFrame,setup):
        Frame.__init__(self,temperatureFrame)
        self.setup = setup #the setup class is passed in to allow access to the latest packet fetched by it 
        self.configure(height=root.winfo_screenheight(), width=root.winfo_screenwidth())
        self.grid_propagate(0) 
        self.createBar('OBC/EPS',('OBC 1','OBC 2','EPS 1'),0,5,7)
        self.createBar('Solar Panels 1-4',('Solar 1','Solar 2','Solar 3','Solar 4'),1,8,11)
        self.createBar('Solar Panels 5-8',('Solar 5','Solar 6','Solar 7','Solar 8'),2,12,15)

        self.createGraph(0,5,7)
        self.createGraph(1,8,11)
        self.createGraph(2,12,15)
        self.grid()
      
    def createBar(self,title,yLabel,column,start,end): #creates a bar graph. #start and end are the byte numbers of the packet
        f = Figure(figsize=(5.66,3), dpi=75) #size of the graph
        ax = f.add_subplot(111) #the subplot is where the data is added
        performance =  [0] * len(yLabel) #initially the plot will be empty
        y_pos = np.arange(len(yLabel))
        ax.barh(y_pos, performance, align='center',
        color='green', ecolor='black')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(yLabel)
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_xlabel('Temperature (Celsius)')
        ax.set_title(title)
        canvas = FigureCanvasTkAgg(f, self) #create a canvas for the graph to be placed on to
        canvas.show()
        canvas.get_tk_widget().grid(row=0,column=column) #the column is passed in as a parameter        
        self.updateBar(f,ax,canvas,title,yLabel,[],start,end,column) #pass in most of the parameters to updateBar

    def updateBar(self,f,ax,canvas,title,yLabel,latestPacket,start,end,column): #update the bar graph
        packet = self.fetchPacket(latestPacket) #get the latest packet which we want to show
        if packet != []:
            plotTemperatures = []
            temperatures = packet[-1] #get the latest of the fetched temperatures
            for i,item in enumerate(temperatures): #extract the required temperatures
                if i>end: break #get the bytes between start and end
                if i>=start:
                    plotTemperatures.append(item[:-1]) #only want the last packet in the array of packets
            ax.clear() #clear the old plot
            y_pos = np.arange(len(yLabel))
            plot = ax.barh(y_pos,plotTemperatures, align='center', color='green', ecolor='black')#plot the temperatures
            ax.set_yticks(y_pos)
            ax.set_yticklabels(yLabel)
            ax.set_xlabel('Temperature (Celsius)')
            ax.set_title(title)
            canvas.get_tk_widget().grid_forget() #clear the old canvas from the grid
            canvas = FigureCanvasTkAgg(f, self) #create a new one
            canvas.show()
            canvas.get_tk_widget().grid(row=0,column=column)
            self.autolabel(plot,ax) #create a legend
        else:
            packet = latestPacket
        self.startTimer2(f,ax,canvas,title,yLabel,packet,start,end,column)
        

    def fetchPacket(self,packet): #get the latest packet from the setup class
        if packet!=self.setup.getLatestPacket():
            packet = self.setup.getLatestPacket()
            return packet 
        else:
            return []
    
    def startTimer(self,f,a,column,canvas,packet,plottedTemperatures,start,end): #each graph should try to update every second
        thread = threading.Timer(1,self.updateGraph,args=(f,a,column,canvas,packet,plottedTemperatures,start,end))
        thread.start()

    def startTimer2(self,f,ax,canvas,title,yLabel,latestPacket,start,end,column): #same for bar graph but with different parameters
        thread = threading.Timer(1,self.updateBar,args=(f,ax,canvas,title,yLabel,latestPacket,start,end,column))
        thread.start()

    def createGraph(self,column,start,end): #create line graph
        f = Figure(figsize=(7,10), dpi=50)
        a = f.add_subplot(111)
        xArray = []
        plotTemperatures = [[] for _ in range((end-start)+1)] #an array for each plot on the grapuh
        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().grid()
        self.updateGraph(f,a,column,canvas,[],plotTemperatures,start,end)

    
    def updateGraph(self,f,a,column,canvas,latestPacket,plotTemperatures,start,end):
        packet = self.fetchPacket(latestPacket)
        if packet != []:
            j = start
            for array in packet: #as more than one telemetry packet could be received, loop through each of them 
                for i,plot in enumerate(plotTemperatures): #add to each list that will be plotted
                    plotTemperatures[i].append((array[j])[:-1])
                    j+=1
                j = start
            xArray = []
            for i,item in enumerate(plotTemperatures[0]): #check how many x elements there should be
                i+=1
                xArray.append(i)
            a.clear() #
            for i,yArray in enumerate(plotTemperatures):
                if column==2:
                    a.plot(xArray,yArray,label="%s"%(i+5)) #plot, add 5 to the label as this is temperatures 5 -8
                else:
                    a.plot(xArray,yArray,label="%s"%(i+1))
                a.legend(loc='upper right')
            a.set_xlabel('Data Points')
            a.set_ylabel('Temperature (C)')
            canvas.get_tk_widget().grid_forget()
            canvas = FigureCanvasTkAgg(f, self)
            canvas.show()
            canvas.get_tk_widget().grid(row=1,column=column)
    
        else:
            packet=latestPacket #if there are no new packets, set packet back to the latest one we have
        self.startTimer(f,a,column,canvas,packet,plotTemperatures,start,end)

    #place the actual value next to the bar
    def autolabel(self,rects,ax):
        for rect in rects:
            width  = rect.get_width()
            y = rect.get_y() + 0.55
            if width<0:
                x = width - 3
            else:
                x = width + 3
            ax.text(x, y,"%d"%(int(width)),ha='center', va='bottom')

class voltage(Frame): #class to plot voltages
    def __init__(self,voltageFrame,setup):
        Frame.__init__(self,voltageFrame)
        self.configure(height=root.winfo_screenheight(), width=root.winfo_screenwidth())
        self.grid_propagate(0) 
        self.setup = setup #instance of the setup class
        self.createBar('Battery Voltage','Volts',3,3,0,0,5,0)
        self.createBar('3v3 OBC Voltage Measurement','Volts',22,22,0,1,5,0)
        self.createBar('3v3 BRO Voltage Measurement','Volts',23,23,0,2,5,0)
        self.createBar('3v6 Payload Voltage Measurement','Volts',24,24,1,0,5,0)
        self.createBar('3v3 GEO Voltage Measurement','Volts',25,25,1,1,5,0)
        self.createBar('5v GEO Voltage Measurement','Volts',26,26,1,2,5,0)
        self.createBar('3v3 OBC Current Measurement','Current',17,17,2,0,2,0)
        self.createBar('3v3 BRO Current Measurement','Current',18,18,2,1,2,0)
        self.createBar('3v6 Payload Current Measurement','Current',19,19,2,2,2,0)
        self.createBar('3v3 GEO Current Measurement','Current',20,20,3,0,2,0)
        self.createBar('5v GEO Current Measurement','Current',21,21,3,1,2,0)
        self.grid()

    #these classes create bar graphs in the same way as the temperature class. The reason for the code duplication is explained in the information sheet.
    
    def createBar(self,title,xLabel,start,end,row,column,limMax,limMin):
        f = Figure(figsize=(5.66,1.5), dpi=75)
        ax = f.add_subplot(111)
        yLabel = ['Reading']
        performance =  [0] * len(yLabel)
        y_pos = np.arange(len(yLabel))
        ax.barh(y_pos, performance, align='center',
        color='green', ecolor='black')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(yLabel)
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_xlabel(xLabel)
        ax.set_title(title)
        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().grid(row=row,column=column)
        self.updateBar(f,ax,canvas,title,xLabel,yLabel,[],start,end,row,column,limMax,limMin)

    def updateBar(self,f,ax,canvas,title,xLabel,yLabel,latestPacket,start,end,row,column,limMax,limMin):
        packet = self.fetchPacket(latestPacket)
        if packet != []:
            plotTemperatures = []
            temperatures = packet[-1] #get the latest of the fetched temperatures
            for i,item in enumerate(temperatures): #extract the required temperatures
                if i>end: break
                if i>=start:
                    plotTemperatures.append(item[:-1])
            ax.clear()
            y_pos = np.arange(len(yLabel))
            ax.barh(y_pos,plotTemperatures, align='center', color='green', ecolor='black')  
            ax.set_yticks(y_pos)
            ax.set_yticklabels(yLabel)
            ax.set_xlabel(xLabel)
            ax.set_title(title)
            ax.set_xlim(limMin,limMax)
            canvas.get_tk_widget().grid_forget()
            canvas = FigureCanvasTkAgg(f, self)
            canvas.show()
            canvas.get_tk_widget().grid(row=row,column=column)
        else:
            packet = latestPacket
        self.startTimer(f,ax,canvas,title,xLabel,yLabel,packet,start,end,row,column,limMax,limMin)

    def startTimer(self,f,ax,canvas,title,xLabel,yLabel,latestPacket,start,end,row,column,limMax,limMin):
        thread = threading.Timer(1,self.updateBar,args=(f,ax,canvas,title,xLabel,yLabel,latestPacket,start,end,row,column,limMax,limMin))
        thread.start()

    def fetchPacket(self,packet):
        if packet!=self.setup.getLatestPacket():
            packet = self.setup.getLatestPacket()
            return packet 
        else:
            return []

class createStamp(object): #this class is used to create a stamp object
    def __init__(self,date_time,hex_values,item):
        self.date_time = date_time
        self.hex_values = hex_values
        self.item = item

    @property
    def get_date_time(self): #getter for date_time
        return self.date_time

    @property
    def get_hex_values(self): #getter for hex values
        return self.hex_values
    
    @property
    def get_data(self): #getter for data
        return self.item

class showStamps: #used to display timestamps
    def __init__(self,root,menuClass):
        self.root=root
        self.writeInsertedTimeList = [] #stores the time value of the timestamp to ensure no duplicates
        self.stampList = [] #list of all timestamps
        self.menuClass = menuClass #instance of the menuclass

    
    def addToList(self,stamp):
        self.stampList.append(stamp) #add new timestamp to the list of all timestamps
    
    
    def showWindow(self):
        tempArray = []  
        window = Toplevel(self.root) #creates small window on top of existing window
        window.title("Timestamps")

        self.canvas = Canvas(window, borderwidth=0, background="#ffffff", width=(root.winfo_screenwidth() - 80), height=(root.winfo_screenheight()-500)) #creates a canvas on the new window
        self.frame = Frame(self.canvas, background="#ffffff") #adds a frame to the canvas
        self.vsb = Scrollbar(window, orient="vertical", command=self.canvas.yview) #adds a scrollbar
        self.canvas.configure(yscrollcommand=self.vsb.set) #configures the scrollbar on the canvas

        self.vsb.pack(side="right", fill="y") 
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4,4), window=self.frame, anchor="nw", tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure) #method called when the user scrolls
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel) #method called when the user uses a mousewheel
        
        insertedTimeList=[] #list stores timestamps that have been inserted so time printouts aren't duplicated
        for i,item in enumerate(self.stampList): #for each stamp in the stamplist
            if item.get_date_time not in insertedTimeList: #only want to print date, time, linebreak and hex values if the time hasn't already been accessed
                if i!=0: #insert a blank line before the date, as long as it isn't the first date
                    blankLabel=Label(self.frame,text=" ")
                    blankLabel.grid()
                timeLabel=Label(self.frame)
                timeLabel["text"] = item.get_date_time
                timeLabel.grid(sticky="W")
                insertedTimeList.append(item.get_date_time) #add to list to ensure time is not duplicated
            
            
            hexLabel=Label(self.frame)
            hexLabel["text"] = "     "+' '.join(item.get_hex_values[i:i+2] for i in range(0, len(item.get_hex_values), 2))
            hexLabel.grid(sticky="W")
        
            """
            firstLine = []
            secondLine = []
            for i,jtem in enumerate(item.get_hex_values): #split the packet up to grid on 2 different lines
                if i<27:
                    firstLine.append(jtem)
                else:
                    secondLine.append(jtem)
            hexLabel=Label(self.frame)
            hexLabel["text"] ="     "+''.join(firstLine)
            hexLabel.grid(sticky="W")
            if len(secondLine)!=0:
                hexLabel2=Label(self.frame)
                hexLabel2["text"] ="     "+', '.join(secondLine)
                hexLabel2.grid(sticky="W")
            """
            if item.get_data!=None:   
                dataLabel=Label(self.frame, text="     %s"%(item.get_data))
                dataLabel.grid(sticky="W")

      

    def onFrameConfigure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all")) #Reset the scroll region to encompass the inner frame'

    def _on_mousewheel(self, event):
        if os.name=='nt': #checks if the user is using windows or not as scrolling is set up differently
            self.canvas.yview_scroll(-1*(event.delta/120), "units")
        else:
            try:
                self.canvas.yview_scroll(-1*(event.delta), "units") #adds mousewheel functionality. For windows do: event.delta/120
            except TclError: #sometimes throws this exception. It doesn't seem to effect anything
                pass

    def writeFile(self,item): #this method adds to an existing file if it already exists or creates a new one if it doesn't
        try:
            my_path = self.menuClass.getWritePath()
            if 'timestamps.txt' not in my_path:
                my_path += '/timestamps.txt'
            with open(my_path, 'a') as file: #append to timestamps.txt
                if item.get_date_time not in self.writeInsertedTimeList: #only want to print date, time, linebreak and hex values if the time hasn't already been accessed
                    if os.path.getsize(my_path)>0: #insert a blank line before the date, as long as the file isn't empty
                        file.write("\n")
                    file.write("%s\n"%(item.get_date_time))
                    self.writeInsertedTimeList.append(item.get_date_time)
                """
                firstLine = []
                secondLine = []
                for i,jtem in enumerate(item.get_hex_values):
                    if i<26:
                        firstLine.append(jtem)
                    else:
                        secondLine.append(jtem)
                file.write("   %s\n"%(', '.join(firstLine)))
                if len(secondLine)!=0:
                  file.write("   %s\n"%(', '.join(secondLine)))
                """
                file.write("     "+' '.join(item.get_hex_values[i:i+2] for i in range(0, len(item.get_hex_values), 2))+'\n')
                if item.get_data!=None: 
                    file.write("   %s\n"%(item.get_data))
        except OSError: #if incorrect file path, do nothing
            pass
        except IOError: #if incorrect file path, do nothing
            pass
        
    
class Radio: #class used to avoid code duplication of serial reads/writes

    def __init__(self):
	    self.ser=serial.Serial()
    
    def openPort(self, port, baud, parity, databits, stopbits, dfc):
        try:
            self.ser = serial.Serial(port=port, baudrate=baud, parity=parity, bytesize=databits, stopbits=stopbits, rtscts=dfc)
            return True
        except SerialException:
            return False
        
    def closePort(self):
        self.ser.close()
        if self.ser.isOpen() == True:
            return False
        else:
            return True
        
    def send(self,command): #enter command to be sent, radio details and whether you want the connection to be closed after being sent
        print("Sent")
        #self.ser.flushInput()
        #self.ser.flushOutput()
        self.ser.write(command) #the command that is sent
        return self.ser

    def read(self):
        hex_values = self.ser.readline() #reads from the radio
        print("ADT: hex values read from serial interface")
        hex_values = hex_values.encode('hex') #converts ASCII to hex
        return hex_values
        
    def readBytes(self, number):
        print("begin read")
        hex_values = self.ser.read(number) #reads from the radio
        print("end read")
        hex_values = hex_values.encode('hex')
        return hex_values

class satelliteData(Frame):
    def __init__(self,satelliteDataFrame,menuClass):
        Frame.__init__(self,satelliteDataFrame)
        self.configure(height=root.winfo_screenheight(), width=root.winfo_screenwidth())
        self.grid_propagate(0)
        self.menuClass = menuClass
        self.setup()
        self.path = 0
        sat = 'noaa 18'
        orb = orbital.Orbital(sat)
        self.fetchData(sat,orb)
        self.grid()

    def startTimer(self,sat,orb):
        if self.menuClass.getTLEPath() != self.path: #if the settings have changed
            try:
                self.beginCalculations()
            except IOError:
                thread = threading.Timer(1,self.fetchData,args=(sat,orb)) #else, continue as before
                thread.start()
        else:
            thread = threading.Timer(1,self.fetchData,args=(sat,orb)) #else, continue as before
            thread.start()
      
    def beginCalculations(self):
        self.path = self.menuClass.getTLEPath()
        f = open("%s" % self.path,'r')
        sat = f.readline()
        line1 = f.readline()
        line2 = f.readline()
        orb = orbital.Orbital(sat,self.path,line1,line2)
        self.fetchData(sat,orb)
     

    
    def setup(self):

        labelSatellite = Label(self)
        labelSatellite["text"] = "Satellite"
        labelSatellite.grid()
        self.satellite = Label(self)
        self.satellite.grid()

        labelTime = Label(self)
        labelTime["text"] = "Time"
        labelTime.grid()
        self.timeData = Label(self)
        self.timeData.grid()

        label1 = Label(self)
        label1["text"] = "Position"
        label1.grid()
        self.positionLabel = Label(self)
        self.positionLabel.grid()

        label2 = Label(self)
        label2["text"] = "Longitude"
        label2.grid()
        self.longitude = Label(self)
        self.longitude.grid()

        label3 = Label(self)
        label3["text"] = "Latitude"
        label3.grid()
        self.latitude = Label(self)
        self.latitude.grid()

        label4 = Label(self)
        label4["text"] = "Altitude"
        label4.grid()
        self.altitude = Label(self)
        self.altitude.grid()

        label5 = Label(self)
        label5["text"] = "Azimuth and Elevation"
        label5.grid()
        self.aziEle = Label(self)
        self.aziEle.grid()

    def fetchData(self,sat,orb):
        now = datetime.utcnow()
        lon = orb.get_lonlatalt(now)   # orb.get_lon(now) # ADT temp hack
        lat = orb.get_lonlatalt(now)   # orb.get_lat(now) # ADT temp hack
        alt = orb.get_lonlatalt(now)   # orb.get_alt(now) # ADT temp hack

        
        self.satellite["text"] = sat

        
        
        self.timeData["text"] = now
        
        
        
        self.positionLabel["text"] = orb.get_position(now)
        

        
        self.longitude["text"] = lon
        

        
        self.latitude["text"] = lat
        

        
        self.altitude["text"] = alt
        

        
        self.aziEle["text"] = orb.get_observer_look(now, 12.65, 55.6167, 5)
        self.startTimer(sat,orb)





class Main(threading.Thread):
    def __init__(self,root):  
        window = Toplevel(root)
        window.title("Ground Station Interface") #title of the window
        
        
        notebook = ttk.Notebook(window,height=window.winfo_screenheight(),width=window.winfo_screenwidth()) #notebook allows multiple frame to be placed on the notebook. Place the notebook on root
        
        setupFrame = ttk.Frame(notebook) #create new frame for the radio information
        
        temperatureFrame = ttk.Frame(notebook) #frame for the temperature telemetry
        voltageFrame = ttk.Frame(notebook)
        satelliteDataFrame = ttk.Frame(notebook)
        notebook.add(setupFrame,text='Setup') #add the frame to the notebook
        notebook.add(temperatureFrame, text='Temperature')
        notebook.add(voltageFrame, text="Current/Voltage Monitoring")
        notebook.add(satelliteDataFrame, text="Satellite Data")
        s=ttk.Style()
        s.theme_use('alt') #set the theme of the notebook
        
        
        notebook.grid()


    

        menuClass = menu(window) #create instance of menu class. Pass in root to allow the class to add things to it
        radio = Radio()
        stamps = showStamps(window,menuClass) #creates instance of showStamps. This is created now as we want to use the same instance throughout the entire system
        self.Setup = setup(setupFrame,menuClass,stamps,radio) #call the setup class. Pass in the setupFrame so we can add to it, menu class instance so we can access the settings and our showStamps instance
        #Temperature = temperature(temperatureFrame,Setup) #call the temperature class passing in the temperature frame
        #Voltage = voltage(voltageFrame,Setup)
        #Data = satelliteData(satelliteDataFrame,menuClass)
    
        #window.mainloop()
        
    
    def update(self,queue):
        thread=threading.Thread(target=self.Setup.updates,args=(queue,))
        thread.start()
            
