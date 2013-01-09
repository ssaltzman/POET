#!/usr/bin/python

####################################################################################
#                                                                                  #
# Copyright (c) 2003 Dr. Conan C. Albrecht                                         #
#                                                                                  #
# This file is part of GroupMind.                                                  #
#                                                                                  #
# GroupMind is free software; you can redistribute it and/or modify                #
# it under the terms of the GNU General Public License as published by             #
# the Free Software Foundation; either version 2 of the License, or                # 
# (at your option) any later version.                                              #
#                                                                                  #
# GroupMind is distributed in the hope that it will be useful,                     #
# but WITHOUT ANY WARRANTY; without even the implied warranty of                   #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                    #
# GNU General Public License for more details.                                     #
#                                                                                  #
# You should have received a copy of the GNU General Public License                #
# along with Foobar; if not, write to the Free Software                            #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA        #
#                                                                                  #
####################################################################################
#
# REQUIRES THE PYTHON IMAGE LIBRARY (PIL)!!!  It's not part of standard python.
#
#

from Filer import Filer
from Constants import *
import datagate
import Image
import StringIO, traceback
import StrikeComPlayingBoard

numzoomlevels = StrikeComPlayingBoard.numzoomlevels
thumbnailwidth = StrikeComPlayingBoard.thumbnailwidth

WEB_IMG_TYPES = {
  'image/png':  'PNG',
  'image/jpg':  'JPEG',
  'image/jpeg': 'JPEG',
  'image/jpe':  'JPEG',
  'image/png':  'PNG',
}

class StrikeComBackground(Filer):
  NAME = 'StrikeComBackground'

  def __init__(self):
      Filer.__init__(self)
     
  def send_file_bytes(self, request): 
    '''Sends the file bytes to the browser'''
    try:
      root = datagate.get_item(request.getvalue('global_rootid', ''))
      
      # defaults if this is our first time    
      if not hasattr(request.session, 'zoom'):
        request.session.zoom = numzoomlevels-1
      if not hasattr(request.session, 'panrow'):
        request.session.panrow = 0
      if not hasattr(request.session, 'pancol'):
        request.session.pancol = 0
      
      # create an in-memory image
      img = Image.open(StringIO.StringIO(root.filebytes))
      realwidth, realheight = img.size
      
      # crop and zoom the graphic
      zoom = request.session.zoom
      numrows = int(round((float(zoom) / float(numzoomlevels)) * (float(root.gridrows) - 1))) + 1
      numcols = int(round((float(zoom) / float(numzoomlevels)) * (float(root.gridcols) - 1))) + 1
      panrow = request.session.panrow # topmost row to show
      pancol = request.session.pancol # leftmost col to show
      cellwidth = float(root.gridwidth) / float(root.gridcols)
      cellheight = float(root.gridheight) / float(root.gridrows)
      pixelleft = int(cellwidth * pancol * (realwidth / float(root.gridwidth)))
      pixelright = int(cellwidth * (pancol + numcols) * (realwidth / float(root.gridwidth)))
      pixeltop = int(cellheight * panrow * (realheight / float(root.gridheight)))
      pixelbottom = int(cellheight * (panrow + numrows) * (realheight / float(root.gridheight)))
      zimg = img.transform((int(root.gridwidth), int(root.gridheight)), Image.EXTENT, (pixelleft, pixeltop, pixelright, pixelbottom))
      del img
      
      # send the new image to the browser
      zimg.save(request.out, WEB_IMG_TYPES.get(root.filetype.lower(), 'JPEG'))
      request.out.flush()
      del zimg
      
    except:
      traceback.print_exc()
      raise
    
    
