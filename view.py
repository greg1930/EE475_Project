'''
Created on 19 Dec 2017

@author: stacstation
'''
from Tkinter import *
from datetime import datetime
from datetime import timedelta
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

#from PIL import Image
#import ImageTk


class GUI(Frame):
   
    def __init__(self,master,controller):
        Frame.__init__(self,master)
        print(master.winfo_screenwidth())
        self.configure(height=master.winfo_screenheight(),width=master.winfo_screenwidth())
        self.root=master
        self.widgetList=[]
        self.preferencesWidgetList =[]
        self.scheduleWidgetList = []
        self.tolerance=DoubleVar()
        self.urlEntry=StringVar()
        self.duration=IntVar()
        self.satelliteList={}
        self.controller = controller
        self.grid_propagate(0)
        self.grid()
       
    def addWidgets(self):
        
        menubar=Menu(self)
        filemenu=Menu(menubar, tearoff=0)
        filemenu.add_command(label="Preferences",command=self.controller.openPreferences)
        filemenu.add_command(label="Update TLE Files",command=self.controller.updateTLE)
        menubar.add_cascade(label="Ground Station Controller",menu=filemenu)
        self.root.config(menu=menubar)
          
        self.canvas = Canvas(self,width=400,height=self.root.winfo_screenheight()-50)
        self.labelFrame=LabelFrame(self.canvas,text="Satellites")
        self.canvas.grid_propagate(0)
        self.canvas.grid(row=0,column=0,rowspan=10)
        self.canvas.create_window((4,4), window=self.labelFrame, anchor="nw", tags="self.labelFrame")
        self.labelFrame.bind("<Configure>", self.onSatFrameConfigure)
        self.canvas.bind('<Enter>', self.bindSatCanvas) #https://stackoverflow.com/questions/17355902/python-tkinter-binding-mousewheel-to-scrollbar
        self.canvas.bind('<Leave>', self.unbindSatCanvas)
        
        addButton=Button(self.labelFrame,text="+",command=self.addSatelliteWindow)
        addButton.grid()
        self.widgetList.append(addButton)
        
        self.nextSatLabel=Label(self)
        self.nextSatLabel.config(font=(None,32))
        self.nextSatLabel.grid(row=1,column=4)
        
        self.countdownLabel=Label(self)
        self.countdownLabel.config(font=(None,32))
        self.countdownLabel.grid(row=2,column=4)
        
        aziText = Label(self,text="Satellite Azimuth")
        aziText.config(font=(None,32))
        aziText.grid(row=3,column=4)
        
        self.satAzimuthLabel=Label(self)
        self.satAzimuthLabel.config(font=(None,32))
        self.satAzimuthLabel.grid(row=4,column=4)
        
        eleText = Label(self,text="Satellite Elevation")
        eleText.config(font=(None,32))
        eleText.grid(row=5,column=4)
        
        self.satElevationLabel=Label(self)
        self.satElevationLabel.config(font=(None,32))
        self.satElevationLabel.grid(row=6,column=4)
        
        Label(self,text="Antenna Azimuth").grid()
        
        self.antAzimuthLabel=Label(self)
        self.antAzimuthLabel.grid(row=7,column=4)
        
        Label(self,text="Antenna Elevation").grid()
        
        self.antElevationLabel=Label(self)
        self.antElevationLabel.grid(row=8,column=4)
        
        
        #self.scheduleFrame = LabelFrame(self,text="Schedule")
        #self.scheduleFrame.grid(row=0,column=5,rowspan=50)
        self.scheduleCanvas = Canvas(self,width=600,height=self.root.winfo_screenheight()-50)    
        self.canvasFrame = LabelFrame(self.scheduleCanvas,text="Schedule")
        #self.vsb = Scrollbar(self, orient="vertical", command=self.scheduleCanvas.yview) #adds a scrollbar
        #self.scheduleCanvas.configure(yscrollcommand=self.vsb.set)
        #self.vsb.grid(column=6) 
        self.scheduleCanvas.grid_propagate(0)
        self.scheduleCanvas.grid(row=0,column=5,rowspan=100)
        self.scheduleCanvas.create_window((4,4), window=self.canvasFrame, anchor="nw", tags="self.canvasFrame")
        self.canvasFrame.bind("<Configure>", self.onScheduleFrameConfigure) #method called when the user scrolls
        self.scheduleCanvas.bind('<Enter>', self.bindScheduleCanvas) #https://stackoverflow.com/questions/17355902/python-tkinter-binding-mousewheel-to-scrollbar
        self.scheduleCanvas.bind('<Leave>', self.unbindScheduleCanvas)
        
        self.figure = Figure(figsize=(4,2))
        self.p = self.figure.add_subplot(111,projection='polar')
        self.p.plot([180,45],[0,-90])
        self.plotCanvas = FigureCanvasTkAgg(self.figure, master=self)
        self.plotCanvas.get_tk_widget().grid(column=4, row=0, rowspan=1, sticky="nesw")
       
        
        
    def bindScheduleCanvas(self,event):
        self.scheduleCanvas.bind_all("<MouseWheel>", self.mousewheelSchedule)
        
    def bindSatCanvas(self,event):
        self.canvas.bind_all("<MouseWheel>", self.mousewheelSat)
        
    def unbindScheduleCanvas(self,event):
        self.scheduleCanvas.unbind_all("<MouseWheel>") 
    
    def unbindSatCanvas(self,event):
        self.canvas.unbind_all("<MouseWheel>") 
    
    def onScheduleFrameConfigure(self, event):
        self.scheduleCanvas.configure(scrollregion=self.scheduleCanvas.bbox("all")) #Reset the scroll region to encompass the inner frame'

    def onSatFrameConfigure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all")) #Reset the scroll region to encompass the inner frame'
    
    def mousewheelSchedule(self, event):
        if os.name=='nt': #checks if the user is using windows or not as scrolling is set up differently
            self.scheduleCanvas.yview_scroll(-1*(event.delta/120), "units")
        else:
            try:
                self.scheduleCanvas.yview_scroll(-1*(event.delta), "units") #adds mousewheel functionality. For windows do: event.delta/120
            except TclError: #sometimes throws this exception. It doesn't seem to effect anything
                pass
    
    def mousewheelSat(self, event):
        if os.name=='nt': #checks if the user is using windows or not as scrolling is set up differently
            self.canvas.yview_scroll(-1*(event.delta/120), "units")
        else:
            try:
                self.canvas.yview_scroll(-1*(event.delta), "units") #adds mousewheel functionality. For windows do: event.delta/120
            except TclError: #sometimes throws this exception. It doesn't seem to effect anything
                pass
    
    def updateScheduleFrame(self,scheduleList):
        for item in self.scheduleWidgetList:
            item.grid_forget()
        self.scheduleWidgetList = []
        for i,item in enumerate(scheduleList):
            if i==0:
                moveLabel = Label(self.canvasFrame,text="Position at %s - move to %s%s,%s%s"%
                (datetime.now().strftime("%Y-%m-%d, %H:%M:%S"),
                round(item.getTLE().getAzimuth(item.getStartTime()),2), u'\u00b0',
                round(item.getTLE().getElevation(item.getStartTime()),2),u'\u00b0'))
                moveLabel.grid(sticky="W")
            else:
                moveLabel = Label(self.canvasFrame,text="Position at %s - move to %s%s, %s%s"%
                ((scheduleList[i-1].getEndTime()+timedelta(seconds=1)).strftime("%Y-%m-%d, %H:%M:%S"),
                round(item.getTLE().getAzimuth(item.getStartTime()),2),u'\u00b0',
                round(item.getTLE().getElevation(item.getStartTime()),2),u'\u00b0'))
                moveLabel.grid(sticky="W")
            self.scheduleWidgetList.append(moveLabel)
            trackLabelStart = Label(self.canvasFrame,text="%s at %s - begin tracking at %s%s, %s%s"%
                                    (item.getSatName(),item.getStartTime().strftime("%Y-%m-%d, %H:%M:%S"),
                                    round(item.getTLE().getAzimuth(item.getStartTime()),2), u'\u00b0',
                                    round(item.getTLE().getElevation(item.getStartTime()),2),u'\u00b0'))
            trackLabelStart.grid(sticky="W")
            self.scheduleWidgetList.append(trackLabelStart)
            trackLabelEnd = Label(self.canvasFrame,text="%s at %s - finish tracking at %s%s, %s%s"%
                                    (item.getSatName(),item.getEndTime().strftime("%Y-%m-%d, %H:%M:%S"),
                                    round(item.getTLE().getAzimuth(item.getEndTime()),2),u'\u00b0',
                                    round(item.getTLE().getElevation(item.getEndTime()),2),u'\u00b0'))
            trackLabelEnd.grid(sticky="W")
            Label(self.canvasFrame).grid()
            self.scheduleWidgetList.append(trackLabelEnd)
            
    def updatePlot(self,nowx,startx,endx,nowy,starty,endy):
        self.p.clear()
        
        self.plotCanvas.get_tk_widget().grid_forget()
        self.figure = Figure(figsize=(4,2))
        self.p = self.figure.add_subplot(111,projection='polar')
        self.p.plot((nowx,startx,endx),(nowy,starty,endy))
        self.plotCanvas = FigureCanvasTkAgg(self.figure, master=self)
        self.plotCanvas.get_tk_widget().grid(column=4, row=0, rowspan=1, sticky="nesw")

      
        
        
    def appliedChanges(self):
        self.appliedChangesWindow = Toplevel()
        Label(self.appliedChangesWindow,text="WARNING. Changes will not be applied update the satellites are recomplied.").grid(row=0)
        Label(self.appliedChangesWindow,text="Do you want to recompile now?").grid(row=1)
        buttonFrame = Frame(self.appliedChangesWindow)
        buttonFrame.grid(row=2)
        Button(buttonFrame,text="Yes",command=self.yesChosen).grid(row=0,column=0)
        Button(buttonFrame,text="No",command=self.noChosen).grid(row=0,column=1)
        
    def yesChosen(self):
        self.appliedChangesWindow.withdraw()
        self.updateButton()
    
    def noChosen(self):
        self.appliedChangesWindow.withdraw()
        
    def updateNextSatLabel(self,satelliteName):
        self.nextSatLabel['text'] = satelliteName
        
    def updateSatAzimuthLabel(self,azimuth):
        self.satAzimuthLabel['text'] = '%s%s'%(azimuth,u'\u00b0')
        
    def updateSatElevationLabel(self,elevation):
        self.satElevationLabel['text'] = '%s%s'%(elevation,u'\u00b0')
        
    def updateAntAzimuthLabel(self,azimuth):
        self.antAzimuthLabel['text'] = azimuth
        
    def updateAntElevationLabel(self,elevation):
        self.antElevationLabel['text'] = elevation
        
    def updateCountdownLabel(self,timeRemaining):
        self.countdownLabel['text'] = timeRemaining
    
    def trackingRunning(self):
        self.popupWindow = Toplevel(self)
        Label(self.popupWindow,text="A satellite is currently being tracked. Please try again after the passover is complete").grid()
        Button(self.popupWindow,text="Ok",command=self.closeWindow).grid()
        
    def closeWindow(self):
        self.popupWindow.withdraw()
    
    def refreshListbox(self):
        options=[]
        self.string_var_list=[]
        self.resultlist=[]
        for i in range(1,len(self.satelliteList)+1):
            options.append(i)
        for label in self.widgetList:
            label.destroy()
        i=0
        for name in self.satelliteList:
            label = Label(self.labelFrame,text=name)
            label.grid(row=i,column=0)
            self.widgetList.append(label)
            
            stringvar=StringVar()
            stringvar.set(self.satelliteList[name])
            self.string_var_list.append(stringvar)
            optionMenu=OptionMenu(self.labelFrame,self.string_var_list[i],*options)
            optionMenu.grid(row=i,column=1)
            self.resultlist.append([self.string_var_list[i],name])
            self.widgetList.append(optionMenu)
            
            deleteButton = Button(self.labelFrame,text="Delete",command=lambda j=name: self.deleteItem(j))
            deleteButton.grid(row=i,column=2)
            self.widgetList.append(deleteButton)
            i+=1
            
        updateButton=Button(self.labelFrame,text="Compile",command=self.updateButton)
        updateButton.grid(row=i,column=0)
        self.widgetList.append(updateButton)
        
        addButton=Button(self.labelFrame,text="+",command=self.addSatelliteWindow)
        addButton.grid(row=i,column=2,sticky="E")
        self.widgetList.append(addButton)
        
    def openPreferences(self,tolerance,duration,urlList):
        self.tolerance.set(tolerance)
        self.duration.set(duration)
        self.urlList = urlList
        self.window=Toplevel(self.root)
        self.window.title("Preferences")
        
        toleranceLabel=Label(self.window,text="Tolerance")
        toleranceLabel.grid(row=0,column=0)
        
        toleranceInput=Entry(self.window,textvariable=self.tolerance,width=10)
        toleranceInput.grid(row=0,column=1)
        
        
        durationLabel = Label(self.window,text="Duration of compilation")
        durationLabel.grid(row=1,column=0)
        
        
        durationInput=Entry(self.window,textvariable=self.duration,width=10)
        durationInput.grid(row=1,column=1)
       
        
        self.urlLabelFrame=LabelFrame(self.window,text="TLE Sources")
        self.urlLabelFrame.grid(row=2,column=0,rowspan=len(urlList),columnspan=2)
        
        for i,url in enumerate(self.urlList):
            Label(self.urlLabelFrame,text=url).grid(row=i,column=0)
            Button(self.urlLabelFrame,text="Delete",command=lambda i=url: self.deleteURL(i)).grid(row=i,column=1)
        
        self.plusButton=Button(self.urlLabelFrame,text="+",command=self.addURLBox).grid(row=len(self.urlList),column=1)
       
        applyButton=Button(self.window,text="Apply",command=self.apply)
        applyButton.grid(row=len(self.urlList)+2,column=0,sticky="E")
        
        
    def deleteURL(self,item):
        self.urlList.remove(item)
        self.window.withdraw()
        self.openPreferences(self.tolerance.get(), self.duration.get(), self.urlList)
    
    
    def addURLBox(self):

        self.urlEntry=Entry(self.urlLabelFrame,textvariable=self.urlEntry,width=20)
        self.urlEntry.grid(row=len(self.urlList)+1,column=0)
        Button(self.urlLabelFrame,text="Add",command=self.addURL).grid(row=len(self.urlList)+1,column=2)
        
    def addURL(self):
        self.urlList.append(self.urlEntry.get())
        self.window.withdraw()
        self.openPreferences(self.tolerance.get(), self.duration.get(), self.urlList)
    
    def apply(self):
        self.controller.setSettings(self.tolerance.get(),self.duration.get(),self.urlList)
        self.appliedChanges()
        self.window.withdraw()
        
             
            
    def updateButton(self):
        for item in self.resultlist:
            self.satelliteList[item[1]]=item[0].get()
        self.controller.setSatelliteList(self.satelliteList)
        
    def deleteItem(self,item):
        self.satelliteList.pop(item)
        self.refreshListbox()
            
    def addSatelliteWindow(self):
        window=Toplevel(self.root)
        window.title('Select Satellites')
        listbox=FancyListbox(window,self)
        listbox.grid()
        file = open('/Users/gregstewart96/stacstation/eclipse-workspace/tle.txt')
        i=0
        for line in file:
            if i==0:
                listbox.insert(END,line.strip())
            i+=1
            if i==3:
                i=0
                
        
                
class FancyListbox(Listbox): # https://stackoverflow.com/questions/12014210/tkinter-app-adding-a-right-click-context-menu

    def __init__(self, parent, view, *args, **kwargs):
        Listbox.__init__(self, parent, *args, **kwargs)
        self.view = view
        self.popup_menu = Menu(self, tearoff=0)
        self.popup_menu.add_command(label="Add", command=self.addElement)
        self.bind("<Button-2>", self.popup) 
        self.popup_menu.bind("<FocusOut>",self.close)#https://stackoverflow.com/questions/21200516/python3-tkinter-popup-menu-not-closing-automatically-when-clicking-elsewhere

    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root+25, 0)
        finally:
            self.popup_menu.grab_release()
            
            
    def close(self,event=None):
        self.popup_menu.unpost()

    def addElement(self):
        for i in self.curselection()[::-1]:
            self.view.satelliteList[self.get(i)] = 1
        self.view.refreshListbox()
            

    
        


#https://stackoverflow.com/questions/6190468/how-to-trigger-function-on-value-change