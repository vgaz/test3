# -*- coding: utf-8 -*-
'''
Created on 26 nov. 2009
@author: vgazeill
@version: 2011-01-03
'''

import logging
LOGGIN_FORMAT = '[TestCI_%(levelname)-8s] %(module)-15s.%(funcName)s: %(message)s'
logging.basicConfig(format=LOGGIN_FORMAT, level=logging.DEBUG)

import os.path
import time
import sys, getopt
import shutil

OLD_STRING = '<?xml-stylesheet type="text/xsl" href="http://nuxsmb03.fr.nds.com/mhacdisupport/www/deliveries/mvm_reports/reports/MHAP_DB/ATT/xsl/tableResults10.xsl"?>'
NEW_STRING = '<?xml-stylesheet type="text/xsl" href="http://nuxsmb03.fr.nds.com/mhacdisupport/www/deliveries/mvm_reports/reports/MHAP_DB/ATT/xsl/tableResults9.xsl"?>'

LOGS_ROOT  = '/opt/MHADV/preint/tests/sources/PYATT/Logs'

FOLDER_LIST = ( 
               '/opt/MHADV/preint/ci/CI_Dev/KDGPVR/CIResults',
               
               )

#######################################################################

if __name__ == '__main__':
    
    deleteDirect = False    
    opts = []
    rootFolder = ""
    cleanOK = True
    line = ""
    fileToChange =""
    
    print 'Change file content'

    helpUsage = 'command line usage: use \n\
                -h or --help    to get help \n'
                
    ## get command line parameters 
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hd", ["help", 
                                                        "direct"  ])
        
    except getopt.GetoptError, err:
        print opts
        ## if bad parameter is detected, print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        sys.exit(1)
        
    for option, attribute in opts:

        ## get variables 
        ## display help options if asked
        if option in ("-h", "--help"):
            print helpUsage
            sys.exit(4)


    locTime = time.localtime()[:6]
    logFile = '_'.join(("change_files",
                        str(locTime[0]),
                        str(locTime[1]),
                        str(locTime[2]),
                        str(locTime[3]),
                        str(locTime[4]),
                        str(locTime[5]),
                        ".log"  ))

    hLog = open(os.path.join(LOGS_ROOT, logFile),'w')
    
    for _folder in FOLDER_LIST:

        if not os.path.isdir(_folder):
            print ">>>>>>> error , bad folder definition " + _folder
            cleanOK = False
            break

        print "Scanning %s " %(_folder)
        
        for currentRoot, subDirs, fileList in os.walk(_folder): 
                                 
            for _file in fileList:
                
                fileToChange = os.path.join(currentRoot, _file) 
                 
                if os.path.isfile(fileToChange) and fileToChange.endswith("MHAres.xml"):
                
                    oldFile = fileToChange + '.old'
                    shutil.copy(fileToChange, oldFile)
                    
                    hOldFile = open(oldFile,         "r")
                    try:
                        hNewFile = open(fileToChange,    "w")
                                          
                        for line in hOldFile.xreadlines():
                            if OLD_STRING in line:
                                line = line.replace(OLD_STRING, NEW_STRING)
                                if hLog:
                                    hLog.write("change line in %s\n" %(fileToChange))
                                    
                            hNewFile.write(line)
                            
                    except IOError:
                        print "Error: can't write in  %s" %(fileToChange)                
                    
                    if hOldFile:
                        hOldFile.close()
                    if hNewFile:
                        hNewFile.close()


    if hLog:
        hLog.close()

    print "END"

