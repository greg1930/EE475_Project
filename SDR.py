'''
Created on 13 Mar 2018

@author: gregstewart96
'''


class Main:
    
    def __init__(self,root=None):
        self.name = None
        self.endtime = None
    
    def update(self,queue):
        while True:
            print('SDR Here')
            name = queue.get()
            endTime = queue.get()
            print('name',name)
            print('end time',endTime)
        """
        self.name = name
        self.endtime = endtime
        print(self.name)
        print(self.endtime)
        """
        
    