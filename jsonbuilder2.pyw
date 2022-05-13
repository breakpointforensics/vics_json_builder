
'''
*****************************************************************************************
Modules
*****************************************************************************************
'''
##Import Modules
import PySimpleGUI as sg 
import os
from builtins import input
from builtins import str
from pathlib import Path
import sys      #Imports the Standard Python sys module.
import logging  #Imports the Standard Python logging module.
import time     #Imports the Standard Python time module.
import os       #Imports the Standard Python os module.
import stat     #Imports the Standard Python stat module.
import subprocess #Imports the Standard Python subprocess module for cmdline calls.
from datetime import timedelta
from datetime import date
import json
import uuid
import math
import datetime


## Define pseudo constants
SCRIPT_NAME = 'JSON BUILDER'
SCRIPT_VERSION = '2'
##Python3 Compliant
##5/13/2022
##Author: David Haddad
JSON_TYPES = '.json'
indentlevel = 4
##Set Timezone paramenter to fixup MAC timestamps later for JSON compliance
tzinfo = '+00:00'

##Get Current UTC Offset
utc_offset = time.localtime().tm_gmtoff
##Get corrected ZTIME delta from local machine
ztimedelta = datetime.timezone(datetime.timedelta(0, -int(utc_offset)))

##Create extension lists of different MimeTypes
IMAGE_TYPES = ['.ai', '.bmp', '.cam', '.cr2', '.gif', '.heic', '.heif', '.ind', '.indd', '.j2k', '.jfi', '.jfif', '.jif', '.jp2', '.jpe', '.jpeg', '.jpf', '.jpg', '.jpx', '.k25', '.mj2', '.nrw', '.pct', '.png', '.psb', '.psd', '.psd', '.raw', '.rw2', '.svg', '.svgz', '.tif', '.tiff', '.wdp', '.x3f', '.xcf', 'arw', 'dib', 'dsc', 'eps', 'indt', 'jpm', 'webp']
VIDEO_TYPES = [',dv', '.3g2', '.3gp', '.amv', '.asf', '.avi', '.drc', '.f4a', '.f4b', '.f4v', '.flv', '.gifv', '.m2ts', '.m2v', '.m4p', '.m4v', '.mng', '.mov', '.mp2', '.mp4', '.mpe', '.mpeg', '.mpg', '.mts', '.nsv', '.ogg', '.ogv', '.rm', '.roq', '.svi', '.ts', '.viv', '.vob', '.wmv', '.yuv', 'f4p', 'm4v', 'mkv', 'mpv', 'mxf', 'rmvb', 'webm']
DOC_TYPES = ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.odt', '.ods', '.odp']

EXT_LIST = (IMAGE_TYPES + VIDEO_TYPES + DOC_TYPES)



initialcwd = os.getcwd()
print ('Initial Directory is: ' + str(initialcwd))

##Get Home dir for user and build paths for setting and log locations
home_dir = Path.home()
bfipappdatasetting = (str(home_dir) + '\\AppData\\Local\\BreakpointForensics\\VICSBUILDER\\Settings\\')
bfipappdatalog = (str(home_dir) + '\\AppData\\Local\\BreakpointForensics\\VICSBUILDER\\Logs\\')
today = date.today()
mkhomelog = ('mkdir "' + bfipappdatalog + '"')
os.system(mkhomelog)
mkhomesetting = ('mkdir "' + bfipappdatasetting + '"')
os.system(mkhomesetting)



IMPORT_SETTINGS = "CustomImportSettings.json"
sg.user_settings_filename(filename=bfipappdatasetting + 'JSONBUILDER_' + SCRIPT_VERSION + '.json')
settings = sg.user_settings()
settings['-SCRIPT_VERSION-'] = SCRIPT_VERSION
precedSourceList = []

## Turn on Logging using standard python logging package, assign logname variable, and set formating for time and messages.
logging.basicConfig(filename=bfipappdatalog + '\\' + str(today) + '_VICSBUILDER.log',level=logging.DEBUG, force=True, format='%(asctime)s %(message)s')
logging.info('Program Started')



def fixjson(jsonin):
    print('Cleaning up JSON Formating')
    logging.info('Opening: ' + jsonin + ' to fixup formatting')
    try:
        ##Try and open the json and fix the formating.
        with open(jsonin, encoding='utf-8-sig', errors='ignore') as json_data:
            data = json.load(json_data, strict=False)
        logging.info('"fixjson" Opened JSON Successfully')
        
        
        with open(jsonin, 'w') as f:
            f.write(json.dumps(data, indent=indentlevel, separators=(',', ':')))
        print('JSON Successfully Updated')
        logging.info('JSON Successfully Updated')
    except KeyError:
        ##If there's a key error cause the lace values aren't added already, log the error.
        logging.exception('Error fixing formatting of JSON data File')
        print('Error fixing formatting of JSON data to  File')
        pass

    return 'Done!'

def buildjson(SourceID,carveoutparent):
    carveoutparent = carveoutparent.replace("/", "\\")
    logging.info('JSON Builder Initialized with SourceID: ' + str(SourceID) + ' & Carved Content Path: ' + carveoutparent)    
    startTime = time.time()
    logging.info('Start Time is: ' + str(startTime))
    ##change cwd to carveoutparent in order to buld correct relative paths
    cwd = carveoutparent
    os.chdir(cwd)
    logging.info('Changing CWD to: ' + cwd)
    print ('Work Directory Set to: ' + cwd)
    MediaID = -1
    GUID = str((uuid.uuid4()))
    logging.info('CaseID GUID Generated: ' + str(GUID))
    jsontarget = (str(SourceID) + '.json')
    jsonoutlocation = os.path.join(carveoutparent, jsontarget)
    logging.info('JSON Will be saved to: ' + str(jsonoutlocation))
    
    ##Build Empty VICS JSON FILE
    try:
        logging.info('Trying to build empty JSON Shell')
        ##Empty VICS SHELL WITH NEW GUID
        data = {'@odata.context': 'http://github.com/VICSDATAMODEL/ProjectVic/DataModels/2.0.xml/US/$metadata#Cases', 'value': [{'CaseID': GUID, 'Media': [], 'SourceApplicationName': 'BFIP4GRIFFEYE'}]}
        
        ##write the values out
        with open('temp.json', 'w') as f:
            f.write(json.dumps(data, indent=indentlevel, separators=(',', ':')))
        print('Empty VICS JSON Created')
        logging.info('Empty VICS JSON Created')
    except (KeyError, OSError, NameError) as error:
        logging.exception('Error writing Empty VICS JSON data to File')
        print('Error writing JSON data to File')
        exception = True
        return  
    
    try:
        logging.info('Trying to open empty JSON Object for writing')    
        ##Opens the empty JSON and keeps it open in data object
        data = json.load(open('temp.json'))
        logging.info('VICS JSON DATA Object Loaded and waiting for entries')
        if type(data) is dict:
            data = [data]
        ##Set target subkey/list to update
        logging.info('Appending Media Subkey')
        data[0]['value'][0]['Media']= []
    
    except (KeyError, OSError, NameError) as error:
        logging.exception('Error Loading JSON Object as data')
        print('Error loading JSON Object')
        exception = True
        return       
    
    
    window['-STATUS-'].update('Building JSON Object Please wait...This might take a while for lots of files')
    
    ##Get total files in source
    count = sum([len(files) for r, d, files in os.walk(carveoutparent)])
    progress = 0
    ##Get initial time to use for tracking when to report status percent updates during hashing
    prev_time = time.time()  
    


        
    logging.info('Starting File Search and JSON Entry Appending Process')    
    for dirpath, dirnames, filenames in os.walk(carveoutparent):
        for filename in filenames:
            if filename.lower().endswith(tuple(EXT_LIST)):
                filedict = {}
                ##Increment MediaID variable
                MediaID = (MediaID +1)
                filedict.update({'MediaID' : MediaID})
                #Category = 0
                #filedict.update({'Category' : Category})
                MD5 = ''
                filedict.update({'MD5' : MD5})
                ##Join the root path and filename for fullpath
                fullpath = os.path.abspath(os.path.join(dirpath, filename))
                MediaSize = os.path.getsize(fullpath)
                filedict.update({'MediaSize' : MediaSize})
                ##Build the relative path for file relative to carveoutparent
                RelativeFilePath = os.path.relpath(os.path.join(dirpath, filename))
                ##Format Slashs for double slashes per VICS Examples
                RelativeFilePath = str(RelativeFilePath.replace("\\", "/"))
                RelativeFilePath = str(RelativeFilePath.replace("/", "\\"))
                filedict.update({'RelativeFilePath' : RelativeFilePath})
                if filename.lower().endswith(tuple(IMAGE_TYPES)):
                    MimeType = 'image'
                if filename.lower().endswith(tuple(VIDEO_TYPES)):
                    MimeType = 'video'
                if filename.lower().endswith(tuple(DOC_TYPES)):
                    MimeType = 'text'                
                filedict.update({'MimeType' : MimeType})            
                IsPrecategorized = False
                filedict.update({'IsPrecategorized' : IsPrecategorized})            
                
                
                
                
                
                ##Build SourceID from cwd
                #basename = os.path.basename(cwd)            
                #SourceID = basename.split('_')[0]
                ##build filepath
                FilePath = (SourceID + '\\' + RelativeFilePath)
           
                ##Add the correct keys to secondary media files dictionary object
                MediaFilesdict = {}
                MediaFilesdict.update({'MD5' : MD5})
                MediaFilesdict.update({'FileName' : filename})
                MediaFilesdict.update({'FilePath' : FilePath})
                
                ##Get MAC times for files and adjust to proper json formatting per VICS spec
               
                
                Created = datetime.datetime.strptime(time.ctime(os.path.getctime(fullpath)- utc_offset), '%c')
                Created = json.dumps(Created.isoformat())
                Created = Created + str(tzinfo)
                Created = Created.replace('"', '')
                MediaFilesdict.update({'Created' : Created})
                
                Written = datetime.datetime.strptime(time.ctime(os.path.getmtime(fullpath)- utc_offset), '%c')
                Written = json.dumps(Written.isoformat())
                Written = Written + str(tzinfo)
                Written = Written.replace('"', '')
                MediaFilesdict.update({'Written' : Written})
                
                Accessed = datetime.datetime.strptime(time.ctime(os.path.getatime(fullpath)- utc_offset), '%c')
                Accessed = json.dumps(Accessed.isoformat())
                Accessed = Accessed + str(tzinfo)
                Accessed = Accessed.replace('"', '')
                MediaFilesdict.update({'Accessed' : Accessed})
                
                Unallocated = True
                MediaFilesdict.update({'Unallocated' : Unallocated})
                MediaFilesdict.update({'SourceID' : SourceID})
                ##Strip the extension from filename
                PhysicalLocation = os.path.splitext(filename)[0]
                ##Set Seperator thats placed in some filenames of recovered files
                sep = '_'
                ##Strips everything right of sep including sep
                PhysicalLocation = str(PhysicalLocation.split(sep,1)[0])
                ##See if remaining value is valid int and write to PhysicalLocation if so
                try:
                    PhysicalLocation = int(PhysicalLocation[1:])
                    MediaFilesdict.update({'PhysicalLocation' : PhysicalLocation})
                ##If not valid int log file and move on
                except:
                    logging.info('Was not able to get valid physical location integer for ' + filename)
                    pass  
                    

                
                ##Update the subdictionary 'MediaFiles' with sub keys
                filedict.update({'MediaFiles': [MediaFilesdict]})
    
                
                
                
                
                #print('')
                #print('_____________________________________________________________')
                ##Print of Individual Fields Section disabled to speed up program
                
                #print ('Media ID= ' + str(MediaID))
                #print ('Category= ' + str(Category))
                #print ('IsPrecategorized= ' + str(IsPrecategorized))
                #print ('Filename= ' + filename)
                #print ('Full Path= ' + str(fullpath))
                #print ('Relative Path= ' + str(RelativeFilePath))
                #print ('MimeType= ' + MimeType)
                #print ('Unallocated= ' + str(Unallocated))
                #print ('SourceID= ' + SourceID)
                #print ('Physical Sector Offset= ' + str(PhysicalLocation))
                #print ('Media Size= ' + str(MediaSize))
                #print ('Created= ' + str(Created))
                #print ('Modified= ' + str(Written))
                #print ('Accessed= ' + str(Accessed))
                
                
                #print('_____________________________________________________________')
                #print('File Dictionary Object:')
                #print(filedict)
                
  
                
                ##Uses append method for data object that remains open until loop completes
                ##appends to Media key
                data[0]['value'][0]['Media'].append(filedict)
                
                ##Build out progress meter
                ##Increment loop progress count
                progress += 1
                ## Checks for time delta since last update
                dt = time.time() - prev_time

                if dt > 3:
                    ## If greater then 3 updates new prev_time
                    prev_time = time.time()
                    ##Compute Progress
                    ##Get Progress percent by comparing progress count with total sum of files.
                    progressPercent = (100.0*progress)/count
                    ##Truncate Percent to whole number
                    progressPercent = math.trunc(progressPercent)
                    ##Return current percent in status bar of window
                    window['-STATUS-'].update('Building JSON BLOB: ' + str(progressPercent) + '%')
                    

                

                
 
    ##Now that loop is finished convert to the data list to a string to do some additional cleanup to ensure proper JSON compliant
    datastring = str(data)
    ##Strip [] add beginning and end of json
    datastring = datastring[1:-1]
    ## Replace single with double quotes
    datastring = datastring.replace("'", '"')
    ##Set booleans to lowercase per JSON spec
    datastring = datastring.replace("True", 'true')
    datastring = datastring.replace("False", 'false')
    
    
    
    
    try:
        logging.info('Trying to open: ' + jsontarget + ' to write completed JSON blob to file')
        window['-STATUS-'].update('Writing JSON to File Please wait...This might take a second...')
        with open(jsontarget, 'a') as f:
            f.write(str(datastring))
        logging.info(jsontarget + ' Opened Successfully')
        
    except (KeyError, OSError, NameError) as error:
        logging.exception('Error writing JSON blob to file')
        print('Error writing JSON blob to file')
        exception = True
        return     
    
    
    window['-STATUS-'].update('Almost done...Cleaning up JSON Formating')
    ##Sending final jsonfile to fixjson function to pretty up formatting
    logging.info('Sending final JSON File to fixjson function to clean up formatting')
    jsonin = jsontarget
    fixjson(jsonin)
    
    
    ##Cleanup Temp File
    try:
        os.remove('temp.json')
    except (OSError, NameError) as error:
        logging.exception('Error Removing Temp File')
        print('Error removing temp file')
        pass     
    
    ##Print and log total runtime
    endtime = time.time()
    total_time = endtime - startTime
    ##print('Total Runtime= ' + str(total_time))
    ##use time delta to format time better
    total_time = str(timedelta(seconds=total_time))
    print('_____________________________________________________________')
    
    os.startfile(cwd)
    ##Now that finished return script to initial CWD.
    os.chdir(initialcwd)
    print ('Restored Working Directory is: ' + str(initialcwd))
    print ('JSON with ' + str(MediaID + 1) + ' Entries Generated')
    print ('Total Runtime= ' + total_time)
    print ('JSON saved to: ' + str(jsonoutlocation))    


def main():
    
    
    global window
    global SourceID


    global SEARCH_TYPES
    global carveoutparent



    '''
    *****************************************************************************************
    Main User Interface
    *****************************************************************************************
    '''
    
    
    sg.theme('Dark Gray 11 ')
    ##Define layout window for PySimpleGUI
    
    icon1 = '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'

     
    layout = [#[sg.Column([[logo]], justification='center')],
              [sg.Text('VICS JSON BUILDER', size=(30, 1), justification='center', font=("Unispace", 25), relief=sg.RELIEF_RIDGE)],
              [sg.Text('Build VICS JSON', font=('Helvetica', 13), relief=sg.RELIEF_RIDGE)],
              [sg.Text('Enter Source Name/ID', size =(28,1)), sg.InputText(sg.user_settings_get_entry('-SourceID-', ''), key = 'SourceID')],
              [sg.Text('_'  * 100, size=(80, 1))],              
              [sg.Text('Select Carved Content Source Folder')],
              [sg.Input(sg.user_settings_get_entry('-carveoutparent-', ""), key='carveoutparent'), sg.FolderBrowse()],
              [sg.Button('Build JSON')],
              #[sg.Text('JSON Output Location', font=('Helvetica', 13), relief=sg.RELIEF_RIDGE)], 
              #[sg.Input(sg.user_settings_get_entry('-jsonpath-', ''), key='jsonpath'), sg.FileSaveAs(file_types=(('JSON', 'json'),))],
              [sg.Text('_'  * 100, size=(80, 1))],
              [sg.Text('JSON Format Fixer', font=('Helvetica', 13), relief=sg.RELIEF_RIDGE)], 
              [sg.Text('Select Existing JSON')],              
              [sg.Input(sg.user_settings_get_entry('-jsonin-', ''), key='jsonin'), sg.FilesBrowse(file_types=(('JSON', 'json'),))],
              [sg.Text('Indent Level', size =(10,1)), sg.Input(size=(4,10), default_text=4, key = 'indentlevel')],
              [sg.Button('Fix JSON'), sg.Push(), sg.Button('Quit'), sg.Button('Logs')],
              #Shows Dynamic Status bar
              [sg.Text(s=(90,1), k='-STATUS-')],
              [sg.Output(size=(78,10), key='-OUTPUT-')],
              [sg.Push(), sg.Text('V2')],
              ]
    
    
    
    window = sg.Window('VICS JSON BUILDER', layout=layout, alpha_channel=.99, icon='icon.ico', location=(1,1), size=(600, 600))
    #print (settings)
   
    while True:
        event, values = window.read()
        #print (values)
               
    
        if event == sg.WIN_CLOSED or event == 'Quit':
            sys.exit()
            break
        
        
        if event == sg.WINDOW_CLOSED:
            sys.exit()
            break
    
            
        
    
        SourceID = values['SourceID']
        carveoutparent = values['carveoutparent'] 
        carveoutparent = carveoutparent.replace("/", "\\")
        indentlevel = values['indentlevel']
        #print ('Location of files to build JSON from: '+ str(carveoutparent))
        #jsonpath = values['jsonpath']
        #jsonpath = jsonpath.replace("/", "\\")
        sg.user_settings_set_entry('-SourceID-', values['SourceID'])
        sg.user_settings_set_entry('-carveoutparent-', values['carveoutparent'])
        #sg.user_settings_set_entry('-jsonpath-', values['jsonpath'])        
        
        jsonin = values['jsonin']
        if os.path.exists(jsonin):
            jsonin = jsonin.replace("/", "\\")
            print ('JSON Input path: ' + str(jsonin))        


            
        ##Register even and validation logic when start button pressed
        if event  == 'Build JSON':

            
            ##Check length of SourceID to validate input
            if len(SourceID) >= 4:
                print('Valid Source ID Entered')
                
    
                ##Use os module to validate if specified folder is valid.
                if os.path.exists(carveoutparent):
                    ##If folder is valid, print notification, log validation, and break loop to continue script.
                    print("Valid Source Folder Entered!")
                    logging.info("Valid Source Folder Entered: " + carveoutparent)
                    
                    
                    logging.info('Calling JSON Builder')
                    window.perform_long_operation(lambda :
                                                  buildjson(SourceID,carveoutparent),
                                                  '-END KEY-')                     
                    
   
                        
                else:
                     print('Please Enter Valid Source Folder Containing Files to build JSON from')
            else:            
                print('Please enter valid SourceID containing at least 4 characters!')
    
        
        
        if event == 'Fix JSON':
            print(indentlevel)
            window['-STATUS-'].update('Parsing JSON Please wait...This might take a second for big files')
            window.perform_long_operation(lambda :
                                                       fixjson(jsonin),
                                                       '-END KEY-')              
          
        
        elif event == '-END KEY-':
            return_value = values[event]
            window['-STATUS-'].update(f'Status: {return_value}')
            print ('All Finished')
            logging.info('JSON  Built')
            
            sg.popup("Process Completed")        
            
        
        ##Opens Log Folder in Explorer
        elif event == 'Logs':
            logpath = os.path.realpath(bfipappdatalog)
            os.startfile(logpath)
        
            
        elif event == '-END KEY-':
            return_value = values[event]
            window['-STATUS-'].update(f'Status: {return_value}')
            print ('All Finished')
            logging.info('Process Finished')
            sg.popup("Process Completed")            
    
    '''
    *****************************************************************************************
    End Main User Interface
    *****************************************************************************************
'''
if __name__ == "__main__":
    main()
