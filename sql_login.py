#!/usr/local/omcs-devops/bin/python3.6
import subprocess
import base64
import logging

private_logger=logging.getLogger()
logger=logging.getLogger("public_log")

def create_query(query):
    pre="""
    SET NEWPAGE 0
    SET SPACE 0
    SET LINESIZE 80
    SET PAGESIZE 0
    SET ECHO OFF
    SET FEEDBACK OFF
    SET HEADING OFF
    set termout off
    """
    return pre+str(query)

def pwd_decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc)
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + enc[i] - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)

def run_sqlplus(query,key,encrypted_pwd):
'''
Executes the query by connecting as apps user. 

'''

    sqlplus_query=create_query(query)+"\n"
    decrypt=pwd_decode(key,encrypted_pwd)

    login="apps/"+decrypt

    p=subprocess.Popen(['sqlplus','-S',login],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (stdout,stderr) = p.communicate(str.encode(sqlplus_query))

    if stderr.decode('utf-8'):
        print("There's error in the result")
        print(stderr.decode('utf-8').split())

    if "logon denied" in stdout.decode('utf-8'):
        print("Unable to login to sql prompt as apps user. Kindly verifyy\n")
        print("login denied")

        return 2
    else:

        return stdout.decode('utf-8').split()


def run_bash(command):
'''
Executes Shell commands
'''
    p=subprocess.Popen(['/bin/bash'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (stdout,stderr) = p.communicate(str.encode(command))

    return stdout.decode('utf-8')

def long_running_bash(command):
'''
Polls for Stdout in Buffer, and displays in console as soon as output gets generated
'''
    error_buffer=[]

    p = subprocess.Popen(str.encode(command),shell=True, bufsize=0, stdout=subprocess.PIPE,stderr=subprocess.PIPE)

    while True:
        output = p.stdout.readline()
        error = p.stderr.readline()
        if  (p.returncode) != 2:
            # print("Return ",p.returncode)

            if output.decode() == '' and p.poll() is not None and p.returncode !=2:
                break
            '''
            redirect output to private log.

            '''
            print(output.decode('utf-8'), end='')
        else:



            if error.decode() == '' and p.poll() is not None:
                # print("break from elsew clause")
                break
            else:

                '''
                redirect error to error log
                
                '''
                error_buffer.append(error.decode('utf-8'))

    if p.returncode==2:
        print("Error is due to")
        for each_line in error_buffer:
            print(each_line)
        exit(1)
    else:
        return p.returncode



def shell_bash(command):
'''
Handles shell Special characters to be executed as is.
Do not use this function, unless absolute necessary.
'''
    p=subprocess.Popen(['/bin/bash'],shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (stdout,stderr) = p.communicate(str.encode(command))
    if not stderr:
        return stdout.decode('utf-8')
    else:
        print("Error message is",stderr.decode('utf-8'))
        return stdout.decode('utf-8')