# -*- coding: utf-8 -*-
'''
Created on 19 aout 2013
@author: vgazeill
@version: 1.01
'''
import logging
LOGGIN_FORMAT = '[TestCI_%(levelname)-8s] %(module)-15s.%(funcName)s: %(message)s'
logging.basicConfig(format=LOGGIN_FORMAT, level=logging.DEBUG)


import os, time


class MyLockFile(object):
    """This class allow user to lock a file
    """
       
    def __init__(self, filePath, bTakeNow=False, logger=None):
        """ input are :  complete path of ressourceFile to lock"""
        self.lockFolder = filePath + ".lock"
        self.filePath = filePath
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger()

        if bTakeNow:
            self.take()

    
    def take(self):
        nbTry = 60
#         self.logger.debug("try to lock %s" %(self.filePath) )                                

        ## try to open file
        while (nbTry > 0):                        ## as time out
            if os.path.isdir(self.lockFolder):
                self.logger.info('%s is locked, retry in 1 sec' %(self.filePath) )            
                time.sleep(1)                     ## wait one sec before retry
                nbTry -= 1
            else:
                try:
                    os.mkdir(self.lockFolder)       ## lock file
#                     self.logger.debug("%s is locked" %(self.filePath) )                                
                    return True
                except OSError as err:
                    self.logger.warning("Can't create lock for %s. Reason: %s" %(self.filePath, err.strerror) )            
        self.logger.error('failed to create lock for %s'%(self.filePath))
        return False                        
    
    def release(self):
        
#         self.logger.debug("try to unlock %s" %(self.filePath) )                                

        if os.path.isdir(self.lockFolder):
            os.rmdir(self.lockFolder)
        else:
            self.logger.warning('Ask for unlock while %s is still unlocked' %(self.lockFolder) )
            
