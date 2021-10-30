import sys
sys.path.append("..") # Adds higher directory to python modules path.
import os
import re
import asana
from atlassian import Confluence, Jira
from datetime import datetime
import logging
import requests
from pathlib import Path

from models import *

# disable ssl warnings
requests.packages.urllib3.disable_warnings() 

# initialize logging
logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.ERROR)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

PARENT_PAGE_ID = 138379763

def getAbsolutePath(path):
    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    abs_file_path = os.path.join(script_dir, path)
    return abs_file_path

def readConfig(filename): 
    myprops = {}
    config_file = getAbsolutePath(filename)
    with open(config_file, 'r') as f:
        for line in f:
            line = line.rstrip() #removes trailing whitespace and '\n' chars

            if '=' not in line: continue #skips blanks and comments w/o =
            if line.startswith('#'): continue #skips comments which contain =

            k, v = line.split('=', 1)
            myprops[k] = v
    return myprops

def main():
    
    myprops = readConfig('../config.properties')

    # replace with your personal access token. 
    personal_access_token = myprops['asana.token']

    # Construct an Asana client
    client = asana.Client.access_token(personal_access_token)
    # Set things up to send the name of this script to us to show that you succeeded! This is optional.
    client.options['client_name'] = "tk_export_proof"

    # Get your user info
    me = client.users.me()

    # Print out your information
    log.debug(f"Hello world! My name is {me['name']}!")
    
    log.info("Fertig!")


## CALL THE MAIN METHOD
if __name__ == '__main__':
    main()