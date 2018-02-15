'''
Created on 16 Jan 2018

@author: stacstation
'''
import view
import test as model
import time
import thread
from Tkinter import *


class Controller:
    
    def __init__(self,root):
        self.gui = view.GUI(root,self)
        self.satelliteList={}
        self.tolerance = 5.00
        self.updateFlag = True
        self.run=model.runSchedule(None,None)
        self.run.start()
    
    def createGUI(self):
        
        self.gui.addWidgets()

    def start(self):
        self.updateFlag=True
        tracker=model.Tracker(self.tolerance)
        scheduleList = tracker.schedule(self.satelliteList)
        print(scheduleList)
        self.run=model.runSchedule(scheduleList,tracker)
        self.run.start()
    
        #time.mktime(run.getCurrentAOSLOSTime().timetuple())
        thread.start_new_thread(self.updateCountdown,(self.run,))
        

            
    def cancelScheduler(self):
        self.run.stopExecuting()
        time.sleep(1)
        print(self.run.getFlag())
      
            
    def openPreferences(self):
        self.gui.openPreferences(self.tolerance)
            
    def setSatelliteList(self,satelliteList):
        
        self.updateFlag=False
        time.sleep(1)
        self.satelliteList=satelliteList
        if self.run.isAlive()==True:
            self.cancelScheduler()
        self.run.join()
        self.start()
        
    def setTolerance(self,tolerance):
        tolerance = round(tolerance,2)
        self.tolerance=tolerance
        
      
    def updateCountdown(self,run):
        #reader=model.AntennaReader()
        while self.updateFlag==True:
            time.sleep(1)
            aoslosTime = time.mktime(run.getCurrentAOSLOSTime().timetuple())
            if run.getIsAOS()==True:
                self.gui.updateNextSatLabel("%s Will Be Visible In:" %(run.getCurrentSatName()))
            else:
                self.gui.updateNextSatLabel("%s Will Be Visible For:" %(run.getCurrentSatName()))
            while aoslosTime-time.time()>0 and self.updateFlag==True:
                self.gui.updateSatAzimuthLabel(round(run.getCurrentAzimuth(),3))
                self.gui.updateSatElevationLabel(round(run.getCurrentElevation(),3))
                #self.gui.updateAntAzimuthLabel(reader.getAzimuth())
                #self.gui.updateAntElevationLabel(reader.getElevation())
                timeRemaining = aoslosTime-time.time()
                m, s = divmod(round(timeRemaining,0), 60) #https://stackoverflow.com/questions/775049/how-to-convert-seconds-to-hours-minutes-and-seconds
                h, m = divmod(m, 60)
                self.gui.updateCountdownLabel("%d:%02d:%02d" % (h, m, s))
                timeDelay = (aoslosTime-time.time())-(timeRemaining-1)
                if timeDelay>0:
                    time.sleep(timeDelay)
        print('here')
        #print(run.getSchedulerInstance())
        print('thread joined')
    
root=Tk()
controller = Controller(root)
controller.createGUI()
root.mainloop()   