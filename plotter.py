'''
Created on 21 Mar 2018

@author: gregstewart96
'''
'''
Created on 31 Jan 2018

@author: stacstation
'''

import test
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as d


class MyClass:
    
    
    def __init__(self):
        sats = ['LILACSAT 2','XW-2B','XW-2D']
       
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m/%d/%h/%M/%S'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        i=0
        for sat in sats:
            tle=test.TLE('/Users/gregstewart96/stacstation/eclipse-workspace/%s.txt'%(sat),12)
            print(sat)
            for item in tle.nextPasses():
                print(item[0])
                print(item[1])
                x=[item[0],item[1]]
                y=[sat,sat]
                yn = [1,1]
                plt.plot(x,y)
               
            5
                
            
        """  
        endTimes=[item[1] for item in tle.nextPasses()]
        
        lists = sorted(startTimes.items())
        x, y = zip(*lists)
        plt.plot(x,y)
        """
        plt.show()
        
        plt.gcf().autofmt_xdate()
        
   
        
run=MyClass()

