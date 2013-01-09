#!/usr/bin/python

"""

TextFile.py : a module that provides a UniversalTextFile class, and a
replacement for the native python "open" command that provides an
interface to that class.

It would usually be used as:

from TextFile import open

then you can use the new open just like the old one (with some added flags and arguments)

or

import TextFile

file = TextFile.open(filename,flags,[bufsize], [LineEndingType], [LineBufferSize])

please send bug reports, helpful hints,  and/or feature requests to:

Chris Barker ChrisHBarker@home.net Copyright/licence is the same as whatever version of python you are running.

"""
import os

## Re-map the open function
_OrigOpen = open

def open(filename,flags = "rt",bufsize = -1, LineEndingType = "", LineBufferSize = ""):
    """
    
    A new open function, that returns a regular python file object for
    the old calls, and returns a new nifty universal text file when
    required.

    This works just like the regular open command, except that a new
    flag and a new parameter has been added.

    The new flag is "t" which indicates that the file to be opened is a
    universal text file. While the standard open() function defaults to
    a text file, on Posix systems, there is no difference between a text
    file and binary fiole so there is a lot of code out there that opens
    files as text, when a binary file is really required. This code
    currently works just fine on Posix systems, so it was neccessary to
    introduce a new flag, to maintian backward compatabilty. The old
    style, line ending dpeendent text file with also provide better
    performance.
    

    To Call:

    file = open(filename,flags = "",bufsize = -1, LineEndingType = ""):

    - filename is the name of the file to be opened
    - flags is a string of one letter flags, the same as the standard open
      command, plus a "t" for universal text file.
    - - "b" means binary file, this returns the standard binary file object
    - - "t" means universal text file
    - - "r" for read only
    - - "w" for write. If there is both "w" and "t" than the user can
        specify a line ending type to be used with the LineEndingType
        parameter.
    - - "a" means append to existing file

    - bufsize specifies the buffer size to be used by the system. Same
      as the regular open function

    - LineEndingType is used only for writing (and appending) files, to specify a
      non-native line ending to be written.
    - - The options are: "native", "DOS", "Posix", "Unix", "Mac", or the
        characters themselves( "\r\n", etc. ). "native" will result in
        using the standard file object, which uses whatever is native
        for the system that python is running on.

    - LineBufferSize is the size of the buffer used to read data in
    a readline() operation. The default is currently set to 200
    characters. If you will be reading files with many lines over 200
    characters long, you should set this number to the largest expected
    line length.

    NOTE: I'm sure the flag checking could be more robust.
    
    """

    if "t" in flags: # this is a universal text file
        if ("w" in flags) and (not "w+" in flags) and LineEndingType == "native":
            return _OrigOpen(filename,flags.replace("t",""), bufsize)
        return UniversalTextFile(filename,flags,LineEndingType,LineBufferSize)
    else: # this is a regular old file
        return _OrigOpen(filename,flags,bufsize)
    
    
class UniversalTextFile:
    """
    
    A class that acts just like a python file object, but has a mode
    that allows the reading of arbitrary formated text files, i.e. with
    either Unix, DOS or Mac line endings. [\n , \r\n, or \r]

    To keep it truly universal, it checks for each of these line ending
    possibilities at every line, so it should work on a file with mixed
    endings as well.

    """
    def __init__(self,filename,flags = "rt",LineEndingType = "native",LineBufferSize = ""):
        self._file = _OrigOpen(filename,flags.replace("t","")+"b")

        LineEndingType = LineEndingType.lower()
        if LineEndingType == "native":
            self.LineSep = os.linesep
        elif LineEndingType == "dos" or LineEndingType == 'windows':
            self.LineSep = "\r\n"
        elif LineEndingType == "posix" or LineEndingType == "unix" :
            self.LineSep = "\n"
        elif LineEndingType == "mac" or LineEndingType == 'macintosh':
            self.LineSep = "\r"
        else:
            self.LineSep = LineEndingType
        
        ## some attributes
        self.closed = 0
        self.mode = flags
        self.softspace = 0
        if LineBufferSize:
            self._BufferSize = LineBufferSize
        else:
            self._BufferSize = 100

    def readline(self):
        start_pos = self._file.tell()
        ##print "Current file posistion is:", start_pos
        line = ""
        TotalBytes = 0
        Buffer = self._file.read(self._BufferSize)
        while Buffer:
            ##print "Buffer = ",repr(Buffer)
            newline_pos = Buffer.find("\n")
            return_pos  = Buffer.find("\r")
            if return_pos == newline_pos-1 and return_pos >= 0: # we have a DOS line
                line = Buffer[:return_pos]+ "\n"
                TotalBytes = newline_pos+1
                break
            elif ((return_pos < newline_pos) or newline_pos < 0 ) and return_pos >=0: # we have a Mac line
                line = Buffer[:return_pos]+ "\n"
                TotalBytes = return_pos+1
                break
            elif newline_pos >= 0: # we have a Posix line
                line = Buffer[:newline_pos]+ "\n"
                TotalBytes = newline_pos+1
                break
            else: # we need a larger buffer
                NewBuffer = self._file.read(self._BufferSize)
                if NewBuffer:
                    Buffer = Buffer + NewBuffer
                else: # we are at the end of the file, without a line ending.
                    self._file.seek(start_pos + len(Buffer))
                    return Buffer

        self._file.seek(start_pos + TotalBytes)
        return line

    def readlines(self,sizehint = None):
        """

        readlines acts like the regular readlines, except that it
        understands any of the standard text file line endings ("\r\n",
        "\n", "\r").

        If sizehint is used, it will read a a maximum of that many
        bytes. It will never round up, as the regular readline sometimes
        does. This means that if your buffer size is less than the
        length of the next line, you'll get an empty string, which could
        incorrectly be interpreted as the end of the file.

        """
        
        if sizehint:
            Data = self._file.read(sizehint)
        else:
            Data = self._file.read()

        if len(Data) == sizehint:
            #print "The buffer is full"
            FullBuffer = 1
        else:
            FullBuffer = 0
        Data = Data.replace("\r\n","\n").replace("\r","\n")
        Lines = [line + "\n" for line in Data.split('\n')]
        ## If the last line is only a linefeed it is an extra line
        if Lines[-1] == "\n":
            del Lines[-1]
        ## if it isn't then the last line didn't have a linefeed, so we need to remove the one we put on.
        else:
            ## or it's the end of the buffer
            if FullBuffer:
                self._file.seek(-(len(Lines[-1])-1),1) # reset the file position
                del(Lines[-1])
            else:
                Lines[-1] = Lines[-1][:-1]
        return Lines

    def readnumlines(self,NumLines = 1):
        """

        readnumlines is an extension to the standard file object. It
        returns a list containing the number of lines that are
        requested. I have found this to be very useful, and allows me
        to avoid the many loops like:

        lines = []
        for i in range(N):
            lines.append(file.readline())

        Also, If I ever get around to writing this in C, it will provide a speed improvement.

        """
        Lines = []
        while len(Lines) < NumLines:
            Lines.append(self.readline())
        return Lines

    def read(self,size = None):
        """
     
        read acts like the regular read, except that it tranlates any of
        the standard text file line endings ("\r\n", "\n", "\r") into a
        "\n"
        
        If size is used, it will read a maximum of that many bytes,
        before translation. This means that if the line endings have
        more than one character, the size returned will be smaller. This
        could be fixed, but it didn't seem worth it. If you want that
        much control, use a binary file.
      
        """
        
        if size:
            Data = self._file.read(size)
        else:
            Data = self._file.read()
            
        return Data.replace("\r\n","\n").replace("\r","\n")
    
    def write(self,string):
        """

        write is just like the regular one, except that it uses the line
          separator specified when the file was opened for writing or
          appending.


        """
        self._file.write(string.replace("\n",self.LineSep))

    def writelines(self,list):
        for line in list:
            self.write(line)
        

    # The rest of the standard file methods mapped
    def close(self):
        self._file.close()
        self.closed = 1
    def flush(self):
        self._file.flush()
    def fileno(self):
        return self._file.fileno()
    def seek(self,offset,whence = 0):
        self._file.seek(offset,whence)
    def tell(self):
        return self._file.tell() 