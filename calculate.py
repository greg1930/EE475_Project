'''
Created on 20 Feb 2018

@author: gregstewart96
'''

class MyClass(object):
    '''
    classdocs
    '''

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
        
calc = MyClass()
print(calc.calculateTime(0,360,0,0))
    