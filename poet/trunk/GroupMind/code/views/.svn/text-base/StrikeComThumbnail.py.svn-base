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
import Image, ImageDraw
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

def RGB( t ): 
    r, g, b = t 
    return (r<<16) + (g<<8) + b
    
    
class StrikeComThumbnail(Filer):
  NAME = 'StrikeComThumbnail'

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

      # calculate the pixel box area
      zoom = request.session.zoom
      numrows = int(round((float(zoom) / float(numzoomlevels)) * (float(root.gridrows) - 1))) + 1
      numcols = int(round((float(zoom) / float(numzoomlevels)) * (float(root.gridcols) - 1))) + 1
      panrow = request.session.panrow # topmost row to show
      pancol = request.session.pancol # leftmost col to show
      cellwidth = float(root.gridwidth) / float(root.gridcols)
      cellheight = float(root.gridheight) / float(root.gridrows)
      pixelleft = int(cellwidth * pancol)
      pixelright = int(cellwidth * (pancol + numcols))
      pixeltop = int(cellheight * panrow)
      pixelbottom = int(cellheight * (panrow + numrows))

      # calculate the width and height of the thumbnail
      thumbnailheight = int((float(root.gridheight) / float(root.gridwidth)) * thumbnailwidth)
      rimg = img.resize((thumbnailwidth, thumbnailheight))
      del img

      # draw the bounding box for the currently viewable area
      draw = ImageDraw.Draw(rimg)
      for i in range(0, 3):
        draw.rectangle([
          max(0, int(pixelleft * (float(thumbnailwidth) / float(root.gridwidth))) - i, 0),
          max(0, int(pixeltop * (float(thumbnailheight) / float(root.gridheight))) - i, 0),
          min(thumbnailwidth, int(pixelright * (float(thumbnailwidth) / float(root.gridwidth))) + i),
          min(thumbnailheight, int(pixelbottom * (float(thumbnailheight) / float(root.gridheight))) + i)
        ], outline=128)
      del draw
      
      # send the new image to the browser
      rimg.save(request.out, WEB_IMG_TYPES.get(root.filetype.lower(), 'JPEG'))
      request.out.flush()
      del rimg
      
    except:
      traceback.print_exc()
      raise
    
    
