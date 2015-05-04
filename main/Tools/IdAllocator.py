# -*- coding: utf-8 -*-
'''
Created on Mar 11, 2010
@author: vgazeill
@version: 1.01
'''
import logging
LOGGIN_FORMAT = '[TestCI_%(levelname)-8s] %(module)-15s.%(funcName)s: %(message)s'
logging.basicConfig(format=LOGGIN_FORMAT, level=logging.DEBUG)


import os, sys, time
import exceptions
import ConfigParser

ERR_NO_FREE_ITEM = "ERR_NO_FREE_ITEM"

class IdAllocator(object):
    """This class allow user to get/free share id(s) from a collection of keys in a given ini file
    """
       
    def __init__(self, ressourceFile, section):
        """ inputs are :  complete path of ressourceFile (ini file format), section to use"""
        if not os.path.isfile(ressourceFile): raise exceptions.IOError, 'file not found'
        self.ressourceFile = ressourceFile
        logging.info('Initialise. Use file %s' %(self.ressourceFile) )
        self.lockFolder = self.ressourceFile + '.lock'
        self.section = section
        self.TAG_FREE = 'FREE'
        

######################################################################################

    def getFreeItem(self, strBusyReason = "", optionList = None):
        """ inputs :
        reason (optional) will be added to BUSY value if an item is found
        optionList (optional) is a reduced list of options to check 
        return a tuple (True, value) or (False, reason) 
        if no item is available, reason is ERR_NO_FREE_ITEM
        """
        itemToReturn = ""
        ret = False

        try:   

            if optionList != None:
                assert optionList != [], "option list is empty"
                    
            assert os.path.isfile(self.ressourceFile), 'ressourceFile not found ' + self.ressourceFile
                
            assert( self.lock() )
           
            fileParser = ConfigParser.RawConfigParser()
            fileParser.read(self.ressourceFile)
            
            l_optVal = fileParser.items(self.section)

            assert len(l_optVal) > 0, "No item in Section " + str(self.section)
            
            ## By default, set return to ERR_NO_FREE_ITEM
            itemToReturn = ERR_NO_FREE_ITEM
            
            for option, value in l_optVal:
                
                ## do not take option if not in reduced list
                if optionList and option not in optionList:
                    continue
                
                ## find first free item
                if value == self.TAG_FREE:
                    strNewTag = "BUSY since " + time.strftime("%A %d %H:%M") + " for " + strBusyReason
                    logging.info(option + " is available. STB reserved. Status set to '" + strNewTag + "'")
                    # reserve this new adress
                    fileParser.set(self.section, option, strNewTag)
                    ## save file
                    with open(self.ressourceFile, 'w') as hFile:
                        fileParser.write(hFile)
                    itemToReturn = option
                    ret = True
                    break
            

        except ConfigParser.NoSectionError, err :
            ret = False
            itemToReturn = 'getFreeItem, ConfigParser.NoSectionError, err =' %(err)
            logging.info(itemToReturn)

        except ConfigParser.NoOptionError, err:  
            ret = False
            itemToReturn = "getFreeItem, bad option in " + self.ressourceFile + " " + err.option
            logging.info(itemToReturn)
        
        except:
            ret = False
            itemToReturn = __name__ + " "  + str(sys.exc_info()[1])
            logging.info(itemToReturn)        

        finally:
            ## Unlock file
            self.unlock()
       
        return ((ret, itemToReturn))
    
     
######################################################################################
    
        
    def freeAllItems(self):
        """ free all items
        """
        
        if not os.path.isfile(self.ressourceFile):
            logging.info('getFreeItem  , err, not found ' + self.ressourceFile )
            
        self.lock()
        
        try:       
            fileParser = ConfigParser.RawConfigParser()
            fileParser.read(self.ressourceFile)
            
            if not fileParser.has_section(self.section):            
                return True
            
            for option, value in fileParser.items(self.section):
                ## find first free item
                if value != self.TAG_FREE:
                    logging.info(option + ' is busy, set to free' )
                    fileParser.set(self.section, option, self.TAG_FREE)

            ## save file
            hFile = open(self.ressourceFile, 'w')
            if hFile:
                fileParser.write(hFile)
                hFile.close()
                                     
        except ConfigParser.NoSectionError, err :
            logging.info('getFreeItem, ConfigParser.NoSectionError, err =' %(err) )
            return False
            
        except ConfigParser.NoOptionError, err:  
            logging.info("getFreeItem, bad option in " + self.ressourceFile + " " + err.option )
            return False
        
        ## unlock file
        finally:
            self.unlock()
        
        return True
    
######################################################################################
    
    def freeItem(self, itemToRelease):
        """ 
        release reservation for the given item
        """
        if not os.path.isfile(self.ressourceFile):
            logging.info('getFreeItem  , err, not found ' + self.ressourceFile )
            return False
        
        self.lock()
    
        try:            
            fileParser = ConfigParser.RawConfigParser()
            fileParser.read(self.ressourceFile)
            

            for option, value in fileParser.items(self.section):
                ## find first free item
                if option == itemToRelease:
                    
                    if value == self.TAG_FREE:
                        logging.info('Warning , try to free a free option ' + option )
                        break
                        
                    # free the item
                    logging.info(option + ' is now free' )
                    fileParser.set(self.section, option, self.TAG_FREE)
                    ## save file
                    hFile = open(self.ressourceFile, 'w')
                    if hFile:
                        fileParser.write(hFile)
                        hFile.close()
                    break
                    
        except ConfigParser.NoSectionError, err :
            logging.info("bad section in " + self.ressourceFile + " " + err.section )
            return False
            
        except ConfigParser.NoOptionError, err:  
            logging.info("bad option in " + self.ressourceFile + " " + err.option )
            return False
        
        finally:
            ## unlock file
            self.unlock()
        
        return True

    
######################################################################################
    
    def lock(self):
    
        nbTry = 60
    
        ## try to open file
        while (nbTry >0):                             ## as time out
            if os.path.isdir(self.lockFolder):
                logging.info('%s is locked, wait 1 sec' %(self.ressourceFile) )            
                time.sleep(1)                               ## wait one sec before retry
                nbTry -= 1
            else:
                try:
                    os.mkdir(self.lockFolder)           ## lock file, 
                    return True
                except OSError:
                    logging.info('failed to create lock for %s. Reason: %s' %(self.ressourceFile, OSError.strerror) )            
        
        return False                        
    
######################################################################################

    
    def unlock(self):
        if os.path.isdir(self.lockFolder):
            os.rmdir(self.lockFolder)
        else:
            logging.info('Warning , ask for unlock while %s is still unlocked' %(self.lockFolder) )
            

######################################################################################


if __name__ == '__main__':
    
    L1 = ["stb15","stb10","stb6" ]
    alloctor = IdAllocator("/opt/MHADV/preint/ci/Config/AvailableSTBRackDev.ini", "STB_POOL")
    print str( alloctor.getFreeItem(optionList = L1))
    print str( alloctor.getFreeItem(optionList = L1))
    print str( alloctor.getFreeItem(optionList = L1))
    print str( alloctor.getFreeItem(optionList = L1))
    alloctor.freeItem("stb10")