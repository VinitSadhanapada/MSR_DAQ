from pymodbus.client import ModbusSerialClient as ModbusClient
import time
import datetime
import csv
import os
from termcolor import colored
import curses
import elmeasure_LG6400 as LG6400
import elmeasure_LG5220 as LG5220
import elmeasure_LG5310 as LG5310
import elmeasure_EN8410 as EN8410
import elmeasure_iELR300 as ELR300
import mqtt_client as mqtt
import random

UNIT = 0x1
#PORT = "/dev/ttyUSB0"
PORT = "COM8"

DEV_ELM_LG6400 = "LG6400"
DEV_ELM_LG5310 = "LG+5310"
DEV_ELM_LG5220 = "LG+5220"
DEV_ELM_EN8400 = "EN8400"
DEV_ELM_EN8100 = "EN8100"
DEV_ELM_EN8410 = "EN8410"
DEV_ELM_ELR300 = "ELR300"

NoOfDevices = 3
deviceModels = [DEV_ELM_ELR300, DEV_ELM_ELR300, DEV_ELM_ELR300]
# deviceModels = [DEV_ELM_EN8410, DEV_ELM_EN8100, DEV_ELM_LG5220, DEV_ELM_LG5220, DEV_ELM_LG5220,
#                     DEV_ELM_LG5220, DEV_ELM_LG5220, DEV_ELM_LG5220, DEV_ELM_LG5220, DEV_ELM_LG5220,
#                     DEV_ELM_LG5220, DEV_ELM_LG5220, DEV_ELM_LG5220]
deviceNames = ["Device 1", "Device 2", "Device 3", "Device 4", "Device 5", "Device 6", "Device 7", "Device 8", "Device 9", "Device 10",
                    "Device 11", "Device 12", "Device 13", "Device 14", "Device 15"]

readingInterval = 10
intervalBwReadings = 0
intervalBwMeter = 0.1
published_msg = 0

ERROR_FILE_NAME = "error_log.txt"
#DEVICE_LOG_FOLDER = "Device Log/" # For raspberry pi
#DEVICE_LOG_FOLDER = "Device Log\\" # For windows

Parameters = ['Time', LG6400.WATTS_TOTAL_STR, LG6400.WATTS_R_PH_STR, LG6400.WATTS_Y_PH_STR, LG6400.WATTS_B_PH_STR,
                        LG6400.PH_AVG_STR, LG6400.PH_R_PH_STR, LG6400.PH_Y_PH_STR, LG6400.PH_B_PH_STR,
                        LG6400.VLN_AVG_STR, LG6400.V_R_PH_STR, LG6400.V_Y_PH_STR, LG6400.V_B_PH_STR,
                        LG6400.A_AVG_STR, LG6400.A_R_PH_STR, LG6400.A_Y_PH_STR, LG6400.A_B_PH_STR,
                        LG6400.FREQUENCY_STR,
                        LG6400.WH_RCVD_STR,
                        LG6400.LOAD_HRS_DL_STR,
                        LG6400.NO_OF_INTR_STR,
                        LG6400.ON_HRS_STR,
                        LG6400.V_R_HARMO_STR, LG6400.V_Y_HARMO_STR, LG6400.V_B_HARMO_STR,
                        LG6400.A_R_HARMO_STR, LG6400.A_Y_HARMO_STR, LG6400.A_B_HARMO_STR]
regAdress = [         LG6400.WATTS_TOTAL_ADD, LG6400.WATTS_R_PH_ADD, LG6400.WATTS_Y_PH_ADD, LG6400.WATTS_B_PH_ADD,
                        LG6400.PH_AVG_ADD, LG6400.PH_R_PH_ADD, LG6400.PH_Y_PH_ADD, LG6400.PH_B_PH_ADD,
                        LG6400.VLN_AVG_ADD, LG6400.V_R_PH_ADD, LG6400.V_Y_PH_ADD, LG6400.V_B_PH_ADD,
                        LG6400.A_AVG_ADD, LG6400.A_R_PH_ADD, LG6400.A_Y_PH_ADD, LG6400.A_B_PH_ADD,
                        LG6400.FREQUENCY_ADD,
                        LG6400.WH_RCVD_ADD,
                        LG6400.LOAD_HRS_DL_ADD,
                        LG6400.NO_OF_INTR_ADD,
                        LG6400.ON_HRS_ADD,
                        LG6400.V_R_HARMO_ADD, LG6400.V_Y_HARMO_ADD, LG6400.V_B_HARMO_ADD,
                        LG6400.A_R_HARMO_ADD, LG6400.A_Y_HARMO_ADD, LG6400.A_B_HARMO_ADD]
regValue   = [0] * len(Parameters)
allRegValues = []

##########################################################################
# Function to print register values on console Method 1
##########################################################################
def printRegValues_1(TotalReadings):
    # First clear the screen
    os.system('cls' if os.name == 'nt' else 'clear')

    print ("Total reading cycle" , TotalReadings)

    now = datetime.datetime.now()
    currentTime = now.strftime("%Y-%m-%d %H:%M:%S")
    print(colored("Time : " + currentTime, 'red'))

    y = 1 # Use this variable as reference to get regValue of parameters

    # Print Voltage and current
    y = Parameters.index(LG6400.VLN_AVG_STR) # Voltage stsrt from 5th position 
    print(colored("\t\t"+Parameters[y]+"\t"+Parameters[y+1]+"\t\t"+Parameters[y+2]+"\t\t"+Parameters[y+3]+"\t\t"+"|"+
                Parameters[y+4]+"\t"+Parameters[y+5]+"\t\t"+Parameters[y+6]+"\t\t"+Parameters[y+7], 'yellow'))
    for x in range(NoOfDevices):
        print("Device "+str(x+1)+"\t"+str(allRegValues[x][y])+"\t\t"+str(allRegValues[x][y+1])+
                "\t\t"+str(allRegValues[x][y+2])+"\t\t"+str(allRegValues[x][y+3])+
                "\t\t"+"|"+str(allRegValues[x][y+4])+"\t\t"+str(allRegValues[x][y+5])+
                "\t\t"+str(allRegValues[x][y+6])+"\t\t"+str(allRegValues[x][y+7]))
       
    # Print Frequency
    y = Parameters.index(LG6400.FREQUENCY_STR) # Frequency stsrt from 5th position
    print() # empty line
    print(colored("\t\t"+Parameters[Parameters.index(LG6400.FREQUENCY_STR)]+
                "\t"+"|"+Parameters[Parameters.index(LG6400.NO_OF_INTR_STR)]+
                "\t"+"|"+Parameters[Parameters.index(LG6400.WH_RCVD_STR)]+
                "\t"+"|"+Parameters[Parameters.index(LG6400.LOAD_HRS_DL_STR)]+
                "\t"+"|"+Parameters[Parameters.index(LG6400.ON_HRS_STR)], 'yellow'))
    for x in range(NoOfDevices):
        print("Device "+str(x+1)+"\t"+str(allRegValues[x][Parameters.index(LG6400.FREQUENCY_STR)])+
                    "\t\t"+"|"+str(allRegValues[x][Parameters.index(LG6400.NO_OF_INTR_STR)])+
                    "\t\t\t"+"|"+str(allRegValues[x][Parameters.index(LG6400.WH_RCVD_STR)])+
                    "\t\t"+"|"+str(allRegValues[x][Parameters.index(LG6400.LOAD_HRS_DL_STR)])+
                    "\t\t\t"+"|"+str(allRegValues[x][Parameters.index(LG6400.ON_HRS_STR)]))
    
    # First Print Watts and PH
    y = Parameters.index(LG6400.WATTS_TOTAL_STR) # Watts start from 1st position in Parameter and regValue array
    print() # empty line
    print(colored("\t\t"+Parameters[y]+"\t"+Parameters[y+1]+"\t"+Parameters[y+2]+"\t"+Parameters[y+3]+"\t"+"|"+
                Parameters[y+4]+"\t\t"+Parameters[y+5]+"\t\t"+Parameters[y+6]+"\t\t"+Parameters[y+7], 'yellow'))
    for x in range(NoOfDevices):
        print("Device "+str(x+1)+"\t"+str(allRegValues[x][y])+"\t\t"+str(allRegValues[x][y+1])+
                "\t\t"+str(allRegValues[x][y+2])+"\t\t"+str(allRegValues[x][y+3])+
                "\t\t"+"|"+str(allRegValues[x][y+4])+"\t\t"+str(allRegValues[x][y+5])+
                "\t\t"+str(allRegValues[x][y+6])+"\t\t"+str(allRegValues[x][y+7]))
    
    # Print Voltage Harmonics
    y = Parameters.index(LG6400.V_R_HARMO_STR) # Frequency stsrt from 5th position
    print() # empty line
    print(colored("\t\t"+Parameters[y]+"\t"+Parameters[y+1]+"\t"+Parameters[y+2]+
                "\t"+Parameters[y+3]+"\t"+Parameters[y+4]+"\t"+Parameters[y+5], 'yellow'))
    for x in range(NoOfDevices):
        print("Device "+str(x+1)+"\t"+str(allRegValues[x][y])+"\t\t"+str(allRegValues[x][y+1])+"\t\t"+str(allRegValues[x][y+2])+
                    "\t\t"+str(allRegValues[x][y+3])+"\t\t"+str(allRegValues[x][y+4])+"\t\t"+str(allRegValues[x][y+5]))


##########################################################################
# Function to print register values on console Method 2
##########################################################################
def printRegValues_2(TotalReadings, stdscr):
    # First clear the screen
    # os.system('cls' if os.name == 'nt' else 'clear')
    stdscr.clear()  # Clear the screen
    row = 0

    stdscr.addstr(row, 20, "Total published message : " + str(published_msg))

    row = row+1
    stdscr.addstr(row, 20, "Total reading cycle : " + str(TotalReadings))

    now = datetime.datetime.now()
    currentTime = now.strftime("%Y-%m-%d %H:%M:%S")
    row = row+1
    stdscr.addstr(row, 20, "Time : " + currentTime)

    y = 1 # Use this variable as reference to get regValue of parameters

    # Print Voltage and current
    y = Parameters.index(LG6400.VLN_AVG_STR) # Voltage stsrt from 5th position 
    row = row+1
    stdscr.addstr(row, 18, str(Parameters[y]))
    stdscr.addstr(row, 34, str(Parameters[y+1]))
    stdscr.addstr(row, 50, str(Parameters[y+2]))
    stdscr.addstr(row, 66, str(Parameters[y+3]))
    stdscr.addstr(row, 82, str(Parameters[y+4]))
    stdscr.addstr(row, 86, str(Parameters[y+5]))
    stdscr.addstr(row, 90, str(Parameters[y+6]))
    stdscr.addstr(row, 100, str(Parameters[y+7]))
    for x in range(NoOfDevices):
        row = row+1
        stdscr.addstr(row, 0, deviceNames[x])
        stdscr.addstr(row, 18, str(allRegValues[x][y]))
        stdscr.addstr(row, 34, str(allRegValues[x][y+1]))
        stdscr.addstr(row, 50, str(allRegValues[x][y+2]))
        stdscr.addstr(row, 66, str(allRegValues[x][y+3]))
        stdscr.addstr(row, 82, str(allRegValues[x][y+4]))
        stdscr.addstr(row, 86, str(allRegValues[x][y+5]))
        stdscr.addstr(row, 90, str(allRegValues[x][y+6]))
        stdscr.addstr(row, 100, str(allRegValues[x][y+7]))
       
    # Print Frequency
    y = Parameters.index(LG6400.FREQUENCY_STR) # Frequency stsrt from 5th position
    row = row+2
    stdscr.addstr(row, 18, str(Parameters[Parameters.index(LG6400.FREQUENCY_STR)]))
    stdscr.addstr(row, 34, str(Parameters[Parameters.index(LG6400.NO_OF_INTR_STR)]))
    stdscr.addstr(row, 58, str(Parameters[Parameters.index(LG6400.WH_RCVD_STR)]))
    stdscr.addstr(row, 88, str(Parameters[Parameters.index(LG6400.LOAD_HRS_DL_STR)]))
    stdscr.addstr(row, 122, str(Parameters[Parameters.index(LG6400.ON_HRS_STR)]))
    for x in range(NoOfDevices):
        row = row+1
        stdscr.addstr(row, 0, deviceNames[x])
        stdscr.addstr(row, 18, str(allRegValues[x][Parameters.index(LG6400.FREQUENCY_STR)]))
        stdscr.addstr(row, 34, str(allRegValues[x][Parameters.index(LG6400.NO_OF_INTR_STR)]))
        stdscr.addstr(row, 58, str(allRegValues[x][Parameters.index(LG6400.WH_RCVD_STR)]))
        stdscr.addstr(row, 88, str(allRegValues[x][Parameters.index(LG6400.LOAD_HRS_DL_STR)]))
        stdscr.addstr(row, 122, str(allRegValues[x][Parameters.index(LG6400.ON_HRS_STR)]))
    
    # First Print Watts and PH
    y = Parameters.index(LG6400.WATTS_TOTAL_STR) # Watts start from 1st position in Parameter and regValue array
    row = row+2
    stdscr.addstr(row, 18, str(Parameters[y]))
    stdscr.addstr(row, 34, str(Parameters[y+1]))
    stdscr.addstr(row, 50, str(Parameters[y+2]))
    stdscr.addstr(row, 66, str(Parameters[y+3]))
    stdscr.addstr(row, 82, str(Parameters[y+4]))
    stdscr.addstr(row, 98, str(Parameters[y+5]))
    stdscr.addstr(row, 114, str(Parameters[y+6]))
    stdscr.addstr(row, 130, str(Parameters[y+7]))
    for x in range(NoOfDevices):
        row = row+1
        stdscr.addstr(row, 0, deviceNames[x])
        stdscr.addstr(row, 18, str(allRegValues[x][y]))
        stdscr.addstr(row, 34, str(allRegValues[x][y+1]))
        stdscr.addstr(row, 50, str(allRegValues[x][y+2]))
        stdscr.addstr(row, 66, str(allRegValues[x][y+3]))
        stdscr.addstr(row, 82, str(allRegValues[x][y+4]))
        stdscr.addstr(row, 98, str(allRegValues[x][y+5]))
        stdscr.addstr(row, 114, str(allRegValues[x][y+6]))
        stdscr.addstr(row, 130, str(allRegValues[x][y+7]))
    
    # Print Voltage Harmonics
    y = Parameters.index(LG6400.V_R_HARMO_STR) # Frequency stsrt from 5th position
    row = row+2
    stdscr.addstr(row, 18, str(Parameters[y]))
    stdscr.addstr(row, 34, str(Parameters[y+1]))
    stdscr.addstr(row, 50, str(Parameters[y+2]))
    stdscr.addstr(row, 66, str(Parameters[y+3]))
    stdscr.addstr(row, 82, str(Parameters[y+4]))
    stdscr.addstr(row, 98, str(Parameters[y+5]))
    for x in range(NoOfDevices):
        row = row+1
        stdscr.addstr(row, 0, deviceNames[x])
        stdscr.addstr(row, 18, str(allRegValues[x][y]))
        stdscr.addstr(row, 34, str(allRegValues[x][y+1]))
        stdscr.addstr(row, 50, str(allRegValues[x][y+2]))
        stdscr.addstr(row, 66, str(allRegValues[x][y+3]))
        stdscr.addstr(row, 82, str(allRegValues[x][y+4]))
        stdscr.addstr(row, 98, str(allRegValues[x][y+5]))
    
    stdscr.refresh()  # Refresh the screen to apply changes

##########################################################################
# Function to convert 2 int variable into a long inverse
##########################################################################
def pack(tup):
    return (tup[0]<<16)|tup[1]

##########################################################################
# Function to convert seconds into hh:mm:ss format
##########################################################################
def format_seconds_to_hhmmss(seconds):
    hours = seconds // (60*60)
    seconds %= (60*60)
    minutes = seconds // 60
    seconds %= 60
    return "%02i:%02i:%02i" % (hours, minutes, seconds)


###########################################################################################
###########################################################################################
###########################################################################################
def ReadMeterDataDefault(client, Address, deviceID):
    # Return 0 to all the values.
    returnVal = [0] * len(Parameters)
    return returnVal

def SimulateMeterData():
    now = datetime.datetime.now()
    regValue = [now.strftime("%Y-%m-%d %H:%M:%S")] 
    # Gen radnom values for each parameter, except time.
    for _ in range(1, len(Parameters)):
        regValue.append(round(random.uniform(0, 500), 2)) # Example Range
    return regValue

##########################################################################
# Function to read meter data and print, store it in a file
##########################################################################
def ReadAndProcessMeterData(client, deviceID, csvFilePointer):
    global errorFile
    if(deviceModels[deviceID-1]==DEV_ELM_LG6400):
        regValue = LG6400.ReadMeterData(client, deviceID, Parameters, errorFile)
    elif(deviceModels[deviceID-1]==DEV_ELM_EN8400):
        regValue = LG6400.ReadMeterData(client, deviceID, Parameters, errorFile)
    elif(deviceModels[deviceID-1]==DEV_ELM_EN8100):
        regValue = LG6400.ReadMeterData(client, deviceID, Parameters, errorFile)
    elif(deviceModels[deviceID-1]==DEV_ELM_LG5220):
        regValue = LG5220.ReadMeterData(client, deviceID, Parameters, errorFile)
    elif(deviceModels[deviceID-1]==DEV_ELM_LG5310):
        regValue = LG5310.ReadMeterData(client, deviceID, Parameters, errorFile)
    elif(deviceModels[deviceID-1]==DEV_ELM_EN8410):
        regValue = EN8410.ReadMeterData(client, deviceID, Parameters, errorFile)
    elif(deviceModels[deviceID-1]==DEV_ELM_ELR300):
        regValue = ELR300.ReadMeterData(client, deviceID, Parameters, errorFile)
    else:
        regValue = ReadMeterDataDefault(client, LG6400.START_ADD, deviceID)

    now = datetime.datetime.now()
    # currentTime = now.strftime("%Y-%m-%d %H:%M:%S")
    regValue[0] = now.strftime("%Y-%m-%d %H:%M:%S")
    # print(regValue[0])

    csvFilePointer.writerow(regValue)

    # Publish to the mqtt
    global published_msg

    # Simulated Data for testing
    regValue = SimulateMeterData()
    csvFilePointer.writerow(regValue)
    
    published_msg = mqtt.publish_message(Parameters, regValue, deviceNames[deviceID-1])
    allRegValues[deviceID-1] = regValue.copy()

##########################################################################
# Thread function to run a code at every x seconds.
# Note: Using time.sleep(x) is not useful as it will add x seconds and 
#       time taken to execute the code as well
##########################################################################
# WIP : Need to findout menthod and write a threading function for this

##########################################################################
# Main function
##########################################################################
def mainFunction(stdscr):
    TotalReadings = 0
    csvFileName = []
    csvFilePointer = []
    connected = 1
    global errorFile

    errorFile = open(ERROR_FILE_NAME, "a")

    # Simulation mode
    client = None
    #client = ModbusClient(port = PORT, stopbits = 1, bytesize = 8, parity = 'E', baudrate = 9600, timeout = 0.5)


    """modify port with com port of the USB device (eg COM3 in windows or /dev/ttyUSB0 in linux)
    try:
        client.connect()
    except:
        print ("Unable to connect the meter")
        errorFile.write("Unable to connect the meter\n")
        connected = 0
    """
    mqtt.mqtt_main() # Initialize mqtt and connect to the broker

    # Open file and initialize it 
    for x in range(NoOfDevices):
        csvFileName.append("Device_" + str(x+1) + ".csv")
        csvFilePointer.append(open(csvFileName[x], "a", newline=''))
        csvFilePointer[x] = csv.writer(csvFilePointer[x])
        csvFilePointer[x].writerow(Parameters)
    
    for x in range(NoOfDevices):
        regValue = SimulateMeterData()  # Generate simulated data for initialization
        allRegValues.append(regValue.copy())

    while connected:
        # print ("Total reading cycle" , TotalReadings)
        TotalReadings = TotalReadings+1

        for x in range(NoOfDevices):
            UNIT = x+1
            # Use simulated data
            regValue = SimulateMeterData()
            csvFilePointer[x].writerow(regValue)
            published_msg = mqtt.publish_message(Parameters, regValue, deviceNames[x])
            allRegValues[x] = regValue.copy()
            #ReadAndProcessMeterData(client, UNIT, csvFilePointer[x])

            time.sleep(intervalBwMeter)
        printRegValues_2(TotalReadings, stdscr)
        time.sleep(intervalBwReadings)
        #     # print ("\n")

        #printRegValues_1(TotalReadings)
        printRegValues_2(TotalReadings, stdscr)
        time.sleep(readingInterval)
        # print ("\n")
        # print ("----****----****----")
    errorFile.close()
    #if connected:
    #    client.close()

#########################################################################################
#########################################################################################
#########################################################################################
# if __name__ == "__main__":
#     mainFunction()

try:
    curses.wrapper(mainFunction)
except KeyboardInterrupt:
    print("exiting the thread")
    mqtt.mqtt_close()