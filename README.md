Mitchell Bailey
Department of Electrical and Computer Engineering  
EECE.5830 - Network Design: Principles, Protocols, and Applications  
4 December 2022  

# README File
## EXTRA CREDIT CLAIMS 
We would like to claim the following extra credit opportunitites for the EECE.5830 Semester Project: 
1. Implement an applet/GUI to show the data transfer (10%)
    * Basis: The GUI that we have implemented for the project displays the current state of data transfer for individual file transfers, along with the status of the current transfer mode and overall program execution. 
2. Implement an applet/GUI to show the (TCP) FSM (10%)
    * Basis: The GUI that we have implemetned for the project provides real-time information on the current FSM state for both the sender FSM and receiver FSM via a text-based interface. 
3. Implement an applet/GUI to take user input parameters for program execution (10% - Proposed Extra Credit)
    * Basis: Our apple/GUI implementation goes above and beyond the other categories of GUI extra credit through the implementation of an additional GUI-based user input feature. Our GUI allows the end-user to select which transmission modes they would like to run (along with the associated test parameters), thus avoiding any need to interact with the CLI or underlying code base. We believe that this design decision and the work associated with its implementation is worthy of an additional extra credit opportunity. 
4.  Single sender/receiver FSM program via common codebase (10% - Proposed Extra Credit)
    * Basis: Our network application leverages a single Python script to execute the core functionality for both the sender FSM and receiver FSM. Our design design decisions have yielded a networked application that relies on a common codebase and could be extended for use as a Python library for future network application development. We believe that this design decision and the work associated with its implementaiton is worthy of an additional extra credit opportunity. 
5. Feature that deletes transfered files automatically (5% - Proposed Extra Credit)
    * Basis: We implemented an extra feature that automatically deletes repeated copies of the transfer file present in the same directory. For example, if we transfer a file and multiple new copies are placed in the same directory as a result of the program execution, then the extra files are deleted. We believe that this design decision and the work assocaited with its implemention is worth of an additional extra credit opportunity. 

## Environment
•	Microsoft Windows 10 Version 21H2 (OS Build 19044.2006)  
•	Python 3.9.7  
•	anaconda 2021.11 (py39_0)  
•	Visual Studio Code 1.71.2  

## Pre-requisites
•	Python 3.9.7  
•	Anaconda Prompt, or equivalent terminal where Python programs can be run.  

## Instructions for Program Execution 
1.	Open a terminal (WSL, Anaconda Prompt, Linux Terminal) capable of executing Python.  
2.	Navigate to the folder containing the program files.
3.  Ensure the file you wish to transfer is in the same directory as the code files. (The enclosed *card.bmp* or *smpte.bmp* files can be used for proof-of-concept code execution).
4.	In a terminal, run the command `python gui.py`. This will launch the graphical user interface (GUI) for the network application. Optionally, `python unittests.py` can be run to verify the protocol operates as intended.
5. From the GUI window, enter the name of the file you wish to transfer between sender FSM and receiver FSM (i.e., *card.bmp* for proof-of-concept code execution). 
6. From the GUI window, select the desired transfer modes. The four packet error data modes are selected by default.
7. From the GUI window, select the transfer test parameters you wish to use for this program execution. The `Start` and `Stop` parameters denote the percentage range (0% to 60% by default). The `Step` parameter denotes the percent change for each trial of the selected transfer modes (30% by default). The `Samples` parameter denotes the number of times that each transfer mode will be executed for each percentage step (1 sample per trial by default).
8.  From the GUI, click the `Begin Transfer` button at the bottom of the window. This action will initialize the current instance of the network application in the receiver FSM mode. The parameters selected above in Step 6 to Step 9 will be provided to the receiver FSM as initialization variables.  
9. Monitor the GUI windows for the sender FSM and receiver FSM throughout the program execution. Once the program execution is complete Python will generate multiple graphs. Review these graphs to gain insight into the performance of the network application. 
10. To exit the program, close all of the windows associated with the sender FSM, receiver FSM, and Python graphs. 
11. If you would like to rerun the network application, then repeat the above instructions for Step 1 to Step 15.
