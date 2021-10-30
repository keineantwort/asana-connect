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
class AsanaObj:
    gid: str


@dataclass
class EnumValue(AsanaObj):
    name: str


@dataclass
class CustomEnumField(AsanaObj):
    value: EnumValue


class STATUS(Enum):
    IN_ANPASSUNG = EnumValue(
        gid='1200621791199812',
        name="In Anpassung (TK)"
    )
    IM_NACHWEIS = EnumValue(
        gid='1200621791199813',
        name="Im Nachweis (TK)",
    )
    IN_PRUEFUNG = EnumValue(
        gid='1200621791199814',
        name="In Prüfung (PwC)"
    )
    EINGEFROREN = EnumValue(
        gid='1200621797503147',
        name="Eingefroren (PwC)"
    )
    ABGESCHLOSSEN = EnumValue(
        gid='1200621791199815',
        name="Abgeschlossen (TK & PwC)"
    )
    def find(gid:int):
        for it in STATUS:
            if gid == it.value.gid:
                return it
        return None

@dataclass
class Task(AsanaObj):
    name: str
    status: CustomEnumField = None

    def set_status(self, status: STATUS):
        if status:
            self.status = CustomEnumField(gid = '1200621791199811', value = status.value)


# disable ssl warnings
requests.packages.urllib3.disable_warnings()

# initialize logging
logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.ERROR)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

"""
GIDs Projekt gematik-AFOs
Asana Status:
    Custom-Field-GID: 1200621791199811
    Values:
        Im Nachweis: 1200621791199813
        In Prüfung: 1200621791199814
"""


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


def main():

    myprops = readConfig('config.properties')

    # replace with your personal access token.
    personal_access_token = myprops['asana.token']

    # Construct an Asana client
    client = asana.Client.access_token(personal_access_token)
    # Set things up to send the name of this script to us to show that you succeeded! This is optional.
    client.options['client_name'] = "tk_export_proof"

    tasks = client.tasks.find_by_project(project=myprops['asana.project_id'], params={"opt_fields": "name,custom_fields"})

    # A_15254-01

    for t in tasks:
        #log.debug(f" Task: {t['name']}")
        task = Task(gid=t['gid'], name=t['name'])
        status = None
        for f in t['custom_fields']:
            if f['gid'] == "1200621791199811":
                status = STATUS.find(f['enum_value']['gid'])
        task.set_status(status)
        #log.debug(f"{task}")
        if "A_15254-01" in task.name:
            #/Users/martin/tmp/upload
            for filename in os.listdir("/Users/martin/tmp/upload"):
                with open(os.path.join("/Users/martin/tmp/upload", filename), 'rb') as f:
                    #to asana
                    content = f.read()
                    log.debug(f" {filename}, {len(content)}")
                    r1 = client.attachments.create_on_task(task_id=task.gid, file_content=content, file_name=filename, file_content_type=None)
                    log.debug(r1)
                    r2 = client.tasks.update(task=task.gid, params= {"custom_fields" : { "1200621791199811" : STATUS.IN_PRUEFUNG.value.gid }})
                    log.debug(r2)


    log.info("Fertig!")


# CALL THE MAIN METHOD
if __name__ == '__main__':
    main()
