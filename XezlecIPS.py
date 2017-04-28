#!/usr/bin/env python

# ips.py by Xezlec (2017)
#
# This code is hereby released into the public domain, but please don't remove
# my name from it.  Thanks.

import argparse
import struct
import sys

# because life is too hard without it.
class PatchEOFError( Exception ):
    def __init__( self, extra_bytes ):
        self.extra_bytes = extra_bytes

# definition of the IPS file format.
rec_hdr   = struct.Struct( '>BHH' ) # 3-byte offset, 2-byte length
rle_rec   = struct.Struct( '>Hc' )  # 2-byte length, 1-byte fill value
trunc_rec = struct.Struct( '>BH' )  # 3-byte truncation length

def field_read( patch, field, is_first=False ):
    read_bytes = patch.read( field.size )

    if is_first and read_bytes[0:3] == b'EOF':
        raise PatchEOFError( read_bytes[3:] )
    if len( read_bytes ) < field.size:
        sys.stderr.write( 'ERROR: Patch file ended unexpectedly.  Maybe patch is corrupt?\n' )
        exit( 1 )

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
            sys.stderr.write( 'ERROR: Patch file ended unexpectedly.  Maybe patch is corrupt?\n' )
            exit( 1 )

    return offset, replacement

# parse args.
parser = argparse.ArgumentParser( description='Apply a patch to a ROM file.' )
parser.add_argument( 'patch', help='The .ips file containing the patch.' )
parser.add_argument( 'rom', help='The game ROM file to patch.' )
args = parser.parse_args()

# open the files.
try:
    rom = open( args.rom, 'r+b' )
except:
    sys.stderr.write( 'ERROR: Failed to open ROM file "%s" for read/write.\n' % args.rom )
    exit( 2 )

try:
    patch = open( args.patch, 'rb' )
except:
    sys.stderr.write( 'ERROR: Failed to open patch file "%s"\n' % args.patch )
    exit( 3 )

# check some preliminary info.
if patch.read( 5 ) != b'PATCH':
    sys.stderr.write( 'ERROR: Specified patch file does not appear to be in the IPS format.\n' )
    exit( 4 )

# do the patching!
num_recs = 0
num_bytes = 0

try:
    while True:
        offset, replacement = rec_read( patch )

        try:
            rom.seek( offset )
        except:
            sys.stderr.write( "ERROR: Failed to seek to position %u in ROM file.\n" %
                              offset )
            exit( 7 )

        try:
            rom.write( replacement )
        except:
            sys.stderr.write( 'ERROR: Failed to write %u bytes to ROM file.\n' %
                              len( replacement ) )
            exit( 8 )

        num_recs += 1
        num_bytes += len( replacement )
except PatchEOFError as e:
    sys.stderr.write( 'Patch applied.  Made %u changes for a total of %u bytes changed.\n' %
                      (num_recs, num_bytes) )

    if len( e.extra_bytes ) != 0:
        # if there are any bytes after the EOF marker, they better be a
        # truncation indicator and nothing else.  read 1 past the end, just
        # to verify.
        extra_bytes = e.extra_bytes + patch.read( 2 )

        if len( extra_bytes ) != trunc_rec.size:
            sys.stderr.write( "ERROR: Patch file has something other than a 3-byte truncation length after EOF\n"
                              "marker.  Patch file is either corrupt or a version I don't support.  I did the\n"
                              "best I could though.\n" )
            exit( 9 )

        trunc_len_hi, trunc_len_lo = trunc_rec.unpack( extra_bytes )
        trunc_len = (trunc_len_hi << 16) | trunc_len_lo

        try:
            rom.truncate( trunc_len )
        except:
            sys.stderr.write( "ERROR: Failed to truncate ROM file.  Might be OK anyway though.\n" )
            exit( 10 )

        sys.stderr.write( 'Also truncated the ROM to %u bytes as instructed.\n' %
                          trunc_len )
