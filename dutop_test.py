#!/usr/bin/python

import os
import sys
import operator

cutoff_percentage=5

#The following matches "du -h"
def human(num, power="K"):
    powers=["K","M","G","T"]
    while num >= 1000:
       num /= 1024.0
       power=powers[powers.index(power)+1]
       human(num,power)
    return "%.1f%s" % (num,power)

def print_du(path):
   dufile=os.popen('find \'' + path + '\' -maxdepth 1 -mindepth 1 \( -type f -o -type l -o -type d \) -print0 | xargs -r0 du --max-depth 0 -k | grep -v "^0"')
   dulist=dufile.readlines()
   if len(dulist) == 0:
      sys.exit(0)
   filedict={}
   #print "dulist %s" %dulist
 
   for line in dulist:
      size,name = line[:-1].split('\t')
      print "Size name %s %s" %(size,name)
      stat_val = os.stat(name)
      #print "Size name stat_val %s %s %s" % (size,name,stat_val)
      filedict.setdefault((int(size), stat_val.st_ino),[]).append(name) #filedict{(4, 35913939): ['./mem.sh']}
      #filedict{(4, 35913939): ['./mem.sh'], (12, 35913752): ['./.dutop_test.py.swp']}
      #print "filedict%s" %filedict
   dulist=None
   #print "value%s\t" % filedict 

   keys = filedict.keys()
   keys.sort()
   keys.reverse()
   #print "keys : %s" %keys
   total=reduce(operator.add, [item[0] for item in keys]) #reduce( (lambda x, y: x * y), [1, 2, 3, 4] )
   #print "total: %s" %total
   found_one=0
   for key in keys:
      size=key[0]
      percentage = size*100/total
      #print "Percentage : %s" %percentage
      if percentage < cutoff_percentage:
         continue
      names = filedict[key][:]
      print(names)
      names = names[0]
      isdir = os.path.isdir(name)
      if isdir and (percentage > (100-cutoff_percentage)):
         filedict=None;keys=None
         if print_du(name):
            return 1
      found_one=1
      print "%2d%%%10s    " % (percentage, human(size))
      for name in names:
         if isdir:
            sys.stdout.write("\033[01;34m")
         print name,
      print "\033[00m"
   return found_one


if len(sys.argv) == 1:
   sys.argv.append('.')

print_du(sys.argv[1]) 
