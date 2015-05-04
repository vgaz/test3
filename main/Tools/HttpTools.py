#!/opt/softs/workshop/current/bin/python
# -*- coding: utf-8 -*-
'''
Created on Mar 16, 2010

@author: vgazeill
'''

import logging
LOGGIN_FORMAT = '[TestCI_%(levelname)-8s] %(module)-15s.%(funcName)s: %(message)s'
logging.basicConfig(format=LOGGIN_FORMAT, level=logging.DEBUG)


import urllib2



def urlToFile(urlStr, outputFile):
    
    hLog = open(outputFile, 'w')
    if not hLog: 
        return(False, "Cant't write output file %s" % (outputFile))
    
    try:
        fileHandle = urllib2.urlopen(urlStr)
        for line in fileHandle.readlines():
            hLog.write(line)
        fileHandle.close()
    
    except IOError:
        return  (False, 'Cannot open URL %s for reading' % (urlStr))
    
    finally:
        if hLog: 
            hLog.close()
    
    return (True, urlStr)


def isValidURL(url):
    
    req = urllib2.Request(url)
    try:
        urllib2.urlopen(req).readlines()
        return True
        
    except IOError:
        return False
    
    
    try:
        f = urllib2.urlopen(url)
        if f:
            f.close
            return True
    except:
        return False
    

#if __name__ == '__main__':
#
#    print str(urlToFile('http://nux08080:8085/job/CSATG5_functional/3164/console',
#              '/local/tmpAtt/log.txt'))
#    
#    
#   
#            
    