############################################################################
#
# AUTHOR    : NIANG Abdou (aniang@nds.com)
# DATE        : 2010/03/05, 2010/03/08, 2010/04/07
# DESCRIPTION    : v0.1 -Send mail with Subject, From, To, CC, Message, 
#            Message part in html format (htm_file),
#            and attached files elements
#############################################################################

import smtplib
import os
import posixpath
import platform

#from email import *
from email.mime.multipart import MIMEMultipart
from email.Utils import formatdate
from email import Encoders
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase

def send_email(SMTP="outbound.cisco.com", Subject="", From="", To=[], CC=[], Message="", html_file="", Files=[]):
    """
    ----------------------------------------------------------------------------------
    Send a mail using SMTP address.
    Usage : send_email (SMTP, From, To, Message, [Subject, CC, html_file, files])
    
    Parameters "SMTP", "From", "To" and "Message" are necessary.
    "Subject", "C"C, "html_file" and "files" are optionnal.
    To send an e-mail in html format you can use "html_file" option.

    By default To and CC parameters are composed by mail addresses.
    To send mails to alias To and CC parameters must have 2 sub-lists.
    To or CC = [ [receiver_list] , [header_list ].
    receiver_list is composed by al the elementary mail addresses.
    header_list is composed by alias.
    ----------------------------------------------------------------------------------
    """ 
#    '''
#    Remarque de Raphael:
#    Apres plusieurs tests, j'ai decouvert que cette methode permet de gruger,
#     non seulement les adresses des expediteurs, mais aussi celles des destinataires
#    De plus, je n'arrive pas a la faire fonctionner avec des alias !?
#    Je vais donc utiliser l'autre fonction...
#    ''' 
    import sys
    
    if SMTP == "":
        print "Error : SMTP is empty"
        sys.exit(1)
    if From == "":
        print "Error : From address is empty"
        sys.exit(1)
    if To == []:
        print "Error : To address is empty"
        sys.exit(1)
    if Message == "":
        print "Error : Message is empty"
        sys.exit(1)


    if type(To[0]) == list and len(To) > 1 and type(To[1]) == list :
        To_header = ";".join(To[1])
        To_receiver = ";".join(To[0])
    else:
        To_header = To_receiver = ";".join(To)


    if  CC != [] and type(CC[0]) == list and type(CC[1]) == list :
        CC_header = ";".join(CC[1])
        CC_receiver = ";".join(CC[0])
    else:
        CC_header = CC_receiver = ";".join(CC)

    msg = MIMEMultipart()
    msg['From'] = From

    msg['Date'] = formatdate(localtime=True)

    msg['To'] = To_header
    
    if CC != "" : 
        msg['CC'] = CC_header

    msg['Subject'] = Subject
    
    if html_file != "":
        temp = open(html_file, 'rb')
        msg.attach(MIMEText(Message + temp.read() , 'html'))
        temp.close()
    else:
        msg.attach(MIMEText(Message))    

    #Attach all the files into mail
    if len(Files) > 0:
        for my_file in Files:
            if (os.path.isfile(my_file)) :
                part = MIMEBase('application', "octet-stream")
                part.set_payload(open(my_file, "rb").read())
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(my_file))
                msg.attach(part)
            else:
                print 'Error : File ' + my_file + ' does not exist.'

    ##For Debug only    
    #print "-->SMTP: %s \r\n\r\n-->From : %s \r\n\r\n-->To: %s \r\n\r\n-->To_h: %s \r\n\r\n-->CC: %s \r\n\r\n-->CC_h: %s \r\n\r\n-->Subject: %s \r\n\r\n-->Files: %s \r\n\r\n-->To_s: %s \r\n\r\n-->CC_s: %s \r\n\r\n-->Message: %s" % (SMTP, From, To, To_header, CC, CC_header, Subject, Files, To_receiver, CC_receiver, Message)

    #####   Send notification mail   #####
    ## Connect to SMTP server
    try:
        mailServer = smtplib.SMTP(SMTP)
    except:
        print 'Error : SMTP connexion failed'
        return(1)

    ## Send mail
    try:
        mailServer.sendmail(From, To_receiver.split(";") + CC_receiver.split(";") , msg.as_string())
    except:
        print 'Error : Could not send mail.'
        return(2)
    ## Quit
    try:
        mailServer.quit()
    except:
        print 'Error : Could not exit properly'
        return(3)

    return (0)

######################################################################################################################
######################################################################################################################
######################################################################################################################
def send_HTML_email(SMTP="outbound.cisco.com", subject="", s_from="", l_to=[], l_cc=[], msgTxt="", msgHtml="", l_files=[]):
    """
    like above but for Html
    """ 
    import sys
    
    if s_from == "":
        print "Error : From address is empty"
        sys.exit(1)
    if l_to == []:
        print "Error : To address is empty"
        sys.exit(1)
    if msgTxt == "" and msgHtml == "" :
        print "Error : Message is empty"
        sys.exit(1)

    if type(l_to[0]) == list and len(l_to) > 1 and type(l_to[1]) == list :
        To_header = ";".join(l_to[1])
        To_receiver = ";".join(l_to[0])
    else:
        To_header = To_receiver = ";".join(l_to)

    if  l_cc != [] and type(l_cc[0]) == list and type(l_cc[1]) == list :
        CC_header = ";".join(l_cc[1])
        CC_receiver = ";".join(l_cc[0])
    else:
        CC_header = CC_receiver = ";".join(l_cc)

    msg = MIMEMultipart('alternative')
    msg['From'] = s_from
    msg['Date'] = formatdate(localtime=True)
    msg['To'] = To_header
  
    if l_cc != "" : 
        msg['CC'] = CC_header
    msg['Subject'] = subject
    
    # ptite bidouille locale, aie aie, pas sur la tete ! 
    def b_containsNonAsciiCharacters(chaine):
        return not all(ord(c) < 128 for c in chaine)   

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(msgTxt, 'plain')

    if b_containsNonAsciiCharacters(msgHtml):
        part2 = MIMEText(msgHtml.encode('utf-8'), 'html','utf-8')
    else:
        part2 = MIMEText(msgHtml, 'html') 
    
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, is best and preferred.
    if msgTxt != "":
        msg.attach(part1)
    if msgHtml != "":
        msg.attach(part2)       # html is prefered

    #Attach all the files into mail
    if len(l_files) > 0:
        for my_file in l_files:
            if (os.path.isfile(my_file)) :
                part = MIMEBase('application', "octet-stream")
                part.set_payload(open(my_file, "rb").read())
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(my_file))
                msg.attach(part)
            else:
                print 'Error : File ' + my_file + ' does not exist.'

    #####   Send notification mail   #####
    ## Connect to SMTP server
    try:
        mailServer = smtplib.SMTP(SMTP)
    except:
        print 'Error : SMTP connexion failed'
        return(1)

    ## Send mail
    try:
        mailServer.sendmail(s_from, To_receiver.split(";") + CC_receiver.split(";") , msg.as_string())
    except:
        print 'Error : Could not send mail.'
        return(2)
    ## Quit
    try:
        mailServer.quit()
    except:
        print 'Error : Could not exit properly'
        return(3)

    return (0)

######################################################################################################################
######################################################################################################################
######################################################################################################################
# AUTHOR    : Raphael DUGAU
# DATE        : 08/06/2010
#'''
#Remarque de Raphael:
#Cette methode ne permet pas de triche, elle s'appui sur la commande mail linux,
#La connaissance du serveur smtp est pour le coup inutile
#Mais ne marche pas sous Windows
#'''
#'''
#Sous Windows en cas de besoin. Si on a powershell 2, faire :
#$smtp = new-object Net.Mail.SmtpClient("frsmtp.nds.com")
#$smtp.Send("sender@nds.com", "rdugau@nds.com", "suj", "coucou")
#'''

#  TODO A ameliorer/mettre au propre
#- Pourquoi join ne marche pas !!?
#- ajouter la possibilite de mail html (utiliser MIMEText et Cie)
#- et modifier alors l'insertion des fichiers joints (utiliser MIMEBase et Cie)



def send_email_linux(subject, send_to, send_cc, msg, file_pathes=[]):

    assert type(send_to) == list
    assert type(send_cc) == list
    assert type(file_pathes) == list

    # pas de guillemet dans le message. On remplace par 2 simple-quotes
    msg = msg.replace('"', "''")

    cmd = '(echo -e ' + '"' + msg + '"'
    
    for f in file_pathes:
        _head, tail = posixpath.split(f)
        cmd = ' '.join((cmd, ';', 'uuencode', '"' + str(f) + '"', tail))

    cmd = ' '.join((cmd, ")", "|", "mail" , "-s", '"' + subject + '"'))

    if  send_cc != []:
        send_cc = ' '.join(send_cc)
        cmd = ' '.join((cmd, '-c', '"' + send_cc + '"'))

    send_to = ' '.join(send_to)
    cmd = ' '.join((cmd, '"' + send_to + '"'))
    
    
    print cmd
    
    if (platform.system() != 'Linux'):
        return - 1

    return os.system(cmd)
    


if __name__ == '__main__':
    
    _subject = "Test d'envoi de mail avec Python !!" 
    _from = "toto@nds.com"
    _message = '"coucou \n\n kiki"' 
    _html_file = "" 
    _files = ["/proc/version"]
    
    _to = ["rdugau@cisco.com"]
    _cc = ["alecaer@cisco.com"] 



#    '''
#    __to=[ _to,['textequisevoit<fauxmail@nds.com>','textequisevoit2<fauxmail2@nds.com>'] ]
#    __cc=[ _cc,['mhappint<mhappint@nds.com>'] ]
#
#    print 'send1'
#    send_email(    Subject=_subject, 
#                        From=_from, 
#                        To=__to, 
#                        CC=__cc, 
#                        Message=_message, 
#                        html_file=_html_file, 
#                        Files=_files)
#                        
#    '''
        
    print 'send2'
    send_email_linux(_subject, _to, _cc, _message, _files)
    
    
    print 'end'
