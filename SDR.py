'''
Created on 13 Mar 2018

@author: gregstewart96
'''


class Main:
    
    def __init__(self):
        self.name = None
        self.endtime = None
    
    def update(self,name,endtime):
        self.name = name
        self.endtime = endtime
        print(self.name)
        print(self.endtime)
        
    