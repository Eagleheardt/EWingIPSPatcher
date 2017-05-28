#!/usr/bin/python3

# Inspired by original python 2.0 code by Xezlec (2017) as ips.py
# graphical front end developed by Eagleheardt (2017)
# see also https://github.com/Eagleheardt

# This is hereby released into the public domain
# please credit our work, if you use it

from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import filedialog
from PIL import Image
from PIL import ImageTk

root=Tk() # gui window is called root
root.title("E-Wing IPS Patcher") # set the title of the window
root.geometry("220x230")

# Global variable declaration

ROMPath = StringVar() # Path of ROM file
IPSPath = StringVar() # Path of IPS file
ROMinf = StringVar() # Display of ROM path
IPSinf = StringVar() # Display of IPS path

ROMinf.set("No ROM Selected")
IPSinf.set("No IPS Selected")

# this mess sets the tray icon to my E-Wing logo
iconImg = Image.open("Icon.bmp")
iconPhoto = ImageTk.PhotoImage(iconImg)
root.tk.call('wm', 'iconphoto', root._w, iconPhoto)

# reads records of IPS file
def readRecord(patchFile):
	# 5 byte header
	# First 3 bytes are the offset in the ROM file 
	# Where the information will be inserted

	# Second 2 bytes are the 'length' of the following data
	first3 = patchFile.read(3)
	# if the first 3 bytes say 'EOF' we've reached the end of the file
	if first3 == b'EOF':
		raise ValueError('END OF FILE')
	offset = int.from_bytes(first3,byteorder='big')
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

# Opens a window for information/errors

def openWindow(titleText="Window Title", bodyText="Body Text"):
	infoWin = Toplevel()
	infoWin.title(titleText)
	infoMsg = Message(infoWin,text=bodyText,width=300).pack(padx=10,pady=5)
	infoBtn = Button(infoWin, text="Close",command=infoWin.destroy).pack(padx=10,pady=10)
	return

# Button execution methods

def btnROMClick():
	# only does basic file checking for ROM

	checkROMPath = filedialog.askopenfilename() # brings up a filedialog to select the ROM
	try:
		checkROMIO = open(checkROMPath,'r+b')
	except:
		openWindow("CrItIcAl ErRoR!", "Unable to read ROM file.")
		ROMinf.set('Unsupported ROM!')
		return
	checkROMIO.close()
	ROMPath.set(checkROMPath)
	ROMinf.set(checkROMPath[-35:])
	return

def btnIPSClick():
	# only does basic file checking for IPS
	checkIPSPath = filedialog.askopenfilename() # brings up a filedialog to select the IPS
	try:
		# IPS patches start with the word "PATCH"
		checkIPSIO = open(checkIPSPath,'rb')
		if checkIPSIO.read(5) != b'PATCH':
			raise ValueError('IPS not supported')
	except:
		openWindow("CrItIcAl ErRoR!", "Unable to read IPS file.")
		IPSinf.set("Unsupported IPS!")
		return
		
	checkIPSIO.close()
	IPSPath.set(checkIPSPath)
	IPSinf.set(checkIPSPath[-35:])
	return

def btnApplyClick():
	
	# Open our files
	finalROM = open(ROMPath.get(),'r+b')
	finalIPS = open(IPSPath.get(),'rb')
	finalIPS.seek(5)
	# Moves the pointer 5 bytes, past the word "PATCH"

	# Do the patching!
	records = 0
	dataWritten = 0
	try:
		while True:
			offset,replacement = readRecord( finalIPS )
			# this will throw a value error at the end of file marker, kicking us out of the loop

			records += 1
			dataWritten += len( replacement )	
			# each loop increases the number of writes
			# and adds the amount of replacement each time

			finalROM.seek( offset )	
			# moves file pointer to the offset
			finalROM.write( replacement )
			# writes the replacement data to the offset location
	except:
		pass
		# when the exception occurs, ignore it

	truncateOffset = finalIPS.read(3)
	# checks 3 bytes past the EOF marker for a truncation length
	if len(truncateOffset) != 0:
		finalROM.truncate(int.from_bytes(Offset,byteorder='big'))
		# if it exists, truncates the file to that size

	# info window with changes made
	openWindow("Attention!", "Records changed: {}. \nBytes changed: {}".format(records,dataWritten))
	
	# close files
	finalROM.close()
	finalIPS.close()
	
	# Reset all variables/Labels
	ROMPath.set("")
	IPSPath.set("")

	ROMinf.set("No ROM Selected")
	IPSinf.set("No IPS Selected")
	return

def btnAbtClick():
	openWindow("Attention!","This utility was created by Eagleheardt.\nInspired by Xezlec's original utility.\n\nThe comments in the code detail what it does\nas well as the specification of the IPS file.")
	return

# Button declaration and placement

# Buttons and labels for ROM section
btnROM = Button(root,text="Choose ROM",command=btnROMClick).pack(padx=5,pady=5,fill=X)
Label(textvariable=ROMinf,justify=LEFT).pack(padx=5,pady=5,fill=X)

# Buttons and labels for IPS section
btnIPS = Button(root,text="Choose Patch",command=btnIPSClick).pack(padx=5,pady=5,fill=X)
Label(textvariable=IPSinf,justify=LEFT).pack(padx=5,pady=5,fill=X)

# Apply, About, Close buttons
btnApply = Button(root,text="Apply Patch",command=btnApplyClick).pack(padx=5,pady=5,fill=X)
btnAbt = Button(root,text="About",command=btnAbtClick).pack(padx=5,pady=5,fill=X)
btnClose = Button(root,text="Close",command=root.destroy).pack(padx=5,pady=5,fill=X)

root.mainloop() # this starts the GUI

# resources:
# https://zerosoft.zophar.net/ips.php
# http://www.smwiki.net/wiki/IPS_file_format
# http://justsolve.archiveteam.org/wiki/IPS_(binary_patch_format)
# Accessed 4/30/2017 - 11am CST

