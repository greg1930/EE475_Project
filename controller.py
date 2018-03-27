'''
Created on 16 Jan 2018

@author: stacstation
'''
import view
import test as model
import time
import thread

import SDR as sdr
import random
import urllib2

    
from Tkinter import *


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
        
    def createGUI(self):
        """add start-up widgets to GUI"""
        self.gui.addWidgets()

    def start(self):
        """tells the label update thred it can keep executing"""
        self.updateFlag=True
        tracker=model.Tracker(self.tolerance,self.duration)
        """get sored list of passovers"""
        scheduleList = tracker.schedule(self.satelliteList)
        """send passover list to GUI"""
        self.gui.updateScheduleFrame(scheduleList)
        """Create runSchedule thread passing in the 
           passover list"""
        self.run=model.runSchedule(scheduleList,tracker)
        self.run.start()
        """start the thread which updates GUI labels every second
        """
        thread.start_new_thread(self.updateCountdown,(self.run,))
        

            
    def cancelScheduler(self):
        """tell model to stop 
           executing passover list"""
        self.run.stopExecuting()
        time.sleep(1)
            
    def openPreferences(self):
        self.gui.openPreferences(self.tolerance,self.duration,self.url_list)
        
    def updateTLE(self):
        model.TLEUpdate()
        self.gui.appliedChanges()
            
    def setSatelliteList(self,satelliteList):
        """check a satellite isn't passing over"""
        if self.run.isAOS==False:
            self.gui.warning("A satellite is currently being tracked. Please try again after the passover is complete")
        """check the user has added satellites"""
        if len(satelliteList)==0:
            self.gui.warning("No satellites have been added. Please add satellites to track then try again")
        else:
            """stop all executing threads"""
            self.updateFlag=False
            time.sleep(3)
            self.satelliteList=satelliteList
            if self.run.isAlive()==True:
                self.cancelScheduler()
            self.run.join()
            """test method
            self.test()"""
            """restart everything"""
            self.start()
        
    def test(self):
        """test method to generate a number of random passover
           lists, checking the number of clashes in each"""
        potentialSats = []
        sats = {}
        resultList = []
        file = open('/home/stacstation/eclipse-workspace/tle.txt')
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
            finalCount,firstCount = tracker.schedule(sats)
            result=firstCount-finalCount
            result=float(result)/float(firstCount)
            result*=100
            resultList.append(result)
            progress = float(i)/float(100)
            progress *= 100
            print('%f %% complete'%(progress))
        final = sum(resultList)/float(len(resultList))
        
        print('%f %% is the result'%(final))
        
    def setSettings(self,tolerance,duration,urlList):
        """check supplied urls are valid before 
           sending to model"""
        validURL = []
        tolerance = round(tolerance,2)
        self.tolerance=tolerance
        self.duration = duration
        for item in urlList:
            try:
                urllib2.urlopen(item)
                validURL.append(item)
            except(urllib2.HTTPError,urllib2.URLError):
                return False
       
        model.TLEUpdate().update(validURL)
        return True
       
        
    def sendCommand(self,name,endtime):
        """call update method in each of the
           external programs"""
        for program in self.externalPrograms:
            program.update(name,endtime)
      
    def updateCountdown(self,run):
        while self.updateFlag==True:
            """pause to allow model to get ahead"""
            time.sleep(1)
            aoslosTime = run.getCurrentAOSLOSTime()
            """if satellite is not yet passing over"""
            if run.getIsAOS()==True:
                self.gui.updateNextSatLabel("%s Will Be Visible In:" %(run.getCurrentSatName()))
                """if satellite is passing over now"""
            else:
                self.gui.updateNextSatLabel("%s Will Be Visible For:" %(run.getCurrentSatName()))
                self.sendCommand(run.getCurrentSatName(),aoslosTime)
                """convert to epoch seconds"""
            aoslosTime = time.mktime(aoslosTime.timetuple())
            """loop until passover is complete"""
            while aoslosTime-time.time()>0 and self.updateFlag==True:
                self.gui.updateSatAzimuthLabel(round(run.getCurrentAzimuth(),2))
                self.gui.updateSatElevationLabel(round(run.getCurrentElevation(),2))
                timeRemaining = aoslosTime-time.time()
                """find time remaining in h,m,s format"""
                m, s = divmod(round(timeRemaining,0), 60) #https://stackoverflow.com/questions/775049/how-to-convert-seconds-to-hours-minutes-and-seconds
                h, m = divmod(m, 60)
                self.gui.updateCountdownLabel("%d:%02d:%02d" % (h, m, s))
                """delay be 1 second, if 1 second has not yet passed"""
                timeDelay = (aoslosTime-time.time())-(timeRemaining-1)
                if timeDelay>0:
                    time.sleep(timeDelay)
    
root=Tk()

controller = Controller(root)
controller.createGUI()
root.mainloop()   