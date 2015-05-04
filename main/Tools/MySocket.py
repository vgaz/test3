# -*- coding: utf-8 -*-
'''
Created on Aug 3, 2010

@author: vgazeill, rdugau
'''

import logging
LOGGIN_FORMAT = '[TestCI_%(levelname)-8s] %(module)-15s.%(funcName)s: %(message)s'
logging.basicConfig(format=LOGGIN_FORMAT, level=logging.DEBUG)

import socket, sys
import os.path
import datetime
import time
from time import strftime

from MyTools import MyException


SOCKET_ERROR        = 'MySocket error: '
SOCKET_ERROR_SEND   = 'Tools.MySocket sending error : '
MSG_ERR_TIMEOUT     = 'Time out overpassed'

TRACE_HEADER = "[ MySocket      ]"
TRACE_SEND_PREFIX = "                                --> "
TRACE_RECV_PREFIX = "<-- "
TRACE_MSG_PREFIX  = "** "


class MySocket(object):
    
    def __init__(self, traceOut = None, prompt = '', traceHeader = ''):
        """ traceOut is used to get information from a caller stream that accepts string"""
        self.ipAdr = ''
        self.port = ''
        self.socketId = None
        self.longBuf = ''
        self.traceOut = traceOut
        self.prompt = prompt
        if traceHeader != '':
            self.traceHeader = ''.join(('[', traceHeader, '] '))
        else:
            self.traceHeader = ''
            

    def traceSend(self, strIn):
        self.trace(TRACE_SEND_PREFIX + strIn)
      
    def traceRecv(self, strIn):
        self.trace(TRACE_RECV_PREFIX + strIn)
      
    def traceMsg(self, strIn):
        self.trace(TRACE_MSG_PREFIX + strIn)
      
    def trace(self, strIn):
        if  self.traceOut == None:
            print ' '.join((TRACE_HEADER, self.traceHeader, strIn))
        else:
            self.traceOut(self.traceHeader + strIn)
      
    def open(self, ip, port):
        self.ipAdr = str(ip)
        self.port = int(port)

        try:
            self.socketId = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socketId.connect((self.ipAdr, self.port))
        except:
            raise MyException(SOCKET_ERROR)
                
    def sendCmd(self, msg):
        # no \n for trace
        msg = msg.strip('\n')
            
        self.traceSend(msg)
        
        # \n needed for the send
        msg = msg + '\n'
        try:
            self.socketId.send(msg)
        except socket.error:
            self.traceMsg('socket error while sending command')
            raise MyException(SOCKET_ERROR_SEND + str(sys.exc_info()[1]))


    def sendCmdAndWaitPrompt(self, msg, timeOutSec = 9, abortFile = None, bExceptionMode=True):
        self.sendCmd(msg)
        self.waitForPrompt(timeOutSec, abortFile, bExceptionMode)

    def waitForPrompt(self, timeOutSec = 9, abortFile = None, bExceptionMode=True):
        assert self.prompt, "no prompt defined"
        self.waitFor(self.prompt, timeOutSec, abortFile, bExceptionMode)
        self.purgePrompt()

    def purgePrompt(self):
        """ remove all prompts inside input message queue"""
        cpt = 0
        try:
            while True:
                self.waitFor(self.prompt, 1, abortFile = None, bExceptionMode=True, bVerbose=False)
                self.traceMsg('Unexpected prompt detected')
                cpt +=1
                if cpt > 50:
                    raise LookupError, "To many Unexpected prompts detected"
        except socket.error:
            pass
        except LookupError:
            raise
        except:
            pass    # means that no prompt was detected , ok

    def waitFor(self, strToWait, timeOut, abortFile = None, bExceptionMode=True, bVerbose = True):
        ret = True
        if strToWait == None:
            strToWait = self.prompt
        svgTimeOut = self.socketId.gettimeout()

        try:
            start_time = datetime.datetime.now()
            unitaryTimeoutSec = 5

            self.socketId.settimeout(float(unitaryTimeoutSec))
                        
            if strToWait != self.prompt:
                self.traceMsg("%s wait for '%s' during %s sec"   %(strftime("%H:%M:%S"), strToWait, str(timeOut)))
        
            b_strFound = False
            last_msg = 0
            while True:

                if abortFile and os.path.isfile(abortFile):
                    raise MyException(SOCKET_ERROR + 'Abort requested manually by user')

                elapsed_seconds = (datetime.datetime.now()-start_time).seconds
                if elapsed_seconds >= timeOut:
                    msg = MSG_ERR_TIMEOUT + ' ' + str(timeOut) + ' sec'
                    if bVerbose:
                        self.traceMsg(SOCKET_ERROR + msg)
#                    # Ici, on test de ne pas lever l'exception en cas de recherche raté du prompt.
#                    # Je pense qu'il faudra retirer ca. A voir ... 
#                    if strToWait == self.prompt:
#                        self.traceMsg("!!!!!!!!!! comportement inattendu *** Perte du prompt ** contacter votre support **** On ne leve pas l'exception")
#                    else:
#                        raise MyException(msg)
                    raise MyException(msg)

                
                # On cherche le patern
                if strToWait in self.longBuf:
                    b_strFound = True

## strToWait = 'X'
## EX1 longBuf = P111X1\nP2222\nP
## EX2 longBuf = P111X1\nP2222\nP\n999

                # On trace toutes les lignes dispos
                while '\n' in self.longBuf:
                    ## update longBuf
                    firstLine, self.longBuf = self.longBuf.split('\n', 1)  ## firstLine = P111X1, self.longBuf = P2222\nP888
                    self.traceRecv(firstLine)

# Arrivé ici on a tracé
# P111X1
# P2222
# puis
# EX1 : longBuf = P
# EX2 : tracé P et longBuf = 999


                # Si on a trouvé le pattern ou le prompt
                if b_strFound:

                    # Si on cherchait un pattern, on indique avoir trouvé
                    if strToWait != self.prompt:
                        self.traceMsg("'%s' detected" %(strToWait))

                    # On retire un éventuel prompt restant 
                    if self.longBuf.startswith(self.prompt):
                        self.longBuf = self.longBuf[len(self.prompt):]
                        # EX1 : longBuf = ''
                        # EX2 : longBuf = 999
#                    
#                    self.traceMsg("                                            ************************** Il reste V\n" + self.longBuf)
#                    self.traceMsg("                                            ************************** Il reste ^")
                    
                    break # on a trouvé le pattern ou le prompt. C'est bon, on sort du while

                try:
#                    self.traceMsg("                                            ************************** Avant le recv V\n" + self.longBuf)
#                    self.traceMsg("                                            ************************** Avant le recv ^")
                    self.longBuf = self.longBuf + self.socketId.recv(512)
                except socket.error:
                    exc_type, exc_str = sys.exc_info()[:2]
                    
                    if exc_type == socket.timeout and bVerbose:
                        if strToWait == self.prompt:
                            s = 'prompt' 
                        else:
                            s = "'" + strToWait + "'" 
                        elapsed_seconds = (datetime.datetime.now()-start_time).seconds
                        if elapsed_seconds < 90:              # tant que moins de 90 secondes
                            last_msg = elapsed_seconds         # le msg s'affiche a chaque passage ( toutes  les 5 sec)
                        elif elapsed_seconds < 3600:
                            if elapsed_seconds - last_msg >= 60: # puis si le dernier message date d'au moins 1 minute
                                last_msg = elapsed_seconds       # on l'affiche
                        else:
                            if elapsed_seconds - last_msg >= 300: # apres 1h si le dernier message date d'au moins 5 minute
                                last_msg = elapsed_seconds       # on l'affiche

                        if last_msg == elapsed_seconds:
                            self.traceMsg("still waiting for %s since %s sec. Timeout=%s" %( s, elapsed_seconds, str(timeOut) ))
                    else:
                        ## timeout is over
                        self.traceMsg(exc_str)
                        ## re raise other errors 
                        raise socket.error

            # fin de while

        
        ## catch any exception and raise a MyException error or return False            
        except:
            errstr = str(sys.exc_info()[1])
            if bExceptionMode:
                raise MyException(SOCKET_ERROR + errstr)
            else:
                ret = False
        finally:
            self.socketId.settimeout(svgTimeOut)
        
        return ret
            
            
    def close(self):
        if self.socketId:
            self.socketId.close()
        
###############################################################################

if __name__ == '__main__':

    firstLine = 'PR111PR1'
    if firstLine.startswith('PR'):
        print firstLine[len('PR'):]


    
    mySocket = MySocket()
#    mySocket.open('127.0.0.1','23')
    mySocket.open('nux17513','23')

    mySocket.sendCmd('ls -a')
    
    mySocket.waitFor('a', 15)
    exit(0)
    
    print "s"
    start_time = datetime.datetime.now()
    time.sleep(2)
    print"e"
    end_time = datetime.datetime.now()
    
    elpased = end_time-start_time
    print elpased.seconds 
    
    
    
    
