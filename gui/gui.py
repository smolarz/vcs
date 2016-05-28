###################################
###### Vacuum Cold Spray GUI ######
###################################
###### Author: Stacey Smolash #####
######         Marie Hebert   #####
######         Melyssa Furt   #####
###### Date  : March 2016     #####
###################################

# comment

# import Python modules
import csv
from decimal import Decimal
import multiprocessing
import numpy as np
#import RPi.GPIO as GPIO
from scikits.audiolab import *
import scipy
import serial
import threading
from time import sleep
import time
from Tkinter import *

# RPi setup
#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(31, GPIO.OUT)
#GPIO.output(31, False)

# serial ports
MFC_PORT = '/dev/ttyACM1'
MOTOR_PORT = '/dev/ttyACM0'
#PRESSURE_PORT = '/dev/cu.usbmodem1421'
BAUD_RATE = 9600

# open serial ports
MFC_SERIAL = serial.Serial(MFC_PORT, BAUD_RATE)
MOTOR_SERIAL = serial.Serial(MOTOR_PORT, BAUD_RATE, timeout=None)
#PRESSURE_SERIAL = serial.Serial(PRESSURE_PORT, BAUD_RATE)
sleep(5)

motorMode = 2

# processes
agProcess = None
motorProcess = None
mfcProcess = None

# threads
#isRecording = False
#pressureThread = None

###############################
########## FUNCTIONS ##########
###############################

##### START SEQUENCE #####

def startSequence():
    
    buttonState = startButtonText.get()
    
    '''global MFC_SERIAL
    MFC_SERIAL.flushInput()
    MFC_SERIAL.flushOutput()'''

    global agProcess
    global motorProcess
    global mfcProcess

    #global isRecording
    #global pressureThread
    
    if buttonState == "Start":

        startButtonText.set("Stop")
        statusVal.set("RUNNING")
        statusCanvas.itemconfig(h_status, fill="red")
       
        # disable substrate inputs
        incrementEntry.config(state="disabled")
        powderMaterialMenu.config(state="disabled")
        powderSizeEntry.config(state="disabled")
        gasMenu.config(state="disabled")
        substrateEntry.config(state="disabled") 

        # disable motor inputs 
        lengthEntry.config(state="disabled")
        widthEntry.config(state="disabled")
        sodEntry.config(state="disabled")
        layersEntry.config(state="disabled")
        yIncrementEntry.config(state="disabled")
        sprayDelayEntry.config(state="disabled")
        xSpeedEntry.config(state="disabled")
        xSpeedButton.config(state="disabled")   
        xSpeedScale.config(state="disabled")

        # disable mfc
        for child in mfc_entry_setFrame.winfo_children():
            child.config(state="disabled")

        mfcScale.config(state="disabled")

        # disable ag
        for child in ag_entry_setFrame.winfo_children():
            child.config(state="disabled")

        agScale.config(state="disabled")

        # disable manual stop button
        manStopButton.config(state="disabled")

        # disable auto mode
        autoModeScale.config(state="disabled")
        zeroButton.config(state="disabled")
        zeroCNozzleButton.config(state="disabled")
        zeroFNozzleButton.config(state="disabled")
        remSubButton.config(state="disabled")
        remNozzleButton.config(state="disabled")
        homeButton.config(state="disabled")
        originSprayButton.config(state="disabled")
        
        # start pressure sensors
        #isRecording = True
        #pressureThread = threading.Thread(target=recordPressure)
        #pressureThread.start()

        # initialize motors with substrate inputs
        sleep(0.1)
        initializeMotorValues()
        print "Motor values initialized..."

        # move substrate to origin
        sleep(0.1)
        originSprayFunction()
        print "Substrate at origin..."

        # move nozzle to SoD
        sleep(0.1)
        zManSOFunction()
        print "Nozzle at SoD..."

        # start aerosol generator
        sleep(0.1)
        agProcess = multiprocessing.Process(target=playAudio)
        agProcess.start()
        agProcess.join(0.1)
        print "AG running..."

        # start mass flow controller
        sleep(0.1)
        mfcProcess = multiprocessing.Process(target=startFlow)
        mfcProcess.start()
        mfcProcess.join(0.1)
        print "MFC running..."

        # start motors
        sleep(0.1)
        motorProcess = multiprocessing.Process(target=moveSubstrate)
        motorProcess.start()
        motorProcess.join(0.1)
        print "Commence spray sequence..."
    
    elif buttonState == "Stop":
        
        # only press stop button if you realize you've made a mistake
        # otherwise wait for the spray process to finish on its own

        startButtonText.set("Start")
        statusVal.set("INTERRUPT")
        statusCanvas.itemconfig(h_status, fill="yellow")

        # enable substrate inputs
        incrementEntry.config(state="normal")
        powderMaterialMenu.config(state="normal")
        powderSizeEntry.config(state="normal")
        gasMenu.config(state="normal")
        substrateEntry.config(state="normal") 

        # enable motor inputs 
        lengthEntry.config(state="normal")
        widthEntry.config(state="normal")
        sodEntry.config(state="normal")
        layersEntry.config(state="normal")
        yIncrementEntry.config(state="normal")
        sprayDelayEntry.config(state="normal")
        xSpeedEntry.config(state="normal")
        xSpeedButton.config(state="normal")   
        xSpeedScale.config(state="normal")

        # enable mfc
        for child in mfc_entry_setFrame.winfo_children():
            child.config(state="normal")

        mfcScale.config(state="normal")

        # enable ag
        for child in ag_entry_setFrame.winfo_children():
            child.config(state="normal")

        agScale.config(state="normal")

        # enable manual stop button
        manStopButton.config(state="normal")

        # enable auto mode
        autoModeScale.config(state="normal")
        zeroButton.config(state="normal")
        zeroCNozzleButton.config(state="normal")
        zeroFNozzleButton.config(state="normal")
        remSubButton.config(state="normal")
        remNozzleButton.config(state="normal")
        homeButton.config(state="normal")
        originSprayButton.config(state="normal")

        # stop aerosol generator
        agProcess.terminate()
        print "AG stopped."

        # stop motors
        sleep(0.1)
        motorProcess.terminate()
        print "Motors stopped."

        # stop pressure sensors
        #sleep(0.1)
        #isRecording = False
        #pressureThread.join()

##### THREADS/PROCESSES #####

def moveSubstrate():
    
    #global agProcess

    #global isRecording

    # start auto spray sequence
    serialOneStep(41, 40)

    # when auto spray sequence is complete:
    stopAG() # stop ag
    enableWidgets() # enable widgets

    #print "SPRAY SEQUENCE COMPLETE!"

    # stop aerosol generator
    #agProcess.terminate()
    #print "AG stopped."

    # stop pressure sensors
    '''sleep(0.1)
    isRecording = False
    pressureThread.join()'''
    
    '''statusVal.set("COMPLETE")
    statusCanvas.itemconfig(h_status, fill="green")'''

    # enable substrate inputs
    '''incrementEntry.config(state="normal")
    powderMaterialMenu.config(state="normal")
    powderSizeEntry.config(state="normal")
    gasMenu.config(state="normal")
    substrateEntry.config(state="normal") 

    # enable motor inputs 
    lengthEntry.config(state="normal")
    widthEntry.config(state="normal")
    sodEntry.config(state="normal")
    layersEntry.config(state="normal")
    yIncrementEntry.config(state="normal")
    sprayDelayEntry.config(state="normal")
    xSpeedEntry.config(state="normal")
    xSpeedButton.config(state="normal")   
    xSpeedScale.config(state="normal")

    # enable mfc
    for child in mfc_entry_setFrame.winfo_children():
        child.config(state="normal")

    mfcScale.config(state="normal")

    # enable ag
    for child in ag_entry_setFrame.winfo_children():
        child.config(state="normal")

    agScale.config(state="normal")

    # enable manual stop button
    manStopButton.config(state="normal")

    # enable auto mode
    autoModeScale.config(state="normal")
    zeroButton.config(state="normal")
    zeroCNozzleButton.config(state="normal")
    zeroFNozzleButton.config(state="normal")
    remSubButton.config(state="normal")
    remNozzleButton.config(state="normal")
    homeButton.config(state="normal")
    originSprayButton.config(state="normal")'''

def playAudio():
    
    f = agEntryFreq.get()                                       # frequency (Hz)
    fs = 48000                                                  # sampling rate (Hz)
    T = 100                                                     # period (s)
    sine_wave = scipy.sin((2*scipy.pi*f/fs)*scipy.arange(fs*T)) # sine wave
   
    while True:
        play(sine_wave, fs)

def startFlow():
    
    global MFC_SERIAL
    MFC_SERIAL.flushInput()
    MFC_SERIAL.flushOutput()
    MFC_SERIAL.write(str(mfcEntryRate.get()))

    while MFC_SERIAL.inWaiting() == 0:
        sleep(0.1)

    if MFC_SERIAL.inWaiting() > 0:
        init = int(MFC_SERIAL.readline())
        if init == 300:
            while True:
                MFC_SERIAL.write(str(200))
                while MFC_SERIAL.inWaiting() == 0:
                    sleep(0.1)
                if MFC_SERIAL.inWaiting() > 0:
                    mfcFeedback = float(MFC_SERIAL.readline())
                    print mfcFeedback # success
                    #if mfcFeedback >= (mfcEntryRate.get() - 0.5) and mfcFeedback <= (mfcEntryRate.get() + 0.5):
                        #print "ok"
                        #mfcCanvas.itemconfig(h_mfc, fill="green")
                    #else:
                        #print "bad"
                        #mfcCanvas.itemconfig(h_mfc, fill="red")

def recordPressure():
    pass

##### MOTORS #####

def initializeMotorValues():
    
    global MOTOR_SERIAL
    MOTOR_SERIAL.write(str(91))
    
    while True:
        while MOTOR_SERIAL.inWaiting() == 0:
            sleep(0.01)
        
        if MOTOR_SERIAL.inWaiting() > 0:
            temp = int(MOTOR_SERIAL.readline())
            #print(temp)

        if temp == 1:
            MOTOR_SERIAL.write(str(widthVal.get()))
            #print(str(widthVal.get()))

        elif temp == 2:
            MOTOR_SERIAL.write(str(lengthVal.get()))
            #print(str(lengthVal.get()))

        elif temp == 3:
            MOTOR_SERIAL.write(str(yIncrementVal.get()))
            #print(str(yIncrementVal.get()))

        elif temp == 4:
            MOTOR_SERIAL.write(str(layersVal.get()))
            #print(str(layersVal.get()))

        elif temp == 5:
            MOTOR_SERIAL.write(str(xSpeedEntryVal.get()))
            #print(str(xSpeedEntryVal.get()))

        elif temp == 6:
            MOTOR_SERIAL.write(str(sodVal.get()))
            #print(str(sodVal.get()))
            
        elif temp == 7: 
            MOTOR_SERIAL.write(str(sprayDelayVal.get()))
            
        elif temp == 8: 
            break

def serialOneStep(step_num, stop_num):
    # For serial communication with the Arduino when only one step
    # number is involved. ie sends one number and then wait for another
    # one to signifiy that it is done

    global MOTOR_SERIAL
    MOTOR_SERIAL.write(str(step_num))

    statusVal.set("RUNNING")
    statusCanvas.itemconfig(h_status, fill="red")

    while MOTOR_SERIAL.inWaiting() == 0:
        sleep(0.01)
    
    if MOTOR_SERIAL.inWaiting() > 0:
        temp = int(MOTOR_SERIAL.readline())
        #print(temp)

    if temp == stop_num:
        statusVal.set("COMPLETE")
        statusCanvas.itemconfig(h_status, fill="green")
        print "DONE"

### x-speed ###

def xScaleSet():
    if xSpeedEntryVal.get() < 0:
        xSpeedEntryVal.set(0)
        xSpeedScaleVal.set(0)
    elif xSpeedEntryVal.get() > 2:
        xSpeedEntryVal.set(2)
        xSpeedScaleVal.set(2)
    else:
        xSpeedScaleVal.set(xSpeedEntryVal.get())

def xEntrySet(val):
    xSpeedEntryVal.set(val)

### manual x ###

def xManScaleSet():
    if xManEntryVal.get() < 0:
        xManEntryVal.set(0)
        xManScaleVal.set(0)
    elif xManEntryVal.get() > 200:
        xManEntryVal.set(200)
        xManScaleVal.set(200)
    else:
        xManScaleVal.set(xManEntryVal.get())

def xManEntrySet(val):
    xManEntryVal.set(val)

def xManHomeButton(): 
    serialOneStep(14, 10)

def xManBwButton(): 
    
    global MOTOR_SERIAL
    MOTOR_SERIAL.write(str(16))

    while MOTOR_SERIAL.inWaiting() == 0:
        sleep(0.01)
    
    if MOTOR_SERIAL.inWaiting() > 0:
        temp = int(MOTOR_SERIAL.read())
        #print(temp)

    if temp == 1:
        MOTOR_SERIAL.write(str(xManEntryVal.get()))
        #print(str(xManEntryVal.get()))

    while MOTOR_SERIAL.inWaiting() == 0:
        sleep(0.01)

    if MOTOR_SERIAL.inWaiting() > 0:
        temp = int(MOTOR_SERIAL.readline())
        #print(temp)

    if temp == 10: 
        print("DONE")

def xManFwButton(): 
    
    global MOTOR_SERIAL
    MOTOR_SERIAL.write(str(15))

    while MOTOR_SERIAL.inWaiting() == 0:
        sleep(0.01)
    
    if MOTOR_SERIAL.inWaiting() > 0:
        temp = int(MOTOR_SERIAL.read())
        #print(temp)

    if temp == 1:
        MOTOR_SERIAL.write(str(xManEntryVal.get()))
        #print(str(xManEntryVal.get()))

    while MOTOR_SERIAL.inWaiting() == 0:
        sleep(0.01)

    if MOTOR_SERIAL.inWaiting() > 0:
        temp = int(MOTOR_SERIAL.readline())
        #print(temp)

    if temp == 10: 
        print("DONE")

def xManFarButton(): 
    serialOneStep(17, 10)

### manual y ###

def yManScaleSet():
    if yManEntryVal.get() < 0:
        yManEntryVal.set(0)
        yManScaleVal.set(0)
    elif yManEntryVal.get() > 50:
        yManEntryVal.set(50)
        yManScaleVal.set(50)
    else:
        yManScaleVal.set(yManEntryVal.get())

def yManEntrySet(val):
    yManEntryVal.set(val)

def yManHomeButton(): 
    serialOneStep(24, 20)

def yManBwButton(): 
    
    global MOTOR_SERIAL
    MOTOR_SERIAL.write(str(26))

    while MOTOR_SERIAL.inWaiting() == 0:
        sleep(0.01)
    
    if MOTOR_SERIAL.inWaiting() > 0:
        temp = int(MOTOR_SERIAL.read())
        #print(temp)

    if temp == 1:
        MOTOR_SERIAL.write(str(yManEntryVal.get()))
        #print(str(yManEntryVal.get()))

    while MOTOR_SERIAL.inWaiting() == 0:
        sleep(0.01)

    if MOTOR_SERIAL.inWaiting() > 0:
        temp = int(MOTOR_SERIAL.readline())
        #print(temp)

    if temp == 20: 
        print("DONE")

def yManFwButton(): 
    
    global MOTOR_SERIAL
    MOTOR_SERIAL.write(str(25))

    while MOTOR_SERIAL.inWaiting() == 0:
        sleep(0.01)
    
    if MOTOR_SERIAL.inWaiting() > 0:
        temp = int(MOTOR_SERIAL.read())
        #print(temp)

    if temp == 1:
        MOTOR_SERIAL.write(str(yManEntryVal.get()))
        #print(str(yManEntryVal.get()))

    while MOTOR_SERIAL.inWaiting() == 0:
        sleep(0.01)

    if MOTOR_SERIAL.inWaiting() > 0:
        temp = int(MOTOR_SERIAL.readline())
        #print(temp)

    if temp == 20: 
        print("DONE")

def yManFarButton(): 
    serialOneStep(27, 20)

### manual z ###

def zManScaleSet():
    if zManEntryVal.get() < 0:
        zManEntryVal.set(0)
        zManScaleVal.set(0)
    elif zManEntryVal.get() > 50:
        zManEntryVal.set(50)
        zManScaleVal.set(50)
    else:
        zManScaleVal.set(zManEntryVal.get())

def zManEntrySet(val):
    zManEntryVal.set(val)

def zManHomeButton(): 
    serialOneStep(34, 30)

def zManBwButton(): 
    
    global MOTOR_SERIAL
    MOTOR_SERIAL.write(str(36))

    while MOTOR_SERIAL.inWaiting() == 0:
        sleep(0.01)
    
    if MOTOR_SERIAL.inWaiting() > 0:
        temp = int(MOTOR_SERIAL.read())
        #print(temp)

    if temp == 1:
        MOTOR_SERIAL.write(str(zManEntryVal.get()))
        #print(str(zManEntryVal.get()))

    while MOTOR_SERIAL.inWaiting() == 0:
        sleep(0.01)

    if MOTOR_SERIAL.inWaiting() > 0:
        temp = int(MOTOR_SERIAL.readline())
        #print(temp)

    if temp == 30: 
        print("DONE")

def zManFwButton(): 
    
    global MOTOR_SERIAL
    MOTOR_SERIAL.write(str(35))

    while MOTOR_SERIAL.inWaiting() == 0:
        sleep(0.01)
    
    if MOTOR_SERIAL.inWaiting() > 0:
        temp = int(MOTOR_SERIAL.read())
        #print(temp)

    if temp == 1:
        MOTOR_SERIAL.write(str(zManEntryVal.get()))
        #print(str(zManEntryVal.get()))

    while MOTOR_SERIAL.inWaiting() == 0:
        sleep(0.01)

    if MOTOR_SERIAL.inWaiting() > 0:
        temp = int(MOTOR_SERIAL.readline())
        #print(temp)

    if temp == 30: 
        print("DONE")

def zManFarButton(): 
    serialOneStep(37, 30)

### zero ###

def xZeroButton(): 
    serialOneStep(13, 10)

def yZeroButton(): 
    serialOneStep(23, 20)

def zZeroButton(): 
    serialOneStep(33, 30)

### manual other ###

def zManSOButton(): 
    zManSOFunction()

def zManSOFunction(): 
    serialOneStep(38, 30)

def resetOriginSprayButton(): 
    serialOneStep(57, 50)

def manStopButton(): 
    # Send through GPIO pin a signal to the Arduino
    # through GPIO pin 24 (physical pin 18) with the 
    # grounds connected for better reference.
    # It inputs in an analog in pin since the output
    # is 3.3 V
    global MOTOR_SERIAL
    
    GPIO.output(31, True)
    sleep(1)
    GPIO.output(31, False)

    while MOTOR_SERIAL.inWaiting() == 0:
        sleep(0.01)
    
    if MOTOR_SERIAL.inWaiting() > 0:
        temp = int(MOTOR_SERIAL.readline())
        print(temp)

    if temp == 101:
        statusVal.set("INTERRUPT")
        statusCanvas.itemconfig(h_status, fill="yellow")

### auto mode ###

def setMode(val):

    global motorMode

    # auto mode
    if autoModeScaleVal.get() == 0:
        
        motorMode = 2

        # enable start button
        startButton.config(state="normal")

        # enable substrate inputs
        incrementEntry.config(state="normal")
        powderMaterialMenu.config(state="normal")
        powderSizeEntry.config(state="normal")
        gasMenu.config(state="normal")
        substrateEntry.config(state="normal")

        # enable motor inputs 
        lengthEntry.config(state="normal")
        widthEntry.config(state="normal")
        sodEntry.config(state="normal")
        layersEntry.config(state="normal")
        yIncrementEntry.config(state="normal")
        sprayDelayEntry.config(state="normal")
        xSpeedEntry.config(state="normal")
        xSpeedButton.config(state="normal")   
        xSpeedScale.config(state="normal")   

        # disable manual mode
        for child in manualXFrame.winfo_children():
            child.config(state="disabled")

        for child in arrowXFrame.winfo_children():
            child.config(state="disabled")

        for child in manualYFrame.winfo_children():
            child.config(state="disabled")

        for child in arrowYFrame.winfo_children():
            child.config(state="disabled")

        for child in manualZFrame.winfo_children():
            child.config(state="disabled")

        for child in arrowZFrame.winfo_children():
            child.config(state="disabled")

        for child in manualZeroFrame.winfo_children():
            child.config(state="disabled")

        for child in manualOtherFrame.winfo_children():
            child.config(state="disabled")

        # enable mfc
        for child in mfc_entry_setFrame.winfo_children():
            child.config(state="normal")

        mfcScale.config(state="normal")

        # enable ag
        for child in ag_entry_setFrame.winfo_children():
            child.config(state="normal")

        agScale.config(state="normal")

    # manual mode
    elif autoModeScaleVal.get() == 1:
        
        motorMode = 1

        # disable start button
        startButton.config(state="disabled")

        # disable substrate inputs
        incrementEntry.config(state="disabled")
        powderMaterialMenu.config(state="disabled")
        powderSizeEntry.config(state="disabled")
        gasMenu.config(state="disabled")
        substrateEntry.config(state="disabled") 

        # disable motor inputs 
        lengthEntry.config(state="disabled")
        widthEntry.config(state="disabled")
        sodEntry.config(state="disabled")
        layersEntry.config(state="disabled")
        yIncrementEntry.config(state="disabled")
        sprayDelayEntry.config(state="disabled")
        xSpeedEntry.config(state="disabled")
        xSpeedButton.config(state="disabled")   
        xSpeedScale.config(state="disabled")

        # enable manual mode
        for child in manualXFrame.winfo_children():
            child.config(state="normal")

        for child in arrowXFrame.winfo_children():
            child.config(state="normal")

        for child in manualYFrame.winfo_children():
            child.config(state="normal")

        for child in arrowYFrame.winfo_children():
            child.config(state="normal")

        for child in manualZFrame.winfo_children():
            child.config(state="normal")

        for child in arrowZFrame.winfo_children():
            child.config(state="normal")

        for child in manualZeroFrame.winfo_children():
            child.config(state="normal")

        for child in manualOtherFrame.winfo_children():
            child.config(state="normal")

        # disable mfc
        for child in mfc_entry_setFrame.winfo_children():
            child.config(state="disabled")

        mfcScale.config(state="disabled")

        # disable ag
        for child in ag_entry_setFrame.winfo_children():
            child.config(state="disabled")

        agScale.config(state="disabled")

def zeroButton(): 
    serialOneStep(2, 50)

def zeroCNozzleButton(): 
    serialOneStep(3, 10)

def zeroFNozzleButton(): 
    serialOneStep(58, 10)

def remSubButton(): 
    serialOneStep(6, 10)

def remNozzleButton(): 
    serialOneStep(7, 10)

def homeButton(): 
    serialOneStep(5, 10)

def originSprayButton(): 
    originSprayFunction()

def originSprayFunction(): 
    serialOneStep(8, 10)

##### MASS FLOW CONTROLLER #####

def mfcEntrySet(val):
    mfcEntryRate.set(val)

def mfcScaleSet():
    if mfcEntryRate.get() < 0:
        mfcEntryRate.set(0)
        mfcScaleRate.set(0)
    elif mfcEntryRate.get() > 15:
        mfcEntryRate.set(15)
        mfcScaleRate.set(15)
    else:
        mfcScaleRate.set(mfcEntryRate.get())

def stopMFC():

    global mfcProcess
    global MFC_SERIAL

    mfcProcess.terminate()
    
    clear_buffer = MFC_SERIAL.readline()
    print "Clearing buffer: "
    print clear_buffer
    
    MFC_SERIAL.write(str(100))

    while MFC_SERIAL.inWaiting() == 0:
        sleep(0.1)
       
    if MFC_SERIAL.inWaiting() > 0:
        mfcFeedback = float(MFC_SERIAL.readline())
        print mfcFeedback
        mfcFeedbackVal.set(mfcFeedback)
        if mfcFeedback >= 0 and mfcFeedback <= 0.5:
            print "ok terminate"
            #mfcCanvas.itemconfig(h_mfc, fill="green")
        else:
            print "bad terminate"
            #mfcCanvas.itemconfig(h_mfc, fill="red")


##### AEROSOL GENERATOR #####

def agEntrySet(val):
    agEntryFreq.set(val)

def agScaleSet():
    if agEntryFreq.get() < 30:
        agEntryFreq.set(30)
        agScaleFreq.set(30)
    elif agEntryFreq.get() > 3000:
        agEntryFreq.set(3000)
        agScaleFreq.set(3000)
    else:
        agScaleFreq.set(agEntryFreq.get())

def stopAG():
    global agProcess
    agProcess.terminate()
    print "AG stopped."    

##### PRESSURE SENSORS #####

# convert psig to torr
def convert(a):
    p = (a + 14.7)
    t = (p * 51.7149)
    return t

##### ENABLE WIDGETS #####

def enableWidgets():
    print "SPRAY SEQUENCE COMPLETE."

    # enable substrate inputs
    incrementEntry.config(state="normal")
    powderMaterialMenu.config(state="normal")
    powderSizeEntry.config(state="normal")
    gasMenu.config(state="normal")
    substrateEntry.config(state="normal") 

    # enable motor inputs 
    lengthEntry.config(state="normal")
    widthEntry.config(state="normal")
    sodEntry.config(state="normal")
    layersEntry.config(state="normal")
    yIncrementEntry.config(state="normal")
    sprayDelayEntry.config(state="normal")
    xSpeedEntry.config(state="normal")
    xSpeedButton.config(state="normal")   
    xSpeedScale.config(state="normal")

    # enable mfc
    for child in mfc_entry_setFrame.winfo_children():
        child.config(state="normal")

    mfcScale.config(state="normal")

    # enable ag
    for child in ag_entry_setFrame.winfo_children():
        child.config(state="normal")

    agScale.config(state="normal")

    # enable manual stop button
    manStopButton.config(state="normal")

    # enable auto mode
    autoModeScale.config(state="normal")
    zeroButton.config(state="normal")
    zeroCNozzleButton.config(state="normal")
    zeroFNozzleButton.config(state="normal")
    remSubButton.config(state="normal")
    remNozzleButton.config(state="normal")
    homeButton.config(state="normal")
    originSprayButton.config(state="normal")

#########################
########## GUI ##########
#########################

# create parent GUI window
root = Tk()
root.title("Vacuum Cold Spray GUI")

# fix size of parent window
root.minsize(1400, 800)
root.maxsize(1400, 800)

###################################
############## HEADER #############
###################################

headerFrame = Frame(root, relief=GROOVE, borderwidth=2, height=150)
headerFrame.pack(side=TOP, fill=X, padx=10, pady=10, ipadx=10, ipady=10)
headerFrame.pack_propagate(0)

### logos ###

logoFrame = Frame(headerFrame)
logoFrame.pack(side=LEFT, expand=1)

concordiaImage = PhotoImage(file="concordia_logo.gif")
concordiaLabel = Label(logoFrame, image=concordiaImage, justify=LEFT)
concordiaLabel.pack()

spraylabImage = PhotoImage(file="spraylab_logo.gif")
spraylabLabel = Label(logoFrame, image=spraylabImage, justify=LEFT)
spraylabLabel.pack(pady=(10,0))

### aerosol generator status ###

agPressureFrame = Frame(headerFrame)
agPressureFrame.pack(side=LEFT, expand=1)

agPressureLabel = Label(agPressureFrame, text="Aerosol Generator (torr)")
agPressureLabel.pack(pady=10)

agPressureVal = DoubleVar()
agPressureVal.set(0)
agPressureDisplay = Label(agPressureFrame, textvariable=agPressureVal, relief=SUNKEN, borderwidth=4, justify=CENTER, width=12, height=2, font="-size 18")
agPressureDisplay.pack()

agCanvas = Canvas(agPressureFrame, width=90, height=25, relief=RAISED, borderwidth=4)
h_ag = agCanvas.create_rectangle(0, 0, 100, 35, fill="red")
agCanvas.pack(pady=20)

### vacuum chamber status ###

vcPressureFrame = Frame(headerFrame)
vcPressureFrame.pack(side=LEFT, expand=1)

vcPressureLabel = Label(vcPressureFrame, text="Vacuum Chamber (torr)")
vcPressureLabel.pack(pady=10)

vcPressureVal = DoubleVar()
vcPressureVal.set(0)
vcPressureDisplay = Label(vcPressureFrame, textvariable=vcPressureVal, relief=SUNKEN, borderwidth=4, justify=CENTER, width=12, height=2, font="-size 18")
vcPressureDisplay.pack()

vcCanvas = Canvas(vcPressureFrame, width=90, height=25, relief=RAISED, borderwidth=4)
h_vc = vcCanvas.create_rectangle(0, 0, 100, 35, fill="red")
vcCanvas.pack(pady=20)

### mass flow controller status ###

mfcFeedbackFrame = Frame(headerFrame)
mfcFeedbackFrame.pack(side=LEFT, expand=1)

mfcFeedbackLabel = Label(mfcFeedbackFrame, text="Flowrate (slpm)")
mfcFeedbackLabel.pack(pady=10)

mfcFeedbackVal = DoubleVar()
mfcFeedbackVal.set(0)
mfcFeedbackDisplay = Label(mfcFeedbackFrame, textvariable=mfcFeedbackVal, relief=SUNKEN, borderwidth=4, justify=CENTER, width=12, height=2, font="-size 18")
mfcFeedbackDisplay.pack()

mfcCanvas = Canvas(mfcFeedbackFrame, width=90, height=25, relief=RAISED, borderwidth=4)
h_mfc = mfcCanvas.create_rectangle(0, 0, 100, 35, fill="red")
mfcCanvas.pack(pady=20)

### door status ###

doorFrame = Frame(headerFrame)
doorFrame.pack(side=LEFT, expand=1)

doorLabel = Label(doorFrame, text="Door")
doorLabel.pack(pady=10)

doorVal = StringVar()
doorVal.set("-")
doorDisplay = Label(doorFrame, textvariable=doorVal, relief=SUNKEN, borderwidth=4, justify=CENTER, width=12, height=2, font="-size 18")
doorDisplay.pack()

doorCanvas = Canvas(doorFrame, width=90, height=25, relief=RAISED, borderwidth=4)
h_door = doorCanvas.create_rectangle(0, 0, 100, 35, fill="red")
doorCanvas.pack(pady=20)

### progress status ###

statusFrame = Frame(headerFrame)
statusFrame.pack(side=LEFT, expand=1)

statusLabel = Label(statusFrame, text="Status")
statusLabel.pack(pady=10)

statusVal = StringVar()
statusVal.set("-")
statusDisplay = Label(statusFrame, textvariable=statusVal, relief=SUNKEN, borderwidth=4, justify=CENTER, width=12, height=2, font="-size 18")
statusDisplay.pack()

statusCanvas = Canvas(statusFrame, width=90, height=25, relief=RAISED, borderwidth=4)
h_status = statusCanvas.create_rectangle(0, 0, 100, 35, fill="red")
statusCanvas.pack(pady=20)

###################################
############## INPUTS #############
###################################

mainFrame = Frame(root)
mainFrame.pack(side=TOP, expand=0, fill=X)

inputFrame = LabelFrame(mainFrame, text="INPUTS", relief=GROOVE, borderwidth=2, height=440, width=200)
inputFrame.pack(side=LEFT, expand=0, padx=10, pady=10, ipadx=10, ipady=10)
inputFrame.pack_propagate(0)

### log sampling time ###

incrementFrame = Frame(inputFrame)
incrementFrame.pack(expand=1)

incrementLabel = Label(incrementFrame, text="Pressure Sampling (s)")
incrementLabel.pack(pady=(0,5))

incrementVal = DoubleVar()
incrementVal.set(0)
incrementEntry = Entry(incrementFrame, textvariable=incrementVal, relief=SUNKEN, borderwidth=1, highlightthickness=0, justify=CENTER, width=15)
incrementEntry.pack()

### powder material ###

powderMaterialFrame = Frame(inputFrame)
powderMaterialFrame.pack(expand=1)

powderMaterialLabel = Label(powderMaterialFrame, text="Powder Material")
powderMaterialLabel.pack(pady=(0,5))

powderMaterial = StringVar()
powderMaterialMenu = OptionMenu(powderMaterialFrame, powderMaterial, "Alumina", "Titania", "Zirconia")
powderMaterialMenu.config(width=15, justify=CENTER)
powderMaterialMenu.pack()

### powder size ###

powderSizeFrame = Frame(inputFrame)
powderSizeFrame.pack(expand=1)

powderSizeLabel = Label(powderSizeFrame, text=u"Powder Size (\u03bcm)")
powderSizeLabel.pack(pady=(0,5))

powderSize = DoubleVar()
powderSize.set(0)
powderSizeEntry = Entry(powderSizeFrame, textvariable=powderSize, relief=SUNKEN, borderwidth=1, highlightthickness=0, justify=CENTER, width=15)
powderSizeEntry.pack()

### gas type ###

gasFrame = Frame(inputFrame)
gasFrame.pack(expand=1)

gasLabel = Label(gasFrame, text="Carrier Gas")
gasLabel.pack(pady=(0,5))

gasVal = StringVar()
gasMenu = OptionMenu(gasFrame, gasVal, "Air", "Helium", "Nitrogen")
gasMenu.config(width=15, justify=CENTER)
gasMenu.pack()

### substrate material ###

substrateFrame = Frame(inputFrame)
substrateFrame.pack(expand=1)

substrateLabel = Label(substrateFrame, text="Substrate Material")
substrateLabel.pack(pady=(0,5))

substrateVal = StringVar()
substrateVal.set(" ")
substrateEntry = Entry(substrateFrame, textvariable=substrateVal, relief=SUNKEN, borderwidth=1, highlightthickness=0, justify=CENTER, width=15)
substrateEntry.pack()

###################################
############## MOTORS #############
###################################

motorFrame = LabelFrame(mainFrame, text="SUBSTRATE", relief=GROOVE, borderwidth=2, height=440, width=820)
motorFrame.pack(side=LEFT, expand=0, padx=10, pady=10, ipadx=10, ipady=10)
motorFrame.pack_propagate(0)

##### INPUTS #####

motorInputFrame = LabelFrame(motorFrame, text="INPUTS", relief=SOLID, borderwidth=1, height=420, width=200)
motorInputFrame.pack(side=LEFT, expand=0, padx=(20,0), pady=(10,20), ipadx=10, ipady=10)
motorInputFrame.pack_propagate(0)

### substrate length ###

motorLengthFrame = Frame(motorInputFrame)
motorLengthFrame.pack(expand=1)

lengthLabel = Label(motorLengthFrame, text="Length (mm)")
lengthLabel.pack(pady=(0,5))

lengthVal = DoubleVar()
lengthVal.set(0)
lengthEntry = Entry(motorLengthFrame, textvariable=lengthVal, relief=SUNKEN, borderwidth=1, highlightthickness=0, justify=CENTER, width=15)
lengthEntry.pack()

### substrate width ###

motorWidthFrame = Frame(motorInputFrame)
motorWidthFrame.pack(expand=1)

widthLabel = Label(motorWidthFrame, text="Width (mm)")
widthLabel.pack(pady=(0,5))

widthVal = DoubleVar()
widthVal.set(0)
widthEntry = Entry(motorWidthFrame, textvariable=widthVal, relief=SUNKEN, borderwidth=1, highlightthickness=0, justify=CENTER, width=15)
widthEntry.pack()

### standoff distance ###

motorSODFrame = Frame(motorInputFrame)
motorSODFrame.pack(expand=1)

sodLabel = Label(motorSODFrame, text="SoD (mm)")
sodLabel.pack(pady=(0,5))

sodVal = DoubleVar()
sodVal.set(0)
sodEntry = Entry(motorSODFrame, textvariable=sodVal, relief=SUNKEN, borderwidth=1, highlightthickness=0, justify=CENTER, width=15)
sodEntry.pack()

### number of layers ###

motorLayersFrame = Frame(motorInputFrame)
motorLayersFrame.pack(expand=1)

layersLabel = Label(motorLayersFrame, text="No. Layers")
layersLabel.pack(pady=(0,5))

layersVal = DoubleVar()
layersVal.set(0)
layersEntry = Entry(motorLayersFrame, textvariable=layersVal, relief=SUNKEN, borderwidth=1, highlightthickness=0, justify=CENTER, width=15)
layersEntry.pack()

### y-increment ###

motorYIncrementFrame = Frame(motorInputFrame)
motorYIncrementFrame.pack(expand=1)

yIncrementLabel = Label(motorYIncrementFrame, text="Y-Increment (mm)")
yIncrementLabel.pack(pady=(0,5))

yIncrementVal = DoubleVar()
yIncrementVal.set(0)
yIncrementEntry = Entry(motorYIncrementFrame, textvariable=yIncrementVal, relief=SUNKEN, borderwidth=1, highlightthickness=0, justify=CENTER, width=15)
yIncrementEntry.pack()

### spray delay ###

motorDelayFrame = Frame(motorInputFrame)
motorDelayFrame.pack(expand=1)

sprayDelayLabel = Label(motorDelayFrame, text="Spray Delay (s)")
sprayDelayLabel.pack(pady=(0,5))

sprayDelayVal = DoubleVar()
sprayDelayVal.set(0)
sprayDelayEntry = Entry(motorDelayFrame, textvariable=sprayDelayVal, relief=SUNKEN, borderwidth=1, highlightthickness=0, justify=CENTER, width=15)
sprayDelayEntry.pack()

### x-speed ###

motorXSpeedFrame = Frame(motorInputFrame)
motorXSpeedFrame.pack(expand=1)

xSpeedLabel = Label(motorXSpeedFrame, text="X-Speed (mm/s)")
xSpeedLabel.pack(pady=(0,5))

xSpeedEntryVal = DoubleVar()
xSpeedEntryVal.set(0)
xSpeedEntry = Entry(motorXSpeedFrame, textvariable=xSpeedEntryVal, relief=SUNKEN, borderwidth=1, highlightthickness=0, justify=CENTER, width=15)
xSpeedEntry.pack()

xSpeedButton = Button(motorXSpeedFrame, text="Set", command=xScaleSet)
xSpeedButton.pack(side=LEFT, padx=(0,5))

xSpeedScaleVal = DoubleVar()
xSpeedScaleVal.set(0)
xSpeedScale = Scale(motorXSpeedFrame, variable=xSpeedScaleVal, orient=HORIZONTAL, from_=0, to=2, resolution=0.01, tickinterval=2, length=150, width=10, command=xEntrySet)
xSpeedScale.pack()

##### MANUAL MODE #####

motorManualFrame = LabelFrame(motorFrame, text="MANUAL", relief=SOLID, borderwidth=1, height=420, width=300)
motorManualFrame.pack(side=LEFT, expand=0, padx=(20,0), pady=(10,20), ipadx=10, ipady=10)
motorManualFrame.pack_propagate(0)

### manual x ###

manualXFrame = Frame(motorManualFrame)
manualXFrame.pack(expand=1)

manualXLabel = Label(manualXFrame, text=u"\u0394X (mm)")
manualXLabel.pack(side=LEFT)

xManEntryVal = DoubleVar()
xManEntryVal.set(0)
xManEntry = Entry(manualXFrame, textvariable=xManEntryVal, relief=SUNKEN, borderwidth=1, highlightthickness=0, justify=CENTER, width=5)
xManEntry.pack(side=LEFT)

xManButton = Button(manualXFrame, text="Set", command=xManScaleSet)
xManButton.pack(side=LEFT)

xManScaleVal = DoubleVar()
xManScaleVal.set(0)
xManScale = Scale(manualXFrame, variable=xManScaleVal, orient=HORIZONTAL, from_=0, to= 200, resolution=0.1, tickinterval=200, length=150, width=10, command=xManEntrySet)
xManScale.pack(side=LEFT)

arrowXFrame = Frame(motorManualFrame)
arrowXFrame.pack(expand=1)

xManHomeButton = Button(arrowXFrame, text=u"\u007C\u25C0", justify=CENTER, width=4, command=xManHomeButton)
xManHomeButton.pack(side=LEFT)

xManBwButton = Button(arrowXFrame, text=u"\u25C0", justify=CENTER, width=4, command=xManBwButton)
xManBwButton.pack(side=LEFT)

xManFwButton = Button(arrowXFrame, text=u"\u25B6", justify=CENTER, width=4, command=xManFwButton)
xManFwButton.pack(side=LEFT)

xManFarButton = Button(arrowXFrame, text=u"\u25B6\u007C", justify=CENTER, width=4, command=xManFarButton)
xManFarButton.pack(side=LEFT)

### manual y ###

manualYFrame = Frame(motorManualFrame)
manualYFrame.pack(expand=1)

manualYLabel = Label(manualYFrame, text=u"\u0394Y (mm)")
manualYLabel.pack(side=LEFT)

yManEntryVal = DoubleVar()
yManEntryVal.set(0)
yManEntry = Entry(manualYFrame, textvariable=yManEntryVal, relief=SUNKEN, borderwidth=1, highlightthickness=0, justify=CENTER, width=5)
yManEntry.pack(side=LEFT)

yManButton = Button(manualYFrame, text="Set", command=yManScaleSet)
yManButton.pack(side=LEFT)

yManScaleVal = DoubleVar()
yManScaleVal.set(0)
yManScale = Scale(manualYFrame, variable=yManScaleVal, orient=HORIZONTAL, from_=0, to= 50, resolution=0.1, tickinterval=50, length=150, width=10, command=yManEntrySet)
yManScale.pack(side=LEFT)

arrowYFrame = Frame(motorManualFrame)
arrowYFrame.pack(expand=1)

yManHomeButton = Button(arrowYFrame, text=u"\u007C\u25C0", justify=CENTER, width=4, command=yManHomeButton)
yManHomeButton.pack(side=LEFT)

yManBwButton = Button(arrowYFrame, text=u"\u25C0", justify=CENTER, width=4, command=yManBwButton)
yManBwButton.pack(side=LEFT)

yManFwButton = Button(arrowYFrame, text=u"\u25B6", justify=CENTER, width=4, command=yManFwButton)
yManFwButton.pack(side=LEFT)

yManFarButton = Button(arrowYFrame, text=u"\u25B6\u007C", justify=CENTER, width=4, command=yManFarButton)
yManFarButton.pack(side=LEFT)

### manual z ###

manualZFrame = Frame(motorManualFrame)
manualZFrame.pack(expand=1)

manualZLabel = Label(manualZFrame, text=u"\u0394Z (mm)")
manualZLabel.pack(side=LEFT)

zManEntryVal = DoubleVar()
zManEntryVal.set(0)
zManEntry = Entry(manualZFrame, textvariable=zManEntryVal, relief=SUNKEN, borderwidth=1, highlightthickness=0, justify=CENTER, width=5)
zManEntry.pack(side=LEFT)

zManButton = Button(manualZFrame, text="Set", command=zManScaleSet)
zManButton.pack(side=LEFT)

zManScaleVal = DoubleVar()
zManScaleVal.set(0)
zManScale = Scale(manualZFrame, variable=zManScaleVal, orient=HORIZONTAL, from_=0, to= 50, resolution=0.1, tickinterval=50, length=150, width=10, command=zManEntrySet)
zManScale.pack(side=LEFT)

arrowZFrame = Frame(motorManualFrame)
arrowZFrame.pack(expand=1)

zManHomeButton = Button(arrowZFrame, text=u"\u007C\u25C0", justify=CENTER, width=4, command=zManHomeButton)
zManHomeButton.pack(side=LEFT)

zManBwButton = Button(arrowZFrame, text=u"\u25C0", justify=CENTER, width=4, command=zManBwButton)
zManBwButton.pack(side=LEFT)

zManFwButton = Button(arrowZFrame, text=u"\u25B6", justify=CENTER, width=4, command=zManFwButton)
zManFwButton.pack(side=LEFT)

zManFarButton = Button(arrowZFrame, text=u"\u25B6\u007C", justify=CENTER, width=4, command=zManFarButton)
zManFarButton.pack(side=LEFT)

### zero ###

manualZeroFrame = Frame(motorManualFrame)
manualZeroFrame.pack(expand=1, pady=(10,0))

xZeroButton = Button(manualZeroFrame, text=u"\u29BF X", justify=CENTER, width=5, command=xZeroButton)
xZeroButton.pack(side=LEFT)

yZeroButton = Button(manualZeroFrame, text=u"\u29BF Y", justify=CENTER, width=5, command=yZeroButton)
yZeroButton.pack(side=LEFT)

zZeroButton = Button(manualZeroFrame, text=u"\u29BF Z", justify=CENTER, width=5, command=zZeroButton)
zZeroButton.pack(side=LEFT)

### other ###

manualOtherFrame = Frame(motorManualFrame)
manualOtherFrame.pack(expand=1, pady=(0,10))

zManSOButton = Button(manualOtherFrame, text=u"SoD", justify=CENTER, width=9, command=zManSOButton)
zManSOButton.pack(side=LEFT, padx=(0,3))

resetOriginSprayButton = Button(manualOtherFrame, text=u"\u29BF Zero", justify=CENTER, width=9, command=resetOriginSprayButton)
resetOriginSprayButton.pack(side=LEFT)

manStopButton = Button(motorManualFrame, text="STOP MOTORS", justify=CENTER, width=22, command=manStopButton)
manStopButton.pack(pady=(0,10))

##### AUTO MODE #####

motorAutoFrame = LabelFrame(motorFrame, text="AUTO", relief=SOLID, borderwidth=1, height=420, width=200)
motorAutoFrame.pack(side=LEFT, expand=0, padx=20, pady=(10,20), ipadx=10, ipady=10)
motorAutoFrame.pack_propagate(0)

### select mode ###

autoModeFrame = Frame(motorAutoFrame)
autoModeFrame.pack(expand=1)

autoModeLabel = Label(autoModeFrame, text="Auto")
autoModeLabel.grid(row=0, column=0, pady=(0,5))

manualModeLabel = Label(autoModeFrame, text="Manual")
manualModeLabel.grid(row=0, column=1, pady=(0,5))

autoModeScaleVal = IntVar()
autoModeScaleVal.set(0)
autoModeScale = Scale(autoModeFrame, variable=autoModeScaleVal, orient=HORIZONTAL, from_=0, to= 1, length=180, width=20, showvalue=0, sliderlength=90, command=setMode)
autoModeScale.grid(row=1, column=0, columnspan=2)

autoZeroRemoveFrame = Frame(motorAutoFrame)
autoZeroRemoveFrame.pack(expand=1)

### zero ###

autoZeroFrame = Frame(autoZeroRemoveFrame)
autoZeroFrame.pack(side=LEFT, expand=1)

autoZeroLabel = Label(autoZeroFrame, text="Zero")
autoZeroLabel.pack(pady=(0,5))

zeroButton = Button(autoZeroFrame, text=u"\u29BF X & Y", justify=CENTER, width=9, command=zeroButton)
zeroButton.pack(pady=(0,5))

zeroCNozzleButton = Button(autoZeroFrame, text=u"\u29BF Z (coarse)", justify=CENTER, width=9, command=zeroCNozzleButton)
zeroCNozzleButton.pack(pady=(0,5))

zeroFNozzleButton = Button(autoZeroFrame, text=u"\u29BF Z (fine)", justify=CENTER, width=9, command=zeroFNozzleButton)
zeroFNozzleButton.pack()

### remove ###

autoRemoveFrame = Frame(autoZeroRemoveFrame)
autoRemoveFrame.pack(side=LEFT, expand=1)

autoRemoveLabel = Label(autoRemoveFrame, text="Remove")
autoRemoveLabel.pack(pady=(0,5))

remSubButton = Button(autoRemoveFrame, text="Substrate", justify=CENTER, width=9, command=remSubButton)
remSubButton.pack(pady=(0,5))

remNozzleButton = Button(autoRemoveFrame, text="Nozzle", justify=CENTER, width=9, command=remNozzleButton)
remNozzleButton.pack(pady=(0,33))

### other ###

autoOtherFrame = Frame(motorAutoFrame)
autoOtherFrame.pack(expand=1)

homeButton = Button(autoOtherFrame, text=u"\u2302 Home", justify=CENTER, width=10, command=homeButton)
homeButton.pack(pady=(0,20))

originSprayButton = Button(autoOtherFrame, text="Go to origin", justify=CENTER, width=10, command=originSprayButton)
originSprayButton.pack()

###################################
############### MFC ###############
###################################

mfc_agFrame = Frame(mainFrame)
mfc_agFrame.pack(side=LEFT, expand=0)

mfcFrame = LabelFrame(mfc_agFrame, text="MASS FLOW CONTROLLER", relief=GROOVE, borderwidth=2, height=200, width=300)
mfcFrame.pack(side=TOP, expand=0, padx=10, pady=10, ipadx=10, ipady=10)
mfcFrame.pack_propagate(0)

mfcLabel = Label(mfcFrame, text="Mass Flow Rate (slpm)")
mfcLabel.pack(side=TOP, expand=1)

mfc_entry_setFrame = Frame(mfcFrame)
mfc_entry_setFrame.pack(side=TOP, expand=1)

mfcEntryRate = DoubleVar()
mfcEntryRate.set(0.0)
mfcEntry = Entry(mfc_entry_setFrame, textvariable=mfcEntryRate, relief=SUNKEN, borderwidth=1, highlightthickness=0, justify=CENTER, width=10)
mfcEntry.pack(side=LEFT)

mfcButton = Button(mfc_entry_setFrame, text="Set", command=mfcScaleSet)
mfcButton.pack(side=LEFT, padx=(10,0))

mfcScaleRate = DoubleVar()
mfcScaleRate.set(0)
mfcScale = Scale(mfcFrame, variable=mfcScaleRate, orient=HORIZONTAL, from_=0, to=15, resolution=0.1, tickinterval=15, length=250, width=30, command=mfcEntrySet)
mfcScale.pack(side=TOP, expand=1)

###################################
################ AG ###############
###################################

agFrame = LabelFrame(mfc_agFrame, text="AEROSOL GENERATOR", relief=GROOVE, borderwidth=2, height=200, width=300)
agFrame.pack(side=TOP, expand=0, padx=10, pady=10, ipadx=10, ipady=10)
agFrame.pack_propagate(0)

agLabel = Label(agFrame, text="Input Frequency (Hz)")
agLabel.pack(side=TOP, expand=1)

ag_entry_setFrame = Frame(agFrame)
ag_entry_setFrame.pack(side=TOP, expand=1)

agEntryFreq = IntVar()
agEntryFreq.set(440)
agEntry = Entry(ag_entry_setFrame, textvariable=agEntryFreq, relief=SUNKEN, borderwidth=1, highlightthickness=0, justify=CENTER, width=10)
agEntry.pack(side=LEFT, expand=0)

agButton = Button(ag_entry_setFrame, text="Set", command=agScaleSet)
agButton.pack(side=LEFT, expand=0, padx=(10,0))

agScaleFreq = IntVar()
agScaleFreq.set(440)
agScale = Scale(agFrame, variable=agScaleFreq, orient=HORIZONTAL, from_=30, to=3000, tickinterval=2970, length=250, width=30, command=agEntrySet)
agScale.pack(side=TOP, expand=1)

###################################
############# BUTTONS #############
###################################

buttonFrame = Frame(root, relief=GROOVE, borderwidth=2, height=90)
buttonFrame.pack(side=TOP, fill=X, padx=10, pady=10, ipadx=10, ipady=10)
buttonFrame.pack_propagate(0)

'''resetImage = PhotoImage(file="reset.gif")
resetButton = Button(buttonFrame, compound=TOP, text="Reset", image=resetImage, command=resetDefaults)
resetButton.pack(side=LEFT, expand=1)'''

#startImage = PhotoImage(file="start.gif")
startButtonText = StringVar()
startButtonText.set("Start")
#startButton = Button(buttonFrame, compound=TOP, textvariable=startButtonText, image=startImage, command=startSequence)
startButton = Button(buttonFrame, compound=TOP, textvariable=startButtonText, command=startSequence)
startButton.pack(side=LEFT, expand=1)

stopMFCButton = Button(buttonFrame, text="Stop MFC", command=stopMFC)
stopMFCButton.pack(side=LEFT, expand=1)

'''stopImage = PhotoImage(file="stop.gif")
emergencyButton = Button(buttonFrame, compound=TOP, text="EMERGENCY STOP", image=stopImage)
emergencyButton.pack(side=LEFT, expand=1)'''

root.mainloop()