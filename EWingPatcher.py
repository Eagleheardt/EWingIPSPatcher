#!/usr/bin/python3

# graphical front end developed by Eagleheardt (2017)
# see also https://github.com/Eagleheardt

# original python 2.0 code was developed by Xezlec (2017) as ips.py

# I used that code and packaged it in an easy to use front end (I hope)

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

# Global variable declaration

ROMPath = StringVar() # Path of ROM file
IPSPath = StringVar() # Path of IPS file
ROMinf = StringVar() # Display of ROM path
IPSinf = StringVar() # Display of IPS path
ROMerr = StringVar() # Info about the ROM - good/bad ROM file
IPSerr = StringVar() # Info about the IPS - good/bad IPS file

ROMinf.set("No ROM Selected")
ROMerr.set("No ROM Info")

IPSinf.set("No IPS Selected")
IPSerr.set("No IPS Info")

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
	offset = int.from_bytes(patchFile.read(3),byteorder='big')
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

# Button execution methods

def btnROMClick():
	# only does basic file checking for ROM
	checkROMPath = filedialog.askopenfilename() # brings up a filedialog to select the ROM
	try:
		checkROMIO = open(checkROMPath,'r+b')
	except:
		infoWin = Toplevel()
		infoWin.title("CrItIcAl ErRoR")
		infoMsg = Message(infoWin,text="Unable to read ROM file.",width=300).pack(padx=10,pady=5)
		infoBtn = Button(infoWin, text="Close",command=infoWin.destroy).pack(padx=10,pady=10)
		ROMinf.set('Unsupported ROM!')
		ROMerr.set('Unsupported ROM!')
		return
	checkROMIO.close()
	ROMPath.set(checkROMPath)
	ROMinf.set(checkROMPath[-15:])
	ROMerr.set('Good ROM!')
	return

def btnIPSClick():
	# only does basic file checking for ROM
	checkIPSPath = filedialog.askopenfilename() # brings up a filedialog to select the ROM
	try:
		# AL7L7L7 IPS patches apparently start with the word "PATCH"
		checkIPSIO = open(checkIPSPath,'rb')
		if checkIPSIO.read(5) != b'PATCH':
			raise ValueError('IPS not supported')
	except:
		infoWin = Toplevel()
		infoWin.title("CrItIcAl ErRoR")
		infoMsg = Message(infoWin,text="Unable to read IPS file.",width=300).pack(padx=10,pady=5)
		infoBtn = Button(infoWin, text="Close",command=infoWin.destroy).pack(padx=10,pady=10)
		IPSinf.set('Unsupported IPS!')
		IPSerr.set('Unsupported IPS!')
		return
		
	checkIPSIO.close()
	IPSPath.set(checkIPSPath)
	IPSinf.set(checkIPSPath[-15:])
	IPSerr.set('Good IPS!')
	return

def btnApplyClick():
	# Open our files
	finalROM = open(ROMPath.get(),'r+b')
	finalIPS = open(IPSPath.get(),'rb')
	finalIPS.seek(5)
	# Moves the pointer 5 bytes, past the "PATCH" word

	# Do the patching!
	records = 0
	dataWritten = 0
	while True:
		offset,replacement = readRecord( finalIPS )
		print("Data to be written {}".format(replacement))
		if offset == b'EOF':
			break

		records += 1
		dataWritten += len( replacement )

		finalROM.seek( offset )
		finalROM.write( replacement )

	truncateLength = int.from_bytes(finalIPS.read(3),byteorder='big')
	if truncateLength != 0:
		finalROM.truncate(truncateLength)
	
	print("Records changed: {}. Amount changed: {}".format(records,dataWritten))
	
	finalROM.close()
	finalIPS.close()

	print("The number of records changed: {}\n\nThe size of all records changed: {}\n\n".format(num_recs,num_bytes))

	return

def btnAbtClick():
	infoWin = Toplevel()
	infoWin.title("Attention!")
	infoMsg = Message(infoWin,text="This utility was created by Eagleheardt.",width=300).pack(padx=10,pady=5)
	infoBtn = Button(infoWin, text="Close",command=infoWin.destroy).pack(padx=10,pady=10)
	return

# Button declaration and placement

# Buttons and labels for ROM section
btnROM = Button(root,text="Choose ROM",command=btnROMClick).grid(row=0,column=0,padx=10,pady=10)
Label(textvariable=ROMinf).grid(row=1,column=0,padx=10,pady=10,sticky=W)
Label(textvariable=ROMerr).grid(row=2,column=0,padx=10,pady=10,sticky=W)

# Buttons and labels for IPS section
btnIPS = Button(root,text="Choose Patch",command=btnIPSClick).grid(row=0,column=1,padx=10,pady=10)
Label(textvariable=IPSinf).grid(row=1,column=1,padx=10,pady=10,sticky=W)
Label(textvariable=IPSerr).grid(row=2,column=1,padx=10,pady=10,sticky=W)

# Apply and About buttons
btnApply = Button(root,text="Apply Patch",command=btnApplyClick).grid(row=3,column=0,columnspan=2,padx=10,pady=10,sticky=E+W)
btnAbt = Button(root,text="About",command=btnAbtClick).grid(row=4,column=0,columnspan=2,padx=10,pady=10,sticky=E+W)

root.mainloop() # this starts the GUI

# resources:
# https://zerosoft.zophar.net/ips.php
# http://www.smwiki.net/wiki/IPS_file_format
# http://justsolve.archiveteam.org/wiki/IPS_(binary_patch_format)
# Accessed 4/30/2017 - 11am CST

