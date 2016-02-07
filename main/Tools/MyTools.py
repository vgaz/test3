#!/opt/softs/workshop/current/bin/python
# -*- coding: utf-8 -*-

import logging
LOGGIN_FORMAT = '[%(levelname)-8s] %(module)-15s.%(funcName)s: %(message)s'
logging.basicConfig(format=LOGGIN_FORMAT, level=logging.DEBUG)

"""

Generic Tools

"""
import os, stat
import sys
import shutil, time, datetime
import re
# import ConfigParser

##############################################################################
# remember:    command >> filename 2>&1    Appends both stdout and stderr to the file "filename" ...
# attention, pre_cmd et post_cmd peuvent contenir plusieurs command separées par des ;
# on fera donc (commandeS) >> filename 2>&1

def redirected_command(cmd, my_file):
    """ format the input command to redirect response from stdout and stderr to a given file """
    new_cmd = '{ '+ cmd + ' ; } >> ' + my_file + ' 2>&1'
    
    # Special # comment case
    if cmd.startswith("#"): 
        new_cmd = cmd
    
    return new_cmd

###########################################################################

def getDateTime ():
    return (str(datetime.datetime.now()).replace(" ","--").replace(":","-"))

######################################################################## 

def getDateFrom_y_m_d(s_time):
    if "/" in s_time:
        y,m,d = s_time.split("/")
    if "-" in s_time:
        y,m,d = s_time.split("-")
    _date =  datetime.date(int(y),int(m),int(d))
    return (_date)
    

######################################################################## 

def getDateFrom_d_m_y(s_time):
    if "/" in s_time:
        d,m,y = s_time.split("/")

    if "-" in s_time:
        d,m,y = s_time.split("-")
    if len(y)==2:
        y= "20" + y   # if only 2 digits for year     
    _date =  datetime.date(int(y),int(m),int(d))
    return (_date)

######################################################################## 

def getYMDFromDate(dateIn, sep="-"):
    s_date = dateIn.strftime('%Y-%m-%d')
    if sep != "-":
        s_date = s_date.replace("-", sep)
    return s_date
    
######################################################################## 
    
    
def getFutureDateTime(s_dateTime):
    """return a time according to the futur delay wanted
    some Meta delays are possible : ASAP, NEXT_NIGHT, NEXT_WE, 
    time format for s_dateTime is : IN_XXMIN or IN_YYHR or IN_YYH with XX or YY as parameters 
    """
    
    ## Manage some specific future date 
    if s_dateTime == "ASAP":
        s_dateTime = datetime.datetime.now().strftime('%Y-%m-%d--%H-%M-%S')
    elif s_dateTime == "NEXT_NIGHT":
        s_dateTime = datetime.datetime.now().strftime('%Y-%m-%d--23-00-00')
    elif s_dateTime == "NEXT_WE":
        _now = datetime.datetime.now()
        i_dayInWeek = datetime.datetime.weekday(datetime.datetime.now()) ## 0 is monday
        t2Sec = time.mktime(_now.timetuple()) + 3600 * 24 * (6 - i_dayInWeek)
        t2Date = time.localtime(t2Sec)
        s_dateTime = time.strftime("%Y-%m-%d--00-03-00", t2Date)           
    elif 'HR' in s_dateTime:
        heure = s_dateTime.split('_')[1].split('HR')[0]
        _now = datetime.datetime.now()
        t2Sec = time.mktime(_now.timetuple()) + 3600 * int(heure)
        t2Date = time.localtime(t2Sec)
        s_dateTime = time.strftime("%Y-%m-%d--%H-%M-%S", t2Date)
    elif 'H' in s_dateTime:
        heure = s_dateTime.split('_')[1].split('H')[0]
        _now = datetime.datetime.now()
        t2Sec = time.mktime(_now.timetuple()) + 3600 * int(heure)
        t2Date = time.localtime(t2Sec)
        s_dateTime = time.strftime("%Y-%m-%d--%H-%M-%S", t2Date)
    elif 'MIN' in s_dateTime:
        minutes = s_dateTime.split('_')[1].split('MIN')[0]
        _now = datetime.datetime.now()
        t2Sec = time.mktime(_now.timetuple()) + 60 * int(minutes)
        t2Date = time.localtime(t2Sec)
        s_dateTime = time.strftime("%Y-%m-%d--%H-%M-%S", t2Date)    

    return datetime.datetime.strptime(s_dateTime, "%Y-%m-%d--%H-%M-%S")
    
###########################################################################

def jourApresJour(dateDebut, dateFin):
    ## generateur renvoyant une date du debut au jour de fin
    _date = dateDebut
    while _date <= dateFin:
        yield _date
        _date = _date + datetime.timedelta(days = 1)
       
##########################################################################
def xmlStrToStr(inString): 
    """replace all XML escape characters by non encoded characters"""  
    inString = inString.replace('&quot;','"')
    inString = inString.replace('&apos;',"'")
    inString = inString.replace('&amp;','&')
    inString = inString.replace('&lt;','<')
    inString = inString.replace('&gt;','>')
    return inString

###########################################################################

def xmlise(my_dict):
    """Return a string in xml format from the input dictionary"""

    d_elem = {}
    
    if str(type(my_dict)) == "<type 'list'>":  # est passé une liste de tuple
        d_local = {}                           # creation dictionnaire
        for key, val in my_dict:
            d_local[key] = val                 # creation key, value
        my_dict = d_local                      # nouveau dico pris en compte


    for key, val in my_dict.items():
        
        # manage element elem@attribute = x  that will be translated in <elem attibute="x"/>
        if '@' in key:
            assert type(val) != dict, "error, can't use a dict value for an attribute " + key
            keyName, attName = key.split('@')
        else:
            keyName = key
            attName = None
        
        if not d_elem.has_key(keyName):
            d_elem[keyName]=[]
        
        if attName != None:
            d_elem[keyName].append((2, attName, val))  ## add attr
        else:
            d_elem[keyName].append((1, val, None))  ## add elem

    rep = ""
    for key, val in d_elem.items():
        
        #open element    
        rep += '\n<%s'%(key)
        
        ## add attibutes
        for attrName, attrVal in [(t[1],t[2]) for t in val if t[0]==2]:
            rep += ' %s="%s"'%(attrName, attrVal)
            
        ## close tag of start elem 
        rep += '>'
        
        for val2 in [t[1] for t in val if t[0]==1]:
            if type(val2) == dict:
                rep += xmlise(val2)
            else:
                rep += str(val2)
        ## end tag for main elem 
        rep += ''.join(('</', key, '>'))        

    return rep

###########################################################################

def createFileIfAbsent(s_fpath, 
                       s_defaultContent = "", 
                       mode = None):
    """create a file in 777 mode if it doesn't exist
    input : full file path, optional text to write in file
    output , True if ok (already exists or well created, False if an error occured
    """
    try:
        if not mode:
            mode = stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC
        if not os.path.isfile(s_fpath):
            hF = open(s_fpath, "w")
            if s_defaultContent:
                hF.write(s_defaultContent)
            hF.close()
            os.chmod(s_fpath, mode)
        
    except:
        logging.error( __name__ + ': ' + str(sys.exc_info()[1]))
        return False
        
    return True

###########################################################################

def createFolder(folder, mode=stat.S_IREAD | stat.S_IWRITE):
    try:
        ret = True
        if not os.path.isdir(folder):
            os.makedirs(folder)
            os.chmod(folder, mode)   
    except:
        ret = False
        
    return ret

###########################################################################

class MyException(Exception):
    
    def __init__(self, txtMsg, my_id=None):
        Exception.__init__(self)
        self.msg = txtMsg
        self.id = my_id
        
    def __str__(self):
        return repr(self.msg)

#####################################################################
    
def getFileList(folder, extension):
    """return a list of files with a given extension and dive into subdirs"""
    listInTest = []
    for currentRoot, unusedSubDirs, subFileList in os.walk(folder):
        for fileName in subFileList:
            completeFileName = os.path.join(currentRoot, fileName)
            
            if not os.path.isfile(completeFileName):
                continue
            if completeFileName.endswith(extension):
                listInTest.append(completeFileName)

    return listInTest

###########################################################################
    
def getFilesTimeStamp(rootPath, extention):
    """ Return a string that is the concatenation of all file date of all file listed.
    If one file has been changed, the result will change """
  
    result = ""
        
    for currentRoot, unused, subFileList in os.walk(rootPath):
        if subFileList:
            for _file in subFileList:
                if _file.endswith(extention):
                    fileDate = os.path.getmtime( os.path.join(currentRoot,_file)  )
                    result += _file + "_" + str(fileDate) + ";"
                        
    return result   
    
###########################################################################

def walklevel(some_dir, level=1):
    ''' Exactement comme os.walk, mais on controle la profondeur '''
    
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]
                
###########################################################################

def getMatchingFiles(s_path, s_paterns, hierarchyLevel = 10):
    """ return a list of fullpath of files that match the patern string 
    inputs : 
        file or folder to investigate
        string of paterns sperated by comma. ie : "toto.rslt,*.log"
    output : list of fullpath files
    """ 
    import glob
    l_ret = []
    
    for _p in [_p.strip() for _p in s_paterns.split(',')]:
        
        ## do not recurse if it is a file 
        _p2 = os.path.abspath(os.path.join(s_path, _p))
        if os.path.isfile(_p2) and s_path not in l_ret:
            l_ret.append(_p2)
            continue
        
        ## folder, add patern extension        
        for root, _l_dirs, _l_files in walklevel(s_path, hierarchyLevel):
            _fp = os.path.join(root, _p)
            for item in glob.iglob(_fp):
                if item in l_ret:
                    continue
                l_ret.append(item)
                
    return l_ret
                                
###########################################################################

def copyDir(pathSRC, pathDST, logger=logging.getLogger()):
    
    """ Copy all files from a source directory to a destination directory
    The parameter logger shall be a logger (type=logging.Loger) that can be passed by caller """
    
    assert (isinstance(logger, logging.Logger))
    
    if pathSRC.endswith(os.path.sep):
        pathSRC = os.path.split(pathSRC)[0]
    if pathDST.endswith(os.path.sep):
        pathDST = os.path.split(pathDST)[0]
        
    if not isDirReadable(pathSRC):
        logger.error("Error pathSRC unreadable " + pathSRC)
        return False

    ## create destPath
    listSubDirs = pathDST.split(os.path.sep)
    dirToCreate = ""
    for subdir in listSubDirs:
#        logger.debug("*****test subdir*** "+str(subdir))
        dirToCreate +=  subdir
        if bOS_is_Windows():
            count = 3
        else:
            count = 1
#        logger.debug("*****test dirToCreate*** "+str(dirToCreate))
        if (dirToCreate.count(os.path.sep)>=count) and not os.path.isdir(dirToCreate):
            os.mkdir(dirToCreate)
        dirToCreate +=  os.path.sep
    
    # create all desPath sub-folders and copy files          
    for root, _dirs, files in os.walk(pathSRC):
        
        #create all desPath sub-folders
        tmpDestPath = "".join((pathDST,root.split(pathSRC)[1]))
#        logger.debug("*****test tmpDestPath*** "+str(tmpDestPath))
        if not os.path.isdir(tmpDestPath):
#            logger.debug("***** create tmpDestPath*** "+str(tmpDestPath))
            os.mkdir(tmpDestPath)
         
        for fileName in files:            
            try:
                shutil.copy( os.path.join(root,fileName) , tmpDestPath)
            except Exception.IOError:
                logger.exception("*** ERROR : " + str(err) + " Can't copy " + root + "/"+ fileName + " to directory " + tmpDestPath)
                return False

    return True

###################################################################################"

def removeAll(path):
    ''' remove all files , dir and subdirs'''
    try:
        removeFilesInDir(path)
        os.rmdir(path)
        return True       

    except:
        return False
    
###################################################################################"

def removeFilesInDir(path):

    """ Remove all files from a directory """

    if not os.path.isdir(path):
        return False

    files=os.listdir(path)

    for x in files:
        fullpath=os.path.join(path, x)
        if os.path.isfile(fullpath):
            os.chmod(fullpath, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC )        # if file if protected, give removing rights
            os.remove(fullpath)
            
        if os.path.islink(fullpath):
            os.remove(fullpath)            
            
        elif os.path.isdir(fullpath):
            removeFilesInDir(fullpath)
            os.rmdir(fullpath)

    return True       

###########################################################################

def isDirReadable(dirToTest):
    """ test if directory is readable """
    return os.access(dirToTest, os.R_OK)

###########################################################################

def isDirWritable(dirToTest):
    """ test if directory is writable """
    try:
        if os.access( dirToTest, os.R_OK):
            testFileName = os.path.join(dirToTest,"TESTFILE.TMP")
            testFile = open(testFileName, "w")
            testFile.close()
            os.remove(testFileName)
            return True

    except (IOError):
        return False

#####################################################################"

def lockFile(filePath, nb_waiting_sec = 4, logger=logging.getLogger(), askerId = ""):
    """ Try to lock a file via creating a folder of the same name
    return True if file is locked
    return False if the file does'nt exist or can't lock file"""

    assert (isinstance(logger, logging.Logger))

    if not os.path.isfile(filePath):
        logger.error("[lockFile] Bad path %s" % (filePath))
        return False

    lockFolder = filePath + '.lock'
    nbTry = 0
    
    while (nbTry < nb_waiting_sec): ## as time out

        try:
            os.mkdir(lockFolder) ## lock file 
            return True
        except Exception.OSError:
            pass ## can't take lock by creating a folder
            ##print '[lockFile] Error occurred when trying to create lock %s. errno = %i (%s)' % (lockFolder, err.errno, err.strerror)

        ## try again
        nbTry += 1
        if nbTry % 5 == 0:
            logger.debug('[lockFile] %s has been locking for %s sec, %s wait again' %(os.path.basename(filePath), nbTry, askerId))            

        time.sleep(1) ## wait one sec before retry
    
    logger.error("[lockFile] error can't take lock file %s after %d tries"%(filePath, nbTry))           
    return False

######################################################################################

def unlockFile(filePath, nb_waiting_sec=4, logger=logging.getLogger(), askerId = ""):
    """ Unlock a file by deleting a lock folder
    The parameter logger shall be a logger (type=logging.Loger) that can be passed by caller """

    assert (isinstance(logger, logging.Logger))

    if not filePath or not os.path.isfile(filePath):
        logger.error("Bad path %s" % (filePath))
        return False

    lockFolder = filePath + '.lock'
    nbTry = 0

    while (nbTry < nb_waiting_sec): 
        if os.path.isdir(lockFolder):
            try:
                os.rmdir(lockFolder)                ## unlock file 
                return True
            
            except Exception.OSError as err:
                logger.exception('Error occurred when trying to remove lock %s. errno = %i (%s)' % (lockFolder, err.errno, err.strerror))

        else:
            # Pas de fichier de lock
            # c'est bizarre mais bon ..
            return True
            
        nbTry += 1
        logger.error('%s conflict when unlocking, wait 1 sec' %(filePath))            
        time.sleep(1) 

    return False


######################################################################################

def traceFileContent(filePath, logger=logging.getLogger()):
    """The parameter logger shall be a logger (type=logging.Loger) that can be passed by caller """

    assert (isinstance(logger, logging.Logger))

    with open(filePath, 'r') as f:
        read_data = f.read()
        read_data = "DUMP FILE " + filePath + '\n---- DUMP start ----\n' + read_data + '\n---- DUMP END ----'

        logger.info(read_data)

        f.close()

    return True

######################################################################################

def bOS_is_Windows():
    import platform
    return (platform.system() == 'Windows')

#####################################################################################################################"
def getIpAddr(filePath, adr_type="v4"):
    ''' return the ip adr by analysing the result of ifconfig. string element.
        filepath:  a path where a file can be written => mandatory
        adr_type: the type of ip adr to get. v4 by default (else "v6")
    '''
    '''
    Ce code est très très limité. En effet il ne tient pas compte
    de la langue ! (marche pas sur Windows Francais)
    de différentes interfaces (prend la premiere)
    ...
    '''
    import platform
       
    if platform.system() == 'Windows':
        #print "cmd windows ipconfig\n"
        os.system("ipconfig > "  + filePath )
    elif platform.system() == 'Linux':
        #print "cmd linux ifconfig\n"
        os.system("/sbin/ifconfig > "  + filePath )
    else:
        return ("null")
    #print "analyse donnees\n"
    fileipcfg = open(filePath,"r")
    ipcfg = fileipcfg.readlines()
    fileipcfg.close()

    ipv4adr = "null"
    if platform.system() == 'Windows':
        #print "analyse fichier windows\n"
        if adr_type == "v6":
            chaine = "IPv6"
        else:
            chaine = "IPv4"
        for ligne in ipcfg:
            if chaine in ligne:
                ipv4adr = ligne.split(":")[1]
                break
    else:
        #print "analyse fichier linux\n"
        if adr_type == "v6":
            for ligne in ipcfg:
                #print ligne
                if "Scope:Global" in ligne:
                    #print "..........trouve ligne ipv6"
                    ligne = ligne.split(": ")[1]
                    ipv4adr = ligne.split(" S")[0]
                    break
        else:
            for ligne in ipcfg:
                #print ligne
                if "Bcast:" in ligne:
                    #print "..........trouve ligne ipv4"
                    ligne = ligne.split(":")[1]
                    ipv4adr = ligne.split(" ")[0]
                    break

    return ipv4adr.strip()

######################################################################################

def CallURL(url, url_params="", logger=logging.getLogger()):
    '''
    The parameter logger shall be a logger (type=logging.Loger) that can be passed by caller """
    
    This function returns a file-like object. Same as urllib2.urlopen()
    It means None if failed
    Use, geturl() or info() and all methods available with urllib.urlopen(), on return value 
    '''
    from time import strftime
    import urllib2

    assert (isinstance(logger, logging.Logger))

    try:
        f = None
        url += url_params
        
        url = urllib2.quote(url, ':/&?=%')
        
        f = urllib2.urlopen(url)
        
        # According to RFC 2616, "2xx" code indicates that the client's
        # request was successfully received, understood, and accepted.
        if (f.code >= 200 and f.code < 300):
#             logger.debug("%s has been open with succes" %  url)
            return f
        # On ne trace qu'en cas de pb
        logger.warning("%s returns: %s (%d)"%(strftime("[%H:%M:%S]"), f.msg, f.code) )
    
    except (urllib2.URLError, urllib2.HTTPError, ValueError):
        logger.error("Error while opening url %s" % url)
            
            
    return f
            
######################################################################################

def rsync(srcPath, dstPath, rsync_options='', password=None, logger=logging.getLogger()):
    '''
    Surcharge de rsync avec traces et Cie
    The parameter logger shall be a logger (type=logging.Loger) that can be passed by caller """
    
    '''
    assert (isinstance(logger, logging.Logger))
        
    # add password
    if password != None:
        os.environ["RSYNC_PASSWORD"] = password
    
    if bOS_is_Windows():  # dans le cas rsync pour windows, l'EXE veut des path de type linux d'ou les str.replace() car les path sont deja au format windows
        sys_cmd= " ".join(('"C:\Program Files (x86)\cwRsync\\bin\\rsync"',  rsync_options, srcPath.replace("\\","/"), dstPath))
    else:
        sys_cmd= " ".join(("rsync", rsync_options, srcPath, dstPath))

    # j'ai des soucis avec os_execute_no_shell. Pour l'instant j'utilise os.system
    logger.debug("Execute " + sys_cmd)
    sys_ret = os.system(sys_cmd)    

    return sys_ret
            
######################################################################################

def getDictFromCsvLine(inStr):
    data = {}
    for par in inStr.split(","):
        hRe = re.search('[ ]*([\w]*)[ ]*=[ ]*"(.*)"', par)
        if hRe:
            data[hRe.group(1)] = hRe.group(2)
    
    return data    

######################################################################################
# 
# def dictToIniFile(inDict, iniFile, section="DATA"):
#     
#     cfParser = ConfigParser.RawConfigParser()
#     cfParser.readfp(open(iniFile))
# 
#     ## clean existing section
#     if cfParser.has_section(section):
#         cfParser.remove_section(section)
#     cfParser.add_section(section)
#     
#     for key, val in inDict.items():
#         cfParser.set(section, str(key), str(val)) 
#         
#     cfParser.write(open(iniFile, 'w'))     
# 
# ######################################################################################
# 
# def iniFileToDict(iniFile, section="DATA"):
#     """return a dictionary from keys/values included in an ini file"""
#     if not os.path.isfile(iniFile):
#         return {}
#     cfParser = ConfigParser.ConfigParser()
#     cfParser.readfp(open(iniFile))
#     return dict( cfParser.items(section) )  

######################################################################################

def getKernelDict(iniFile, section="KERNEL_DATA"):
    """return a dictionary specific for kernel keys from kernel.txt"""
    dico = {}
    for k, v in iniFileToDict(iniFile, section).items():
        dico["kernel_" + k.lower()] = v
    return dico  

##############################################################################"

def filterDictsWithKeyVal(l_dict, key, val):
    """ return a sub dict list from a dict lis imput that match a given key
    inputs : list if dictionaries
             key to find in each dictionary
    output : list of values matching dict
    """
    l_ret = [] 
    for d in l_dict:
        if (key, val) in d.items():
            l_ret.append(d)
    return l_ret
################################################################################



def transformToHtml( xmlFile, xslFile, htmlFile):
    """ transform from xml , xsl to html"""
    import libxml2
    import libxslt
    try:
        
        hXsl = libxslt.parseStylesheetDoc(libxml2.parseFile(xslFile))
        h_xml = libxml2.parseFile(xmlFile)
        result = hXsl.applyStylesheet(h_xml, {"publication_process":"'True'"})
        hXsl.saveResultToFilename(htmlFile, result, 0)
        
        hXsl.freeStylesheet()
        h_xml.freeDoc()
        result.freeDoc()

    except:
        print("transformToHtml exception : %s" %(sys.exc_info()[1]))                  
        return False 
    
    return True


######################################################################################

def validateXmlWithXsd(xml_filename, xsd_filename):
    ret = True
    
    if bOS_is_Windows():
        return ret
    
    """@todo: ALAIN  à decrire
    + sous eclipse, j'ai des tag rouge d'erreur car ne trouve pas etree.* ??? et toi ??"""

    from lxml import etree

    xmlschema_doc = etree.parse(xsd_filename)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    doc = etree.parse(xml_filename)
    ret = xmlschema.validate(doc)
    if ret == False:
        showXsdErr(str(xmlschema.error_log.last_error))
    
    return ret

######################################################################################
def showXsdErr(errorxsd):
    """
    """
    parts = errorxsd.split(":")
    fichier = parts[0]
    ligne = parts[1]
    element = parts[6]
    pb = "".join(parts[7:])
    
    logging.error("File: " + fichier + "\n" +\
          "Line: " + ligne + "\n" +\
          "Element: " + element + "\n" +\
          "Pb: " + pb
          )

##########################################################################################
def getLinePosition(file_pathname, chaine):
    '''return position of the line containing the string passed
    '''
    position = 0
    try:
        filin = open(file_pathname, 'r')
        position = filin.tell()
        ligne = filin.readline()
        while ligne != "":
            if chaine in ligne:              # found  string return curser before it
                filin.close()
                return position
            position = filin.tell()
            ligne = filin.readline()
    except IOError:
        pass
    filin.close()
    return position

    

############################################################################

def changeDivContent(resultFilePath, divId, content):
    """Change content of a given div
    """
    from xml.dom import minidom
    xmlHandle = minidom.parse(resultFilePath) # parse the XML file 
    
    for node in xmlHandle.getElementsByTagName("div"):
        if divId == str(node.getAttribute('id')):
            node.firstChild.data = content

    xmlstr = xmlHandle.toxml('utf-8')
    f = open(resultFilePath, 'w')
    f.write(xmlstr)
    f.close()

######################################################################################
if __name__ == '__main__':

    print(getDateFrom_d_m_y("22/3/45"))
    print(getDateFrom_d_m_y("22/3/1945"))
    exit(0)
    dateDebut = datetime.datetime.now()
    dateFin = dateDebut + datetime.timedelta(days = 22)
    for a_date in jourApresJour(dateDebut, dateFin):
        print (a_date)
   

    
    dictToIniFile({"user":"toto"},
                  "/a/home.users/vgazeill/EclipseWorkspace/GIT/pyatt/Config/sessions.txt", 
                  )
    exit(0)

