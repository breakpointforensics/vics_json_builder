
'''
*****************************************************************************************
Modules
*****************************************************************************************
'''
#Import Modules
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
#Python3 Compliant
#5/02/2022
#Author: David Haddad
JSON_TYPES = '.json'
##Set Timezone paramenter to fixup MAC timestamps later for JSON compliance
tzinfo = '+00:00'

##Get Current UTC Offset
utc_offset = time.localtime().tm_gmtoff
##Get corrected ZTIME delta from local machine
ztimedelta = datetime.timezone(datetime.timedelta(0, -int(utc_offset)))
print ('LOCAL UTC OFFSET: ' + str(utc_offset))
print ('Delta Value to adjust back to Zeulu Time: ' + str(ztimedelta))



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
            f.write(json.dumps(data, indent=4, separators=(',', ':')))
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
            f.write(json.dumps(data, indent=4, separators=(',', ':')))
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
                PhysicalLocation = os.path.splitext(filename)[0]
                PhysicalLocation = int(PhysicalLocation[1:])
                MediaFilesdict.update({'PhysicalLocation' : PhysicalLocation})            
                
                
                
                ##Update the subdictionary 'MediaFiles' with sub keys
                filedict.update({'MediaFiles': [MediaFilesdict]})
    
                
                
                
                
                #print('')
                #print('_____________________________________________________________')
                ##Print of Individual Fields Section disabled to speed up program
                
                #print ('Media ID= ' + str(MediaID))
                ##print ('Category= ' + str(Category))
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
    print ('JSON saved to: ' + str(jsonoutlocation))    
    
    
def cypher(message):
    cypher_words = []
    for letter in message:
        cypher_letter = format(ord(letter), 'b')
        cypher_words.append(cypher_letter)
    return ' '.join(cypher_words)    

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
    #Define layout window for PySimpleGUI
    

     
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


            
        #Register even and validation logic when start button pressed
        if event  == 'Build JSON':

            
            #Check length of SourceID to validate input
            if len(SourceID) >= 4:
                print('Valid Source ID Entered')
                
    
                #Use os module to validate if specified folder is valid.
                if os.path.exists(carveoutparent):
                    #If folder is valid, print notification, log validation, and break loop to continue script.
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
            
        
        #Opens Log Folder in Explorer
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
