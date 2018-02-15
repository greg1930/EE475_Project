'''
Created on 4 Dec 2017

@author: gregstewart96
'''
#from pyorbital import orbital
from datetime import datetime
import serial
from pyorbital import orbital
from pyorbital import tlefile
import time
import threading
from threading import Timer
from twisted.test.test_pb import Observable
import sched
import time
import operator
from libxml2mod import doc
from datetime import timedelta


class TLE:

    def __init__(self,path,satName):
        self.lat = 55.8667
        self.lon = -4.4333
        self.alt = 125
        self.satName = satName
        f = open("%s" % path,'r')
        sat = f.readline()
        line1 = f.readline()
        line2 = f.readline()
        self.orb = orbital.Orbital(sat,path,line1,line2)
    
    def getSatName(self):
        return self.satName
  
    def getAzimuth(self,time):
        azi = self.orb.get_observer_look(time, self.lon, self.lat,self.alt)
        return azi[0]
        
    def getElevation(self,time):
        ele = self.orb.get_observer_look(time, self.lon, self.lat,self.alt)
        return ele[1]
    
    def getLongitude(self,time):
        result = self.orb.get_lonlatalt(time)
        return result
        
    def nextPass(self):
        now = datetime.utcnow()
        nextPass = self.orb.get_next_passes(now,12,self.lon,self.lat,self.alt,0.001,0)
        return nextPass[0]
    
    def nextPasses(self):
        now = datetime.utcnow()
        nextPass = self.orb.get_next_passes(now,12,self.lon,self.lat,self.alt,0.001,0)
        return nextPass
    

    
class Antenna(threading.Thread):
    def __init__(self,threadID,value):
        super(Antenna, self).__init__()
        self.portA='/dev/ttyUSB0'
        self.portE='/dev/ttyUSB1'
        self.baud=9600
        self.parity='N'
        self.databits=8
        self.stopbits=1
        self.rtscts=0
        self.timeout='None'
        self.xonxoff=0
        self.threadID=threadID
        self.value=value
        self.serA=serial.Serial(port=self.portA, baudrate=self.baud, parity=self.parity, 
                      bytesize=self.databits, stopbits=self.stopbits, 
                      rtscts=self.rtscts, timeout=0.5,
                      xonxoff=self.xonxoff)
        self.serE=serial.Serial(port=self.portE, baudrate=self.baud, parity=self.parity, 
                      bytesize=self.databits, stopbits=self.stopbits, 
                      rtscts=self.rtscts, timeout=0.5,
                      xonxoff=self.xonxoff)
        
    def run(self):
        if self.value!=None:
            if self.threadID=='Azimuth':
                self.updateAzimuth(self.value)
            elif self.threadID=='Elevation':
                self.updateElevation(self.value)        
            
        
    def updateAzimuth(self,azi):
        """
        ser=serial.Serial(port=self.portA, baudrate=self.baud, parity=self.parity, 
                      bytesize=self.databits, stopbits=self.stopbits, 
                      rtscts=self.rtscts, timeout=None,
                      xonxoff=self.xonxoff)
        """
        #time.sleep(3)
        if azi<0.1 and azi>-0.1:
            azi=0
        if azi>348:
            azi=348.0
        azi=''.join(['A',str(azi)])
        #self.serA.write(b'%s\r' % azi)
        #ser.close()
        #ser.write("L,1\r" )
        
    def updateElevation(self,ele):
        """
        ser1=serial.Serial(port=self.portE, baudrate=self.baud, parity=self.parity, 
                          bytesize=self.databits, stopbits=self.stopbits, 
                          rtscts=self.rtscts, timeout=None,
                          xonxoff=self.xonxoff)
        """
        #time.sleep(3)
        if ele<0.1 and ele>-0.1:
            ele=0
        ele=''.join(['E',str(ele)])
        #self.serE.write(b'%s\r' % ele)
        #ser1.close()
        
        
        
        
class AntennaReader(Antenna):
    def __init__(self):
        Antenna.__init__(self,None,None)
        
    def getAzimuth(self):
        """
        ser=serial.Serial(port=self.portA, baudrate=self.baud, parity=self.parity, 
                          bytesize=self.databits, stopbits=self.stopbits, 
                          rtscts=self.rtscts, timeout=None,
                          xonxoff=self.xonxoff)
        """
        #self.serA.write("L,1\r" )
        azimuth = self.serA.readline()
        azimuth = azimuth.split(' ',1)[0]
        if '=' in azimuth:
            azimuth = azimuth[2:]
        else:
            azimuth = azimuth[1:]
        return azimuth
        #ser.close()
        
    def getElevation(self):
        """
        ser=serial.Serial(port=self.portE, baudrate=self.baud, parity=self.parity, 
                          bytesize=self.databits, stopbits=self.stopbits, 
                          rtscts=self.rtscts, timeout=None,
                          xonxoff=self.xonxoff)
        """
        """ser.write("L,1\r" )"""
        elevation = self.serE.readline()
        elevation = elevation.split(' ',1)[0]
        if '=' in elevation:
            elevation = elevation[2:]
        else:
            elevation = elevation[1:]
        return elevation
        """ser.close()"""
        
class Passover:
    def __init__(self,tle,startTime,endTime,satName,priority):
        self.tle = tle
        self.startTime = startTime
        self.endTime = endTime
        self.satName = satName
        self.priority = priority
        
    def getTLE(self):
        return self.tle
    
    def getStartTime(self):
        return self.startTime
    
    def setStartTime(self,time):
        self.startTime = time
        
    def setEndTime(self,time):
        self.endTime = time
    
    def getEndTime(self):
        return self.endTime
    
    def getSatName(self):
        return self.satName
    
    def getPriority(self):
        return self.priority
    
class scheduledSat(Passover):
    def __init__(self,tle,startTime,endTime,satName,priority,sched,event):
        Passover.__init__(self,tle, startTime, endTime, satName, priority)
        self.sched = sched
        self.event = event
    def getSched(self):
        return self.sched
    def getEvent(self):
        return self.event
    
        
class Tracker: 
    
    def __init__(self,tolerance):
        self.tolerance = tolerance
        
    def schedule(self,satelliteList):
        passovers=[]
        self.scheduleList = []
        for name,priority in satelliteList.iteritems(): #loop through all the tles we want to track
            path = '/home/stacstation/eclipse-workspace/%s.txt'%(name)
            f = open("%s" % path,'r')
            satName = f.readline()
            satName = satName.split(' ',1)[0]
            tle=TLE(path,satName) #create tle instance
            allPasses = tle.nextPasses() #get an array for the new passover start and end
            for passes in allPasses:
                passover = Passover(tle,passes[0],passes[1],satName,priority)
                passovers.append(passover)
        
        #print(self.clashCount)   
        #passovers=sorted(passovers,key=operator.itemgetter(2)) #sort by the second element (time) as it's a list of lists
        passovers = sorted(passovers, key=lambda passover: passover.getStartTime())
        passovers = self.longestPhase(passovers)
        for item in passovers:
            
            print(item.getSatName())
            print(item.getPriority())
            print(item.getStartTime())
            print(item.getEndTime())
            print(item.getTLE().getAzimuth(item.getStartTime()))
            print(item.getTLE().getAzimuth(item.getEndTime()))
            print
        passovers = self.clashDetect(passovers)
        passovers = sorted(passovers, key=lambda passover: passover.getStartTime())
        passovers = self.clashDetect(passovers)
        """assert clashCount==0"""
        for item in passovers:
            
            print(item.getSatName())
            print(item.getPriority())
            print(item.getStartTime())
            print(item.getEndTime())
            print(item.getTLE().getAzimuth(item.getStartTime()))
            print(item.getTLE().getAzimuth(item.getEndTime()))
            print
        
        
        """
        for i,passes in enumerate(passovers): #loop through the starting times
            print
            tle = passes.getTLE()
            passoverStart = passes.getStartTime()
            passoverEnd = passes.getEndTime()
            previousPassoverEnd = passovers[i-1].getEndTime()
            satelliteName = passes.getSatName()
            s=sched.scheduler(time.time,time.sleep)
            print ('starttime')
            print(passoverStart)
            print ('endtime')
            print(passoverEnd)
            if i==0:
                self.scheduleList.append(scheduledSat(tle,passoverStart,None,satelliteName,priority,None,None)) 
            else:
                self.scheduleList.append(scheduledSat(tle,passoverStart,None,satelliteName,priority,(time.mktime(previousPassoverEnd.timetuple())+1)-time.time(),None))
           
            
            
          
            self.scheduleList.append(scheduledSat(tle,None,passoverEnd,satelliteName,priority,time.mktime(passoverStart.timetuple())-time.time(),None))
        """
        return passovers
    

    
    def longestPhase(self,passovers):
        for passes in passovers:
            passoverStart = passes.getStartTime()
            passoverEnd = passes.getEndTime()
            tle = passes.getTLE()
            azi0=self.azimuthZero(passoverStart, passoverEnd,tle)
            phase1=time.mktime(azi0.timetuple())-(time.mktime(passoverStart.timetuple()))
            phase2=time.mktime(passoverEnd.timetuple())-(time.mktime(azi0.timetuple())+1)
            if phase1>=phase2:
                print('phase1 chosen. phase1 %.2f ........ phase2 %.2f' % (phase1,phase2))
                passes.setEndTime(azi0)
            elif phase2>phase1:
                print('phase2')
                passes.setStartTime(azi0+timedelta(seconds=1))
        return passovers
    
    def compare(self,passover,clashChecked,clashCount):
        startTime = passover.getStartTime()
        endTime = passover.getEndTime()
        priority = passover.getPriority()
        satName = passover.getSatName()
        tle = passover.getTLE()
        if len(clashChecked)!=0:
            for item in clashChecked:
                case_one_transfer_time = self.calculateTime(item.getTLE().getAzimuth(item.getEndTime()), tle.getAzimuth(startTime), item.getTLE().getElevation(item.getEndTime()), tle.getElevation(startTime))
                case_four_transfer_time = self.calculateTime(tle.getAzimuth(endTime), item.getTLE().getAzimuth(item.getStartTime()), tle.getElevation(endTime), item.getTLE().getElevation(item.getStartTime()))
                if startTime>item.getStartTime() and (item.getEndTime()+timedelta(seconds=case_one_transfer_time))>startTime and item.getEndTime()<endTime:
                    clashCount+=1
                    
                    print('case 1', case_one_transfer_time)
                    if priority<item.getPriority():
                        time = startTime
                        while time>item.getStartTime():
                            transferTime = self.calculateTime(item.getTLE().getAzimuth(time), tle.getAzimuth(startTime), item.getTLE().getElevation(time), tle.getElevation(startTime))
                            if (time+timedelta(seconds=transferTime)) < startTime: break
                            time = time - timedelta(seconds=1)
                        item.setEndTime(time)
                    elif priority>item.getPriority():
                        startTime = item.getEndTime()                        
                    else:
                        optimise = self.optimisePassover(item, passover, 0)
                        item.setEndTime(optimise[0])
                        startTime = optimise[1]
                        
                        
    
                elif startTime>item.getStartTime() and item.getEndTime()>startTime and item.getEndTime()>endTime:
                    clashCount+=1
                    if priority<item.getPriority():
                        time=startTime
                        while time>item.getStartTime():
                            transferTime = self.calculateTime(item.getTLE().getAzimuth(time), tle.getAzimuth(startTime), item.getTLE().getElevation(time), tle.getElevation(startTime))
                            if (time+timedelta(seconds=transferTime)) < startTime: break
                            time = time - timedelta(seconds=1)
                            clashChecked.append(Passover(item.getTLE(),endTime,item.getEndTime(),item.getSatName(),item.getPriority()))
                        item.setEndTime(time)
                    elif priority>item.getPriority():
                        return clashChecked,clashCount
                    else:
                        time = item.getEndTime()
                        while time>endTime:
                            transferTime = self.calculateTime(item.getTLE().getAzimuth(time), tle.getAzimuth(endTime), item.getTLE().getElevation(time), tle.getElevation(endTime))
                            if (time-timedelta(seconds=transferTime))<endTime:
                                endPhase = (item.getEndTime()-(time+timedelta(seconds=1))).total_seconds()
                                break
                            time=time-timedelta(seconds=1)
                        optimise = self.optimisePassover(item, passover, endPhase)
                        clashChecked.append(Passover(item.getTLE(),endTime,item.getEndTime(),item.getSatName(),item.getPriority()))
                        item.setEndTime(optimise[0])
                        startTime = optimise[1]
                        
                    
                    
                        
                elif startTime<item.getStartTime() and endTime>item.getStartTime() and endTime>item.getEndTime():
                    clashCount+=1
                    if priority<item.getPriority():
                        clashChecked.remove(item)
                    elif priority>item.getPriority():
                        time = item.getStartTime()
                        while time>startTime:
                            transferTime = self.calculateTime(tle.getAzimuth(time),item.getTLE().getAzimuth(item.getStartTime()),tle.getElevation(time),item.getTLE().getElevation(item.getStartTime()))
                            if (time + timedelta(seconds=transferTime))<item.getStartTime(): break
                            time = time - timedelta(seconds=1)
                        clashChecked.append(Passover(tle,item.getEndTime(),endTime,satName,priority))
                        endTime = time
                    else:
    
                        time = endTime
                        while time>item.getEndTime():
                            transferTime = self.calculateTime(tle.getAzimuth(time), item.getTLE().getAzimuth(item.getEndTime()), tle.getElevation(time), item.getTLE().getElevation(item.getEndTime()))
                            if (time-timedelta(seconds=transferTime))<item.getEndTime(): 
                                endPhase = (endTime-(time+timedelta(seconds=1))).total_seconds()
                                break
                            time=time-timedelta(seconds=1)
                        optimise = self.optimisePassover(passover, item, endPhase)
                        clashChecked.append(Passover(tle,item.getEndTime(),endTime,satName,priority))
                        endTime = optimise[0]
                        item.setStartTime(optimise[1])
                        
                    
                elif startTime<item.getStartTime() and (endTime+timedelta(seconds=case_four_transfer_time))>item.getStartTime() and endTime<item.getEndTime():
                    clashCount+=1
                    print(endTime+timedelta(seconds=case_four_transfer_time))
                    if priority<item.getPriority():
                        item.setStartTime(endTime)
                    elif priority>item.getPriority():
                        time = item.getStartTime()
                        while time>startTime:
                            transferTime = self.calculateTime(tle.getAzimuth(time),item.getTLE().getAzimuth(item.getStartTime()),tle.getElevation(time),item.getTLE().getElevation(item.getStartTime()))
                            if (time + timedelta(seconds=transferTime))<item.getStartTime(): break
                            time = time - timedelta(seconds=1)
                        endTime = time
                    else:
                        optimise = self.optimisePassover(passover, item, 0)
                        endTime = optimise[0]
                        item.setStartTime(optimise[1])
        clashChecked.append(Passover(tle,startTime,endTime,satName,priority))
        return clashChecked,clashCount
    
    
    def clashDetect(self,passovers):
        clashChecked = []
        clashCount = 0
        for passover in passovers:
            clashChecked,clashCount = self.compare(passover,clashChecked,clashCount)
        print(clashCount)
        return clashChecked
    
    def optimisePassover(self,firstSatellite,secondSatellite,additionalTime):
        print('optimise')
        currentTime = firstSatellite.getStartTime()
        optimalTime = None
        firstSatEndTime = None
        secondSatStartTime = None
        while currentTime<firstSatellite.getEndTime():
            offset = 0
            delta = None
            while delta>1:
                transferTime = self.calculateTime(firstSatellite.getTLE().getAzimuth(currentTime),secondSatellite.getTLE().getAzimuth(currentTime+timedelta(seconds=offset)),firstSatellite.getTLE().getElevation(currentTime),secondSatellite.getTLE().getElevation(currentTime+timedelta(seconds=offset)))
                if secondSatellite.getTLE().getAzimuth(currentTime+timedelta(seconds=transferTime))>secondSatellite.getTLE().getAzimuth(currentTime+timedelta(seconds=offset)):
                    delta = secondSatellite.getTLE().getAzimuth(currentTime+timedelta(seconds=transferTime)) - secondSatellite.getTLE().getAzimuth(currentTime+timedelta(seconds=offset))
                else:
                    delta = secondSatellite.getTLE().getAzimuth(currentTime+timedelta(seconds=offset)) - secondSatellite.getTLE().getAzimuth(currentTimetimedelta(seconds=offset))
                offset+=1
            if currentTime + timedelta(seconds=transferTime) >= secondSatellite.getStartTime():
                firstSatPassover = (currentTime - firstSatellite.getStartTime()).total_seconds() + additionalTime
                secondSatPassover = currentTime+timedelta(seconds=transferTime)
                secondSatPassover = (secondSatellite.getEndTime()-secondSatPassover).total_seconds()
    
                if firstSatPassover>secondSatPassover:
                    timeDifference = firstSatPassover - secondSatPassover
                else:
                    timeDifference = secondSatPassover - firstSatPassover
                if timeDifference<optimalTime or optimalTime==None:
                    optimalTime=timeDifference
                    firstSatEndTime = currentTime
                    secondSatStartTime = currentTime + timedelta(seconds=transferTime)
                    finalTranfer = transferTime
        
            currentTime = currentTime + timedelta(seconds=1)
        print(finalTranfer)
        return [firstSatEndTime,secondSatStartTime]
    
    def calculateTime(self,aziStart,aziEnd,eleStart,eleEnd):
        
        if aziEnd>aziStart:
            aziDeltaAngle = aziEnd - aziStart
        else:
            aziDeltaAngle = aziStart-aziEnd
        if eleEnd>eleStart:
            eleDeltaAngle = eleEnd - eleStart
        else:
            eleDeltaAngle = eleStart - eleEnd
        if aziDeltaAngle<29:
            aziTime = aziDeltaAngle/1.32
        else:
            fullSpeedTime = (aziDeltaAngle-30)/2.1
            rampUpSlowDown = 19
            aziTime = fullSpeedTime + rampUpSlowDown
        if eleDeltaAngle<29:
            eleTime = eleDeltaAngle/1.32
        else:
            fullSpeedTime = (eleDeltaAngle-30)/2.1
            rampUpSlowDown = 19
            eleTime = fullSpeedTime + rampUpSlowDown
        if aziTime>eleTime:
            return aziTime
        else:
            return eleTime

    def azimuthZero(self,starttime,endtime,tle):
        times = starttime
        while True:
            if (tle.getAzimuth(times))<348 and tle.getAzimuth((times+timedelta(seconds=1)))>348:
                return times
            elif tle.getAzimuth(times)>348 and tle.getAzimuth((times+timedelta(seconds=1)))<348:
                return times
            elif time.mktime(times.timetuple())>time.mktime(endtime.timetuple()):
                return endtime
            else:
                times = times+timedelta(seconds=1)
    
        
            
        
    
    def positionAntenna(self,starttime,tle):
        print('position')
        azimuth=tle.getAzimuth(starttime)
        aziGetter = Antenna("Azimuth",azimuth)
        aziGetter.start()
        elevation=tle.getElevation(starttime)
        ele = Antenna("Elevation",elevation)
        ele.start()  
        print('position finished')
          
    def trackSatellite2(self,endtime,tle):
        print('track start')
        azi = Antenna("Azimuth", None)
        azi.start()
        ele = Antenna("Elevation",None)
        ele.start()
        azimuth=tle.getAzimuth(datetime.utcnow())
        elevation=tle.getElevation(datetime.utcnow())
        while time.time()<endtime:
            if tle.getAzimuth(datetime.utcnow())>azimuth+self.tolerance:
                azimuth=tle.getAzimuth(datetime.utcnow())+self.tolerance
                azi.join()
                azi = Antenna("Azimuth", azimuth)
                azi.start()
            elif tle.getAzimuth(datetime.utcnow())<azimuth-self.tolerance:
                azimuth=tle.getAzimuth(datetime.utcnow())-self.tolerance
                azi.join()
                azi = Antenna("Azimuth", azimuth)
                azi.start()
            if tle.getElevation(datetime.utcnow())>elevation+self.tolerance:
                elevation=tle.getElevation(datetime.utcnow())+self.tolerance
                ele.join()
                ele = Antenna("Elevation",elevation)
                ele.start()
            elif tle.getElevation(datetime.utcnow())<elevation-self.tolerance:
                elevation=tle.getElevation(datetime.utcnow())-self.tolerance
                ele.join()
                ele = Antenna("Elevation",elevation)
                ele.start()
        print('tracking ends')
                
    def trackSatellite(self,starttime,endtime,tle):
        timeDifference = starttime-time.time()
        endtime=endtime+timeDifference
        azimuth=tle.getAzimuth(datetime.utcfromtimestamp(starttime))
        aziGetter = Antenna("Azimuth",azimuth)
        aziGetter.start()
        elevation=tle.getElevation(datetime.utcfromtimestamp(starttime))
        ele = Antenna("Elevation",elevation)
        ele.start()  
        while ((time.time()+timeDifference)<endtime):
            if tle.getAzimuth(datetime.utcfromtimestamp(time.time()+timeDifference))<azimuth-5 or tle.getAzimuth(datetime.utcfromtimestamp(time.time()+timeDifference))>azimuth+5:
                print("entered azi")
                azimuth=tle.getAzimuth(datetime.utcfromtimestamp(time.time()+timeDifference))
                aziGetter = Antenna("Azimuth",azimuth)
                aziGetter.start()
            if tle.getElevation(datetime.utcfromtimestamp(time.time()+timeDifference))>elevation+5 or tle.getElevation(datetime.utcfromtimestamp(time.time()+timeDifference))<elevation-5:
                print("entered ele")
                elevation=tle.getElevation(datetime.utcfromtimestamp(time.time()+timeDifference))
                ele = Antenna("Elevation",elevation)
                ele.start() 
                
        print("FINISHED EXECUTION")  
        
class runSchedule(threading.Thread):
    
    def __init__(self,scheduleList,tracker):
        super(runSchedule, self).__init__()
        self.scheduleList=scheduleList
        self.satelliteName=''
        self.aosTime = ''
        self.losTime=''
        self.continueExecutingFlag=True
        self.tracker = tracker
        self.isAOS=True
        
    
    def run(self):
        print(threading.enumerate())
        if self.scheduleList!=None:
            for item in self.scheduleList:
                if self.continueExecutingFlag==True:
                    self.satelliteName = item.getSatName()
                    self.tle = item.getTLE()
                    self.aosTime = item.getStartTime()
                    self.isAOS=True
                    self.tracker.positionAntenna(self.aosTime,self.tle)
                    self.losTime = item.getEndTime()
                    while self.continueExecutingFlag==True and time.time()<time.mktime(self.losTime.timetuple()):
                        time.sleep(1)
                    if self.continueExecutingFlag==False:
                        return
                    self.isAOS=False
                    self.tracker.trackSatellite2(time.mktime(self.losTime.timetuple()),self.tle)
                    print('moving on to the next satellite')
                                
    
    def getCurrentSatName(self):
        return self.satelliteName
    
    def getScheduleList(self):
        return self.scheduleList
    
    def stopExecuting(self):
        self.continueExecutingFlag=False
    
    def getCurrentAzimuth(self):
        return self.tle.getAzimuth(datetime.now())
    
    def getCurrentElevation(self):
        return self.tle.getElevation(datetime.now())
    
    def getIsAOS(self):
        return self.isAOS
    
    def getSchedulerInstance(self):
        return self.s
    
    def getFlag(self):
        return self.continueExecutingFlag
    
    def getCurrentAOSLOSTime(self):
        if self.isAOS==True:
            return self.aosTime
        else:
            return self.losTime

            
        
class main:
    
    
    
   
    tlefile.fetch('/home/stacstation/eclipse-workspace/tle.txt')
    file = open('/home/stacstation/eclipse-workspace/tle.txt')
    buffer = [] 
    i=0
    for line in file:
        buffer.append(line)
        i+=1
        if i==3:
            fileout = open('/home/stacstation/eclipse-workspace/%s.txt'%(buffer[0].strip()),"w")
            for item in buffer:
                fileout.write(item)
            i=0
            buffer=[]
    """
    sat1 = 'LQSAT'
    sat2 = 'UKUBE-1'
    path = ['/home/stacstation/eclipse-workspace/%s.txt'%(sat1), '/home/stacstation/eclipse-workspace/%s.txt'%(sat2)]
    tle = TLE(path[1])
    passover = tle.nextPass()
    tuple1=(2018, 1, 10, 16, 53,32,919902)
    ele = tle.getElevation(datetime(*tuple1))
    
    #helper.getAzimuth()
    #helper.getElevation()
    #aziThread = Antenna("Azimuth",azi)
    #eleThread = Antenna("Elevation",ele)
    #aziThread.start()
    #eleThread.start()
    #print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    #s=sched.scheduler(time.time,time.sleep)
    #s.enterabs(time.time(), 1, tracker.trackSatellite, (time.mktime(passover[0].timetuple()),time.time()+180,orb,tle))
   # time.mktime(passover[0].timetuple())
  #  s.run()
    """
   
    
    
    
    
    
    
        
Main = main()
