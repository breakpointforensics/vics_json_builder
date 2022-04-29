
'''
*****************************************************************************************
Modules
*****************************************************************************************
'''
#Import Modules

from tkinter import Tk  		    #Imports the standard Python Tkinter module as the alias Tk.
from tkinter.filedialog import askdirectory    #Import just askopenfilename from tkFileDialog
import os
from builtins import input
from builtins import str
from pathlib import Path
import sys      #Imports the Standard Python sys module.
import time     #Imports the Standard Python time module.
import os       #Imports the Standard Python os module.
import stat     #Imports the Standard Python stat module.
from datetime import timedelta
from datetime import date
#import logging  #Imports the Standard Python logging module.
import subprocess #Imports the Standard Python subprocess module for cmdline calls.
import uuid

import json

# Define pseudo constants
SCRIPT_NAME = 'Prec2Dict_ramappend'
SCRIPT_VERSION = '1'
#Python3 Compliant
#4/29/2022
#Author: David Haddad



initialcwd = os.getcwd()
print ('Initial Directory is: ' + str(initialcwd))
IMAGE_TYPES = ['.ai', '.bmp', '.cam', '.cr2', '.gif', '.heic', '.heif', '.ind', '.indd', '.j2k', '.jfi', '.jfif', '.jif', '.jp2', '.jpe', '.jpeg', '.jpf', '.jpg', '.jpx', '.k25', '.mj2', '.nrw', '.pct', '.png', '.psb', '.psd', '.psd', '.raw', '.rw2', '.svg', '.svgz', '.tif', '.tiff', '.wdp', '.x3f', '.xcf', 'arw', 'dib', 'dsc', 'eps', 'indt', 'jpm', 'webp']
VIDEO_TYPES = [',dv', '.3g2', '.3gp', '.amv', '.asf', '.avi', '.drc', '.f4a', '.f4b', '.f4v', '.flv', '.gifv', '.m2ts', '.m2v', '.m4p', '.m4v', '.mng', '.mov', '.mp2', '.mp4', '.mpe', '.mpeg', '.mpg', '.mts', '.nsv', '.ogg', '.ogv', '.rm', '.roq', '.svi', '.ts', '.viv', '.vob', '.wmv', '.yuv', 'f4p', 'm4v', 'mkv', 'mpv', 'mxf', 'rmvb', 'webm']
EXT_LIST = (IMAGE_TYPES + VIDEO_TYPES)

Tk().withdraw() 
carveoutparent = askdirectory(title='Please select Sources Root Folder:')
carveoutparent = carveoutparent.replace("/", "\\")
startTime = time.time()
#change cwd to carveoutparent in order to buld correct relative paths
cwd = carveoutparent
os.chdir(cwd)
print ('Word Directory Set to: ' + cwd)
MediaID = -1
GUID = str((uuid.uuid4()))

#Build Empty VICS JSON FILE
try:
    #Empty VICS SHELL WITH NEW GUID
    data = {'@odata.context': 'http://github.com/VICSDATAMODEL/ProjectVic/DataModels/2.0.xml/US/$metadata#Cases', 'value': [{'CaseID': GUID, 'Media': [], 'SourceApplicationName': 'BFIP4GRIFFEYE'}]}
    
    #write the values out
    with open('test.json', 'w') as f:
        f.write(json.dumps(data, indent=4, separators=(',', ':')))
    print('Config JSON Successfully Updated')
except KeyError:
    logging.exception('Error writing JSON data to File')
    print('Error writing JSON data to File')          
    pass  

#Opens the empty JSON and keeps it open in data object
data = json.load(open('test.json'))
if type(data) is dict:
    data = [data]
    
    
for dirpath, dirnames, filenames in os.walk(carveoutparent):
    for filename in filenames:
        if filename.lower().endswith(tuple(EXT_LIST)):
            filedict = {}
            #Increment MediaID variable
            MediaID = (MediaID +1)
            filedict.update({'MediaID' : MediaID})
            Category = 0
            filedict.update({'Category' : Category})
            MD5 = ''
            filedict.update({'MD5' : MD5})
            #Join the root path and filename for fullpath
            fullpath = os.path.abspath(os.path.join(dirpath, filename))
            MediaSize = os.path.getsize(fullpath)
            filedict.update({'MediaSize' : MediaSize})
            #Build the relative path for file relative to carveoutparent
            relativepath = os.path.relpath(os.path.join(dirpath, filename))
            #Format Slashs for double slashes per VICS Examples
            relativepath = str(relativepath.replace("\\", "/"))
            relativepath = str(relativepath.replace("/", "\\"))
            filedict.update({'relativepath' : relativepath})
            Unallocated = True
            filedict.update({'Unallocated' : Unallocated})
            PhysicalLocation = os.path.splitext(filename)[0]
            PhysicalLocation = int(PhysicalLocation[1:])
            filedict.update({'PhysicalLocation' : PhysicalLocation})
            Created = time.ctime(os.path.getctime(fullpath))
            filedict.update({'Created' : Created})
            Modified = time.ctime(os.path.getmtime(fullpath))
            filedict.update({'Modified' : Modified})
            Accessed = time.ctime(os.path.getatime(fullpath))
            filedict.update({'Accessed' : Accessed})
            if filename.lower().endswith(tuple(IMAGE_TYPES)):
                MimeType = 'image'
            if filename.lower().endswith(tuple(VIDEO_TYPES)):
                MimeType = 'video'
            filedict.update({'MimeType' : MimeType})
            
            
            IsPrecategorized = False
            filedict.update({'IsPrecategorized' : IsPrecategorized})
            #Build SourceID from cwd
            basename = os.path.basename(cwd)
            SourceID = basename.split('_')[0]
            filedict.update({'SourceID' : SourceID})
            
            print('')
            print('_____________________________________________________________')
            '''
            print ('Media ID= ' + str(MediaID))
            print ('Category= ' + str(Category))
            print ('IsPrecategorized= ' + str(IsPrecategorized))
            print ('Filename= ' + filename)
            print ('Full Path= ' + str(fullpath))
            print ('Relative Path= ' + str(relativepath))
            print ('MimeType= ' + MimeType)
            print ('Unallocated= ' + str(Unallocated))
            print ('SourceID= ' + SourceID)
            print ('Physical Sector Offset= ' + str(PhysicalLocation))
            print ('Media Size= ' + str(MediaSize))
            print ('Created= ' + str(Created))
            print ('Modified= ' + str(Modified))
            print ('Accessed= ' + str(Accessed))
            '''
            
            print('_____________________________________________________________')
            print('File Dictionary Object:')
            print(filedict)
            
            '''
            with open('Test.json', 'a') as f:
                f.write(str(filedict) + '\n')
            '''    
            
            #Uses append method for data object that remains open until loop completes
            data.append(filedict)


#write the values out to file now that finished.
with open('test.json', 'w') as f:
    f.write(json.dumps(data, indent=4, separators=(',', ':')))


#Print and log total runtime
endtime = time.time()
total_time = endtime - startTime
#print('Total Runtime= ' + str(total_time))
#use time delta to format time better
total_time = str(timedelta(seconds=total_time))
print('_____________________________________________________________')

os.startfile(cwd)
#Now that finished return script to initial CWD.
os.chdir(initialcwd)
print ('Restored Working Directory is: ' + str(initialcwd))
print ('JSON with ' + str(MediaID + 1) + ' Entries Generated')
print ('Total Runtime= ' + total_time)
os.system('pause')
