# -*- coding: utf-8 -*-
'''
Created on Dec 5, 2014

@author: vgazeill
'''
from fabric.api import local, run, env

path_server_apache = "sudo service apache2 restart"

def setenv():
    env.host_string = 'nuxcompil8'
    env.user = 'mhappint'
    env.password = 'Quit6co2015'
       
def l_start():
    """ local syncdb and run server"""
    local("python ./manage.py syncdb")
    local("python ./manage.py runserver")
   
def updateDB():
    """update local CI Django database"""
    print("running updateDB")
    local("python ./manage.py updateDB")
 
def sauveTables():
    """sauveTables"""
    import datetime
    s_file = datetime.datetime.now().strftime('%Y-%m-%d--%H-%M-%S') + "_tables.json"
    local("python manage.py dumpdata --indent 2 > ./svg/%s"%s_file)
 
def chargeTables(s_filePath):
    """chargement d'une sauvegarde. Usage fab chargeTables:./svg/monFichierDeSauvegarde.json"""
    print(s_filePath)
    local("python manage.py loaddata %s"%s_filePath)

def apache_start():
    """start apache server """
    local("sudo service apache2 start")
    
def apache_restart():
    """restart apache server """
    setenv()
    run( path_server_apache + "/bin/apachectl -k restart")
    
def apache_stop():
    """stop apache server """
    setenv()
    run( path_server_apache + "/bin/apachectl -k stop")    