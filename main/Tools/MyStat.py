# -*- coding: utf-8 -*-
'''
Created on 12 jan 2015
@author: vgazeill
@version: 1.01
'''
import logging
LOGGIN_FORMAT = '[TestCI_%(levelname)-8s] %(module)-15s.%(funcName)s: %(message)s'
logging.basicConfig(format=LOGGIN_FORMAT, level=logging.DEBUG)


class Stat(object):
    """ Manage tests statistics
    contructor may accept a tupple (cptTestsOk, cptTestsKo, cptTestsNA)"""
    def __init__(self, t_init=None):
        
        if t_init:
            self.cptTestsOk = int(t_init[0])
            self.cptTestsKo = int(t_init[1])
            self.cptTestsNA = int(t_init[2]) ## non applicable neutral ,not run etc..
            self.cptAllTests = self.cptTestsOk + self.cptTestsKo + self.cptTestsNA
        else:
            self.cptTestsOk = 0
            self.cptTestsKo = 0
            self.cptTestsNA = 0      ## non applicable neutral ,not run etc..
            self.cptAllTests = 0
    
    def add(self, cptOk, cptKo=0, cptNA=0):
        """append new test results to current statistic"""
        if cptKo <0 or cptNA<0 or cptOk<0: 
            raise ValueError, "negative value passed"

        self.cptTestsOk += cptOk
        self.cptTestsKo += cptKo
        self.cptTestsNA += cptNA
        self.cptAllTests += cptOk + cptKo + cptNA


    def addOk(self):
        """append new test OK"""
        self.add(1)

    def addKo(self):
        """append new test KO"""
        self.add(0,1)

    def addNA(self):
        """append new test NA"""
        self.add(0,0,1)

    def addStat(self, statIn):
        """append new stat """
        self.add(statIn.cptTestsOk,
                 statIn.cptTestsKo,
                 statIn.cptTestsNA)
        
    def getRatio(self):  
        if self.cptAllTests != 0:
            return int(float(self.cptTestsOk - self.cptTestsNA)/float(self.cptAllTests - self.cptTestsNA) * 100)
        else:
            return 0

    def toString(self):
        """return a string of stat results"""
        return 'nbTestsOk="%d" nbTestsKo="%d" nbTestsNA="%d" nbTests="%d" ratio="%d"'%(  self.cptTestsOk,
                                                                                         self.cptTestsKo,
                                                                                         self.cptTestsNA,
                                                                                         self.cptAllTests,
                                                                                         self.getRatio())
    def __str__(self):
        return self.toString()
    def __rep__(self):
        return self.toString()



class NamedStat(Stat):
    
    def __init__(self, t_init=None, name = ""):
        Stat.__init__(self, t_init)
        self.name = name

    def toString(self):
        """return a string of stat results"""
        return '%s nbTestsOk="%d" nbTestsKo="%d" nbTestsNA="%d" nbTests="%d" ratio="%d"'%(self.name, 
                                                                                          self.cptTestsOk,
                                                                                         self.cptTestsKo,
                                                                                         self.cptTestsNA,
                                                                                         self.cptAllTests,
                                                                                         self.getRatio())    

        