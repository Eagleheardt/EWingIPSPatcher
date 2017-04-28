#!/usr/bin/python3

# graphical front end developed by Eagleheardt (2017)
# see also https://github.com/Eagleheardt

# in the name of all that is holy, use TABS, please!!

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

import struct
import sys

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

# because life is too hard without it.
class PatchEOFError( Exception ):
	def __init__( self, extra_bytes ):
		self.extra_bytes = extra_bytes

# definition of the IPS file format.
rec_hdr = struct.Struct( '>BHH' ) # 3-byte offset, 2-byte length
rle_rec = struct.Struct( '>Hc' )  # 2-byte length, 1-byte fill value
trunc_rec = struct.Struct( '>BH' )  # 3-byte truncation length
# These are used to handle C type structures
# > denotes big-endian 
# B is an unsigned char
# H is an unsigned short
# c is a regular char

def field_read( patch, field, is_first=False ):
	read_bytes = patch.read( field.size )

	if is_first and read_bytes[0:3] == b'EOF':
		raise PatchEOFError( read_bytes[3:] )
	if len( read_bytes ) < field.size:
		#infoWin = Toplevel()
		#infoWin.title("CrItIcAl ErRoR")
		#infoMsg = Message(infoWin,text="Patch file ended unexpectedly.  Maybe patch is corrupt?",width=300).pack(padx=10,pady=5)
		#infoBtn = Button(infoWin, text="Close",command=infoWin.destroy).pack(padx=10,pady=10)
		# Personal perferance: I don't mind creating and destroying these widgets
		# Someone could branch this and optimize it
		# I've never been accused of 'optimizing' my code... :(
		return

	return field.unpack( read_bytes )

def rec_read( patch ):
	offset_hi, offset_lo, length = field_read( patch, rec_hdr, True )
	offset = (offset_hi << 16) | offset_lo

	if length == 0:
		length, fill = field_read( patch, rle_rec )
		replacement = fill * length
	else:
		replacement = patch.read( length )
	if len( replacement ) < length:
		infoWin = Toplevel()
		infoWin.title("CrItIcAl ErRoR")
		infoMsg = Message(infoWin,text="Patch file ended unexpectedly.  Maybe patch is corrupt?",width=300).pack(padx=10,pady=5)
		infoBtn = Button(infoWin, text="Close",command=infoWin.destroy).pack(padx=10,pady=10)
		return

	return offset, replacement

# Button execution methods

def btnROMClick():
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
	checkIPSPath = filedialog.askopenfilename() # brings up a filedialog to select the ROM
	try:
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

	# Do the patching!
	
	num_recs = 0
	num_bytes = 0

	try:
		#offset,replacement = rec_read( finalIPS )
		while not False:
			offset,replacement = rec_read( finalIPS )

			try:
				finalROM.seek( offset )
			except:
				#sys.stderr.write( "ERROR: Failed to seek to position %u in ROM file.\n" %offset )
				#return
				raise PatchEOFError('EOF')

			try:
				finalROM.write( replacement )
			except:
				raise PatchEOFError('EOF')
				#return
				#sys.stderr.write( 'ERROR: Failed to write %u bytes to ROM file.\n' %len( replacement ) )

			num_recs += 1
			num_bytes += len( replacement )
	except PatchEOFError as e:
		infoWin = Toplevel()
		infoWin.title("Attention!")
		infoMsg = Message(infoWin,text="Patch Applied!",width=300).pack(padx=10,pady=5)
		infoBtn = Button(infoWin, text="Close",command=infoWin.destroy).pack(padx=10,pady=10)
		#sys.stderr.write( 'Patch applied.  Made %u changes for a total of %u bytes changed.\n' %
			#(num_recs, num_bytes) )

		if len( e.extra_bytes ) != 0:
		# if there are any bytes after the EOF marker, they better be a
		# truncation indicator and nothing else.  read 1 past the end, just
		# to verify.
			extra_bytes = str(e.extra_bytes) + str(finalIPS.read( 2 ))

			if len( extra_bytes ) != trunc_rec.size:
				infoWin = Toplevel()
				infoWin.title("CrItIcAl ErRoR")
				infoMsg = Message(infoWin,text="Everything is horrible!",width=300).pack(padx=10,pady=5)
				infoBtn = Button(infoWin, text="Close",command=infoWin.destroy).pack(padx=10,pady=10)
				return

			trunc_len_hi, trunc_len_lo = trunc_rec.unpack( extra_bytes )
			trunc_len = (trunc_len_hi << 16) | trunc_len_lo

			try:
				finalROM.truncate( trunc_len )
			except:
				#sys.stderr.write( "ERROR: Failed to truncate ROM file.  Might be OK anyway though.\n" )
				return

			#sys.stderr.write( 'Also truncated the ROM to %u bytes as instructed.\n' %trunc_len )
	
	# Close everything
	finalROM.close()
	finalIPS.close()

	# Kappa?
	infoWin = Toplevel()
	infoWin.title("CrItIcAl ErRoR")
	infoMsg = Message(infoWin,text="Kappa!",width=300).pack(padx=10,pady=5)
	infoBtn = Button(infoWin, text="Close",command=infoWin.destroy).pack(padx=10,pady=10)
	return

# Should combine the ROM and IPS
# magic happens here

def btnAbtClick():
	return
	# todo Brings up a toplevel widget that will tell people about me

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
