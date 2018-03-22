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
from Queue import Queue
import sched
import time
import operator

from datetime import timedelta


class TLE:
    """class to create an instance of pyorbital's 'Orbital' class and provide helper methods to 
       access the name,azimuth,elevation and passover periods for the satellite corresponding to
       the TLE file passed in
    """
    def __init__(self,path,duration):
        self.lat = 55.8667
        self.lon = -4.4333
        self.alt = 125
        self.duration = duration
        f = open("%s" % path,'r')
        sat = f.readline()
        line1 = f.readline()
        line2 = f.readline()
        self.orb = orbital.Orbital(sat,path,line1,line2)
        
  
    def getAzimuth(self,time):
        """ returns element 0 of get_observer_look which contains the azimuth
            The result will be dependent on the datetime object 'time'
        """
        azi = self.orb.get_observer_look(time, self.lon, self.lat,self.alt)
        return azi[0]
        
    def getElevation(self,time):
        """ returns element 1 of get_observer_look which contains the elevation
            The result will be dependent on the datetime object 'time'
        """
        ele = self.orb.get_observer_look(time, self.lon, self.lat,self.alt)
        return ele[1]
    
    def nextPasses(self):
        """
        returns a list of lists containing the start time, end time and max elevation of the periods
        the satellite will be in line of site of the ground station.
        """
        now = datetime.utcnow()
        nextPass = self.orb.get_next_passes(now,self.duration,self.lon,self.lat,self.alt,-0.358,0.001)
        return nextPass
    

    
class Antenna(threading.Thread):
    def __init__(self,threadID,q):
        super(Antenna, self).__init__()
        """
        self.portA='/dev/ttyUSB0'
        self.portE='/dev/ttyUSB1'
        """
        self.baud=9600
        self.parity='N'
        self.databits=8
        self.stopbits=1
        self.rtscts=0
        self.timeout='None'
        self.xonxoff=0
        self.threadID=threadID
        self.queue = q
      
        """
        self.serA=serial.Serial(port=self.portA, baudrate=self.baud, parity=self.parity, 
                      bytesize=self.databits, stopbits=self.stopbits, 
                      rtscts=self.rtscts, timeout=0.5,
                      xonxoff=self.xonxoff)
        self.serE=serial.Serial(port=self.portE, baudrate=self.baud, parity=self.parity, 
                      bytesize=self.databits, stopbits=self.stopbits, 
                      rtscts=self.rtscts, timeout=0.5,
                      xonxoff=self.xonxoff)
        """
        
    def run(self): #https://stackoverflow.com/questions/13481276/threading-in-python-using-queue
        while True:
            value = self.queue.get()
            if value == None:
                break
            else:
                if self.threadID=='Azimuth':
                    self.updateAzimuth(value)
                elif self.threadID=='Elevation':
                    self.updateElevation(value)        
    
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
        print('azi')
        print(azi)
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
        if ele<0.1:
            ele=0
        elif ele>90:
            ele = 90
        print('ele')
        print(ele)
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
    """This method contains getter and setter function for each of the required characteristics
       of a satellite passover
    """
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
    """ This class contains methods, to create passovers, sort passovers, detect and fix passover
        clashes, calculate the antenna rotation time, position the antenna and track a satellite
    """
    
    def __init__(self,tolerance,duration):
        self.tolerance = tolerance
        self.duration = duration
        
    def schedule(self,satelliteList):
        passovers=[] #list for holding Passover class instances
        #loop through all the tles we want to track
        for name,priority in satelliteList.iteritems(): 
            #path to the relevant TLE file
            path = '/Users/gregstewart96/stacstation/eclipse-workspace/%s.txt'%(name) 
            f = open("%s" % path,'r') #open the TLE file
            satName = f.readline() #read line 1
            satName = satName.split(' ',1)[0]#get rid of whitespace in line 1
            tle=TLE(path,self.duration) #create tle instance
            #get a tuple containing passovers of the satellite
            allPasses = tle.nextPasses() 
            #loop through all the satellites passovers
            for passes in allPasses: 
                #create a Passover instance for each passover
                passover = Passover(tle,passes[0],passes[1],satName,priority) 
                #add Passover instance to the list.
                passovers.append(passover)
        #sort passover based on the start time
        passovers = sorted(passovers, key=lambda passover: passover.getStartTime()) 
        
        passovers = self.longestPhase(passovers)
        passovers = sorted(passovers, key=lambda passover: passover.getStartTime())
        
        for item in passovers:
            
            print(item.getSatName())
            print(item.getPriority())
            print(item.getStartTime())
            print(item.getEndTime())
            print(item.getTLE().getAzimuth(item.getStartTime()))
            print(item.getTLE().getAzimuth(item.getEndTime()))
            print
        
        
        for i in range(0,5):
            passovers,clashCount = self.clashDetect(passovers)
            passovers = sorted(passovers, key=lambda passover: passover.getStartTime())
            if clashCount==0: break
            
        #return clashCount
        
        
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
        """ find the longest phase and adjust the passover accordingly.
        """
        # loop through each passover
        for passes in passovers:
            passoverStart = passes.getStartTime()
            passoverEnd = passes.getEndTime()
            tle = passes.getTLE()
            #get azi0 point
            azi0=self.azimuthZero(passoverStart, passoverEnd,tle)
            #get the size of phase1
            phase1=time.mktime(azi0.timetuple())-(time.mktime(passoverStart.timetuple()))
            #get the size of phase2
            phase2=time.mktime(passoverEnd.timetuple())-(time.mktime(azi0.timetuple())+1)
            #if phase 1 is longer
            if phase1>=phase2:
                print('phase1 chosen. phase1 %.2f ........ phase2 %.2f' % (phase1,phase2))
                #set end time to azi0.
                passes.setEndTime(azi0)
            #if phase 2 is longer
            elif phase2>phase1:
                print('phase2')
                #set start time to one second after azi0
                passes.setStartTime(azi0+timedelta(seconds=1))
        return passovers
    
    def longestPhase2(self,passovers):
        for passes in passovers:
            passoverStart = passes.getStartTime()
            passoverEnd = passes.getEndTime()
            tle = passes.getTLE()
            name = passes.getSatName()
            priority = passes.getPriority()
            azi0=self.azimuthZero(passoverStart, passoverEnd,tle)
            phase1=time.mktime(azi0.timetuple())-(time.mktime(passoverStart.timetuple()))
            phase2=time.mktime(passoverEnd.timetuple())-(time.mktime(azi0.timetuple())+1)
            if phase1>0 and phase2>0:
                passes.setEndTime(azi0)
                passovers.append(Passover(tle,azi0+timedelta(seconds=1),passoverEnd,name,priority))
            elif phase1>0:
                passes.setEndTime(azi0)
            elif phase2>0: 
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
                    """
                    print('case 1')
                    print(startTime)
                    print(item.getStartTime())
                    """
                    oldEndTime = item.getEndTime()
                    if priority<item.getPriority():
                        time = startTime
                        while time>item.getStartTime():
                            transferTime = self.calculateTime(item.getTLE().getAzimuth(time), tle.getAzimuth(startTime), item.getTLE().getElevation(time), tle.getElevation(startTime))
                            if (time+timedelta(seconds=transferTime)) < startTime: 
                                item.setEndTime(time)
                                break
                            time = time - timedelta(seconds=1)
                        if item.getEndTime()==oldEndTime:
                            clashChecked.remove(item)
        
                    elif priority>item.getPriority():
                        if item.getEndTime() + timedelta(seconds=case_one_transfer_time)<endTime:
                            startTime = item.getEndTime()+timedelta(seconds=case_one_transfer_time)+timedelta(seconds=1)
                        else:
                            return clashChecked,clashCount
                    else:
                        optimise = self.optimisePassover(item, passover, 0)
                        item.setEndTime(optimise[0])
                        startTime = optimise[1]   
                        
                        
                        
    
                elif startTime>item.getStartTime() and item.getEndTime()>startTime and item.getEndTime()>endTime:
                    clashCount+=1
                    """
                    print('case 2')
                    print(startTime)
                    print(item.getStartTime())
                    """
                    if priority<item.getPriority():
                        time=startTime
                        while time>item.getStartTime():
                            transferTime = self.calculateTime(item.getTLE().getAzimuth(time), tle.getAzimuth(startTime), item.getTLE().getElevation(time), tle.getElevation(startTime))
                            if (time+timedelta(seconds=transferTime)) < startTime: break
                            time -= timedelta(seconds=1)
                        time2 = item.getEndTime()
                        while time2>endTime:
                            transferTime = self.calculateTime(item.getTLE().getAzimuth(time2),tle.getAzimuth(endTime),item.getTLE().getElevation(time2),tle.getElevation(endTime))
                            if time2 - timedelta(seconds=transferTime) < endTime:
                                if time2==item.getEndTime(): break
                                time2 += timedelta(seconds=1)
                                clashChecked.append(Passover(item.getTLE(),time2,item.getEndTime(),item.getSatName(),item.getPriority()))
                                break
                            time2 -= timedelta(seconds=1)
                        item.setEndTime(time)
                        
                    elif priority>item.getPriority():
                        return clashChecked,clashCount
                    
                    else:
                        time = item.getEndTime()
                        while time>endTime:
                            transferTime = self.calculateTime(item.getTLE().getAzimuth(time), tle.getAzimuth(endTime), item.getTLE().getElevation(time), tle.getElevation(endTime))
                            if (time-timedelta(seconds=transferTime))<endTime:
                                if time == item.getEndTime():
                                    endPhase = 0
                                else:
                                    endPhase = (item.getEndTime()-(time+timedelta(seconds=1))).total_seconds()
                                break
                            time=time-timedelta(seconds=1)
                        optimise = self.optimisePassover(item, passover, endPhase)
                        if optimise[0] == item.getStartTime():
                            return clashChecked,clashCount
                        if endPhase>0:
                            clashChecked.append(Passover(item.getTLE(),endTime,item.getEndTime(),item.getSatName(),item.getPriority()))
                        item.setEndTime(optimise[0])
                        startTime = optimise[1]
                        
                    
                    
                        
                elif startTime<item.getStartTime() and endTime>item.getStartTime() and endTime>item.getEndTime():
                    clashCount+=1
                    """
                    print('case 3')
                    print(startTime)
                    print(item.getStartTime())
                    """
                    if priority<item.getPriority():
                        clashChecked.remove(item)
                        
                    elif priority>item.getPriority():
                        time = item.getStartTime()
                        while time>startTime:
                            transferTime = self.calculateTime(tle.getAzimuth(time),item.getTLE().getAzimuth(item.getStartTime()),tle.getElevation(time),item.getTLE().getElevation(item.getStartTime()))
                            if (time + timedelta(seconds=transferTime))<item.getStartTime(): break
                            time = time - timedelta(seconds=1)
                        time2 = endTime
                        while time2>item.getEndTime():
                            transferTime = self.calculateTime(tle.getAzimuth(time2), item.getTLE().getAzimuth(item.getEndTime()), tle.getElevation(time2), item.getTLE().getElevation(item.getEndTime()))
                            if time2-timedelta(seconds=transferTime) < item.getEndTime():
                                if time2==endTime: break
                                time2 += timedelta(seconds=1) 
                                clashChecked.append(Passover(tle,time2,endTime,satName,priority))
                                break
                            time2 -= timedelta(seconds=1)
                        endTime = time
                        
                    else:
                        time = endTime
                        while time>item.getEndTime():
                            transferTime = self.calculateTime(tle.getAzimuth(time), item.getTLE().getAzimuth(item.getEndTime()), tle.getElevation(time), item.getTLE().getElevation(item.getEndTime()))
                            if (time-timedelta(seconds=transferTime))<item.getEndTime():
                                if time==endTime:
                                    endPhase = 0
                                else:
                                    endPhase = (endTime-(time+timedelta(seconds=1))).total_seconds()
                                break
                            time=time-timedelta(seconds=1)
                        optimise = self.optimisePassover(passover, item, endPhase)
                        if optimise[0] == startTime:
                            return clashChecked,clashCount
                        if endPhase>0:
                            clashChecked.append(Passover(tle,item.getEndTime(),endTime,satName,priority))
                        endTime = optimise[0]
                        item.setStartTime(optimise[1])
                        
                        
                    
                elif startTime<item.getStartTime() and (endTime+timedelta(seconds=case_four_transfer_time))>item.getStartTime() and endTime<item.getEndTime():
                    clashCount+=1
                    
                    print('case 4')
                    print(startTime)
                    print(item.getStartTime())
                    
                    if priority<item.getPriority():
                        if endTime + timedelta(seconds=case_four_transfer_time)<item.getEndTime():
                            item.setStartTime(endTime + timedelta(seconds=case_four_transfer_time) + timedelta(seconds=1))
                        else:
                            clashChecked.remove(item)
                    elif priority>item.getPriority():
                        oldEndTime = endTime
                        time = item.getStartTime() 
                        while time>startTime:
                            transferTime = self.calculateTime(tle.getAzimuth(time),item.getTLE().getAzimuth(item.getStartTime()),tle.getElevation(time),item.getTLE().getElevation(item.getStartTime()))
                            if (time + timedelta(seconds=transferTime))<item.getStartTime(): 
                                endTime = time
                                break
                            time -= timedelta(seconds=1)
                        if endTime == oldEndTime:
                            return clashChecked,clashCount
                      
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
            
            percentage = float(len(clashChecked))/float(len(passovers))
            percentage*=100
            #print('%f %% complete'%(percentage))
        print(clashCount)
        return clashChecked,clashCount
        
    
    def optimisePassover(self,firstSatellite,secondSatellite,additionalTime):
        #print('optimise')
        currentTime = firstSatellite.getStartTime()
        optimalTime = None
        firstSatEndTime = firstSatellite.getEndTime()
        secondSatStartTime = secondSatellite.getStartTime()

        while currentTime<firstSatellite.getEndTime():
            
            aziDelta = 0
            eleDelta = 0
            aziOffset = 0
            eleOffset = 0
            i = 0
     
            while True:
                aziTime = self.calculateOneTime(firstSatellite.getTLE().getAzimuth(currentTime),secondSatellite.getTLE().getAzimuth(currentTime+timedelta(seconds=aziDelta)))
                nextOffset = (secondSatellite.getTLE().getAzimuth(currentTime+timedelta(seconds=aziTime))) - (secondSatellite.getTLE().getAzimuth(currentTime+timedelta(seconds=aziDelta)))
                if (aziOffset>0 and nextOffset>aziOffset) or (aziOffset<0 and nextOffset<aziOffset):
                    break
                elif aziOffset<0 and nextOffset>0:
                    if nextOffset-360<aziOffset:
                        break
                    else:
                        aziOffset = nextOffset - 360
                
                elif aziOffset>0 and nextOffset<0:
                    if nextOffset+360>aziOffset:
                        break
                    else:
                        aziOffset = nextOffset + 360
                
                else:
                    aziOffset = nextOffset
                  
        
                aziDelta += self.calculateOneTime(0, abs(aziOffset)) #in seconds
             
                i+=1
                
                if aziOffset < self.tolerance and aziOffset >(self.tolerance*-1):
                    break
                if i>200:
                    print('sleep')
                    time.sleep(1000)
                    time_to_start = self.calculateOneTimeTime(firstSatellite.getTLE().getAzimuth(currentTime),secondSatellite.getTLE().getAzimuth(secondSatellite.getStartTime()))
                    time_to_end = self.calculateOneTime(firstSatellite.getTLE().getAzimuth(currentTime),secondSatellite.getTLE().getAzimuth(secondSatellite.getEndTime()))
                    aziTime = max(time_to_start,time_to_end)
                    break
            i=0
            
            while True:
                eleTime = self.calculateOneTime(firstSatellite.getTLE().getElevation(currentTime),secondSatellite.getTLE().getElevation(currentTime+timedelta(seconds=eleDelta)))
                
                nextOffset = (secondSatellite.getTLE().getElevation(currentTime+timedelta(seconds=eleTime))) - (secondSatellite.getTLE().getElevation(currentTime+timedelta(seconds=eleDelta)))
                
                if (eleOffset>0 and nextOffset>eleOffset) or (eleOffset<0 and nextOffset<eleOffset):
                    break
                
                elif eleOffset<0 and nextOffset>0:
                    if nextOffset-360<eleOffset:
                        break
                    else:
                        eleOffset = nextOffset - 360
                
                elif eleOffset>0 and eleOffset<0:
                    if nextOffset+360>eleOffset:
                        break
                    else:
                        eleOffset = nextOffset + 360
                
                else:
                    eleOffset = nextOffset
              
                
                eleDelta += self.calculateOneTime(0, abs(eleOffset)) #in seconds
                
                i+=1
                
                if eleOffset < self.tolerance and eleOffset >(self.tolerance*-1):
                    break
                if i>200:
                    print('sleep')
                    time.sleep(1000)
                    time_to_start = self.calculateOneTime(firstSatellite.getTLE().getElevation(currentTime),secondSatellite.getTLE().getElevation(secondSatellite.getStartTime()))
                    time_to_end = self.calculateOneTime(firstSatellite.getTLE().getElevation(currentTime),secondSatellite.getTLE().getElevation(secondSatellite.getEndTime()))
                    eleTime = max(time_to_start,time_to_end)
                    break
        
            transferTime = max(aziTime,eleTime)
            if currentTime + timedelta(seconds=transferTime) >= secondSatellite.getStartTime() and currentTime + timedelta(seconds=transferTime)<=secondSatellite.getEndTime():
                firstSatPassover = (currentTime - firstSatellite.getStartTime()).total_seconds() + additionalTime
                secondSatPassover = currentTime+timedelta(seconds=transferTime)
                secondSatPassover = (secondSatellite.getEndTime()-secondSatPassover).total_seconds()
                timeDifference = max(firstSatPassover,secondSatPassover) - min(firstSatPassover,secondSatPassover)
                if timeDifference<optimalTime or optimalTime==None:
                    optimalTime=timeDifference
                    firstSatEndTime = currentTime
                    secondSatStartTime = currentTime + timedelta(seconds=transferTime)
                    error = self.calculateOneTime(0,self.tolerance)
                    secondSatStartTime += timedelta(seconds=error)
        
            currentTime = currentTime + timedelta(seconds=1)
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
        
    def calculateOneTime(self,start,end):
        delta = abs(end-start)
        if delta<29:
            time = delta/1.32
        else:
            time = ((delta-30)/2.1)+19
        return time
            

    def azimuthZero(self,starttime,endtime,tle):
        """ Return the second before the azimuth crosses the 0 to 360 point, no matter if the azimuth
            is increasing or decreasing
        """
        times = starttime #set the time variable to the start time
        while True: #loop indefinitely
            #if the satellite is less than one now and greater than 359 one second later
            if (tle.getAzimuth(times))<1 and tle.getAzimuth((times+timedelta(seconds=1)))>359:
                return times #return time variable
            #if the satellite is greater than 359 and less than 1 one second later
            elif tle.getAzimuth(times)>359 and tle.getAzimuth((times+timedelta(seconds=1)))<1:
                return times 
            #if the time is greater than the end time, the azimuth must not have crossed the point at all
            elif time.mktime(times.timetuple())>time.mktime(endtime.timetuple()):
                return endtime
            else: #if nothing returned
                times += timedelta(seconds=1) #increment time variable by one second
    
        
            
        
    
    def positionAntenna(self,starttime,tle):
        print('position')
        aziQ = Queue()
        aziQ.put(tle.getAzimuth(starttime))
        azi = Antenna("Azimuth",aziQ)
        azi.start()
        aziQ.put(None)
        eleQ = Queue()
        eleQ.put(tle.getElevation(starttime))
        ele = Antenna("Elevation",eleQ)
        ele.start()  
        eleQ.put(None)
        azi.join()
        ele.join()
        print('position finished')
          
    def trackSatellite2(self,endtime,tle):
        print('track start')
        aziQ = Queue()
        eleQ = Queue()
        azi = Antenna("Azimuth", aziQ)
        azi.start()
        ele = Antenna("Elevation",eleQ)
        ele.start()
        azimuth=tle.getAzimuth(datetime.utcnow())
        elevation=tle.getElevation(datetime.utcnow())
        while time.time()<time.mktime(endtime.timetuple()):
            if tle.getAzimuth(datetime.utcnow())>azimuth+self.tolerance:
                azimuth=tle.getAzimuth(datetime.utcnow())+self.tolerance
                if azimuth>tle.getAzimuth(endtime):
                    azimuth = tle.getAzimuth(endtime)
                aziQ.queue.clear()
                aziQ.put(azimuth)
            elif tle.getAzimuth(datetime.utcnow())<azimuth-self.tolerance:
                azimuth=tle.getAzimuth(datetime.utcnow())-self.tolerance
                if azimuth<tle.getAzimuth(endtime):
                    azimuth = tle.getAzimuth(endtime)
                aziQ.queue.clear()
                aziQ.put(azimuth)
            if tle.getElevation(datetime.utcnow())>elevation+self.tolerance:
                elevation=tle.getElevation(datetime.utcnow())+self.tolerance
                if elevation > 90:
                    elevation = 90
                eleQ.queue.clear()
                eleQ.put(elevation)
            elif tle.getElevation(datetime.utcnow())<elevation-self.tolerance:
                elevation=tle.getElevation(datetime.utcnow())-self.tolerance
                if elevation < 0:
                    elevation = 0
                eleQ.queue.clear()
                eleQ.put(elevation)
                
        aziQ.put(None)
        eleQ.put(None)
        azi.join()
        ele.join()
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
                    self.losTime = item.getEndTime()
                    self.isAOS=True
                    self.tracker.positionAntenna(self.aosTime,self.tle)
                    while self.continueExecutingFlag==True and time.time()<time.mktime(self.aosTime.timetuple()):
                        time.sleep(1)
                    print('stopped sleeping')
                    print('flag',self.continueExecutingFlag)
                    if self.continueExecutingFlag==False:
                        return
                    self.isAOS=False
                    self.tracker.trackSatellite2(self.losTime,self.tle)
                    print('moving on to the next satellite')
            self.isAOS=True
                                
    
    def getCurrentSatName(self):
        return self.satelliteName
    
    def getTLE(self):
        return self.tle
    
    def getAOS(self):
        return self.aosTime
    
    def getLOS(self):
        return self.losTime
    
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
  
    def getFlag(self):
        return self.continueExecutingFlag
    
    def getCurrentAOSLOSTime(self):
        if self.isAOS==True:
            return self.aosTime
        else:
            return self.losTime

            
        
class TLEUpdate:
    
    def update(self,urls):
            
        tlefile.fetch('/Users/gregstewart96/stacstation/eclipse-workspace/tle.txt',urls)
        file = open('/Users/gregstewart96/stacstation/eclipse-workspace/tle.txt')
        buffer = [] 
        i=0
        for line in file:
            buffer.append(line)
            i+=1
            if i==3:
                fileout = open('/Users/gregstewart96/stacstation/eclipse-workspace/%s.txt'%(buffer[0].strip()),"w")
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
   
    
    
    
    
    
    
        
tle = TLEUpdate()
tle.update(('http://celestrak.com/NORAD/elements/amateur.txt','http://celestrak.com/NORAD/elements/engineering.txt'))

