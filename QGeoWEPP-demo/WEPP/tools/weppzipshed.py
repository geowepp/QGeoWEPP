#
# weppzipshed()
#
# Zips all low level model input files for a watershed run into a single zip file
# Usage: weppshedzip runfile slopefile manfile soilfile clifile
#    
# May 27, 2010
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

print("----------Starting weppzipshed--------------\n")

if (len(sys.argv) != 2):
    print("Usage: weppzipshed runfile\n")
    print("--------------Done with watershed zip--------------\n")
    exit()

runFile = sys.argv[1]
try:
   fpe = open(runFile, 'r')
except:
   print("Could not open" + runFile)

file = zipfile.ZipFile("weppInputsShed.zip", "w")

print("Added: " + runFile)

f = open("wepp.run","w")

for line in fpe:
   line = line.strip()
   if ("." in line):
       if ("output" not in line):
           filename = "../runs/" + line
           f.write(line + "\n")
           if (os.path.exists(filename) == True):
              file.write(filename, os.path.basename(filename), zipfile.ZIP_DEFLATED)
              print("Added: " + filename)
       else:
          line = line[10:]
          f.write(line + "\n")
   else:
      f.write(line + "\n")
f.close()

file.write("wepp.run", os.path.basename("wepp.run"), zipfile.ZIP_DEFLATED)

file.close()

print("The WEPP input files for this run have been zipped in tools/weppInputsShed.zip")
print("Copy the zip file to another location. To run this with the WEPP FORTRAN Model:")
print("1. unzip weppInputsShed.zip")
print("2. From within the same directory as the run file redirect the run file to wepp, such as:")
print("     c:\weppinstall\wepp\wepp.exe < wepp.run")
print("5. Check the subdirectory for model outputs.")
print("--------------Done with weppzipshed --------------\n")    
