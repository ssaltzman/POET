#!/usr/bin/python

from Constants import *
from BaseView import BaseView
import Directory
import datagate
import sys



class StrikeComLegend(BaseView):
  NAME = 'StrikeComLegend'
  
  def __init__(self):
    BaseView.__init__(self)


  #####################################
  ###   Client view methods
     
  def send_content(self, request):
    user = datagate.get_item(request.session.user.id)
    request.writeln(HTML_HEAD)
    request.writeln('''
      <body bgcolor="#C3C191"><center>
      <table border=0 cellspacing=0 cellpadding=15><tr>
      <td align="center" style="color:#666633">Your Assets<br>Are Bordered</td>
      <td align="center" style="color:#666633">Uncommitted Assets<br>Are Translucent</td>
      <td align="center" style="color:#666633">Committed Assets<br>Are Solid</td>
      <td align="center" style="color:#666633">You are currently logged in as<br>
      '''+user.name+'''
      </td>
      </tr></table>
      </body></html>
    ''')
    
    
