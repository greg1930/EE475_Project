'''
Created on 19 Dec 2017

@author: stacstation
'''
from Tkinter import *
from datetime import datetime
from datetime import timedelta



class GUI(Frame):
   
    def __init__(self,master,controller):
        Frame.__init__(self,master)
        self.root=master
        self.widgetList=[]
        self.preferencesWidgetList =[]
        self.scheduleWidgetList = []
        self.tolerance=DoubleVar()
        self.urlEntry=StringVar()
        self.duration=IntVar()
        self.satelliteList={}
        self.controller = controller
        self.grid()
       
    def addWidgets(self):
        """add default widgets to the frame"""
        menubar=Menu(self)
        filemenu=Menu(menubar, tearoff=0)
        filemenu.add_command(label="Preferences",command=self.controller.openPreferences)
        filemenu.add_command(label="Update TLE Files",command=self.controller.updateTLE)
        menubar.add_cascade(label="Ground Station Controller",menu=filemenu)
        self.root.config(menu=menubar)
          
        self.canvas = Canvas(self,width=400,height=self.root.winfo_screenheight()-50)
        self.labelFrame=LabelFrame(self.canvas,text="Satellites")
        self.canvas.grid_propagate(0)
        self.canvas.grid(row=0,column=0,rowspan=30)
        self.canvas.create_window((4,4), window=self.labelFrame, anchor="nw", tags="self.labelFrame")
        self.labelFrame.bind("<Configure>", self.onSatFrameConfigure)
        self.canvas.bind('<Enter>', self.bindSatCanvas)
        self.canvas.bind('<Leave>', self.unbindSatCanvas)
        
        addButton=Button(self.labelFrame,text="+",command=self.addSatelliteWindow)
        addButton.grid()
        self.widgetList.append(addButton)
        
        self.nextSatLabel=Label(self,text="Satellite Will Be Visible In:")
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
        
        self.scheduleCanvas = Canvas(self,width=500,height=self.root.winfo_screenheight()-50)    
        self.canvasFrame = LabelFrame(self.scheduleCanvas,text="Schedule")
        
        self.scheduleCanvas.grid_propagate(0)
        self.scheduleCanvas.grid(row=0,column=5,rowspan=100)
        self.scheduleCanvas.create_window((4,4), window=self.canvasFrame, anchor="nw", tags="self.canvasFrame")
        self.canvasFrame.bind("<Configure>", self.onScheduleFrameConfigure)
        self.scheduleCanvas.bind('<Enter>', self.bindScheduleCanvas) 
        self.scheduleCanvas.bind('<Leave>', self.unbindScheduleCanvas)
        
        img = PhotoImage(file='/home/stacstation/eclipse-workspace/logo.gif')
        img = img.zoom(5)
        img = img.subsample(6)
        logo=Label(self,image=img)
        logo.image=img
        logo.grid(row=0,column=4)
        
    def bindScheduleCanvas(self,event):
        """bind canvas for upward and downward scrolling events"""
        self.scheduleCanvas.bind_all("<Button-4>",self.mousewheelSchedule)
        self.scheduleCanvas.bind_all("<Button-5>",self.mousewheelSchedule)
        
    def bindSatCanvas(self,event):
        self.canvas.bind_all("<Button-4>",self.mousewheelSat)
        self.canvas.bind_all("<Button-5>",self.mousewheelSat)
        
    def unbindScheduleCanvas(self,event):
        """unbind from canvas"""
        self.scheduleCanvas.unbind_all("<Button-4>")
        self.scheduleCanvas.unbind_all("<Button-5>")
    
    def unbindSatCanvas(self,event):
        self.canvas.unbind_all("<Button-4>") 
        self.canvas.unbind_all("<Button-5>") 
    
    def onScheduleFrameConfigure(self, event):
        """configure canvas for scrolling"""
        self.scheduleCanvas.configure(scrollregion=self.scheduleCanvas.bbox("all")) 
    def onSatFrameConfigure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    def mousewheelSchedule(self, event):
        """check which event has been triggered to know which direction
           to scroll"""
        try:
            if event.num==4:
                self.scheduleCanvas.yview_scroll(1, "units") 
            elif event.num==5:
                self.scheduleCanvas.yview_scroll(-1, "units")
        #sometimes throws this exception. It doesn't seem to effect anything
        except TclError:
            pass
    
    def mousewheelSat(self, event):
        try:
            if event.num==4:
                self.canvas.yview_scroll(1, "units") 
            elif event.num==5:
                self.canvas.yview_scroll(-1, "units")
        except TclError: 
            pass
    
    def updateScheduleFrame(self,scheduleList):
        """add labels to schedule frame"""
        for item in self.scheduleWidgetList:
            item.grid_forget()
        """add labels to list so they can be destoryed in future"""
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
            
        
    def appliedChanges(self):
        """warn users when they click apply"""
        self.appliedChangesWindow = Toplevel()
        Label(self.appliedChangesWindow,text="WARNING. Changes will not be applied update the satellites are recomplied.").grid(row=0)
        Label(self.appliedChangesWindow,text="Do you want to recompile now?").grid(row=1)
        buttonFrame = Frame(self.appliedChangesWindow)
        buttonFrame.grid(row=2)
        Button(buttonFrame,text="Yes",command=self.yesChosen).grid(row=0,column=0)
        Button(buttonFrame,text="No",command=self.noChosen).grid(row=0,column=1)
        
    def yesChosen(self):
        """if yes close window and update"""
        self.appliedChangesWindow.withdraw()
        self.updateButton()
    
    def noChosen(self):
        """if no just close window"""
        self.appliedChangesWindow.withdraw()
        
    def updateNextSatLabel(self,satelliteName):
        self.nextSatLabel['text'] = satelliteName
        
    def updateSatAzimuthLabel(self,azimuth):
        self.satAzimuthLabel['text'] = '%s%s'%(azimuth,u'\u00b0')
        
    def updateSatElevationLabel(self,elevation):
        self.satElevationLabel['text'] = '%s%s'%(elevation,u'\u00b0')
        
        
    def updateCountdownLabel(self,timeRemaining):
        self.countdownLabel['text'] = timeRemaining
    
    def warning(self,message):
        """warn users of a specified message"""
        self.popupWindow = Toplevel(self)
        Label(self.popupWindow,text=message).grid()
        Button(self.popupWindow,text="OK",command=self.closeWindow).grid()
        
    def closeWindow(self):
        self.popupWindow.withdraw()
    
    def refreshListbox(self):
        """refresh list of satellites"""
        options=[]
        self.string_var_list=[]
        self.resultlist=[]
        """number of ranking options there should be"""
        for i in range(1,len(self.satelliteList)+1):
            options.append(i)
        """destroy old labels"""
        for label in self.widgetList:
            label.destroy()
        i=0
        """add labels,optionmenu,button"""
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
        """open preferences window"""
        self.tolerance.set(tolerance)
        self.duration.set(duration)
        self.urlList = urlList
        self.window=Toplevel(self.root)
        self.window.title("Preferences")
        
        toleranceLabel=Label(self.window,text="Tolerance")
        toleranceLabel.grid(row=0,column=0)
        
        toleranceInput=Entry(self.window,textvariable=self.tolerance,width=10)
        toleranceInput.grid(row=0,column=1)
        Label(self.window,text=u'\u00b0').grid(row=0,column=2,sticky="W")
        
        
        durationLabel = Label(self.window,text="Duration of compilation")
        durationLabel.grid(row=1,column=0)
        
        
        durationInput=Entry(self.window,textvariable=self.duration,width=10)
        durationInput.grid(row=1,column=1)
        Label(self.window,text="Hours").grid(row=1,column=2,sticky="W")
       
        
        self.urlLabelFrame=LabelFrame(self.window,text="TLE Sources")
        self.urlLabelFrame.grid(row=2,column=0,rowspan=len(urlList),columnspan=2)
        
        for i,url in enumerate(self.urlList):
            Label(self.urlLabelFrame,text=url).grid(row=i,column=0)
            Button(self.urlLabelFrame,text="Delete",command=lambda i=url: self.deleteURL(i)).grid(row=i,column=1)
        
        self.plusButton=Button(self.urlLabelFrame,text="+",command=self.addURLBox).grid(row=len(self.urlList),column=1)
       
        applyButton=Button(self.window,text="Apply",command=self.apply)
        applyButton.grid(row=len(self.urlList)+2,column=0,sticky="E")
        
        
    def deleteURL(self,item):
        """remove url from preferences"""
        self.urlList.remove(item)
        self.window.withdraw()
        self.openPreferences(self.tolerance.get(), self.duration.get(), self.urlList)
    
    
    def addURLBox(self):
        """add entry box to preferences window"""
        self.urlEntry=Entry(self.urlLabelFrame,textvariable=self.urlEntry,width=20)
        self.urlEntry.grid(row=len(self.urlList)+1,column=0)
        Button(self.urlLabelFrame,text="Add",command=self.addURL).grid(row=len(self.urlList)+1,column=1)
        
    def addURL(self):
        """add entered url to list of urls"""
        self.urlList.append(self.urlEntry.get())
        self.window.withdraw()
        self.openPreferences(self.tolerance.get(), self.duration.get(), self.urlList)
    
    def apply(self):
        """apply changes made to preferences""" 
        try:
            """check controller is happy with new settings"""
            if self.controller.setSettings(self.tolerance.get(),self.duration.get(),self.urlList)==True:
                self.appliedChanges()
                self.window.withdraw()
            else:
                self.warning("One of the URLs entered is invalid")
                """execption thrown if wrong value type has been supplied"""
        except ValueError:
            self.warning("One of the values you have entered is invalid")
        
             
            
    def updateButton(self):
        """send new satellite list to controller"""
        for item in self.resultlist:
            self.satelliteList[item[1]]=item[0].get()
        self.controller.setSatelliteList(self.satelliteList)
        
    def deleteItem(self,item):
        """delete satellite from satellite window"""
        self.satelliteList.pop(item)
        self.refreshListbox()
            
    def addSatelliteWindow(self):
        """creates window showing satellites that could
           be added"""
        window=Toplevel(self.root)
        window.title('Select Satellites')
        listbox=FancyListbox(window,self)
        listbox.grid()
        file = open('/home/stacstation/eclipse-workspace/tle.txt')
        i=0
        for line in file:
            if i==0:
                listbox.insert(END,line.strip())
            i+=1
            if i==3:
                i=0
                
        
                
class FancyListbox(Listbox): 

    def __init__(self, parent, view, *args, **kwargs):
        Listbox.__init__(self, parent, *args, **kwargs)
        self.view = view
        self.popup_menu = Menu(self, tearoff=0)
        self.popup_menu.add_command(label="Add", command=self.addElement)
        """if the user right clicks"""
        self.bind("<Button-3>", self.popup) 
        """if the user clicks away from window"""
        self.popup_menu.bind("<FocusOut>",self.close)

    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root+25, 0)
        finally:
            self.popup_menu.grab_release()
            
            
    def close(self,event=None):
        self.popup_menu.unpost()

    def addElement(self):
        """add selected item to the View's satellite 
           list"""
        for i in self.curselection()[::-1]:
            self.view.satelliteList[self.get(i)] = 1
        """refresh the list of satellites on GUI"""
        self.view.refreshListbox()
            

