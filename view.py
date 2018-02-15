'''
Created on 19 Dec 2017

@author: stacstation
'''
from Tkinter import *
from PIL import Image
import ImageTk


class GUI(Frame):
   
    def __init__(self,master,controller):
        Frame.__init__(self,master)
        print(master.winfo_screenwidth())
        self.configure(height=master.winfo_screenheight(),width=master.winfo_screenwidth())
        self.root=master
        self.widgetList=[]
        self.tolerance=DoubleVar()
        self.satelliteList={}
        self.controller = controller
        self.grid_propagate(0)
        self.grid()
       
    def addWidgets(self):
        
        menubar=Menu(self)
        filemenu=Menu(menubar, tearoff=0)
        filemenu.add_command(label="Preferences",command=self.controller.openPreferences)
        menubar.add_cascade(label="Ground Station Controller",menu=filemenu)
        self.root.config(menu=menubar)
          
        
        labelFrame=LabelFrame(self,text="Satellites")
        labelFrame.grid(row=0,column=0,rowspan=10)
        self.canvas = Canvas(labelFrame)
        self.canvas.grid()
        self.vsb = Scrollbar(self.canvas, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.grid(column=3)
        
        addButton=Button(self,text="+",command=self.addSatelliteWindow)
        addButton.grid()
        
        self.nextSatLabel=Label(self)
        self.nextSatLabel.config(font=(None,32))
        self.nextSatLabel.grid(row=0,column=4)
        
        self.countdownLabel=Label(self)
        self.countdownLabel.config(font=(None,32))
        self.countdownLabel.grid(row=1,column=4)
        
        Label(self,text="Satellite Azimuth").grid()
        
        self.satAzimuthLabel=Label(self)
        self.satAzimuthLabel.grid()
        
        Label(self,text="Satellite Elevation").grid()
        
        self.satElevationLabel=Label(self)
        self.satElevationLabel.grid()
        
        Label(self,text="Antenna Azimuth").grid()
        
        self.antAzimuthLabel=Label(self)
        self.antAzimuthLabel.grid()
        
        Label(self,text="Antenna Elevation").grid()
        
        self.antElevationLabel=Label(self)
        self.antElevationLabel.grid()
        
    def onFrameConfigure(self, event): #https://stackoverflow.com/questions/3085696/adding-a-scrollbar-to-a-group-of-widgets-in-tkinter
        self.canvas.configure(scrollregion=self.canvas.bbox("all")) #Reset the scroll region to encompass the inner frame'
    
    
    def updateNextSatLabel(self,satelliteName):
        self.nextSatLabel['text'] = satelliteName
        
    def updateSatAzimuthLabel(self,azimuth):
        self.satAzimuthLabel['text'] = azimuth
        
    def updateSatElevationLabel(self,elevation):
        self.satElevationLabel['text'] = elevation
        
    def updateAntAzimuthLabel(self,azimuth):
        self.antAzimuthLabel['text'] = azimuth
        
    def updateAntElevationLabel(self,elevation):
        self.antElevationLabel['text'] = elevation
        
    def updateCountdownLabel(self,timeRemaining):
        self.countdownLabel['text'] = timeRemaining
        
    def refreshListbox(self):
        options=[]
        self.string_var_list=[]
        self.resultlist=[]
        for i in range(1,len(self.satelliteList)+1):
            options.append(i)
        for label in self.widgetList:
            label.destroy()
        for i,name in enumerate(self.satelliteList):
            label = Label(self.canvas,text=name)
            label.grid(row=i,column=0)
            self.widgetList.append(label)
            
            stringvar=StringVar()
            stringvar.set(self.satelliteList[name])
            self.string_var_list.append(stringvar)
            optionMenu=OptionMenu(self.canvas,self.string_var_list[i],*options)
            optionMenu.grid(row=i,column=1)
            self.resultlist.append([self.string_var_list[i],name])
            self.widgetList.append(optionMenu)
            
            deleteButton = Button(self.canvas,text="Delete",command=lambda j=name: self.deleteItem(j))
            deleteButton.grid(row=i,column=2)
            self.widgetList.append(deleteButton)

        updateButton=Button(self.canvas,text="Compile",command=self.updateButton)
        updateButton.grid()
        self.widgetList.append(updateButton)
        
    def openPreferences(self,tolerance):
        self.tolerance.set(tolerance)
        
        window=Toplevel(self.root)
        window.title("Preferences")
        
        toleranceLabel=Label(window,text="Tolerance")
        toleranceLabel.grid(row=0,column=0)
        
        toleranceInput=Entry(window,textvariable=self.tolerance,width=10)
        toleranceInput.grid(row=0,column=1)
        
        applyButton=Button(window,text="Apply",command=self.apply)
        applyButton.grid(row=1,column=0)
        
    def apply(self):
        self.controller.setTolerance(self.tolerance.get())
             
            
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
        file = open('/home/stacstation/eclipse-workspace/tle.txt')
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
        self.bind("<Button-3>", self.popup) 
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