#!/usr/bin/python

import BaseView
from Constants import *
import datagate
import Directory
import sys

class StrikeCom(BaseView.BaseView):
  NAME = 'StrikeCom'

  def __init__(self):
    BaseView.BaseView.__init__(self)
    self.interactive = 1
    
     
  ########################################
  ###   View methods
  
  def send_content(self, request):
    # ensure the session has the neccesary attributes for StrikeCom panels
    if not hasattr(request.session, 'viewturn'):
      request.session.viewturn = 1
      
    if request.getvalue('subview', '') == 'game':
      self.send_game(request)
    elif request.getvalue('subview', '') == 'navigation':
      self.send_navigation(request)
    else:
      self.send_main_frames(request)
      

  def send_main_frames(self, request):
    # get the game objects
    game = datagate.get_item(request.getvalue('global_rootid'))
    teams = game.search1(name='groups')
    team = Directory.get_group(game.id, request.session.user.id)
    if not team:
      raise 'You have not been added to a team in this game.'
    try: 
      chats = game.search1(name='chats') # just use first team's chat for now -- eventually we want to see what team the user is on and link to the chat parent for that team
    except IndexError:
      raise 'You cannot play a StrikeCom game without any teams.  Please add at least one team and try again.'
    chat = chats.search1(name=team.name)
    board = game.search1(name='board')
    turns = game.search1(name='turns')
    
    # send the html
    request.writeln(HTML_HEAD_NO_CLOSE)
    request.writeln('''
      </head>
      <frameset border="0" rows="45,*">
        <frame marginheight="0" marginwidth="0" scrolling="no" name="navigation" src="''' + request.cgi_href(subview='navigation') + '''">
        <frame marginheight="0" marginwidth="0" scrolling="no" name="game" src="''' + request.cgi_href(subview='game') + '''">
      </frameset>
      </html>
    ''')


  def send_navigation(self, request):
    game = datagate.get_item(request.getvalue('global_rootid'))
    turns = game.search1(name='turns')

    request.writeln(HTML_HEAD_NO_CLOSE)
    request.writeln('''
      <script language='JavaScript' type='text/javascript'>
        function changeturn(turnnum) {
          window.parent.game.location.href = "''' + request.cgi_href(subview='game', turnnum=None) + '''&turnnum=" + turnnum;
        }

      </script>
    ''')
    request.writeln('</head>')
    request.writeln('<body bgcolor="#12255D" bottommargin="4" topmargin="4" leftmargin="4" rightmargin="4">')
    request.writeln('<table border=0 cellspacing=0 cellpadding=0 width="100%"><tr>')
    request.writeln('<td valign="middle" style="color:#CCC" align="left" width="20%"><img src="/strikecom/bullseye.png" border="0"></td>')
    request.writeln('<td valign="middle" style="color:#CCC" align="center" width="60%">')
    request.writeln('Turn:')
    request.writeln('<select name="currentturn" onchange="changeturn(this.value)">')
    request.writeln('<option value="0">Pregame</option>')
    allturns = turns.get_child_items()
    for i in range(1, turns.totalturns+1):
      request.writeln('<option value="' + str(i) + '">' + str(i) + '</option>')
    request.writeln('</select>')
    request.writeln('/')
    request.writeln(str(turns.totalturns))
    request.writeln('<td valign="middle" style="color:#CCC" align="right" width="20%"><a href="http://www.cmi.arizona.edu"><img src="/strikecom/cmi.jpg" border=0></a></td>')
    request.writeln('</tr></table>')
    request.writeln('</body></html>')
    
      
  def send_game(self, request):
    '''Shows the game window'''
    # get the game objects
    game = datagate.get_item(request.getvalue('global_rootid'))
    teams = game.search1(name='groups')
    team = Directory.get_group(game.id, request.session.user.id)
    if not team:
      raise 'You have not been added to a team in this game.'
    try: 
      chats = game.search1(name='chats') # just use first team's chat for now -- eventually we want to see what team the user is on and link to the chat parent for that team
    except IndexError:
      raise 'You cannot play a StrikeCom game without any teams.  Please add at least one team and try again.'
    chat = chats.search1(name=team.name)
    board = game.search1(name='board')
    turns = game.search1(name='turns')

    request.writeln(HTML_HEAD)
    request.writeln('''
      <frameset border="0" cols="*,200">  
        <frameset border="0" rows="*,50">
          <frame marginheight="0" marginwidth="0" name="playingboard" src="''' + request.cgi_href(global_rootid=turns.id, view='StrikeComPlayingBoard', frame=None) + '''">
          <frame scrolling="no" marginheight="0" marginwidth="0" name="legend" src="''' + request.cgi_href(view='StrikeComLegend', frame=None) + '''">
        </frameset>
        <frame scrolling="no" marginheight="0" marginwidth="0" name="chat" src="''' + request.cgi_href(global_rootid=chat.id, view='StrikeComCommenter', frame=None) + '''">
      </frameset>
    ''')    

     
    
  #######################################
  ###   Administrator methods
  
  def initialize_activity(self, request, game):
    '''Called from the Administrator when this game is created.  Sets up the initial items in the tree.'''
    BaseView.BaseView.initialize_activity(self, request, game)
    
    # set up the first level objects
    for childname in [ 'chats', 'board', 'turns' ]:
      child = datagate.create_item(creatorid=request.session.user.id, parentid=game.id)
      child.name = childname
      child.save()
      
    # set up the playing board
    board = game.search1(name='board')
    board.gridrows = '3'
    board.gridcols = '3'
    for r in range(int(board.gridrows)):
        for c in range(int(board.gridcols)):
            cell = 'terrain' + str(r) + '-' + str(c)
            setattr(board, cell, 'Default')
            #setattr(board, cell, request.getvalue(cell, 'Default'))
    board.gridheight = '500'
    board.gridwidth = '500'
    board.filename = ''
    board.save()
    
    # set up the turns
    turns = game.search1(name="turns")
    turns.totalturns = 5
    turns.currentturn = 0
    turns.save()
    self.ensure_enough_turns(request, turns)
    

  def send_admin_page(self, request):
    '''Shows the administrator page for this view. (when the user clicks Edit in the administrator)'''
    # get the game objects
    game = datagate.get_item(request.getvalue('itemid'))
    teams = game.search1(name='groups')
    board = game.search1(name='board')
    turns = game.search1(name='turns')
    
    # toc
    request.writeln('Strikecom Setup:')
    request.writeln('<ul>')
    request.writeln('<li><a href="#general">General Setup</a></li>')
    request.writeln('<li><a href="#assets">Assets</a></li>')
    request.writeln('<li><a href="#teams">Game Teams</a></li>')
    request.writeln('<li><a href="#board">Playing Board</a></li>')
    request.writeln('</ul>')
    
    ##### Strikecom General Setup #####
    request.writeln('<a name="general"></a><h1>General Setup:</h1>')
    request.writeln(request.cgi_form(gm_action='StrikeCom.numturns', totalturns=None))
    request.writeln('<div>Total number of turns: <input type="text" size="10" value="' + str(turns.totalturns) + '" name="totalturns"></div>')
    request.writeln('<div align="center"><input type="submit" value="Save"></div>')
    request.writeln('</form>')


    ##### Strikecom Assets Setup #####

    zeroTurn = turns.get_child(turns.childids[0]).search1(name='assetmoves')
    assets = zeroTurn.get_child_items()
    
    request.writeln('<a name="assets"></a><h1>Asset Setup:</h1>')        
        
    if len(teams.get_child_items()) == 0:
      request.writeln('Please add at least one team before setting up assets.')
    else:
      request.writeln(request.cgi_form(view='AssetLibraryExporter', global_meetingid=game.id, gm_contenttype='application/x-gzip',contentdisposition="AssetLibrary.gz"))
      request.writeln('<div align="center"><input type="button" value="Create Asset" onclick="window.open(\'' + request.cgi_href(global_rootid=game.id, view='StrikeComAsset', assetid=None) + '\',\'blah\',\'width=400,height=400\')">')
      if len(assets) > 0:
        request.writeln('<input type="submit" value="Export Assets">')
      request.writeln('</form>')
      request.writeln(request.cgi_multipart_form(action = 'AssetLibraryExporter.assetimporter', global_meetingid=game.id))
      request.writeln('Import Asset Library: <input type="file" size="20" name="_assetlibrary">')
      request.writeln('<input type="submit" value="Import Assets"></form>')
        

      request.writeln('''</div>''')
      request.writeln('<center>')
      request.writeln('''
       <table border=1 cellspacing=0 cellpadding=5>
          <tr id="headers">
            <th>Asset Icon</th>
            <th>Name</th>
            <th>Actions</th>
            <th>Team</th>
            <th>Assignments</th>
          </tr>
      ''')
     
      # since assets are multiple times in the tree, we need to boil it
      # down to the last instance of the asset in the tree
      assets.reverse()
      unique = {}
      for asset in assets :
        if asset.assetid not in unique:
          unique[asset.assetid]=asset
      assets = unique.values()
  
      assets.sort(lambda a,b: cmp(a.name.lower(), b.name.lower()))
      ctr=0
      for asset in assets:
          request.writeln('''
              <tr name="asset_row'''+str(ctr)+'''" id="asset_row'''+str(ctr)+'''"><td>
          ''')
          if asset.filename:
            request.writeln('<img src="'''+ request.cgi_href(view="Filer", global_rootid=asset.id, gm_contenttype=asset.filetype) + '">')
          else:
            request.writeln('&nbsp;')
          request.writeln('</td><td>')
          request.writeln(str(asset.name))
          request.writeln('</td>')
         
          request.writeln('<td align="center" id="actions_td'+str(ctr)+'">') #note if you don't add the ctr var at the end it isn't unigue and weird things happen.
          request.writeln('<a href="#" onclick="window.open(\'' + request.cgi_href(global_rootid=game.id, view='StrikeComAsset', assetid=asset.id) + '\',\'blah\',\'width=400,height=800\')">Edit</a>')
          request.writeln('|')
          request.writeln('<a href="' + request.cgi_href(global_meetingid=game.id, itemid=game.id, gm_action='StrikeCom.delasset', assetid = asset.id, assetname=asset.name) + '">Delete</a>');
          request.writeln('</td><td>')
          
          # team assigned to this asset
          request.writeln(request.cgi_form(gm_action='StrikeCom.assetteam', global_meetingid=game.id, _assetid=asset.id))
          request.writeln('<select name="_teamid" onchange="this.form.submit()">')
          if asset.getvalue('teamid', '') == '':  # make sure this asset is assigned a team
            asset.teamid = teams[0].id
            asset.save()
          for group in teams:
            selected = group.id == asset.teamid and ' selected' or ''
            request.writeln('<option ' + selected + ' value="' + group.id + '">' + group.name + '</option>')
          request.writeln('</select>')        
          request.writeln('</form>')
          
          # team member rights in this asset
          request.writeln('</td><td>')        
          request.writeln(request.cgi_form(gm_action='StrikeCom.assignasset', global_meetingid=game.id, id='assignform', _itemid=asset.id, _assetid=asset.assetid))
          request.writeln('''<table border=1 cellspacing=0 cellpadding=5 id='new_table' id='new_table'>''')
          group = datagate.get_item(asset.teamid)
          
          if group == None:
            group = teams.get_child_items()[0]
          group_ctr = 1
          request.writeln('''<tr><td align='left'>&nbsp;</td><td align='center'><b> <a href='#asset_row' onclick=switchCheckBoxes('see_check'''+str(ctr)+''+str(group_ctr)+'''')>See</a> : <a href='#asset_row' onclick=switchCheckBoxes('move_check'''+str(ctr)+''+str(group_ctr)+'''')>Move</a></b></td></tr>''')
          user_ctr=0
          for member in group:
              user = Directory.get_user(member.user_id) #user is the actual user object.  member is the child of a group
              request.writeln('''<tr><td align='right'>'''+user.name+'''</td>''')
              try:
                  asset.visible_by.index(user.id)
                  request.writeln('''<td align='left'>&nbsp;&nbsp;<input id="see_check'''+str(ctr)+""+str(group_ctr)+""+str(user_ctr)+'''" name="_'''+str(user.id)+''':see"  value='on' checked type='checkbox'> : ''')                    
              except ValueError: #not in the asset yet --> no check                   
                  request.writeln('''<td align='left'>&nbsp;&nbsp;<input id="see_check'''+str(ctr)+""+str(group_ctr)+""+str(user_ctr)+'''" name="_'''+str(user.id)+''':see"  value='on' type='checkbox'> : ''')
              
              try:
                  asset.move_by.index(user.id)
                  request.writeln('''<input id='move_check'''+str(ctr)+""+str(group_ctr)+""+str(user_ctr)+'''' name="_'''+str(user.id)+''':move" value='on' checked type='checkbox'></td></tr>''')
              except ValueError: #not in the asset yet --> no check                   
                  request.writeln('''<input id='move_check'''+str(ctr)+""+str(group_ctr)+""+str(user_ctr)+'''' name="_'''+str(user.id)+''':move" value='on' type='checkbox'></td></tr>''')
              
              user_ctr=user_ctr+1
                          
          request.writeln('''
              <tr><td>&nbsp;</td><td><input type='submit' value='Assign'></td></tr></table></form>
          </tr>''')
          ctr=ctr+1
      
      request.writeln('</table>')
      request.writeln('</center>')
      
  

    ##### Strikecom Teams #####
    request.writeln('<a name="teams"></a><h1>Game Teams:</h1>')
    # groups in this meeting
    groups = datagate.get_child_items(teams.id)
    allusers = Directory.get_users()
    allusers.sort(lambda a,b: cmp(a.username, b.username))
    request.writeln('''
      <script language='JavaScript' type='text/javascript'>
      <!--
        var old_td;
        var old_index = -1;
        var assetindex;
        
        function addTeam() {
          var text = prompt("New Team Name:");
          if (text != null && text != '') {
            text = encode(text);
            window.location.href = "''' + request.cgi_href(global_meetingid=game.id,gm_action='StrikeCom.addgroup', itemid=game.id, name=None) + '''&name=" + text + "#teams";
          }
        }
        function switchCheckBoxes(switch_id)
        {
        //Conan can be changed to work differently.  Other than just ! the boxes 
            var mode = 'move';
            if(switch_id.indexOf('see')!=-1)
            {
               mode = 'see';
            }
            
            var ctr = 0;
            var boxes = document.getElementById(switch_id+""+ctr);
            while(boxes!=null)
            {
             boxes.checked = !boxes.checked;
             
             ctr++;
             boxes = document.getElementById(switch_id+""+ctr);
            }
            
            
        }
      //-->
      </script>
      <center>
      <div align="right"><a href="javascript:addTeam()">Add New Team</a></div>
      <table border=1 cellspacing=0 cellpadding=5>
        <tr>
          <th>Team Name</th>
          <th>Users</th>    
          <th>Actions</th>
        </tr>
    ''')
    for group in groups:
      groupusers = [ Directory.get_user(child.user_id) for child in group]
      groupusers.sort(lambda a,b: cmp(a.username, b.username))
      request.writeln('<tr>')
      request.writeln('<td valign="top">' + html(group.name) + '</td>')
      request.writeln('<td>')
      request.writeln(request.cgi_form(gm_action='StrikeCom.groupusers', global_meetingid=game.id, allusers=None, groupusers=None, groupid=None))
      request.writeln('<input type="hidden" name="groupid" value="' + group.id + '">')
      request.writeln('<table border=0 cellspacing=0 cellpadding=0><tr><td>')
      request.writeln('All Users:<br>')
      request.writeln('<select size="5" name="allusers" multiple>')
      for user in allusers:
        if not user in groupusers:
          request.writeln('<option value="' + user.id + '">' + html(user.name) + '</option>')
      request.writeln('</select>')
      request.writeln('</td><td>')
      request.writeln('<p><input type="submit" value="->" name="submit"></p>')
      request.writeln('<p><input type="submit" value="<-" name="submit"></p>')
      request.writeln('</td><td>')
      request.writeln('Team Members:<br>')
      request.writeln('<select size="5" name="members" multiple>')
      for user in groupusers:
        request.writeln('<option value="' + user.id + '">' + html(user.name) + '</option>')
      request.writeln('</select>')
      request.writeln('</td></tr></table>')
      request.writeln('</form>')
      request.writeln('</td>')
      
      request.writeln('''<td valign="top"><a href="javascript:confirm_url('Delete this team and remove users from the game?', \'''' + request.cgi_href(global_meetingid=game.id, itemid=game.id, gm_action='StrikeCom.delgroup', groupid = group.id, groupname = group.name, allusers=None, groupusers=None) + '''\');">Delete</td>''')
      request.writeln('</tr>')
    request.writeln('''
      </table>
      </center>
    ''')    
    

    #####  Strikecom Playing Board #####
    kargs = {'action':'StrikeCom.boardsetup', 'gridrows':None, 'gridcols':None, 'backgroundfile':None, 'gridheight':None, 'gridwidth':None}
    for r in range(int(board.gridrows)):
      for c in range(int(board.gridcols)):
        cell = 'terrain' + str(r) + '-' + str(c)
        kargs[cell] = None
    
    request.writeln('''
      <a name="board"></a><h1>Playing Board:</h1>
      <center>
      ''' + request.cgi_multipart_form(**kargs) + '''
      <table border=0 cellspacing=10>
        <tr>
          <td>Grid:</td>
          <td><input type="text" size="5" name="gridrows" value="''' + board.gridrows + '''"> rows by <input type="text" size="5" name="gridcols" value="''' + board.gridcols + '''"> columns</td>
        </tr><tr>
          <td>Size in Pixels:</td>
          <td><input type="text" size="5" name="gridheight" value="''' + board.gridheight + '''"> pixels high by <input type="text" size="5" name="gridwidth" value="''' + board.gridwidth + '''"> pixels wide</td>
        </tr><tr>
          <td valign="top">Background Image:</td>
          <td valign="top">
     ''')
    if board.filename:
      request.writeln('''<img src="''' + request.cgi_href(view="Filer", global_rootid=board.id, gm_contenttype=board.filetype) + '''" width="90" height="90"></div>''')     
    request.writeln('''
            <div>Change Image: <input type="file" size="20" name="_backgroundfile"></div>
            <div>(note that you must have a background image to enable zooming)</div>
          </td>
        </tr>
      </table>
    ''')
    request.writeln('Terrain type for each cell:</b>')
    width = str(round(float(board.gridwidth) / float(board.gridcols)))
    height = str(round(float(board.gridheight) / float(board.gridrows)))
    if board.filename:
      request.writeln('<table border=1 cellspacing=0 cellpadding=0 background="' + request.cgi_href(view="Filer", global_rootid=board.id, gm_contenttype=board.filetype) + '">')
    else:
      request.writeln('<table border=1 cellspacing=0 cellpadding=0>')
    for r in range(int(board.gridrows)):
      request.writeln('<tr>')
      for c in range(int(board.gridcols)):
        cell = 'terrain' + str(r) + '-' + str(c)
        request.write('<td valign="top" align="left" width="' + width + '" height="' + height + '">')
        request.write('<input type="text" name="' + cell + '" size="8" value="' + board.getvalue(cell, '') + '">')
        request.writeln('</td>')
      request.writeln('</tr>')

    request.writeln('''
      </table>
    ''')
    
    request.writeln('''
      <input type="submit" value="Save Board Setup">
      </form>
      </center>
    ''')
    
  #############################################
  ###   Administrator actions

  def boardsetup_action(self, request):
    game = datagate.get_item(request.getvalue('itemid'))
    teams = game.search1(name='groups')
    chats = game.search1(name='chats')
    board = game.search1(name='board')
    board.gridrows = request.getvalue('gridrows' ,'');
    board.gridcols = request.getvalue('gridcols', '');
    board.gridheight = request.getvalue('gridheight', '');
    board.gridwidth = request.getvalue('gridwidth', '');
    for r in range(int(board.gridrows)):
      for c in range(int(board.gridcols)):
        cell = 'terrain' + str(r) + '-' + str(c)
        setattr(board, cell, request.getvalue(cell, ''))
    fileitem = request.form['_backgroundfile']
    if fileitem.filename:
      board.filebytes = fileitem.file.read()
      board.filetype = fileitem.type
      board.filename = fileitem.filename
    board.save()
    
    
  def addgroup_action(self, request):
    game = datagate.get_item(request.getvalue('itemid'))
    teams = game.search1(name='groups')
    chats = game.search1(name='chats')
    board = game.search1(name='board')
    name = request.getvalue('name', '')
    if name:
      group = datagate.create_item(creatorid=request.session.user.id, parentid=teams.id)
      group.name = name
      group.save()
      

      teamchat = datagate.create_item(creatorid=request.session.user.id, parentid=chats.id)
      teamchat.name = name
      teamchat.save()
      BaseView.get_view('strikecomcommenter').initialize_activity(request, teamchat)
      
      
  def delgroup_action(self, request):
    game = datagate.get_item(request.getvalue('itemid'))
    turns = game.search1(name='turns')
    groupid = request.getvalue('groupid')
    group = datagate.get_item(groupid)
    # go through the assets for this group and delete any assets who were in this group
    for turn in turns:
      for asset in turn.search1(name='assetmoves'):
        if asset.teamid == groupid:
          asset.delete()
    datagate.del_item(request.getvalue('groupid', ''))
    game = datagate.get_item(request.getvalue('itemid'))
    chats = game.search1(name='chats')
    group_name = request.getvalue('groupname','')
    group_chat = chats.search1(name=group_name)
    datagate.del_item(group_chat.id)


  def delasset_action(self, request):
    game = datagate.get_item(request.getvalue('itemid'))
    turns = game.search1(name='turns')
    for turn in turns:
      moves = turn.search1(name='assetmoves')
      for asset in moves:
        if asset.assetid == request.getvalue('assetid'):
          asset.delete()
          try:
            delattr(turn,"committedasset_"+asset.assetid) # remove them from the committedassets for all turns
          except AttributeError:
            pass
          

  def groupusers_action(self, request):
    game = datagate.get_item(request.getvalue('itemid'))
    teams = game.search1(name='groups')
    chats = game.search1(name='chats')
    board = game.search1(name='board')
    submit = request.getvalue('submit', '')
    group = teams.get_child(request.getvalue('groupid', ''))
    if submit == '->':
      group_users = [ child.user_id for child in group.get_child_items() ]
      for user_id in request.getlist('allusers'):
        if not user_id in group_users:
          child = datagate.create_item(creatorid=request.session.user.id, parentid=group.id)
          child.user_id = user_id
          child.save()  
    elif submit == '<-':
      for user_id in request.getlist('members'):
        for child in group.get_child_items():
          if child.user_id == user_id:
            datagate.del_item(child.id)
            break


  def assetteam_action(self, request):
    game = datagate.get_item(request.getvalue('itemid'))
    teams = game.search1(name='groups')
    asset_id = request.getvalue('_assetid')
    asset = datagate.get_item(asset_id)
    asset.teamid = request.getvalue('_teamid')
    log.debug("assetteam"+asset.teamid)
    # remove all the user rights (those users are on the old team)
    asset.move_by = []
    asset.visible_by = []
    asset.save()
    
            
  def assignasset_action(self, request):
    game = datagate.get_item(request.getvalue('itemid'))
    teams = game.search1(name='groups')
    turns = game.search1(name='turns')
    item_id = request.getvalue('_itemid')
    asset_id = request.getvalue('_assetid')
   
    for team in teams:
        for user in team:
            see_assignment = request.getvalue('_'+str(user.user_id)+':see')
            move_assignment = request.getvalue('_'+str(user.user_id)+':move')
            # we go through all the assets in all turns here because multiple copies of
            # each asset exist (one for each time it is changed)
            if see_assignment == 'on': #the box is checked
              for turn in turns:
                for asset in turn.search1(name='assetmoves'):
                  if asset.getvalue('assetid', '') == asset_id:
                    try:
                        asset.visible_by.index(user.user_id) #if it's not there add it 
                        asset.save()
                    except ValueError:
                        asset.visible_by.append(user.user_id)
                        asset.save()
            else: #examine all unchecked inputs to see if they used to be in the vis list
              for turn in turns:
                for asset in turn.search1(name='assetmoves'):
                  if asset.getvalue('assetid', '') == asset_id:
                    try:
                        asset.visible_by.remove(user.user_id)
                        asset.save()
                    except ValueError:
                        pass
            
                    
            if move_assignment == 'on':
              for turn in turns:
                for asset in turn.search1(name='assetmoves'):
                  if asset.getvalue('assetid', '') == asset_id:
                    try:
                        asset.move_by.index(user.user_id) #if it's not there add it 
                        asset.save()
                    except ValueError:
                        asset.move_by.append(user.user_id)
                        asset.save()
            else: #examine all unchecked inputs to see if they used to be in the vis list
              for turn in turns:
                for asset in turn.search1(name='assetmoves'):
                  if asset.getvalue('assetid', '') == asset_id:
                    try:
                        asset.move_by.remove(user.user_id)
                        asset.save()
                    except ValueError:
                        pass

    
  def numturns_action(self, request):
    game = datagate.get_item(request.getvalue('itemid'))
    turns = game.search1(name='turns')
    try:
      turns.totalturns = int(request.getvalue('totalturns', ''))
      turns.save()
      self.ensure_enough_turns(request, turns)
    except ValueError:
      pass
      
    
  def ensure_enough_turns(self, request, turns):
    '''Ensure sthere are enough turn items in the tree for the total turns in the game'''
    # make sure we have enough children for the turns
    while len(turns.get_child_items()) <= turns.totalturns:
      turn = datagate.create_item(parentid=turns.id, creatorid=request.session.user.id)
      turn.committed = {}
      assetmoves = datagate.create_item(parentid=turn.id, creatorid=request.session.user.id)
      assetmoves.name = 'assetmoves'
      assetmoves.save()
      whiteboard = datagate.create_item(parentid=turn.id, creatorid=request.session.user.id)
      whiteboard.name = 'whiteboard'
      whiteboard.save()
      turn.save()
  
 
    
    
    
    
    
    
    
    
    
    
    
    
    
