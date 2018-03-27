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
from Queue import Queue


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
    """
    The antenna class is a thread responsible for sending 
    commands to the antenna controllers
    """
    def __init__(self,threadID,q):
        super(Antenna, self).__init__()
        """Azimuth controller port"""
        self.portA='/dev/ttyUSB0' 
        """Elevation controller port"""
        self.portE='/dev/ttyUSB1'
        """serial settings"""
        self.baud=9600
        self.parity='N'
        self.databits=8
        self.stopbits=1
        self.rtscts=0
        self.timeout='None'
        self.xonxoff=0
        
        self.threadID=threadID
        self.queue = q
        
        self.serA=serial.Serial(port=self.portA, baudrate=self.baud, parity=self.parity, 
                      bytesize=self.databits, stopbits=self.stopbits, 
                      rtscts=self.rtscts, timeout=0.1,
                      xonxoff=self.xonxoff)
        self.serE=serial.Serial(port=self.portE, baudrate=self.baud, parity=self.parity, 
                      bytesize=self.databits, stopbits=self.stopbits, 
                      rtscts=self.rtscts, timeout=0.1,
                      xonxoff=self.xonxoff)
        
        
    def run(self): 
        """continuously loop checking for new value placed in queue"""
        while True:
            value = self.queue.get()
            """ None indicates the tracking is complete so stop looping"""
            if value == None:
                self.serA.close()
                self.serE.close()
                break
            else:
                if self.threadID=='Azimuth':
                    self.updateAzimuth(value)
                elif self.threadID=='Elevation':
                    self.updateElevation(value)        
    
    def updateAzimuth(self,azi):
        if azi<0.1 and azi>-0.1:
            azi=0
        if azi>348:
            azi=348.0
        """join A with value"""
        azi=''.join(['A',str(azi)])
        """send to azimuth controller"""
        self.serA.write(b'%s\r' % azi)
        self.serA.read()
        
            
        
    def updateElevation(self,ele):
        """repeat for elevation controller"""
        if ele<0.1:
            ele=0
        elif ele>90:
            ele = 90
        print('ele')
        print(ele)
        ele=''.join(['E',str(ele)])
        self.serE.write(b'%s\r' % ele)
        self.serE.read()
        
        
        
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
            path = '/home/stacstation/eclipse-workspace/%s.txt'%(name) 
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
        """check for crossing of 0degree point"""
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
        
        """check for clashes 4 times to reduce chance of remaining clashes"""
        """test purposes
        firstCount = 0
        """
        for i in range(0,5):
            passovers,clashCount = self.clashDetect(passovers)
            """test purposes
            if i==0:
                firstCount=clashCount
            """
            passovers = sorted(passovers, key=lambda passover: passover.getStartTime())
            if clashCount==0: break
        
        """for use with test method   
        return clashCount,firstCount
        """
        
        for item in passovers:
            
            print(item.getSatName())
            print(item.getPriority())
            print(item.getStartTime())
            print(item.getEndTime())
            print(item.getTLE().getAzimuth(item.getStartTime()))
            print(item.getTLE().getAzimuth(item.getEndTime()))
            print
        
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
  
    
    def compare(self,passover,clashChecked,clashCount):
        """sat 1 values"""
        startTime = passover.getStartTime()
        endTime = passover.getEndTime()
        priority = passover.getPriority()
        satName = passover.getSatName()
        tle = passover.getTLE()
        """no need check if it's the first element"""
        if len(clashChecked)!=0:
            for item in clashChecked:
                """antenna rotation time for case1"""
                case_one_transfer_time = self.calculateTime(item.getTLE().getAzimuth(item.getEndTime()), tle.getAzimuth(startTime), item.getTLE().getElevation(item.getEndTime()), tle.getElevation(startTime))
                """antenna rotation time for case4"""
                case_four_transfer_time = self.calculateTime(tle.getAzimuth(endTime), item.getTLE().getAzimuth(item.getStartTime()), tle.getElevation(endTime), item.getTLE().getElevation(item.getStartTime()))
                if startTime>item.getStartTime() and (item.getEndTime()+timedelta(seconds=case_one_transfer_time))>startTime and item.getEndTime()<endTime:
                    clashCount+=1
                    oldEndTime = item.getEndTime()
                    """if of higher priority"""
                    if priority<item.getPriority():
                        time = startTime
                        """find point where we need to transfer from tracking one satellite to another"""
                        while time>item.getStartTime():
                            transferTime = self.calculateTime(item.getTLE().getAzimuth(time), tle.getAzimuth(startTime), item.getTLE().getElevation(time), tle.getElevation(startTime))
                            if (time+timedelta(seconds=transferTime)) < startTime: 
                                item.setEndTime(time)
                                break
                            time = time - timedelta(seconds=1)
                        """if no time to track sat2 before sat 1"""
                        if item.getEndTime()==oldEndTime:
                            clashChecked.remove(item)
                        
                        """if of lower priority"""
                    elif priority>item.getPriority():
                        if item.getEndTime() + timedelta(seconds=case_one_transfer_time)<endTime:
                            startTime = item.getEndTime()+timedelta(seconds=case_one_transfer_time)+timedelta(seconds=1)
                        else:
                            return clashChecked,clashCount
                        
                        """if of equal priority"""
                    else:
                        optimise = self.optimisePassover(item, passover, 0)
                        item.setEndTime(optimise[0])
                        startTime = optimise[1]   
                        
                        
                        
    
                elif startTime>item.getStartTime() and item.getEndTime()>startTime and item.getEndTime()>endTime:
                    clashCount+=1
                    """case2"""
                    if priority<item.getPriority():
                        time=startTime
                        """find point where we need to transfer from tracking sat2 to sat1"""
                        while time>item.getStartTime():
                            transferTime = self.calculateTime(item.getTLE().getAzimuth(time), tle.getAzimuth(startTime), item.getTLE().getElevation(time), tle.getElevation(startTime))
                            if (time+timedelta(seconds=transferTime)) < startTime: break
                            time -= timedelta(seconds=1)
                        time2 = item.getEndTime()
                        """find point where we can go back to sat2 after sat1"""
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
                        """don't add sat1 to clash checked as it isn't possible to track sat1"""
                        return clashChecked,clashCount
                    
                    else:
                        time = item.getEndTime()
                        """find how much of sat2 we can capture after sat1"""
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
                    case3
                    """
                    if priority<item.getPriority():
                        """not possible to track sat2"""
                        clashChecked.remove(item)
                        
                    elif priority>item.getPriority():
                        time = item.getStartTime()
                        """find point we need to stop tracking sat1 and start tracking sat2"""
                        while time>startTime:
                            transferTime = self.calculateTime(tle.getAzimuth(time),item.getTLE().getAzimuth(item.getStartTime()),tle.getElevation(time),item.getTLE().getElevation(item.getStartTime()))
                            if (time + timedelta(seconds=transferTime))<item.getStartTime(): break
                            time = time - timedelta(seconds=1)
                        time2 = endTime
                        """find point we can resume tracking sat1 after sat2"""
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
                        """find how long of sat1 can be captured after sat2"""
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
                    """case4"""
                    if priority<item.getPriority():
                        """find time we can start tracking sat2"""
                        if endTime + timedelta(seconds=case_four_transfer_time)<item.getEndTime():
                            item.setStartTime(endTime + timedelta(seconds=case_four_transfer_time) + timedelta(seconds=1))
                        else:
                            clashChecked.remove(item)
                    elif priority>item.getPriority():
                        oldEndTime = endTime
                        time = item.getStartTime() 
                        """find time we need to move from tracking sat1 to sat2"""
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
        """list of passovers free from clashes"""
        clashChecked = []
        clashCount = 0
        for passover in passovers:
            """check passover against passovers already in 
               clashChecked list for clashes"""
            clashChecked,clashCount = self.compare(passover,clashChecked,clashCount)
        print(clashCount)
        return clashChecked,clashCount
        
    
    def optimisePassover(self,firstSatellite,secondSatellite,additionalTime):
        """try and make both passovers as equal as possible"""
        currentTime = firstSatellite.getStartTime()
        optimalTime = None
        firstSatEndTime = firstSatellite.getEndTime()
        secondSatStartTime = secondSatellite.getStartTime()
        """find the transfer time between two passovers during any point in the passover
           need to try and guess accurately where the satellite we're moving to will be
           when we get to it. Try and make a better guess each time
        """
        while currentTime<firstSatellite.getEndTime():
            """difference between guess and actual value in seconds"""
            aziDelta = 0
            eleDelta = 0
            """difference between guess and actual value in degrees"""
            aziOffset = 0
            eleOffset = 0
            i = 0
            
            """azimuth first"""
            while True:
                """transfer time between sat1 and guess end position of sat2"""
                aziTime = self.calculateOneTime(firstSatellite.getTLE().getAzimuth(currentTime),secondSatellite.getTLE().getAzimuth(currentTime+timedelta(seconds=aziDelta)))
                """find the difference between the actual position of sat2 and the guess"""
                nextOffset = (secondSatellite.getTLE().getAzimuth(currentTime+timedelta(seconds=aziTime))) - (secondSatellite.getTLE().getAzimuth(currentTime+timedelta(seconds=aziDelta)))
                """check for weird differences between this offset and the previous offset to prevent
                   cases of going from 0degrees to 360degrees etc. Or if the offset is bigger
                   than the previous one"""
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
                        """if all is good, make this our current offset"""
                else:
                    aziOffset = nextOffset
                  
                    """translate this angle to antenna transfer time
                       add to previous offset"""
                aziDelta += self.calculateOneTime(0, abs(aziOffset)) #in seconds
             
                i+=1
                
                """check if the offset is within the user specified tolerance"""
                if aziOffset < self.tolerance and aziOffset >(self.tolerance*-1):
                    break
                """if we've went round more than 200 times, something has went 
                   wrong...backup plan!"""
                if i>200:
                    """calculate time from current sat1 position to the start point of sat2"""
                    time_to_start = self.calculateOneTimeTime(firstSatellite.getTLE().getAzimuth(currentTime),secondSatellite.getTLE().getAzimuth(secondSatellite.getStartTime()))
                    """calculate time from current sat1 position to the end point of sat2 passover"""
                    time_to_end = self.calculateOneTime(firstSatellite.getTLE().getAzimuth(currentTime),secondSatellite.getTLE().getAzimuth(secondSatellite.getEndTime()))
                    """take the largest one, logic being that sat2 should be somewhere in between"""
                    aziTime = max(time_to_start,time_to_end)
                    break
            i=0
            
            """repeat process for elevation"""
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
            
            """the biggest is the transferTime we use"""
            transferTime = max(aziTime,eleTime)
            """ensure that if we move now, we will land during the sat2 passover"""
            if currentTime + timedelta(seconds=transferTime) >= secondSatellite.getStartTime() and currentTime + timedelta(seconds=transferTime)<=secondSatellite.getEndTime():
                """if we move now"""
                """first passover length, taking into account the additionalTime"""
                firstSatPassover = (currentTime - firstSatellite.getStartTime()).total_seconds() + additionalTime
                secondSatPassover = currentTime+timedelta(seconds=transferTime)
                secondSatPassover = (secondSatellite.getEndTime()-secondSatPassover).total_seconds()
                """find the difference between the two passover durations"""
                timeDifference = max(firstSatPassover,secondSatPassover) - min(firstSatPassover,secondSatPassover)
                """if the difference if smaller than one we've seen before, this is the current
                   best option"""
                if timeDifference<optimalTime or optimalTime==None:
                    optimalTime=timeDifference
                    firstSatEndTime = currentTime
                    secondSatStartTime = currentTime + timedelta(seconds=transferTime)
                    error = self.calculateOneTime(0,self.tolerance)
                    """so it doesn't get flagged in future checks"""
                    secondSatStartTime += timedelta(seconds=error)
            """generate next possibility"""
            currentTime = currentTime + timedelta(seconds=1)
        return [firstSatEndTime,secondSatStartTime]
    
    def calculateTime(self,aziStart,aziEnd,eleStart,eleEnd):
        """calculate the transfer time for both azimuth
           and elevation. Return the largest"""
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
        """same as above but only for
           either azimuth or elevation
        """
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
        """send antenna to a positon"""
        """queue for thread"""
        aziQ = Queue()
        """add value to queue"""
        aziQ.put(tle.getAzimuth(starttime))
        """create thread, pass in queue"""
        azi = Antenna("Azimuth",aziQ)
        azi.start()
        """pass in None, to stop thread
           looping forever"""
        aziQ.put(None)
        eleQ = Queue()
        eleQ.put(tle.getElevation(starttime))
        ele = Antenna("Elevation",eleQ)
        ele.start()  
        eleQ.put(None)
        """wait for threads to stop"""
        azi.join()
        ele.join()
          
    def trackSatellite(self,endtime,tle):
        """to be called when satellite is passing over"""
        aziQ = Queue()
        eleQ = Queue()
        azi = Antenna("Azimuth", aziQ)
        azi.start()
        ele = Antenna("Elevation",eleQ)
        ele.start()
        """get current of satellite azi/ele"""
        azimuth=tle.getAzimuth(datetime.utcnow())
        elevation=tle.getElevation(datetime.utcnow())
        """loop until passover is finished"""
        while time.time()<time.mktime(endtime.timetuple()):
            """check if azimuth is outside tolerance"""
            if tle.getAzimuth(datetime.utcnow())>azimuth+self.tolerance:
                azimuth=tle.getAzimuth(datetime.utcnow())+self.tolerance
                if azimuth>tle.getAzimuth(endtime):
                    azimuth = tle.getAzimuth(endtime)
                """clear queue"""
                aziQ.queue.clear()
                """add new azimuth to queue"""
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
                
    
                
         
        
class runSchedule(threading.Thread):
    """thread to run list of passovers"""
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
        if self.scheduleList!=None:
            for item in self.scheduleList:
                """check controller wishes us to continue executing"""
                if self.continueExecutingFlag==True:
                    self.satelliteName = item.getSatName()
                    self.tle = item.getTLE()
                    self.aosTime = item.getStartTime()
                    self.losTime = item.getEndTime()
                    self.isAOS=True
                    """get antenna into position for next passover"""
                    self.tracker.positionAntenna(self.aosTime,self.tle)
                    """pause until satellite is passing over"""
                    while self.continueExecutingFlag==True and time.time()<time.mktime(self.aosTime.timetuple()):
                        time.sleep(1)
                    """if controller has asked us to stop"""
                    if self.continueExecutingFlag==False:
                        return
                    self.isAOS=False
                    """track satellite"""
                    self.tracker.trackSatellite(self.losTime,self.tle)
                    
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
        """fetch supplied list of urls into tle.txt"""
        tlefile.fetch('/home/stacstation/eclipse-workspace/tle.txt',urls)
        """create separate tle file for each satellite in tle.txt"""
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
        
        
tle = TLEUpdate()
tle.update(('http://celestrak.com/NORAD/elements/amateur.txt','http://celestrak.com/NORAD/elements/engineering.txt'))

