#
# weppzipoutputs()
#
# Zips all low level model output files for a run into a single zip file
# Usage: weppzipoutputs runfile 
#    
# Jan 27, 2012
# Jim Frankenberger
#
import os, sys
import subprocess, shutil, signal, time
import zipfile



#-------------------------------------------------------------------------------------------------
#
#   Start processing here.
#
#-------------------------------------------------------------------------------------------------

print("----------Starting weppzipoutputs--------------\n")

if (len(sys.argv) != 2):
    print("Usage: weppzipoutptus runfile\n")
    print("--------------Done with weppzipoutputs--------------\n")
    exit()

runFile = sys.argv[1]
try:
   fpe = open(runFile, 'r')
except:
   print("Could not open" + runFile)

file = zipfile.ZipFile("weppOutputs.zip", "w")


for line in fpe:
   line = line.strip()
   if ("." in line):
       if ("output" in line):
          filename = line
          if (os.path.exists(filename) == True):
              file.write(filename, os.path.basename(filename), zipfile.ZIP_DEFLATED)
              print("Added: " + filename)

file.close()


print("The WEPP outputs files for this run have been zipped in tools/weppOutputs.zip")
print("--------------Done with weppzipoutputs --------------\n")    
