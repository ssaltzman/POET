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

from BaseView import BaseView
from Constants import *
import datagate, GUID

class StrikeComAsset(BaseView):
  NAME = 'StrikeComAsset'
  
  def __init__(self):
    BaseView.__init__(self)


  def send_content(self, request):
    '''Shows the main Asset window to the user (allows creating of assets)'''
    if request.getvalue('subaction', '') == 'close' and not hasattr(request, 'error'):
      self.send_close(request)
    else:
      self.send_asset_form(request)
      
      
      
  def send_close(self, request):
    # the submit form in the send_asset_form method below submits and then 
    # reloads this form.  Rather than messing with javascript to submit and
    # then close, I send a subaction='close' parameter in the form.  When this
    # parameter comes in (on the submission and then reload of the page), I
    # close the form and cause the parent to reload.
    request.writeln(HTML_HEAD_NO_CLOSE)
    request.writeln('''
      <script language='JavaScript' type='text/javascript'>
        window.opener.location.href = "''' + request.cgi_href(view='Administrator', global_adminview="StrikeCom") + '''";
        window.close();
      </script>
      </head>
      <body></body></html>
   ''')    
      
      
  def send_asset_form(self, request):
    game = datagate.get_item(request.getvalue('global_rootid'))
    asset = None
    if request.getvalue('assetid', ''): # are we editing?
      asset = datagate.get_item(request.getvalue('assetid', ''))
    request.writeln(HTML_HEAD)
         #x -done (-1)
         #y -done (-1)
         #width -done
         #height -done
         #Ability to move (how many spaces can it move from it's last know position) - int
         #Visibility by players (list of user ids and group ids that can see this item)
         #Movability by players (list of user ids and group ids that can move this item)
         #Ability to see beyond my cell (range of cells around the asset that it can see.  Visibility width and height) 
            #4 things:
                #above/below right/left
         #Strike strength (int - 0 thru 10) Done
         #Defense strength (int - 0 thru 10) Done
         #
         #Image bytes -to be done by Conan
         #Acceptable terrain type (list of strings that we created) - Done

    request.writeln(HTML_BODY)
    
    board = game.search1(name='board') #get the board
    board_cols = board.getvalue('gridcols','') #get the number of cols and rows for the 'terrain+row-col+' getvalue call
    board_rows = board.getvalue('gridrows','')

    #loop the terrainsROW-COL attributes of the board and pull the uniques out - we only need each terrain once
    board_terrains = []
    for row in range(int(board_cols)):
        for col in range(int(board_rows)):
            terrain = board.getvalue('terrain'+str(row)+'-'+str(col),'')
            if terrain not in board_terrains:
                if terrain != None:
                    board_terrains.append(terrain)

    request.writeln(request.cgi_multipart_form(gm_action="StrikeComAsset.newasset", subaction="close", name=None, row=None, col=None, width=None, height=None, assetid=asset and asset.id or ''))
    request.writeln('''
      <p>''' + (asset == None and 'New' or 'Edit') + ''' Asset:</p>
      ''' + (hasattr(request, 'error') and request.error or '') + '''
      <center>
      <table border=0 cellspacing=0 cellpadding=3>
      <tr>
        <td valign="top">Name:</td>
        <td valign="top"><input type="text" size="20" name="name" value="''' + (asset and asset.name or '') + '''"></td>
      </tr><tr>
        <td valign="top">Location:</td>
        <td valign="top">Row:<input type="text" size="5" name="row" value="''' + (asset and asset.row or '-1') + '''"> Column:<input type="text" size="5" name="col" value="''' + (asset and asset.col or '-1') + '''"></td>
      </tr><tr>
        <td valign="top">Size:</td>
        <td valign="top">Height:<input type="text" size="5" name="height" value="''' + (asset and asset.height or '1') + '''"> Width:<input type="text" size="5" name="width" value="''' + (asset and asset.width or '1') + '''"></td>
      </tr><tr>
      </tr><tr>
        <td valign="top">Strengths:</td>
        <td valign="top">Striking: <select name="_striking" size="1">
    ''')
    strike_strength = asset and asset.striking or '1'
    for x in range(1,11) :
        if x == int(strike_strength):
            request.writeln('<option value="'+str(x)+'" selected>'+str(x)+'</option>')
        else:
            request.writeln('<option value="'+str(x)+'">'+str(x)+'</option>')
    request.writeln('''
        </select>
    Defensive: <select name="_defensive" size="1">
    ''')
    defense_strength = asset and asset.defensive or '1'
    for x in range(1,11) :
        if x == int(defense_strength):
            request.writeln('<option value="'+str(x)+'" selected>'+str(x)+'</option>')
        else:
            request.writeln('<option value="'+str(x)+'">'+str(x)+'</option>')
    request.writeln('''
        </select></td>
        </tr><tr>
        <td valign="top">Recon:</td>
        <td valign="top">
          Sight: 
          <select name="_sight">
    ''')
    sight = asset and asset.sight or '1'
    for x in range(1,11) :
        if x == int(sight):
            request.writeln('<option value="'+str(x)+'" selected>'+str(x)+'</option>')
        else:
            request.writeln('<option value="'+str(x)+'">'+str(x)+'</option>')
    request.writeln('''
          </select>
          Visibility:
          <select name="_visibility">
    ''')
    visibility = asset and asset.visibility or '1'
    for x in range(1,11) :
        if x == int(visibility):
            request.writeln('<option value="'+str(x)+'" selected>'+str(x)+'</option>')
        else:
            request.writeln('<option value="'+str(x)+'">'+str(x)+'</option>')
    request.writeln('''  
          </select>
        </td>
        </tr><tr>
        <td valign="top">Terrain type:</td>
        <td valign="top">
           <select name="_terrains" multiple>
    ''')

    
    for terrain in board_terrains:
      log.debug(str(terrain))
      try:
        asset.terrains.index(terrain)
        request.writeln('<option selected value="' + terrain + '">' + html(terrain) + '</option>')
      except (ValueError, AttributeError):
        request.writeln('<option value="' + terrain + '">' + html(terrain) + '</option>')           

    request.writeln('''
        </select>
        </td>
        </tr><tr>
        <td valign="top">Icon:</td>
        <td valign="top">
    ''')

    if asset:
      request.writeln('<div><img src="'''+ request.cgi_href(view="Filer", global_rootid=asset.id, gm_contenttype=asset.filetype) + '"></div>')
      request.writeln('''
          </td>
        </tr><tr>
          <td valign="top"><div>Change Icon:</td>
          <td valign="top">
      ''')
      request.writeln('<input type="file" size="20" name="_icon"></div>')
    else:
      request.writeln('<input type="file" size="20" name="_icon">')
    request.writeln('''
        </td>
      </tr>
      </table>
      <input type="submit" value="'''+(asset == None and 'Submit' or 'Update')+'''">
      </center>
      </form>

      </body></html>
    ''')


    
  ################################
  ###   Actions
  
  def newasset_action(self, request):
    '''Adds the new asset to the board'''
    if request.getvalue('assetid', ''): # editing
      asset = datagate.get_item(request.getvalue('assetid', ''))
    else: # new item
      game = datagate.get_item(request.getvalue('global_rootid'))
      turns = game.search1(name='turns')
      fileitem = request.form['_icon']
      if not fileitem.filename:
        request.error = 'Assets must have an associated icon.'
        return
      zeroTurn = turns.get_child(turns.childids[0]).search1(name='assetmoves')
      asset = datagate.create_item(parentid=zeroTurn.id, creatorid=request.session.user.id)
      asset.filename = ''
    asset.assetid = GUID.generate()
    asset.name = request.getvalue('name', '')
    asset.width = request.getvalue('width', '')
    asset.height = request.getvalue('height', '')
    asset.row = request.getvalue('row', '')
    asset.col = request.getvalue('col', '')
    asset.striking = request.getvalue('_striking')
    asset.defensive = request.getvalue('_defensive')
    asset.sight = request.getvalue('_sight')
    asset.visibility = request.getvalue('_visibility')
    asset.terrains = request.getlist('_terrains')

    asset.visible_by=[]
    
    asset.move_by=[]
    fileitem = request.form['_icon']
    if fileitem.filename:
      asset.filebytes = fileitem.file.read()
      asset.filetype = fileitem.type
      asset.filename = fileitem.filename
    asset.save()
