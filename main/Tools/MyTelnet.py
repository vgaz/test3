#!/opt/softs/workshop/current/bin/python
# -*- coding: utf-8 -*-

import logging
LOGGIN_FORMAT = '[%(levelname)-8s] %(module)-15s.%(funcName)s: %(message)s'
logging.basicConfig(format=LOGGIN_FORMAT, level=logging.DEBUG)

"""

Generic Tools

"""
import os
import telnetlib
import socket

##########################################################################

def telnetRemoveFolderContent(d_input):
    """ remove a remote folder content with telnet connexion
    input  dict including
    adr = "172.21.122.2" 
    login = xxxx
    password = "=#pega,2k"
    prompt = 
    folder = "/vol/stb/upchz/DMS_Integ/GW/webkit/ci"
    logger  : logging instance
    """
    TELNET_PORT     = 23
    telnetSession = None    
    ret = 0
    try:
        for key in ("adr", "login", "password", "prompt", "folder", "logger"):
            if key not in d_input:raise Exception, 'key %s not found'%(key)
            
        ## opening telnet session on STB server
        d_input['logger'].info("%s/* via Telnet %s" %(d_input["folder"], d_input["adr"]))
        telnetSession = telnetlib.Telnet(d_input["adr"], TELNET_PORT, 30)
        ret = telnetSession.read_until("login: ", 30)
        telnetSession.write(d_input["login"] + "\n")

        ret = telnetSession.read_until("Password: ", 30)
        telnetSession.write(d_input["password"] + "\n")
        ret = telnetSession.read_until(d_input["prompt"], 30)
        d_input['logger'].debug(ret)
        d_input['logger'].debug("Telnet %s:%s connected"%(d_input["adr"], TELNET_PORT))

        mF = os.path.dirname(d_input["folder"])
        telnetSession.write('cd %s \n'%(mF))
        ret = telnetSession.read_until(d_input["prompt"], 30)
        
        telnetSession.write('pwd \n')
        ret = telnetSession.read_until(d_input["prompt"], 30)

        if mF in ret:
            cde = 'rm -r -f ./%s/*'%(os.path.basename(d_input["folder"])) 
            telnetSession.write(cde + '\n')
            ret = telnetSession.read_until(d_input["prompt"], 300)
            d_input['logger'].debug(ret)

    except (EOFError, socket.error):
        d_input['logger'].error("Telnet connection failure")
        ret = 610
        
    except TypeError, e:
        d_input['logger'].error("Telnet typeError:" + str(e))
        ret = e
        
    if telnetSession:
        telnetSession.write("exit\n")
        telnetSession.close()
        telnetSession = None
        d_input['logger'].debug("Close Telnet connection")

    return ret    
    
#######################################################################
    
if __name__ == '__main__':
    

    
    d_upch = {
                "adr":"172.21.122.1",
                "login" :"upchz",
                "password" : "51038739",
                "prompt":"-bash-3.00$",
                "folder" : "/vol/stb/upchz/DMS_Integ/GW/webkit/ci",
                "jobVersion":"10751"
                }
    
    d_pega = {
              "adr":"172.21.122.2", 
              "login" :"pegasus",
              "password" : "=#pega,2k",
              "folder":"/vol/stb/pegasus/users/ci/tests/ch1",
              "prompt":"-bash-4.1$",
              "logger":logging
              }
    logging.disable(logging.DEBUG)
    telnetRemoveFolderContent(d_pega)
    print "fin" 
    

