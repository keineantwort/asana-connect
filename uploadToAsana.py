import logging
import os
import re
from dataclasses import dataclass, field
#from atlassian import Confluence, Jira
from datetime import datetime
from enum import Enum
from pathlib import Path

import asana
import requests

#from models import *

@dataclass
class EnumValue:
    name: str
    gid: str
    gid2: str = None

class STATUS(Enum):
    IN_ANPASSUNG = EnumValue(
        gid='1200621791199812',
        gid2='1200769985237987',
        name="In Anpassung (TK)"
    )
    IM_NACHWEIS = EnumValue(
        gid='1200621791199813',
        gid2="1200769985237988",
        name="Im Nachweis (TK)",
    )
    IN_PRUEFUNG = EnumValue(
        gid='1200621791199814',
        gid2="1200769985237989",
        name="In Prüfung (PwC)"
    )
    EINGEFROREN = EnumValue(
        gid='1200621797503147',
        gid2="1200769985237990",
        name="Eingefroren (PwC)"
    )
    ABGESCHLOSSEN = EnumValue(
        gid='1200621791199815',
        gid2="1200769985237991",
        name="Abgeschlossen (TK & PwC)"
    )
    def find(gid:int):
        for it in STATUS:
            if gid == it.value.gid or gid == it.value.gid2:
                return it
        return None

@dataclass
class Task:
    gid: str
    task_id: str
    name: str
    status_custom_field_gid: str
    status: STATUS = None


# disable ssl warnings
requests.packages.urllib3.disable_warnings()

# initialize logging
logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.ERROR)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def getAbsolutePath(path):
    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    abs_file_path = os.path.join(script_dir, path)
    return abs_file_path


def readConfig(filename):
    myprops = {}
    config_file = getAbsolutePath(filename)
    with open(config_file, 'r') as f:
        for line in f:
            line = line.rstrip()  # removes trailing whitespace and '\n' chars

            if '=' not in line:
                continue  # skips blanks and comments w/o =
            if line.startswith('#'):
                continue  # skips comments which contain =

            k, v = line.split('=', 1)
            myprops[k] = v
    return myprops

def get_tasks_from_asana(project_id, custom_field_gid, splitter): 
    tasksFromAsana = client.tasks.find_by_project(project=project_id, params={"opt_fields": "name,custom_fields"})  
    tasks = {}
    for t in tasksFromAsana:
        #log.debug(f" Task: {t['name']}")
        name = t['name']
        task_id = name.split(splitter, 1)[0]
        task = Task(gid=t['gid'], name=name, task_id=task_id, status_custom_field_gid=custom_field_gid)
        status = None
        for f in t['custom_fields']:
            if f['gid'] == "1200621791199811" or f['gid'] == "1200769985237986":
                status = STATUS.find(f['enum_value']['gid'])
        task.status = status
        if not task.status:
            log.debug(f"!! Task '{task.name}' has no state!")
        tasks[task_id] = task
    return tasks

def main():
    
    myprops = readConfig('config.properties')

    # replace with your personal access token.
    personal_access_token = myprops['asana.token']
    global client
    # Construct an Asana client
    client = asana.Client.access_token(personal_access_token)
    # Set things up to send the name of this script to us to show that you succeeded! This is optional.
    client.options['client_name'] = "tk_export_proof"

    tasks = {
        **get_tasks_from_asana(project_id=myprops['asana.project_id.1'], splitter=" -- ", custom_field_gid="1200621791199811"),
        **get_tasks_from_asana(project_id=myprops['asana.project_id.2'], splitter=" - ", custom_field_gid="1200769985237986")
        }
    log.debug(len(tasks))
    
    if "A_15254-01" in tasks:
        task = tasks["A_15254-01"]
        for filename in os.listdir("/Users/martin/tmp/upload"):
            with open(os.path.join("/Users/martin/tmp/upload", filename), 'rb') as f:
                #to asana
                content = f.read()
                log.debug(f" {filename}, {len(content)}")
                #r1 = client.attachments.create_on_task(task_id=task.gid, file_content=content, file_name=filename, file_content_type=None)
                #log.debug(r1)
                #f.close()
            #r2 = client.tasks.update(task=task.gid, params={"custom_fields" : { task.status_custom_field_gid : STATUS.IN_PRUEFUNG.value.gid }})
            #log.debug(r2)

    log.info("Fertig!")


# CALL THE MAIN METHOD
if __name__ == '__main__':
    main()
