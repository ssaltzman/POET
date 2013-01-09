#!/usr/bin/python

import run_cmd
import daemonize
import os, os.path, sys
from Constants import *

LOG_DIR = '/var/log/groupmind'
LOG_FILE = join(LOG_DIR, 'gm.log')
ERR_FILE = join(LOG_DIR, 'gm.err')
PID_FILE = '/var/run/groupmind.pid'

# ensure the correct directories exist
if not os.path.exists(LOG_DIR):
  os.makedirs(LOG_DIR)

# first fork this process to a daemon
daemonize.startstop(stdout=LOG_FILE, stderr=ERR_FILE, pidfile=PID_FILE)

# start the server
run_cmd.main()