import os, sys
import subprocess, shutil, signal, time, math

print("----------Starting testhill.py --------------\n")

if (len(sys.argv) != 13):
    print("Usage: testhill [with 12 parameter]\n")
    print("--------------Done with testhill-------------\n")
    exit()

outwater = sys.argv[1]
inslope = sys.argv[2]
mainfile = sys.argv[3]
graphfile = sys.argv[4]
clifile = sys.argv[5]
soilfile = sys.argv[6]
manfile = sys.argv[7]
runfile = sys.argv[8]
root = sys.argv[9]
intcon = sys.argv[10]
floatcon = sys.argv[11]
strcon = sys.argv[12]


print("<OUT_WATER_FILE>= " + outwater);
print("<IN_SLOPE_FILE>= " + inslope);
print("<OUT_MAIN_FILE>= " + mainfile)
print("<OUT_GRAPHICS_FILE>= " + graphfile)
print("<IN_CLI_FILE>= " + clifile)
print("<IN_SOIL_FILE>= " + soilfile)
print("<IN_MAN_FILE>= " + manfile)
print("<IN_RUN_FILE>= " + runfile)
print("<ROOT_DIR>= " + root)
print("integer constant= " + intcon)
print("float constant= " + floatcon)
print("string constant= " + strcon)

print("--------------Done with testhill-------------\n")