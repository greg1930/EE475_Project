'''
Created on 16 Jan 2018

@author: stacstation
'''
import view
import test as model
import time
import thread
import threading
from Queue import Queue
from datetime import datetime
import SDR as sdr
import random

    
from Tkinter import *

class test(threading.Thread):
    def __init__(self,q):
        super(test, self).__init__()
        self.queue = q
    def run(self):
        while True:
            value = self.queue.get()
            if value==None:
                break
            else:
                print('running',value)
                for i in range(0,9):
                    print('running')
                    time.sleep(1)

class Controller:
    
    def __init__(self,root):
        self.externalPrograms = [sdr.Main()]
        self.gui = view.GUI(root,self)
        self.satelliteList={}
        self.tolerance = 5.00
        self.duration = 12
        self.url_list = ['http://celestrak.com/NORAD/elements/amateur.txt','http://celestrak.com/NORAD/elements/engineering.txt']
        self.updateFlag = True
        self.run=model.runSchedule(None,None)
        self.run.start()
        """
        q = Queue()
        t = test(q)
        t.start()
        #threading.Thread(target=self.func, args=(q,)).start()
        for i in range(1,21):
            q.queue.clear()
            q.put(i)
            time.sleep(1)
        q.put(None)
        """
    
    def createGUI(self):
        
        self.gui.addWidgets()
        

    def start(self):
        self.updateFlag=True
        tracker=model.Tracker(self.tolerance,self.duration)
        scheduleList = tracker.schedule(self.satelliteList)
        print(scheduleList)
        self.gui.updateScheduleFrame(scheduleList)
        self.run=model.runSchedule(scheduleList,tracker)
        self.run.start()
    
        #time.mktime(run.getCurrentAOSLOSTime().timetuple())
        thread.start_new_thread(self.updateCountdown,(self.run,))
        

            
    def cancelScheduler(self):
        self.run.stopExecuting()
        time.sleep(1)
        print(self.run.getFlag())
      
            
    def openPreferences(self):
        self.gui.openPreferences(self.tolerance,self.duration,self.url_list)
        
    def updateTLE(self):
        model.TLEUpdate()
        self.gui.appliedChanges()
            
    def setSatelliteList(self,satelliteList):
        if self.run.isAOS==False:
            self.gui.trackingRunning()
        else:
            self.updateFlag=False
            time.sleep(1)
            self.satelliteList=satelliteList
            if self.run.isAlive()==True:
                self.cancelScheduler()
            self.run.join()
            #self.test()
            self.start()
        
    def test(self):
        potentialSats = []
        sats = {}
        success = 0
        fail = 0
        file = open('/Users/gregstewart96/stacstation/eclipse-workspace/tle.txt')
        i=0
        for line in file:
            if i==0:
                potentialSats.append(line.strip())
            i+=1
            if i==3:
                i=0
        for i in range(1,11):
            size = random.randint(1,8)
            randomList = random.sample(potentialSats, size)
            for item in randomList:
                sats[item]=random.randint(1,size)
            tracker=model.Tracker(self.tolerance,self.duration)
            clashCount = tracker.schedule(sats)
            if clashCount==0:
                success+=1
            else:
                fail+=1
            progress = float(i)/float(100)
            progress *= 100
            print('%f %% complete'%(progress))
        result = float(success)/float((success+fail))
        result *= 100
        print('%f %% is the result'%(result))
        
    def setSettings(self,tolerance,duration,urlList):
        tolerance = round(tolerance,2)
        self.tolerance=tolerance
        self.duration = duration
        model.TLEUpdate().update(urlList)
        
    def sendCommand(self,name,endtime):
        for program in self.externalPrograms:
            program.update(name,endtime)
      
    def updateCountdown(self,run):
        #reader=model.AntennaReader()
        while self.updateFlag==True:
            time.sleep(1)
            aoslosTime = run.getCurrentAOSLOSTime()
            self.gui.updatePlot(run.getTLE(),run.getAOS(),run.getLOS())
            #self.gui.updatePlot(run.getTLE().getAzimuth(datetime.utcnow()),run.getTLE().getAzimuth(run.getAOS()),run.getTLE().getAzimuth(run.getLOS()),
                               
                        #run.getTLE().getElevation(datetime.utcnow()),run.getTLE().getElevation(run.getAOS()),run.getTLE().getElevation(run.getLOS()))
            if run.getIsAOS()==True:
                self.gui.updateNextSatLabel("%s Will Be Visible In:" %(run.getCurrentSatName()))
            else:
                self.gui.updateNextSatLabel("%s Will Be Visible For:" %(run.getCurrentSatName()))
                self.sendCommand(run.getCurrentSatName(),aoslosTime)
            aoslosTime = time.mktime(aoslosTime.timetuple())
            while aoslosTime-time.time()>0 and self.updateFlag==True:
                self.gui.updateSatAzimuthLabel(round(run.getCurrentAzimuth(),2))
                self.gui.updateSatElevationLabel(round(run.getCurrentElevation(),2))
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