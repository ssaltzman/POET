#!/usr/bin/python

from Constants import *
from BaseView import BaseView
import Directory
import datagate
import sys, time

# constants for zooming
numzoomlevels = 20
thumbnailwidth = 120

class StrikeComPlayingBoard(BaseView):
  NAME = 'StrikeComPlayingBoard'
  TOP_LEVEL_COMPONENT = 0
  REGULAR_COMPONENT = 0
  def __init__(self):
    BaseView.__init__(self)
    self.interactive = 1


  #####################################
  ###   Client view methods
     
  def send_content(self, request):
    '''Shows the main meeting window to the user (allows selection of activities)'''
    # get the game objects
    turns = datagate.get_item(request.getvalue('global_rootid'))
    game = turns.get_parent()
    teams = game.search1(name='groups')
    board = game.search1(name='board')
    team = Directory.get_group(game.id, request.session.user.id)
    teammembers = [ item.user_id for item in team ]
    turnnum = int(request.getvalue('turnnum', 0))
    
    # get the current turn object
    turn = turns[turnnum]

    # zoom and pan defaults if this is our first time    
    if not hasattr(request.session, 'zoom'):
      request.session.zoom = numzoomlevels-1
    if not hasattr(request.session, 'panrow'):
      request.session.panrow = 0
    if not hasattr(request.session, 'pancol'):
      request.session.pancol = 0
    # get the current zoom
    zoom = request.session.zoom
    numrows = int(round((float(zoom) / float(numzoomlevels)) * (float(board.gridrows) - 1))) + 1
    numcols = int(round((float(zoom) / float(numzoomlevels)) * (float(board.gridcols) - 1))) + 1
    panrow = request.session.panrow # topmost row to show
    pancol = request.session.pancol # leftmost col to show
    width = str(round(float(board.gridwidth) / numcols)-numcols) # the width of each cell (the -numcols trims the extra space due to the border)
    height = str(round(float(board.gridheight) / numrows)-numrows) # the height of each cell (the -numcols trims the extra space due to the border)
    pix_per_col=round(int(board.gridwidth)/int(board.gridcols))
    pix_per_row=round(int(board.gridheight)/int(board.gridrows))
    zoom_x_min = float(round(pix_per_col*int(request.session.pancol)))
    zoom_x_max = float(round((pix_per_col*int(numcols))+zoom_x_min))
    zoom_y_min = float(round(pix_per_row*int(request.session.panrow)))
    zoom_y_max = float(round((pix_per_row*int(numrows))+zoom_y_min))

    # figure out the current turn
    turn = turns[int(request.getvalue('turnnum', 0))]
    
    # get a list of my team members
    teamids_st = ''
    if len(teammembers) > 0:
      teamids_st = '"' + '","'.join(teammembers) + '"'
      
    # write the html for the main panel
    request.writeln(HTML_HEAD_NO_CLOSE + '''
      <script language='JavaScript' type='text/javascript'>
        var selected = null;                              // the asset, not the row.  the row is selected.assetrow
        var committers = [];                              // array of those who have committed on this turn
        var assets = [];                                  // array of all assets (Asset object defined below)
        var teammembers = [''' + teamids_st + '''];       // my team members
        
        // this is a javascript object constructor -- represents assets
        function Asset(id, assetid, name, width, height, row, col, vis_by, move_by, tooltip) {
          this.id = id;             // the item id in the tree (same asset might be multiple times in the tree, so this changes)
          this.assetid = assetid;   // the asset id that is unique to the asset throughout the tree (this stays the same for each asset)
          this.name = name;
          this.width = width;
          this.height = height;
          this.row=row;
          this.col=col;
          if (vis_by.length == 0) {
            this.vis_by = [];
          }else{
            this.vis_by = vis_by.split(',');
          }
          if (move_by.length == 0) {
            this.move_by = [];
          }else{
            this.move_by = move_by.split(',');
          }
          this.tooltip = tooltip;
        }
        
        /** Helper function to set opacity of assets */
        function setOpacity(obj, opacity) {
            opacity = (opacity == 100)?99.999:opacity;
            // IE/Win
            obj.style.filter = "alpha(opacity:"+opacity+")";
            // Safari<1.2, Konqueror
            obj.style.KHTMLOpacity = opacity/100;
            // Older Mozilla and Firefox
            obj.style.MozOpacity = opacity/100;
            // Safari 1.2, newer Firefox and Mozilla, CSS3
            obj.style.opacity = opacity/100;
        }
        
        /** Handles a click on an asset -- just selects it */
        function assetOnClickHandler(event) {
            // short circuit if we're not on this tool
            if (currenttool != null && currenttool != document.getElementById('moveasseticon')) {
              return;
            }
            var rel = event.target;
            var tr = document.getElementById(rel.assetrowid);
            // if I've committed, don't allow clicking on assets
            if (committers.join(',').indexOf("''' + request.session.user.id + '''") >= 0) {
              return;
            }
            // if I don't have move access to this item, don't allow it
            if (tr.asset.move_by.join(',').indexOf("''' + request.session.user.id + '''") < 0) {
              return;
            }
            
            // if the asset has already been committed for this turn, don't allow it
            //if (committedassets.join(',').indexOf(tr.asset.name) >= 0) {
            //  return;
            //}
            
            
            if(selected == null)
            {
                tr.bgColor="red";
                selected = tr.asset;
                return;
            }
            else
            {
                selected.assetrow.bgColor=null;                
                if(selected==tr.asset)  //they clicked on the previously selected row
                {
                    selected=null;
                    return;
                }
                selected=tr.asset;
                tr.bgColor="red";
            }
        }
        
        /** Handles the click on the table -- initiates a call to the server to record a move event */
        function tableOnClickHandler(row,col) {
            // short circuit if we're not on the asset move tool
            if (currenttool != null && currenttool != document.getElementById('moveasseticon')) {
              return;
            }
            
            // if no item is selected, ignore this event
            if (selected == null){
              return;
            }
            
            //if (committedassets.join(',').indexOf(selected.name) >= 0) {
            //  selected.assetrow.bgColor = null; //this fixes the late selection bug.
            //  return;
            //}
                       
            // if I've committed, don't allow clicking on assets
            if (committers.join(',').indexOf("''' + request.session.user.id + '''") >= 0) {
              return;
            }
            
            // if we put the item back where it already was, ignore this event
            if (row == selected.row && col == selected.col) { 
              return;
            }
            
            // if we get here, we need to move the asset.  send the event to the server
            getEvents().location.href = "''' +  request.cgi_href(turnid=turn.id, gm_action="StrikeComPlayingBoard.asset_movement", frame='events', assetid=None, row=None, col=None)+ '''&assetid="+selected.id+"&row="+row+"&col="+col;

        }
        
        /** Called from the server when an asset has been added to or moved on the board */
        function processAdd(update, asset) {
          // if asset is already here, remove it from wherever it was
          // this must be done because we reassign the assets[asset.id] too a new asset below. 
          // this essentially strands the old one without a reference
          var oldasset = assets[asset.assetid];
          if (oldasset != null && oldasset.assetrow) {
            // remove it from its row in the table (if it's onscreen)
            if (oldasset.assetrow.parentNode != null) {
              oldasset.assetrow.parentNode.removeChild(oldasset.assetrow);
            }
          }
          
          // add the asset to our list of assets (might replace one already in there)
          assets[asset.assetid] = asset;
        
          // create the asset row (we don't add it to a table at this point)
          assetrow = document.createElement('tr');
          assetrow.onclick = assetOnClickHandler;
          assetrow.onmouseover = showAssetTip;
          assetrow.onmouseout = hideddrivetip;
          assetrow.id = 'asset' + asset.name; // so we can locate it later
          assetrow.asset = asset;             // cache the asset in the tr element
          asset.assetrow = assetrow;          // so we can get back to it from the Asset object
          // icon part
          var iconcell = assetrow.appendChild(document.createElement('td'));
          iconcell.assetrowid = assetrow.id
          var imgicon = iconcell.appendChild(document.createElement('img'));
          imgicon.src="''' + request.cgi_href(view="Filer", global_rootid=None) + '''&global_rootid=" + asset.id;
          imgicon.assetrowid = assetrow.id;
          asset.iconcell = iconcell;
          asset.imgicon = imgicon;


          // update the entire playing board because we've had a change
          if (update) {
            updatePlayingBoard();
          }
        }
        
        /** 
         *  Updates the status and placement of assets on the entire board.
         *  Whenever things change on the board (new assets, moved assets, committed assets),
         *  this method runs to update everything.  It first takes all assets off the board,
         *  then it puts them back on according to the current state of this turn.
         */
        function updatePlayingBoard() {
          var teamst = teammembers.join(',')
          var committersst = committers.join(',')
          var mecommitted = committersst.indexOf("''' + request.session.user.id + '''") >= 0;
          
          // update the my teammate status
          for (var i = 0; i < teammembers.length; i++) {
            memberid = teammembers[i];
            if (committersst.indexOf(memberid) >= 0) {  // if this person is commmitted
              // update the user text
              var li = document.getElementById('status' + memberid);
              if (li != null && li.committed == null) {
                li.committed = true;  // just add a simple attribute so we can efficiently check in the future
                var text = li.firstChild.nodeValue;
                li.removeChild(li.firstChild);
                li.appendChild(document.createTextNode(text + " (Committed)"));
              }
              // update my commit button if it's me
              if (memberid == "''' + request.session.user.id + '''") {
                var commitbutton = document.getElementById('commitbutton');
                if (!commitbutton.disabled) {
                  commitbutton.disabled = true;
                  commitbutton.value = 'Turn Committed';
                }//if
              }//if
            }//if
          }//for
          
          // update the asset visibility, placement, and opacity
          for (var assetid in assets) {
            // get this asset and its table row
            var asset = assets[assetid];
            var assetrow = asset.assetrow;
            
            // first move it entirely off screen so it is invisible and not in any table
            if (assetrow.parentNode != null) {
              assetrow.parentNode.removeChild(assetrow);
            }
            
            // I can see this asset if condition1, condition2, or condition3 is true
            //   1. a) I have rights to view the asset (commit status doesn't matter)
            var c1 = asset.vis_by.join(',').indexOf("''' + request.session.user.id + '''") >= 0;
            
            //   2. a) I am committed + 
            //      b) one of my teammates can move the asset and that teammate has committed
            var c2 = false;
            if (!c1) {  // only run c2 if c1 was false
              var c2a = mecommitted;
              var c2b = false;
              for (var j = 0; j < teammembers.length; j++) {
                var teammateid = teammembers[j];
                if (asset.move_by.join(',').indexOf(teammateid) >= 0 && committersst.indexOf(teammateid) >= 0) {
                  c2b = true;
                  break;
                }//if
              }//for
              c2 = (c2a && c2b);
            }
            
            //   3. a) I am committed + 
            //      b) a non-teammate (opponent) can move the asset and that person is committed + 
            //      c) my team's asset is committed by someone on my team and that asset can see the opponent's asset
            var c3 = false;
            if (!(c1 || c2)) {  // only run this if necessary
              var c3a = mecommitted;
              var c3b = false;
              var c3c = false;  
              for (var j = 0; j < asset.move_by.length; j++) {
                var userid = asset.move_by[j];
                if (teamst.indexOf(userid) < 0 && committersst.indexOf(userid) >= 0) {
                  c3b = true;
                  break;
                }//if
              }//for
              if (c3a && c3b) { // only evaluate c3c if necessary, since it can be time consuming
                // right now all this checks is whether my team has an asset in the same
                // cell as the opponent's asset.  if we do, we can see the opponent's asset
                // this obviously needs more complexity and intelligence
                for (var teamassetid in assets) {
                  var teamasset = assets[teamassetid];
                  if (teamasset.row == asset.row && teamasset.col == asset.col) {  // check if this asset and the opponent's asset are in the same cell
                    for (var k = 0; k < teamasset.move_by.length; k++) { // go through those on my team that have rights to move this
                      var userid = teamasset.move_by[k];
                      if (committersst.indexOf(userid) >= 0 && teamst.indexOf(userid) >= 0) { // if one of my team members has rights to move the item and has committed the move
                        c3c = true;
                        break;
                      }
                    }//for
                  }//if
                }//for
              }//if
              c3 = (c3a && c3b && c3c);
            }
            
            // If none are true, continue to next asset
            if (!(c1 || c2 || c3)) {
              continue;
            }//if
            
            // even if I can see the asset, it might be off the current zoom
            if (asset.row > -1 && asset.col > -1) { // on the map somewhere
              var tbody = document.getElementById(asset.row+"x"+asset.col);
              if (tbody == null) {
                continue;
              }//if
            }//if
            
            // if we get here, I can see the asset.  place the asset in the right table and cell
            if(asset.row > -1 && asset.col > -1) { // on the map somewhere
              var tbody = document.getElementById(asset.row+"x"+asset.col);
              tbody.appendChild(assetrow);
            }else{ // offmap
              var tbody = document.getElementById('offmaptbody');
              tbody.appendChild(assetrow);
            }
            
            // if c3 was true, I am looking at an opponent's asset, so change the background color to note this
            if (c3) {
              asset.iconcell.bgColor = "#00CC00";
            }
            
            // higlight this asset if it is one I can move and the asset has not been committed
            if (c3 || asset.move_by.join(',').indexOf("''' + request.session.user.id + '''") >= 0) {
              asset.iconcell.style.borderBottom = 'groove gray 2px';
              asset.iconcell.style.borderTop    = 'groove gray 2px';
              asset.iconcell.style.borderLeft   = 'groove gray 2px';
              asset.iconcell.style.borderRight  = 'groove gray 2px';
            }

            // opacity of icon
            if (mecommitted) {
              setOpacity(asset.imgicon, 100);
            }else{  
              setOpacity(asset.imgicon, 75);
            }
            
          }//for
          
          // now that all the assets are placed on the board, resize their icons to fit well within each cell of the table
          for (var r = ''' + str(panrow) + '''; r < ''' + str(numrows+panrow) + '''; r++) {
            for (var c = ''' + str(pancol) + '''; c < ''' + str(numrows+pancol) + '''; c++) {
              var table_body = document.getElementById(r + 'x' + c);
              var row_count = table_body.childNodes.length
              var max_icon_height = ((''' + height + '''*.75)/ Math.max(2, row_count))-6; //max 2 to assume at least two rows for size, the -6 removes the width of the borders, .75 makes the image a 1/4 smaller than the cell it is in
              var max_icon_width = (''' + width + '''*.75)-6;
              for (var i=0;i<row_count;i++) {
                //tbody----assetrow------imgicon-------img 
                var icon = table_body.childNodes[i].childNodes[0].childNodes[0];
                if (icon.origheight == null) { // save the image's original height and width if we haven't done so before
                  icon.origheight = icon.height;
                  icon.origwidth = icon.width;
                }
                if ((max_icon_height * icon.origwidth) / icon.origheight > max_icon_width) { // image is too wide at this height, so go even smaller than we were going to go
                  icon.height = (max_icon_width * icon.origheight) / icon.origwidth;  // so the height is scalable to the new width
                  icon.width = max_icon_width;
                }else{ 
                  icon.height = max_icon_height;
                  icon.width = (max_icon_height * icon.origwidth) / icon.origheight;  // so the width is scalable to the new height
                }
              }//for           
            }//for
          }//for
          var table_body = document.getElementById('offmaptbody');
          var row_count = table_body.childNodes.length
          var max_icon_height = ((''' + height + '''*.75)/ 2)-6; // 2 to assume two rows for size, the -6 removes the width of the borders, .75 makes the image a 1/4 smaller than the cell it is in
          var max_icon_width = (''' + width + '''*.75)-6;
          for (var i=0;i<row_count;i++) {
            //tbody----assetrow------imgicon-------img 
            var icon = table_body.childNodes[i].childNodes[0].childNodes[0];
            if (icon.origheight == null) { // save the image's original height and width if we haven't done so before
              icon.origheight = icon.height;
              icon.origwidth = icon.width;
            }
            if ((max_icon_height * icon.origwidth) / icon.origheight > max_icon_width) { // image is too wide at this height, so go even smaller than we were going to go
              icon.height = (max_icon_width * icon.origheight) / icon.origwidth;  // so the height is scalable to the new width
              icon.width = max_icon_width;
            }else{ 
              icon.height = max_icon_height;
              icon.width = (max_icon_height * icon.origwidth) / icon.origheight;  // so the width is scalable to the new height
            }
          }//for           
        }//function updatePlayingBoard
        


        /** Shows the tooltip for an asset */
        function showAssetTip(event) {
          // step back to the table row we're on
          var obj = event.target;
          while (obj != null && obj.asset == null) {
            obj = obj.parentNode;
          }
          if (obj != null) {
            var asset = obj.asset;
            ddrivetip(asset.tooltip);
          }
        }
        
        /** Called when the user clicks the commit button to finish the turn */
        function commit() {
          // if I've committed, don't allow clicking on assets
          if (committers.join(',').indexOf("''' + request.session.user.id + '''") >= 0) {
            return;
          }
          // ensure the user really wants to commit
          if (!confirm('Commit all of your asset movements for this turn?')) {
            return;
          }
          getEvents().location.href = "''' +  request.cgi_href(turnid=turn.id, gm_action="StrikeComPlayingBoard.commit", frame='events')+ '''";
        }
        
        /* Handles a commit event from the server */
        function processCommit(turnid, committerlist) {
          // if we aren't on this turn, skip the event since we only care about committers on our turn
          if (turnid != "''' + turn.id + '''") {
            return;
          }
          
          // update the committer list
          committers = committerlist.split(",");
          
          // update the board
          updatePlayingBoard();
        }
        


        /////////////////////////////////////////////////////
        ///   THIS SECTION IS FOR DRAWING ON THE BOARD
        
        var currenttool = null;
        /** Changes the current tool */
        function changetool(newtool) {
          // set the current tool if it is null (it is null when the page first loads)
          if (currenttool == null) {
            currenttool = document.getElementById('moveasseticon')
          }
          // short circuit if we selected the same tool
          if (currenttool == newtool) {
            return;
          }
          // deselect the old tool
          currenttool.style.borderRight = 'outset #666633 3px';
          currenttool.style.borderLeft = 'outset #666633 3px';
          currenttool.style.borderTop = 'outset #666633 3px';
          currenttool.style.borderBottom = 'outset #666633 3px';
          // select the new tool
          currenttool = newtool;
          currenttool.style.borderRight = 'inset #666633 3px';
          currenttool.style.borderLeft = 'inset #666633 3px';
          currenttool.style.borderTop = 'inset #666633 3px';
          currenttool.style.borderBottom = 'inset #666633 3px';
        }
        
        var xPoints = null;
        var yPoints = null;
        /** Responds to a mouse down on the playing board */
        function canvasMouseDown(evt) {
          evt = (evt) ? evt : ((event) ? event : null);
          if (currenttool == document.getElementById('lineicon')) {
            var div = document.getElementById('GraphicsCanvas');
            xPoints = [];
            yPoints = [];
            
            //if zoomed hook
            
            //xPoints[xPoints.length] = evt.clientX - div.offsetLeft + document.body.scrollLeft;
            //yPoints[yPoints.length] = evt.clientY - div.offsetTop + document.body.scrollTop;
            xPoints[xPoints.length] = ((evt.clientX - div.offsetLeft + document.body.scrollLeft)*('''+str(numcols)+'''/'''+str(board.gridcols)+'''))+ '''+str(zoom_x_min)+''';
            yPoints[yPoints.length] = ((evt.clientY - div.offsetTop  + document.body.scrollTop) *('''+str(numrows)+'''/'''+str(board.gridrows)+'''))+ '''+str(zoom_y_min)+''';
            return false;
            
          }else if (currenttool == document.getElementById('texticon')) {
            var text = prompt("Text:");
            text = encode(text);
            var div = document.getElementById('GraphicsCanvas');
            //var x = evt.clientX - div.offsetLeft + document.body.scrollLeft;
            //var y = evt.clientY - div.offsetTop + document.body.scrollTop;
            var x = ((evt.clientX - div.offsetLeft + document.body.scrollLeft)*('''+str(numcols)+'''/'''+str(board.gridcols)+'''))+ '''+str(zoom_x_min)+''';
            var y = ((evt.clientY - div.offsetTop  + document.body.scrollTop) *('''+str(numrows)+'''/'''+str(board.gridrows)+'''))+ '''+str(zoom_y_min)+''';
            getEvents().location.href = "''' +  request.cgi_href(turnid=turn.id, gm_action="StrikeComPlayingBoard.draw", frame='events')+ '''&_type=text&_color=" + currentcolor + "&_text=" + text + "&_xPoints=" + x + "&_yPoints=" + y;
            return false;
          
          }else if (currenttool == document.getElementById('flagicon')) {
            var text = prompt("Flag Popup Text:");
            text = encode(text);
            var div = document.getElementById('GraphicsCanvas');
            //var x = evt.clientX - div.offsetLeft + document.body.scrollLeft;
            //var y = evt.clientY - div.offsetTop + document.body.scrollTop;
            var x = ((evt.clientX - div.offsetLeft + document.body.scrollLeft)*('''+str(numcols)+'''/'''+str(board.gridcols)+'''))+ '''+str(zoom_x_min)+''';
            var y = ((evt.clientY - div.offsetTop  + document.body.scrollTop) *('''+str(numrows)+'''/'''+str(board.gridrows)+'''))+ '''+str(zoom_y_min)+''';
            getEvents().location.href = "''' +  request.cgi_href(turnid=turn.id, gm_action="StrikeComPlayingBoard.draw", frame='events')+ '''&_type=flag&_color=" + currentcolor + "&_text=" + text + "&_xPoints=" + x + "&_yPoints=" + y;
            return false;
          }
        }
        
        /** Responds to a mouse movement across the playing board */
        function canvasMouseMove(evt) {
        
        //(xp[ind]-zoom_x_min)*(board.gridcols/numcols)
        //-'''+str(zoom_x_min)+''')*('''+str(board.gridcols)+'''/'''+str(numcols)+''');
        
        
          if (xPoints != null && yPoints != null && currenttool == document.getElementById('lineicon')) {
            evt = (evt) ? evt : ((event) ? event : null);
            var div = document.getElementById('GraphicsCanvas'); 
            xPoints[xPoints.length] = ((evt.clientX - div.offsetLeft + document.body.scrollLeft)*('''+str(numcols)+'''/'''+str(board.gridcols)+'''))+ '''+str(zoom_x_min)+''';
            yPoints[yPoints.length] = ((evt.clientY - div.offsetTop  + document.body.scrollTop) *('''+str(numrows)+'''/'''+str(board.gridrows)+'''))+ '''+str(zoom_y_min)+''';
            return false;
          }
        }

        /** Responds to a mouse up on the playing board */
        function canvasMouseUp(evt) {
          if (xPoints != null && yPoints != null && currenttool == document.getElementById('lineicon')) {
            evt = (evt) ? evt : ((event) ? event : null);
            getEvents().location.href = "''' +  request.cgi_href(turnid=turn.id, gm_action="StrikeComPlayingBoard.draw", frame='events')+ '''&_type=line&_color=" + currentcolor + "&_xPoints=" + xPoints.join(',') + "&_yPoints=" + yPoints.join(',');
            xPoints = null;
            yPoints = null;
            return false;
          }
        }
            
        /** Drawing events sent from the server to us.
        Figure out the mins and maxs for the area that you want to see.  For example if you have a 500X500 pixel map with 3 rows and 3 cols you have:
        500/3 = 166 px/row and 166 px/col **round off errors are present but small.
        So if want to see cols 1 and 2 you want to see pixels 166 thru 500 on the x-axis so we set our zoom_x_min at 166 and zoom_x_max at 500.
        The same logic is applied to figure out the y limits as well.
        Now that we have our limits we can filter the original points so that we keep only the points whos x AND y values fall within our desired range.
        Now we scale.
        (xp[ind]-zoom_x_min)*(board.gridcols/numcols)

        **The following example is for the x coordinate, but the same logic applies to the y coordinate.
        first we subtract off the zoom_x_min from the x coordinate of the point, this translates the point to the proper scaled x coordinate.  
        Next we multiply the point by the 'scaling factor', the fewer cells we show (the more intense the zoom) the more we need stretch the x coordinate.
        so we figure the 'scaling factor' as board.gridcols/numcols (numcols being the number of columns that are being shown).  Therefore, the more cols we show
        the LESS the 'scaling factor' becomes.

        Still needs a bit of tweaking but for the most part is good to go.
        
        --Chris 12Jul05
        
        */
        function processDraw(creatorid, type, color, text, xp, yp) {
          if (creatorid == "''' + request.session.user.id + '''" || teammembers.join(',').indexOf(creatorid) >= 0) {
            canvas.setColor("#" + color);
            var div = document.getElementById('GraphicsCanvas');
            new_xp = [];
            new_yp = [];
            
            //we only need to loop the entire array for the line but this also takes care of the xp[0] and yp[0] points as well.
            
            if (type == 'line') {
            for (var ind = 0; ind < xp.length; ind++) {
              if (parseInt(xp[ind]) > '''+str(zoom_x_min)+''' && parseInt(xp[ind]) < '''+str(zoom_x_max)+''')
                if (parseInt(yp[ind]) > '''+str(zoom_y_min)+''' && parseInt(yp[ind]) < '''+str(zoom_y_max)+''')
                {
                  new_xp[new_xp.length]=(xp[ind]-'''+str(zoom_x_min)+''')*('''+str(board.gridcols)+'''/'''+str(numcols)+''');
                  new_yp[new_yp.length]=(yp[ind]-'''+str(zoom_y_min)+''')*('''+str(board.gridrows)+'''/'''+str(numrows)+''');                        
                }//if
              }//for
              xp = new_xp;
              yp = new_yp;
              canvas.drawPolyline(xp, yp); 
            }else if (type == 'text') {
              if (parseInt(xp[0]) > '''+str(zoom_x_min)+''' && parseInt(xp[0]) < '''+str(zoom_x_max)+''')
                if (parseInt(yp[0]) > '''+str(zoom_y_min)+''' && parseInt(yp[0]) < '''+str(zoom_y_max)+''')
                { 
                  xp[0] = (xp[0]-'''+str(zoom_x_min)+''')*('''+str(board.gridcols)+'''/'''+str(numcols)+''');
                  yp[0] = (yp[0]-'''+str(zoom_y_min)+''')*('''+str(board.gridrows)+'''/'''+str(numrows)+''');
                  canvas.drawString(text, xp[0], yp[0]); 
                }
            }else if (type == 'flag') {
              if (parseInt(xp[0]) > '''+str(zoom_x_min)+''' && parseInt(xp[0]) < '''+str(zoom_x_max)+''')
                if (parseInt(yp[0]) > '''+str(zoom_y_min)+''' && parseInt(yp[0]) < '''+str(zoom_y_max)+''')    
                {
                  xp[0] = (xp[0]-'''+str(zoom_x_min)+''')*('''+str(board.gridcols)+'''/'''+str(numcols)+''');
                  yp[0] = (yp[0]-'''+str(zoom_y_min)+''')*('''+str(board.gridrows)+'''/'''+str(numrows)+''');
                  canvas.drawImage('/strikecom/flag.png', xp[0], yp[0], 24, 24, 'onmouseover="ddrivetip(\\'' + text + '\\')" onmouseout="hideddrivetip()"')
                }
            }
            canvas.paint();
            canvas.setColor("#" + currentcolor);
          }
        }

        var currentcolor = "0F039A";
        COLORS = [
          [ "FFFFFF","FFCBCB","FFEDCB","FEFFCB","CBFFCB","CBCBFD","E3D5F5","EBDFEB"],
          [ "DADADA","FFA0A0","FFDDA0","FEFFA0","A0FFA0","A0A0FF","C9B2EC","DBC3DB"],
          [ "B6B6B6","FF7474","FFCE74","FEFF74","75FF74","7574FF","B08FE4","CBA8CB"],
          [ "919191","FF4848","FFBE48","FDFF48","46FF48","4848FF","996BDD","BB8CBB"],
          [ "6D6D6D","FF1D1D","FFAF1D","FDFF1D","1BFF1D","1D1DFF","8048D3","AA71AA"],
          [ "484848","EF0B00","F09B00","F0F000","00F000","1804F0","692DC2","975996"],
          [ "242424","C40900","C47F03","C4C415","00C402","1402C4","56259F","7C497B"],
          [ "010101","990702","996302","999903","009902","0F039A","431D7B","5F395F"],
        ];
        /** Responds to a color change click */
        function changecolor(evt) {
          evt = (evt) ? evt : ((event) ? event : null);
          var colorpicker = document.getElementById('colorpicker');
          var x = evt.clientX - colorpicker.x;
          var y = evt.clientY - colorpicker.y;
          currentcolor = COLORS[Math.floor(y/15)][Math.floor(x/15)];
          canvas.setColor("#" + currentcolor);
          document.getElementById('currentcolor').bgColor = "#" + currentcolor;
          evt.cancelBubble = true;
        }
        
      </script>
      <!-- for tooltips -->
      <style type="text/css">
        #dhtmltooltip{
          position: absolute;
          width: 150px;
          border: 2px ridge black;
          padding: 2px;
          color: #333300;
          background-color: #C3C191;
          font-size: 12px;
          visibility: hidden;
          z-index: 100;
        }
        .tooltiptext{
          color: #666633;
          font-size: 9px;
        }
      </style>    
      </head>
    ''')
    request.writeln('<body bgcolor="#D9DDBC" style="background-image:url(/strikecom/blue-middle.png); background-repeat: repeat-x;" onload="getEvents().refreshEvents()">')
    request.writeln('''
      <div id="dhtmltooltip"></div>
      <script type="text/javascript">
      
        // this is for the tooltips
        /***********************************************
        * Cool DHTML tooltip script-  Dynamic Drive DHTML code library (www.dynamicdrive.com)
        * This notice MUST stay intact for legal use
        * Visit Dynamic Drive at http://www.dynamicdrive.com/ for full source code
        ***********************************************/
        
        var offsetxpoint=-60 //Customize x offset of tooltip
        var offsetypoint=20 //Customize y offset of tooltip
        var ie=document.all
        var ns6=document.getElementById && !document.all
        var enabletip=false
        if (ie||ns6)
        var tipobj=document.all? document.all["dhtmltooltip"] : document.getElementById? document.getElementById("dhtmltooltip") : ""
        
        function ietruebody(){
        return (document.compatMode && document.compatMode!="BackCompat")? document.documentElement : document.body
        }
        
        function ddrivetip(thetext, thecolor, thewidth){
        if (ns6||ie){
        if (typeof thewidth!="undefined") tipobj.style.width=thewidth+"px"
        if (typeof thecolor!="undefined" && thecolor!="") tipobj.style.backgroundColor=thecolor
        tipobj.innerHTML=thetext
        enabletip=true
        return false
        }
        }
        
        function positiontip(e){
        if (enabletip){
        var curX=(ns6)?e.pageX : event.x+ietruebody().scrollLeft;
        var curY=(ns6)?e.pageY : event.y+ietruebody().scrollTop;
        //Find out how close the mouse is to the corner of the window
        var rightedge=ie&&!window.opera? ietruebody().clientWidth-event.clientX-offsetxpoint : window.innerWidth-e.clientX-offsetxpoint-20
        var bottomedge=ie&&!window.opera? ietruebody().clientHeight-event.clientY-offsetypoint : window.innerHeight-e.clientY-offsetypoint-20
        
        var leftedge=(offsetxpoint<0)? offsetxpoint*(-1) : -1000
        
        //if the horizontal distance isn't enough to accomodate the width of the context menu
        if (rightedge<tipobj.offsetWidth)
        //move the horizontal position of the menu to the left by it's width
        tipobj.style.left=ie? ietruebody().scrollLeft+event.clientX-tipobj.offsetWidth+"px" : window.pageXOffset+e.clientX-tipobj.offsetWidth+"px"
        else if (curX<leftedge)
        tipobj.style.left="5px"
        else
        //position the horizontal position of the menu where the mouse is positioned
        tipobj.style.left=curX+offsetxpoint+"px"
        
        //same concept with the vertical position
        if (bottomedge<tipobj.offsetHeight)
        tipobj.style.top=ie? ietruebody().scrollTop+event.clientY-tipobj.offsetHeight-offsetypoint+"px" : window.pageYOffset+e.clientY-tipobj.offsetHeight-offsetypoint+"px"
        else
        tipobj.style.top=curY+offsetypoint+"px"
        tipobj.style.visibility="visible"
        }
        }
        
        function hideddrivetip(){
        if (ns6||ie){
        enabletip=false
        tipobj.style.visibility="hidden"
        tipobj.style.left="-1000px"
        tipobj.style.backgroundColor=''
        tipobj.style.width=''
        }
        }
        document.onmousemove=positiontip
      </script>
    ''')
    request.writeln('<div>&nbsp;</div>')

    # main table header (holds the offmap assets and playing board)
    request.writeln('<table border=0 cellspacing=0 cellpadding=0 width="100%"><tr><td valign="top" width="80" onClick="tableOnClickHandler(-1,-1)">')

    # offmap assets
    request.writeln('<div align="center" style="color:#666633">Offmap Assets:</div>')
    request.writeln('<table border=0 cellspacing=0 cellpadding=5><tbody id="offmaptbody"></tbody></table>')
    
    # splitter between offmap assets and playing board
    request.writeln('</td><td valign="top">')

    # playing board
    request.writeln('<table border=0 cellspacing=0 cellpadding=2><tr>')
    request.writeln('<td colspan="3" align="center"><a target="_parent" href="' + request.cgi_href(frame=None, gm_action="zoom", panrow=panrow-1, pancol=pancol, zoom=zoom) + '"><img border=0 src="/strikecom/arrow_up_double_triangle.png">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img border=0 src="/strikecom/arrow_up_double_triangle.png"></a></td>')
    request.writeln('</tr><tr>')
    request.writeln('<td align="center"><a target="_parent" href="' + request.cgi_href(frame=None, gm_action="zoom", panrow=panrow, pancol=pancol-1, zoom=zoom) + '"><img border=0 src="/strikecom/arrow_left_double_triangle.png"><br>&nbsp;<br>&nbsp;<br><img border=0 src="/strikecom/arrow_left_double_triangle.png"></a></td>')
    request.writeln('<td>')
    request.writeln('<div style="position:relative;" id="GraphicsCanvas">')
    request.writeln('''
      <!-- for the drawing on board -->
      <script type="text/javascript" src="/strikecom/wz_jsgraphics.js"></script>
      <script language='JavaScript' type='text/javascript'>
        var canvasdiv = document.getElementById('GraphicsCanvas');
        var canvas = new jsGraphics("GraphicsCanvas");
        canvas.setColor("#" + currentcolor);
      </script>
    ''')
    width = str(round(float(board.gridwidth) / numcols)-numcols)
    height = str(round(float(board.gridheight) / numrows)-numrows)
    if board.filename: 
      request.writeln('<table border=1 cellspacing=0 cellpadding=0 background="' + request.cgi_href(view="StrikeComBackground", global_rootid=board.id, gm_contenttype=board.filetype) + '">')
    else:
      request.writeln('<table border=1 cellspacing=0 cellpadding=0>')
    for r in range(panrow, numrows+panrow):
      request.writeln('<tr>')      
      for c in range(pancol, numcols+pancol):
        request.write('<td valign="center" align="center" onMouseUp="canvasMouseUp(event)" onMouseDown="canvasMouseDown(event)" onMouseMove="canvasMouseMove(event)" onClick="tableOnClickHandler('+str(r)+','+str(c)+')" width="' + width + '" height="' + height + '">')
        request.write('<table border=0 cellspacing=0 cellpadding=0>')
        request.write('<tbody id="'+str(r)+"x"+str(c)+'">')
        request.write('</tbody>')
        request.write('</table>')
        request.writeln('&nbsp;</td>')
      request.writeln('</tr>')
    request.writeln('</table>')
    request.writeln('</div>')  #end of the canvas
    request.writeln('</td>')
    request.writeln('<td align="center"><a target="_parent" href="' + request.cgi_href(frame=None, gm_action="zoom", panrow=panrow, pancol=pancol+1, zoom=zoom) + '"><img border=0 src="/strikecom/arrow_right_double_triangle.png"><br>&nbsp;<br>&nbsp;<br><img border=0 src="/strikecom/arrow_right_double_triangle.png"></a></td>')
    request.writeln('<td>')
    request.writeln('</tr><tr>')
    request.writeln('<td colspan="3" align="center"><a target="_parent" href="' + request.cgi_href(frame=None, gm_action="zoom", panrow=panrow+1, pancol=pancol, zoom=zoom) + '"><img border=0 src="/strikecom/arrow_down_double_triangle.png">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img border=0 src="/strikecom/arrow_down_double_triangle.png"></a></td>')
    request.writeln('</tr></table>')
    
    # splitter between playing board and player status
    request.writeln('</td><td valign="top">')
    
    # player status
    request.writeln('<div align="center" style="color:#666633">Team Status:</div>')
    teammates = [ datagate.get_item(mate.user_id) for mate in team.get_child_items() ]
    teammates.sort(lambda a,b: cmp(a.username.lower(), b.username.lower()))
    for user in teammates:
      request.writeln('<div id="status' + user.id + '">' + user.username + '</div>')
    request.writeln('<br>')

    # footer for the center cell
    request.writeln('<div align="center"><input id="commitbutton" type="button" value="Commit" onclick="commit()"</div>')
    
    # thumbnail of entire map (if we have a background map)
    if board.filename:
      request.writeln('<div>&nbsp;</div>')
      request.writeln('<center>')
      request.writeln('<table style="border:2px #666633 ridge" border=0 cellspacing=0 cellpadding=5><tr><td><center>')
      
      # thumbnail
      thumbnailheight = int((float(board.gridheight) / float(board.gridwidth)) * thumbnailwidth)
      request.writeln('<img usemap="backgroundpan" border=1 src="' + request.cgi_href(view="StrikeComThumbnail", global_rootid=board.id, gm_contenttype=board.filetype) + '">')
      request.writeln('<map name="backgroundpan">')
      thumbnailcellheight = int(float(thumbnailheight) / float(board.gridrows))
      thumbnailcellwidth = int(float(thumbnailwidth) / float(board.gridcols))
      for r in range(0, int(board.gridrows)):
        for c in range(0, int(board.gridcols)):
          x = int(round(float(thumbnailwidth) / float(board.gridcols) * c))
          y = int(round(float(thumbnailheight) / float(board.gridrows) * r))
          request.writeln('<area shape="rect" coords="%i,%i,%i,%i" target="_parent" href="%s">' % (x, y, x+thumbnailcellwidth, y+thumbnailcellheight, request.cgi_href(gm_action="zoom", frame=None, panrow=r, pancol=c, zoom=zoom)))
      request.writeln('<area shape="default" nohref>')
      request.writeln('</map>')
      request.writeln('<div>&nbsp;</div>')
      
      # zoom slider
      request.write('<table border=1 cellspacing=0 cellpadding=0><tr><td>')
      request.write('<table border=0 cellspacing=0 cellpadding=0><tr>')
      for i in range(0, numzoomlevels):
        if i == zoom:
          request.write('<td width="5" height="7" bgcolor="#003366"></td>')
        else:
          request.write('<td width="5" height="7" bgcolor="#CCCCCC" onclick="getMain().location.href=\'' + request.cgi_href(frame=None, gm_action='zoom', zoom=i) + '\'"> </td>')
      request.writeln('</tr></table></td></tr></table>')
      
      # end of border table over the thumbnail and zoom
      request.writeln('</center>')
      request.writeln('</td></tr></table>')
      request.writeln('</center>')
  
    # whiteboard controls
    request.writeln('<div>&nbsp;</div>')
    request.writeln('<center>')
    request.writeln('<table style="border:2px #666633 ridge" border=0 cellspacing=0 cellpadding=5><tr>')
    request.writeln('<td><img style="border:inset #666633 3px" id="moveasseticon" onclick="changetool(this)" border=0 src="/strikecom/assetmover.png"></td><td style="color:#666633">Move Assets</td>')
    request.writeln('</tr><tr>')
    request.writeln('<td><img style="border:outset #666633 3px" id="lineicon" onclick="changetool(this)" border=0 src="/strikecom/paintbrush.png"></td><td style="color:#666633">Draw</td>')
    request.writeln('</tr><tr>')
    request.writeln('<td><img style="border:outset #666633 3px" id="texticon" onclick="changetool(this)" border=0 src="/strikecom/text.png"></td><td style="color:#666633">Write Text</td>')
    request.writeln('</tr><tr>')
    request.writeln('<td><img style="border:outset #666633 3px" id="flagicon" onclick="changetool(this)" border=0 src="/strikecom/flag.png"></td><td style="color:#666633">Place Flag</td>')
    request.writeln('</tr><tr>')
    request.writeln('<td style="color:#666633">Color:</td><td id="currentcolor" bgcolor="#0F039A">&nbsp;</td>')
    request.writeln('</tr><tr>')
    request.writeln('<td align="center" colspan="2"><img id="colorpicker" src="/strikecom/colorpicker.gif" onclick="changecolor(event)" border="0"></td>')
    request.writeln('</tr></table>')
    request.writeln('</center>')
    
    # footer for main table (holds the offmap assets and playing board)
    request.writeln('</td></tr></table>')
    request.writeln("</body>")
    request.writeln("</html>")



##################################  
###   Actions


  def zoom_action(self, request):
    '''Changes the zoom and/or pan'''
    turns = datagate.get_item(request.getvalue('global_rootid'))
    game = turns.get_parent()
    board = game.search1(name='board')
    gridrows = float(board.gridrows)
    gridcols = float(board.gridcols)
    try:
      # get the new zoom and number of rows/cols to show
      oldpanrow = int(request.getvalue('panrow', request.session.panrow))
      oldpancol = int(request.getvalue('pancol', request.session.pancol))
      oldzoom = request.session.zoom
      oldnumrows = int(round((float(oldzoom) / float(numzoomlevels)) * (gridrows - 1))) + 1
      oldnumcols = int(round((float(oldzoom) / float(numzoomlevels)) * (gridcols - 1))) + 1
      newzoom = int(request.getvalue('zoom'))
      newnumrows = int(round((float(newzoom) / float(numzoomlevels)) * (gridrows - 1))) + 1
      newnumcols = int(round((float(newzoom) / float(numzoomlevels)) * (gridcols - 1))) + 1
      # calculate the new panrows and pancols (top left corner of graphic to show)
      request.session.zoom = newzoom
      request.session.panrow = oldpanrow + (int(round((oldnumrows - newnumrows) / 2.0)))
      request.session.pancol = oldpancol + (int(round((oldnumcols - newnumcols) / 2.0)))
      # be sure we didn't go off any edge of the graphic
      request.session.panrow = min(request.session.panrow, gridrows - newnumrows)
      request.session.panrow = max(request.session.panrow, 0)
      request.session.pancol = min(request.session.pancol, gridcols - newnumcols)
      request.session.pancol = max(request.session.pancol, 0)
      
    
      
    except ValueError:
      pass

  def _get_current_asset_state(self, turnsid, turnnum):
    '''Goes through the entire game actions and gets the current state
       of all assets up to a specific turn number.
       In other words, assets have entries many times
       (once for each time they are moved, edited, changed, etc.).  This
       method goes through them and returns a list containing only the most 
       recent change for each asset.  The assets are returned in
       no particular order.
    '''
    all_assets = {}  # use a dictionary because it only allows one for each name
    turns = datagate.get_item(turnsid)
    for turn in turns.get_child_items()[0:turnnum+1]:  # process all events up to the current turn -- will put the game in the correct state for this turn
      assets = turn.search1(name='assetmoves').get_child_items()
      for a in assets:
        all_assets[a.name] = a
    return all_assets.values()   #return the assets
    
    
  def create_tooltip(self, asset): 
    '''Creates the tooltip for an asset (it's easier to do it here in python than in javascript)
       Don't forget to escape any special characters twice because it gets interpreted once by python, then by javascript.
    '''
    html = []
    html.append('<div align=center>' + asset.name.replace('"', '\\"') + '</div>')
    html.append('<hr>')
    html.append('<center>')
    html.append('<table border=0 cellspacing=0 cellpadding=2')
    if int(asset.row) < 0 or int(asset.col) < 0:
      html.append('<tr><td class=tooltiptext>Position:</td><td class=tooltiptext>Offmap</td></tr>')
    else:
      html.append('<tr><td class=tooltiptext>Position:</td><td class=tooltiptext>' + str(int(asset.row)+1) + ', ' + str(int(asset.col)+1) + '</td></tr>')
    html.append('<tr><td class=tooltiptext>Size:</td><td class=tooltiptext>' + str(asset.height) + ' by ' + str(asset.width) + '</td></tr>')
    visby = []
    for userid in asset.visible_by:
      user = datagate.get_item(userid)
      if user:
        visby.append(user.username)
    html.append('<tr><td class=tooltiptext>Visible to:</td><td class=tooltiptext>' + ', '.join(visby).replace('"', '\\"') + '</td></tr>')
    moveby = []
    for userid in asset.move_by:
      user = datagate.get_item(userid)
      if user:
        moveby.append(user.username)
    html.append('<tr><td class=tooltiptext>Movable by:</td><td class=tooltiptext>' + ', '.join(moveby).replace('"', '\\"') + '</td></tr>')
    html.append('<tr><td class=tooltiptext>Striking:</td><td class=tooltiptext>' + str(asset.striking) + '</td></tr>')
    html.append('<tr><td class=tooltiptext>Defensive:</td><td class=tooltiptext>' + str(asset.defensive) + '</td></tr>')
    html.append('<tr><td class=tooltiptext>Sight:</td><td class=tooltiptext>' + str(asset.sight) + '</td></tr>')
    html.append('<tr><td class=tooltiptext>Visibility:</td><td class=tooltiptext>' + str(asset.visibility) + '</td></tr>')
    html.append('</table>')
    html.append('</center>')
    return ''.join(html)


  def get_initial_events(self, request, rootid):
    '''Retrieves a list of initial javascript calls that should be sent to the client
       when the view first loads.  Typically, this is a series of add_processor
       events.'''
    # figure out the current turn
    turns = datagate.get_item(rootid)
    game = turns.get_parent()
    turnnum = int(request.getvalue('turnnum', 0))
    turn = turns[turnnum]
    events = []
    # events for assets
    for a in self._get_current_asset_state(rootid, turnnum):
      events.append('processAdd(false, new parent.content.Asset("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s"))' % (a.id, a.assetid, a.name, a.width, a.height, a.row, a.col, ','.join(a.visible_by), ','.join(a.move_by), self.create_tooltip(a)))
    events.append('updatePlayingBoard()')  # explicitly tell the playing board to update (since we have false above)
    events.append('processCommit("%s","%s")' % (turn.id, ','.join(turn.committed.keys())))
    # events for whiteboard drawings
    whiteboard = turn.search1(name='whiteboard')
    for draw in whiteboard:
      events.append('processDraw("%s","%s","%s","%s",[%s],[%s])' % (draw.creatorid, draw.type, draw.color, draw.text, ','.join(draw.xPoints), ','.join(draw.yPoints)))
    return events

    
  def asset_movement_action(self, request):
    '''Processes an asset movement action - when the user moves an asset on the board'''
    row = request.getvalue('row')
    col = request.getvalue('col')
    turn = datagate.get_item(request.getvalue('turnid'))
    assetmoves = turn.search1(name='assetmoves')
    asset = datagate.get_item(request.getvalue('assetid'))
    newasset = datagate.create_item(creatorid=request.session.user.id, parentid=assetmoves.id)
    newasset.assetid = asset.assetid
    newasset.name = asset.name
    newasset.width = asset.width
    newasset.height = asset.height
    newasset.row = row
    newasset.col = col
    newasset.filebytes = asset.filebytes
    newasset.filetype = asset.filetype
    newasset.filename = asset.filename
    newasset.striking = asset.striking
    newasset.defensive = asset.defensive
    newasset.sight = asset.sight
    newasset.visibility = asset.visibility
    newasset.terrains = asset.terrains
    newasset.visible_by = asset.visible_by
    newasset.move_by = asset.move_by
    newasset.teamid = asset.teamid
    newasset.save()
    return [ 'processAdd(true, new parent.content.Asset("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s"))' % (newasset.id, newasset.assetid, newasset.name, newasset.width, newasset.height, newasset.row, newasset.col, ','.join(newasset.visible_by), ','.join(newasset.move_by), self.create_tooltip(newasset)) ]


  def draw_action(self, request):
    whiteboard = datagate.get_item(request.getvalue('turnid')).search1(name='whiteboard')
    draw = datagate.create_item(creatorid=request.session.user.id, parentid=whiteboard.id)
    draw.type = request.getvalue('_type')
    draw.color = request.getvalue('_color')
    draw.xPoints = request.getvalue('_xPoints','').split(',')
    draw.yPoints = request.getvalue('_yPoints','').split(',')
    draw.text = request.getvalue('_text','')
    draw.save()
    return [ 'processDraw("%s","%s","%s","%s",[%s],[%s])' % (draw.creatorid, draw.type, draw.color, draw.text, ','.join(draw.xPoints), ','.join(draw.yPoints)) ]


  def commit_action(self, request):
    '''Processes a commit on the board'''
    # set this user as committed for all turns up to this turn (just in case we skipped a turn for some reason)
    allturns = datagate.get_item(request.getvalue('global_rootid'))
    turnid = request.getvalue('turnid')
    for turn in allturns:
      if not turn.committed.has_key(request.session.user.id):
        turn.committed[request.session.user.id] = time.time()
        turn.save()
      if turn.id == turnid:  # if we are at this turn, move on (don't commit for future turns)
        break
    
    # now send the committers to refresh the views
    return [ 'processCommit("%s","%s")' % (turnid, ','.join(turn.committed.keys())) ]
