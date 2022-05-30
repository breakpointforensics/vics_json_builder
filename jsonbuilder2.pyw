
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

#Imports the splash screen controler used only after commpiling with pyinstaller using splashscreen flag.  uses try method in ase pyi_splash not available so program doesn't crash.
try:
    
    import pyi_splash
    
    # Update the text on the splash screen
    pyi_splash.update_text("Loading")
    pyi_splash.update_text("Please be patient...")
    
    # Close the splash screen. It does not matter when the call
    # to this function is made, the splash screen remains open until
    # this function is called or the Python program is terminated.
    pyi_splash.close()
 
except ImportError:
     pass
 
## Define pseudo constants
SCRIPT_NAME = 'JSON BUILDER'
SCRIPT_VERSION = '3.01'
##Python3 Compliant
##5/29/2022
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
appdatasetting = (str(home_dir) + '\\AppData\\Local\\BreakpointForensics\\VICSBUILDER\\Settings\\')
appdatalog = (str(home_dir) + '\\AppData\\Local\\BreakpointForensics\\VICSBUILDER\\Logs\\')
today = date.today()
mkhomelog = ('mkdir "' + appdatalog + '"')
os.system(mkhomelog)
mkhomesetting = ('mkdir "' + appdatasetting + '"')
os.system(mkhomesetting)



sg.user_settings_filename(filename=appdatasetting + 'JSONBUILDER_' + SCRIPT_VERSION + '.json')
settings = sg.user_settings()
settings['-SCRIPT_VERSION-'] = SCRIPT_VERSION

## Turn on Logging using standard python logging package, assign logname variable, and set formating for time and messages.
logging.basicConfig(filename=appdatalog + '\\' + str(today) + '_VICSBUILDER.log',level=logging.DEBUG, force=True, format='%(asctime)s %(message)s')
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
    except FileNotFoundError:
        
        print('*ERROR*Please Select Valid JSON')
        return    

    return 'Done!'

def buildjson(sourceID,carveoutparent):
    carveoutparent = carveoutparent.replace("/", "\\")
    logging.info('JSON Builder Initialized with sourceID: ' + str(sourceID) + ' & Carved Content Path: ' + carveoutparent)    
    startTime = time.time()
    logging.info('Start Time is: ' + str(startTime))
    ##change cwd to carveoutparent in order to buld correct relative paths
    cwd = carveoutparent
    os.chdir(cwd)
    logging.info('Changing CWD to: ' + cwd)
    print ('Work Directory Set to: ' + cwd)
    ##Create a MediaID Counter to assign ID to files in final JSON
    MediaID = -1
    ##Generate a random case GUID
    GUID = str((uuid.uuid4()))
    logging.info('CaseID GUID Generated: ' + str(GUID))
    jsontarget = (str(sourceID) + '.json')
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
        ##Check if value is dictionary and convert for now to list for more efficient value updates.
        ##Will be converted back to dictionary later after json data blob complete
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
                ##MD5 Field is left blank since we don't waste time calculating MD5 values right now as it will be repeated later anyways with Griffeye import.
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
                ##Since no categorization happening during intial file recovery, IsPrecategorized is hardcoded False
                IsPrecategorized = False
                filedict.update({'IsPrecategorized' : IsPrecategorized})            
                
 
                ##Build sourceID from cwd, not used in favor of user selected sourceID
                #basename = os.path.basename(cwd)            
                #sourceID = basename.split('_')[0]
                ##build filepath
                FilePath = (sourceID + '\\' + RelativeFilePath)
           
                ##Add the correct keys to secondary media files dictionary object
                MediaFilesdict = {}
                MediaFilesdict.update({'MD5' : MD5})
                MediaFilesdict.update({'FileName' : filename})
                MediaFilesdict.update({'FilePath' : FilePath})
                
                ##Get MAC times for files and adjust to proper json formatting per VICS spec
               
                ##Grab Filesystem timestamp and adjust to UTC time based on delta of local system offset
                Created = datetime.datetime.strptime(time.ctime(os.path.getctime(fullpath)- utc_offset), '%c')
                Created = json.dumps(Created.isoformat())
                Created = Created + str(tzinfo)
                Created = Created.replace('"', '')
                MediaFilesdict.update({'Created' : Created})
                
                ##Grab Filesystem timestamp and adjust to UTC time based on delta of local system offset                
                Written = datetime.datetime.strptime(time.ctime(os.path.getmtime(fullpath)- utc_offset), '%c')
                Written = json.dumps(Written.isoformat())
                Written = Written + str(tzinfo)
                Written = Written.replace('"', '')
                MediaFilesdict.update({'Written' : Written})
                
                ##Grab Filesystem timestamp and adjust to UTC time based on delta of local system offset                
                Accessed = datetime.datetime.strptime(time.ctime(os.path.getatime(fullpath)- utc_offset), '%c')
                Accessed = json.dumps(Accessed.isoformat())
                Accessed = Accessed + str(tzinfo)
                Accessed = Accessed.replace('"', '')
                MediaFilesdict.update({'Accessed' : Accessed})
                
                Unallocated = True
                MediaFilesdict.update({'Unallocated' : Unallocated})
                MediaFilesdict.update({'sourceID' : sourceID})
                
                
                ##Set Seperator thats placed in some filenames of recovered files
                sep1 = 'Archives\\'
                sep2 = '_'
                sep3 = '.'
                ##See if File is from Extracted Archive and if we can determine phys location from path
                if '\\Archives\\' in RelativeFilePath:
                    try:
                        #print('Unpacked Archive Found')
                        ##Strips to Left ##Strips at first 'Archives\\' and leading characters
                        PhysicalLocation = str(RelativeFilePath.split(sep1,1)[1])
                        ##Strips to Right ##Strips at first '_' and trailing characters
                        PhysicalLocation = str(PhysicalLocation.split(sep2,1)[0])
                        ##Strips to Right ##Strips at first '.' and trailing characters
                        PhysicalLocation = str(PhysicalLocation.split(sep3,1)[0])                        
                        ##Strip Leading Character and convert to int
                        PhysicalLocation = int(PhysicalLocation[1:])
                        MediaFilesdict.update({'PhysicalLocation' : PhysicalLocation})
                    except:
                        logging.info('Was not able to get valid physical location integer for Unpacked Archive File: ' + RelativeFilePath)
                        ##If unable to deduce physical sector don't add the key:value                        
                        #PhysicalLocation = 0
                        #MediaFilesdict.update({'PhysicalLocation' : PhysicalLocation})                     
                
                if '\\Archives\\' not in RelativeFilePath:
                    
                    ##See if we can determine phys location from filename
                    ##Strip the extension from filename
                    PhysicalLocation = os.path.splitext(filename)[0]
        
                    ##Strips everything right of sep2 including sep
                    PhysicalLocation = str(PhysicalLocation.split(sep2,1)[0])
                    ##Try and strip leading character, and See if remaining value is valid int and write to PhysicalLocation if so
                    try:
                        PhysicalLocation = int(PhysicalLocation[1:])
                        MediaFilesdict.update({'PhysicalLocation' : PhysicalLocation})
                    ##If not valid int log file and move on
                    except:
                        logging.info('Was not able to get valid physical location integer for ' + filename)
                        ##If unable to deduce physical sector don't add the key:value
                        #PhysicalLocation = 0
                        #MediaFilesdict.update({'PhysicalLocation' : PhysicalLocation})  
                    

                
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
                #print ('sourceID= ' + sourceID)
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
                    window['-STATUS-'].update('Building JSON BLOB: '+ str(sourceID) + ' ' + str(progressPercent) + '%')
                    

                
 

    ##Strips the single json blob from list to remove hard out brackets from final json for VICS compliance. 
    data = data[0]
    
    
    ##Try and open the final JSON and write out data.
    try:  
        logging.info('Trying to open: ' + jsontarget + ' to write completed JSON blob to file')
        window['-STATUS-'].update('Writing JSON to File Please wait...This might take a second...')        
        with open(jsontarget, 'w') as f:
            f.write(json.dumps(data, indent=4, separators=(',', ':')))
        print(str(sourceID) + ' JSON Successfully Updated')
        logging.info('JSON Successfully Updated')    
    
    except (KeyError, OSError, NameError) as error:
        logging.exception('Error writing JSON blob to file for: ' + str(sourceID))
        print('Error writing JSON blob to file for: ' + str(sourceID))
        exception = True
        return    

    
    window['-STATUS-'].update('Almost done...Cleaning up...')

    
    
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
    logging.info('JSON with ' + str(MediaID + 1) + ' Entries Generated')
    print ('Total Runtime= ' + total_time)
    logging.info('Total Runtime= ' + total_time)
    print ('JSON saved to: ' + str(jsonoutlocation))
    logging.info('JSON saved to: ' + str(jsonoutlocation))
    window['-STATUS-'].update('Completed')


def main():
    
    
    global window
    global sourceID


    global SEARCH_TYPES
    global carveoutparent



    '''
    *****************************************************************************************
    Main User Interface
    *****************************************************************************************
    '''
    
    
    sg.theme('Dark Gray 11 ')
    ##Define layout window for PySimpleGUI
    
    icon1 = b'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'

     
    layout = [
              [sg.Titlebar('Breakpoint Forensics', icon=icon1, background_color="#373737")],
              [sg.Text('VICS JSON BUILDER', size=(30, 1), justification='center', font=("Unispace", 25), relief=sg.RELIEF_RIDGE)],
              [sg.Text('Build VICS JSON', font=('Helvetica', 13), relief=sg.RELIEF_RIDGE)],
              [sg.Text('Enter Source Name/ID', size =(28,1)), sg.InputText(sg.user_settings_get_entry('-sourceID-', ''), key = 'sourceID')],
              [sg.Text('_'  * 100, size=(80, 1))],              
              [sg.Text('Select Carved Content Source Folder')],
              [sg.Input(sg.user_settings_get_entry('-carveoutparent-', ""), key='carveoutparent'), sg.FolderBrowse()],
              [sg.Button('Build JSON')],
              [sg.Text('_'  * 100, size=(80, 1))],
              [sg.Text('JSON Format Fixer', font=('Helvetica', 13), relief=sg.RELIEF_RIDGE)], 
              [sg.Text('Select Existing JSON')],              
              [sg.Input(sg.user_settings_get_entry('-jsonin-', ''), key='jsonin'), sg.FilesBrowse(file_types=(('JSON', 'json'),))],
              [sg.Text('Indent Level', size =(10,1)), sg.Input(size=(4,10), default_text=4, key = 'indentlevel')],
              [sg.Button('Fix JSON'), sg.Push(), sg.Button('Quit'), sg.Button('Logs')],
              #Shows Dynamic Status bar
              [sg.Text(s=(90,1), k='-STATUS-')],
              [sg.Output(size=(78,10), key='-OUTPUT-')],
              [sg.Push(), sg.Text('V3')],
              ]
    
    
    
    window = sg.Window('VICS JSON BUILDER', layout=layout, alpha_channel=.99, icon=icon1, size=(600, 670))
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
    
            
        
    
        sourceID = values['sourceID']
        carveoutparent = values['carveoutparent'] 
        carveoutparent = carveoutparent.replace("/", "\\")
        indentlevel = values['indentlevel']
        #print ('Location of files to build JSON from: '+ str(carveoutparent))
        #jsonpath = values['jsonpath']
        #jsonpath = jsonpath.replace("/", "\\")
        sg.user_settings_set_entry('-sourceID-', values['sourceID'])
        sg.user_settings_set_entry('-carveoutparent-', values['carveoutparent'])
        #sg.user_settings_set_entry('-jsonpath-', values['jsonpath'])        
        
        jsonin = values['jsonin']
        if os.path.exists(jsonin):
            jsonin = jsonin.replace("/", "\\")
            print ('JSON Input path: ' + str(jsonin))        


            
        ##Register even and validation logic when start button pressed
        if event  == 'Build JSON':

            
            ##Check length of sourceID to validate input
            if len(sourceID) >= 4:
                print('Valid Source ID Entered')
                
    
                ##Use os module to validate if specified folder is valid.
                if os.path.exists(carveoutparent):
                    ##If folder is valid, print notification, log validation, and break loop to continue script.
                    print("Valid Source Folder Entered!")
                    logging.info("Valid Source Folder Entered: " + carveoutparent)
                    
                    
                    logging.info('Calling JSON Builder')
                    window.perform_long_operation(lambda :
                                                  buildjson(sourceID,carveoutparent),
                                                  '-END KEY-')                     
                    
   
                        
                else:
                     print('Please Enter Valid Source Folder Containing Files to build JSON from')
            else:            
                print('Please enter valid sourceID containing at least 4 characters!')
    
        
        
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
            logpath = os.path.realpath(appdatalog)
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
