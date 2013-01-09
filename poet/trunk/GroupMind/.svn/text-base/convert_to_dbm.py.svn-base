#!/usr/bin/python

import glob, dbm, dumbdbm, anydbm, os, os.path


outdir = 'data'
indir = 'dbmdata'
files = glob.glob('dbmdata/*.dat')

for file in files:
  file = os.path.splitext(os.path.split(file)[1])[0]
  print 'Working on', file
  indb = anydbm.open(os.path.join(indir, file))
  outdb = dbm.open(os.path.join(outdir, file), 'n')
  for key in indb.keys():
    outdb[key] = indb[key]
  outdb.close()
  indb.close()
  