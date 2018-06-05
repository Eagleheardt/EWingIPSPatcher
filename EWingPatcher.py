#!/usr/bin/python3

# Developed by Eagleheardt (2017 - 2018)
# see also https://github.com/Eagleheardt

# This is hereby released into the public domain

# Please credit me, if you use any parts of this!

from tkinter import * # imports the TKinter library
from tkinter import ttk # imports the TKinter nicer buttons
from tkinter.ttk import * # imports the TKinter nicer buttons
from tkinter import filedialog # imports the TKinter filedialog popup interface
import os # imports low level OS functions

########################################################################################
########################################################################################

#################### Global Variable Declaration ####################

########################################################################################
########################################################################################

mainWindow=Tk() # gui window is called mainWindow
mainWindow.title("E-Wing IPS Patcher") # set the title of the window
mainWindow.geometry("400x280") # main window starts off this size

fullROMPath = StringVar() # Path of ROM file
fullPatchPath = StringVar() # Path of patch file
ROMinf = StringVar() # Display of ROM path
patchInf = StringVar() # Display of patch path

changeNameEnabled = IntVar() # checks if the user wants to rename the file (0=no, 1=yes)

fullROMPath.set("") # sets ROM path to empty string
fullPatchPath.set("") # sets patch path to empty string
ROMinf.set("No ROM Selected") # Sets default message for the ROM
patchInf.set("No patch Selected") # Sets default message for the patch

aboutString = (
"""
If the "Append patch name" box
is checked, the name of the patch
will be added to the name of the ROM
when patching occurs.\n
It is free, hopefully easy to use,
and open source!\n
The comments in the code detail
the functions.\n
See the IPS and BPS file type specifications for more information!\n
This utility was created by Eagleheardt
"""
) # Information about myself and the program ###########################################

########################################################################################
########################################################################################

#################### Generic Method Declarations ####################

########################################################################################
########################################################################################

# opens a window for information/errors

def openWindow(titleText="Window Title", bodyText="Body Text"):

	infoWin = Toplevel()
	infoWin.title(titleText)
	infoMsg = Message(infoWin,text=bodyText,width=300).pack(padx=10,pady=5)
	infoBtn = Button(infoWin, text="Close",command=infoWin.destroy).pack(padx=10,pady=10)

	return # exits openWindow(titleText="Window Title", bodyText="Body Text") function

# sets the ROM path

def setROMPath():

	# brings up a filedialog to select the ROM file
	# sets the title of the window to "Select ROM file"
	r = filedialog.askopenfilename(title = "Select ROM file")

	# sets the ROM path to the global variable
	fullROMPath.set("{0}".format(r))

	return # exits setROMPath() function

# sets the patch patch

def setPatchPath():

	# brings up a filedialog to select the IPS file
	# sets the title of the window to "Select IPS file"
	p = filedialog.askopenfilename(title = "Select IPS file")

	# sets the IPS path to the global variable
	fullPatchPath.set("{0}".format(p))

	return # exits setPatchPath() function

# gets int position of final right slash in a given string

def lastSlash(someString):
	
	return someString.rfind("/")

# rename the file

def fileRename(oFilePath, patchName, newName=""):
		
	dotNdex = oFilePath.rfind(".") # finds the last dot
	f = ("{0}".format(oFilePath)) # oFilePath set to f
	d = f[dotNdex:] # d is the file extension

	if newName == "":
		# if no name specified

		# p is the whole file path of the original file
		# concatinated with the phrase " patched with "
		# followed by the name of the patch
		# and the file extension of the original file
		p = ("{0} patched with {1}.{2}".format(oFilePath,patchName,d))

		# replaces the original file with the newly formatted one
		os.replace(oFilePath, p)
	else:
		# if there is a custom name specified

		k = lastSlash(oFilePath) # gets the index of the last slash in the file
		filePath = ("{0}".format(oFilePath[:k])) # formats the file path
		
		# holds the new file name with the original file extension
		p = ("{0}{1}.{2}".format(oFilfilePathePath,newName,d))

		# replaces the original file with the newly formatted one
		os.replace(oFilePath, p)

	return # exits fileRename(oFilePath, patchName, newName="") function

# Resets the global variables and the labels on the main window

def resetMainWindow():

	fullROMPath.set("")
	fullPatchPath.set("")

	ROMinf.set("No ROM Selected")
	patchInf.set("No patch Selected")
	return # exits resetMainWindow() function

# Checks the ROM makes sure it can be open for reading in byte mode

def checkROM(checkfullROMPath):

	try:
		# tries to open the ROM
		checkROMIO = open(checkfullROMPath,'r+b')
	except:
		# catches any error with the ROM opening
		# opens a window notifying of the error
		
		openWindow("CrItIcAl ErRoR!", "Unable to read ROM file.")
		fullROMPath.set("") # sets the global variable to empty string
		ROMinf.set('Unsupported ROM!') # sets the information label to unsupported ROM
	else:
		# if no exception happens this block goes off

		k = lastSlash(checkfullROMPath) # gets the position of the last slash in the path
		fullROMPath.set(checkfullROMPath) # sets the global variable to the path directed in
		ROMinf.set("..." + checkfullROMPath[k:]) # sets the label to ".../ROM_NAME"
	finally:
		# this block fires no matter what

		checkROMIO.close() # closes the file
		return # exits the checkROM(checkfullROMPath) function

def checkPatch(checkPatchPath):
	# does basic file checking for patch files

	try:
		checkPatchFile = open(checkPatchPath,'rb') # opens patch file

		if checkPatchFile.read(5) != b'PATCH': # IPS patches start with the word "PATCH"
			raise LookupError('Invalid Patch') # triggers an error

		else:
			k = lastSlash(checkPatchPath) # gets the position
			fullPatchPath.set(checkPatchPath) # sets full patch path
			patchInf.set("..." + checkPatchPath[k:]) # sets the label to ".../IPS_NAME"
		
	except:
		# if an error occurs
 	
		openWindow("CrItIcAl ErRoR!", "Unable to read patch file.")
		patchInf.set("Unidentified patch!") # sets the label to "Unidentified patch!"
		fullPatchPath.set("") # sets the global variable to empty string
	finally:
		checkPatchFile.close() # closes patch file

		return # exits checkPatch(checkPatchPath) function

########################################################################################
########################################################################################

#################### IPS Method Declarations ####################

########################################################################################
########################################################################################

# reads records of IPS file

def readIPSRecord(patchFile):
	# IPS files have a 5 byte header, per record

	# First 3 bytes of the header are the offset in the ROM file 
	# Where the information will be inserted
	
	first3 = patchFile.read(3)

	# if the first 3 bytes say 'EOF' we've reached the end of the file
	if first3 == b'EOF':
		raise EOFError('END OF FILE')
		# This error will serve as the terminating condition of a loop later
	offset = int.from_bytes(first3,byteorder='big')

	# The last 2 bytes of the header are the 'length' of the following data
	loadLength = int.from_bytes(patchFile.read(2),byteorder='big')

	# If the loadLength is 0, then the next record is an 'RLE' style record
	# RLE records just output a repeated single character
	if loadLength == 0:
		RLESize = int.from_bytes(patchFile.read(2),byteorder='big')
		RLEChar = patchFile.read(1)
		replacement = RLEChar * RLESize
		# The output is the RLEChar times the RLESize
		return offset, replacement
	else:
		# If the length is more than 0, the replacement data output
		# will be the next loadLength amount of bytes
		replacement = patchFile.read(loadLength)
		return offset, replacement

# patches a ROM with an IPS patch

def patchIPSFile(aROM,aPatch):
	# Open the files

	finalROM = open(aROM,'r+b')
	finalIPS = open(aPatch,'rb')
	finalIPS.seek(5) # Moves the pointer 5 bytes, past the string "PATCH"
	
	records = 0 # number of times data is written
	dataWritten = 0 # amount of data that was inserted into the ROM
	try:	
		while True:
			offset,replacement = readIPSRecord(finalIPS) # reads a record

			records += 1 # increases the number of writes
			dataWritten += len(replacement)	# adds the amount of write each time
			
			finalROM.seek(offset) # moves file pointer to the offset
			finalROM.write(replacement) # writes the replacement data
	except:
		pass # when the exception occurs, the loop is broken
		
	truncateOffset = finalIPS.read(3)
	# checks 3 bytes past the EOF marker for a truncation length
	if len(truncateOffset) != 0:
		finalROM.truncate(int.from_bytes(Offset,byteorder='big'))
		# if it exists, truncates the file to that size

	# info window with changes made
	openWindow("Attention!", "Number of records changed: {} \n"
				 "Number of bytes changed: {}".format(records,dataWritten))
	
	# close files
	finalROM.close()
	finalIPS.close()

	return

########################################################################################
########################################################################################

#################### Button Execution Methods ####################

########################################################################################
########################################################################################

# Click to select ROM file

def btnROMClick():

	setROMPath()
	checkROM(fullROMPath.get())

	return # exits btnROMClick() function

# Click to select patch file

def btnIPSClick():

	setPatchPath()
	checkPatch(fullPatchPath.get())

	return # exits btnIPSClick() function

# do the patching!

def btnApplyClick():
	
	ROMCheck = fullROMPath.get()
	
	if ROMCheck == "":
		# if no ROM set

		openWindow("CrItIcAl ErRoR!","No ROM selected!")
		return # exits btnApplyClick() function
	else:
		try:
			# tries to check the path once more
			checkPatch(fullPatchPath.get())
		except:	
			# if the ROM doest verify
			openWindow("CrItIcAl ErRoR!","Unidentified patch!")
		else:
			# if the ROM does verify
			p = fullPatchPath.get() # holds the patch path
			r = fullROMPath.get()   # holds the ROM path

			patchIPSFile(r,p) # calls the patch on the file
		
			if changeNameEnabled.get() == 1:
				# if the user wants to rename the ROM
				k = lastSlash(p)
				nameOfPatch = p[k+1:]
				fileRename(oFilePath=ROMCheck, patchName=nameOfPatch, newName="")
		
			resetMainWindow() # resets the varbiables and window
		finally:

			return # exits btnApplyClick() function

# Displays information about my program

def btnAbtClick():

	openWindow("Attention!",aboutString)

	return # exits btnAbtClick() function

########################################################################################
########################################################################################

#################### Button Declaration and Placement ####################

########################################################################################
########################################################################################

#checkbox to enable file renaming
renameFileChecker = Checkbutton(mainWindow,
			text="Append patch name",
			variable=changeNameEnabled).pack(padx=5,pady=5,anchor=W)

# Buttons and labels for ROM section
btnROM = Button(mainWindow,text="Choose ROM",command=btnROMClick).pack(padx=5,pady=5,fill=X)
Label(textvariable=ROMinf,justify=LEFT).pack(padx=5,pady=5,fill=X)

# Buttons and labels for patch section
btnPatch = Button(mainWindow,text="Choose Patch",command=btnIPSClick).pack(padx=5,pady=5,fill=X)
Label(textvariable=patchInf,justify=LEFT).pack(padx=5,pady=5,fill=X)

# Apply, About, Close buttons
btnApply = Button(mainWindow,text="Apply Patch",command=btnApplyClick).pack(padx=5,pady=5,fill=X)
btnAbt = Button(mainWindow,text="About",command=btnAbtClick).pack(padx=5,pady=5,fill=X)
btnClose = Button(mainWindow,text="Close",command=mainWindow.destroy).pack(padx=5,pady=5,fill=X)

########################################################################################
########################################################################################

mainWindow.mainloop() ##### This Starts the GUI #####

########################################################################################
########################################################################################

# resources:
# http://effbot.org/tkinterbook/
# https://zerosoft.zophar.net/ips.php
# http://www.smwiki.net/wiki/IPS_file_format
# http://justsolve.archiveteam.org/wiki/IPS_(binary_patch_format)