#
# check_water_balance()
#
# Looks at the WEPP water output file and reports a summary of the water balance.
#
# Usage: checkWaterBalance waterFile slopeFile
#    where waterFile is the name of a WEPP water balance output file
#
# January 8, 2010
# Jim Frankenberger
#
import os, sys
import subprocess, shutil, signal, time


ofeLengths = {}
width = {}
precips = {}
initialH2Os = {}
initialFrozes = {}
initialSnow = {}
finalSnow = {}
finalH2Os= {}
finalFrozes = {}
runoffs = {}
drainq = {}
irr = {}
ess = {}
eps = {}
dps = {}
lats = {}
ups = {}
baseFlow = {}
upsub = {}
ers = {}
minBalance = {}
maxBalance = {}
minDay = {}
minYr = {}
maxDay = {}
maxYr = {}
firstMinBal = {}
firstMaxBal = {}
firstMinDay = {}
firstMinYr = {}
firstMaxDay = {}
firstMaxYr = {}
initialSurfStor = {}
finalSurfStor = {}
lastStor = {}
fbalance = {}


print("Starting check water balance\n")

def getTotalLen(ofe):
   totalLen = 0
   for i in range(ofe):
       totalLen = totalLen + ofeLengths[i]
   return totalLen

def readWaterFile(waterFile,shed,f):
  global ofeLengths,width,precips,initialH2Os,initialFrozes,initialSnow,finalSnow,finalH2Os,finalFrozes,runoffs,drainq,irr
  global ess,eps,dps,lats,ups,upsub,ers,minBalance,maxBalance,minDay,minYr,maxDay,maxYr,firstMinBal,firstMaxBal,firstMinDay
  global firstMinYr,firstMaxDay,firstMaxYr,initialSurfStor,finalSurfStor,baseflow,lastStor
  
  f.write("Daily Water Balance Error Summarized by OFE\n\n")
#  f.write("OFE  DAY YEAR Balance Error(mm)\n")
  
  noFile = False
  firstTime = {}
  totalLen = 0
  try:
    fpe = file(waterFile,"r")
  except:
    print("Could not open water file: " + waterFile + "\n")
    noFile = True
    return -1

  for i in range(100):
     firstTime[i] = True

  for line in fpe:
        line = line.strip()
        tokens = line.split()
        numCols = len(tokens)
        irradd = 0
        tiledrain = 0
        if (numCols >= 13):    
            try:
                ofe = int(tokens[0])
                totalLen = getTotalLen(ofe)
                ofe = ofe - 1
            except ValueError:
                ofe = -999
            try:
                day = int(tokens[1])
            except ValueError:
                day = -999
            try:
                yr = int(tokens[2])
            except ValueError:
                yr = -999
            try:
                precip = float(tokens[3])
            except ValueError:
                precip = -999
            try:
                runoff = float(tokens[5])
            except ValueError:
                runoff = -999
            try:
                ep = float(tokens[6])
            except ValueError:
                ep = -999
            try:
                es = float(tokens[7])
            except ValueError:
                es = -999
                
            if (numCols >= 17):
              nextCol = 9
              try:
                er = float(tokens[8])
                pass
              except ValueError:
                er = -999
            else:
               er = 0
               nextCol = 8
                
            try:
                dp = float(tokens[nextCol])
            except ValueError:
                dp = -999
            try:
                upQ = float(tokens[nextCol+1])
            except ValueError:
                upQ = -999
                
            if (numCols > 13):
              try:
                sublat = float(tokens[nextCol+2])
              except ValueError:
                sublat = -999
            else:
                nextCol = nextCol - 1
                sublat = 0
                
            try:
                lat = float(tokens[nextCol+3])
            except ValueError:
                lat = -999 
            try:
                soilw = float(tokens[nextCol+4])
            except ValueError:
                soilw = -999
            try:
                soilf = float(tokens[nextCol+5])
            except ValueError:
                soilf = -999

            if (numCols > 13):                
              try:
                snow = float(tokens[nextCol+6])
              except ValueError:
                snow= -999
              try:
                runOFE = float(tokens[nextCol+7])
              except ValueError:
                runOFE = -999
            else:
               snow = 0
               runOFE = runoff

            if (numCols > 18):
                try:
                   tiledrain = float(tokens[nextCol+8])
                except ValueError:
                   tiledrain = -999
            else:
               irradd = 0

            if (numCols > 17):
                try:
                   irradd = float(tokens[nextCol+9])
                except ValueError:
                   irradd = -999
            else:
               tiledrain = 0   
               
            if (numCols > 20):
                try:
                    surfwater = float(tokens[nextCol+10])
                except ValueError:
                    surfwater = -999
                try:
                    baseF = float(tokens[nextCol+11])
                except ValueError:
                    baseF = -999
            else:
                surfwater = 0
                baseF = 0
                
            if (ofe >= 0):
              if (firstTime[ofe] == True):
                firstTime[ofe] = False
                initialH2Os[ofe] = soilw + es + ep + er + dp + lat + soilf + tiledrain + runOFE + snow + surfwater - precip - irradd - upQ - sublat
                # if initial precip is snow we need to not subtract it
                #if (snow > 0):
                #    initialH2Os[ofe] = initialH2Os[ofe] - snow

                # the added runon from above OFE's needs to be  removed               
                #if (ofe > 0):
                #   initialH2Os[ofe] = initialH2Os[ofe] - upQ - sublat
               
                precips[ofe] = 0
                initialFrozes[ofe] = 0
                initialSnow[ofe] = 0
                finalH2Os[ofe] = 0
                finalFrozes[ofe] = 0
                finalSnow[ofe] = 0
                runoffs[ofe] = 0
                ess[ofe] = 0
                eps[ofe] = 0
                dps[ofe] = 0
                lats[ofe] = 0
                ups[ofe] = 0
                baseFlow[ofe] = 0
                upsub[ofe] = 0
                ers[ofe] = 0
                irr[ofe] = 0
                drainq[ofe] = 0
                maxBalance[ofe] = -1000
                maxDay[ofe] = 0
                maxYr[ofe] = 0
                minBalance[ofe] = 1000
                minDay[ofe] = 0
                minYr[ofe] = 0
                firstMaxDay[ofe] = 0
                firstMinDay[ofe] = 0
                firstMaxYr[ofe] = 0
                firstMinYr[ofe] = 0
                firstMaxBal[ofe] = 0
                firstMinBal[ofe] = 0
                finalSurfStor[ofe] = 0
                initialSurfStor[ofe] = 0
                lastStor[ofe] = 0

              precips[ofe] = precips[ofe] + precip
              finalH2Os[ofe] = soilw
              finalFrozes[ofe] = soilf
              finalSnow[ofe] = snow
              finalSurfStor[ofe] = surfwater
              
              # runoff is over the total length, need to scale to this OFE
              if (shed == 0):
                 runoffs[ofe] = runoffs[ofe] + (runoff*(totalLen/ofeLengths[ofe]))
                 ro = (runoff*(totalLen/ofeLengths[ofe]))
              else:
                 runoffs[ofe] = runoffs[ofe] + runoff
                 ro = runoff
              ess[ofe] = ess[ofe] + es
              eps[ofe] = eps[ofe] + ep
              ers[ofe] = ers[ofe] + er
              dps[ofe] = dps[ofe] + dp
              lats[ofe] = lats[ofe] + lat
              ups[ofe] = ups[ofe] + upQ
              upsub[ofe] = upsub[ofe] + sublat
              irr[ofe] = irr[ofe] + irradd
              drainq[ofe] = drainq[ofe] + tiledrain
              baseFlow[ofe] = baseFlow[ofe] + baseF

              balance = (precips[ofe] + ups[ofe] + upsub[ofe]- runoffs[ofe] - ess[ofe] - eps[ofe] - ers[ofe] -
                  dps[ofe] - lats[ofe] + initialH2Os[ofe] - finalH2Os[ofe] + initialFrozes[ofe] - finalFrozes[ofe] +
                  initialSnow[ofe] - finalSnow[ofe] +  irr[ofe] - drainq[ofe] + initialSurfStor[ofe] - finalSurfStor[ofe])

              if (balance > maxBalance[ofe]):
                  maxBalance[ofe] = balance
                  maxDay[ofe] = day
                  maxYr[ofe] = yr

              if (balance < minBalance[ofe]):
                  minBalance[ofe] = balance
                  minDay[ofe] = day
                  minYr[ofe] = yr

              if (balance > 3):
                   if (firstMaxDay[ofe] == 0):
                       firstMaxDay[ofe] = day
                       firstMaxYr[ofe] = yr
                       firstMaxBal[ofe] = balance
                       
              if (balance < -3):
                  if (firstMinDay[ofe] == 0):
                      firstMinDay[ofe] = day
                      firstMinYr[ofe] = yr
                      firstMinBal[ofe] = balance
              str2 = "%d     %d   %d     %8.2f" % (ofe+1, day, yr, balance)
#              print(str2)
#              f.write(str2 + "\n")
              lastStor[ofe] = finalSurfStor[ofe]

  fpe.close()               
  return

def getOFEInfo(slopeFile,shedSlope):
  noFile = False
  try:
    fpe = file(slopeFile,"r")
  except:
    print("Could not open slope file: " + slopeFile + "\n")
    noFile = True
    return -1

  line = fpe.readline()
  line = line.strip()
  ver = float(line)
  needOFECount = True
  if (ver < 10):
      # this is really the number of OFE's
      ofes = int(ver)
      needOFECount = False

  # read any comment lines that begin with a #
  doneComments = False
  while (doneComments == False):  
     line = fpe.readline()
     line = line.strip()
     if (line[0] != '#'):
        doneComments = True

  if (needOFECount == True):
      ofes = int(line)
      line = fpe.readline()
      line = line.strip()

  # read aspect and width
  tokens = line.split()
  try:
      aspect = float(tokens[0])
  except:
      aspect = -1

  try:
      width[0] = float(tokens[1])
  except:
      width[0] = -1

  # for each OFE get the length
  for i in range(ofes):
    # read line with number of slope points and length
    line = fpe.readline()
    line = line.strip()
    tokens = line.split()
    try:
        ofeLengths[i] = float(tokens[1])
    except:
        ofeLengths[i] = -1
    # skip the line with the detail slope points
    line = fpe.readline()

    if (shedSlope == 1):
        # read line with aspect and width
        line = fpe.readline()
        line = line.strip()
        tokens = line.split()
        try:
           aspect = float(tokens[0])
        except:
           aspect = -1

        try:
           width[i+1] = float(tokens[1])
        except:
           width[i+1] = -1
    else:
        width[i+1] = width[0]
  fpe.close()        
   
  return ofes

#
# Open the slope file to figure out the number of OFE's and their lengths.
#
firstTime = True



if (len(sys.argv) != 4):
    print("Usage: checkWaterBalance waterFile slopeFile 0|1\n")
    print("    0=hillslope data, 1=watershed data\n")
    exit()

waterFile = sys.argv[1]
slopeFile = sys.argv[2]

shed = int(sys.argv[3])

ofes = getOFEInfo(slopeFile,shed)

f = open('output.txt', 'w')
 
readWaterFile(waterFile,shed,f)

#
# compute the water balance
#
if (shed == 1):
    print("Most values represent what is occuring in the channels and do not include the hillslopes. The area in this case is the channel area and does not include the hillslopes.")
    
for i in range(ofes):
#   Figure out the amount of water available to runoff, plant evap, soil evap, residue evap, drainage, later flow, deep seepage
#   baseflow is included in the surface runon (ups) varaible
    waterAvail = precips[i] - (finalH2Os[i]-initialH2Os[i]) - (finalFrozes[i]-initialFrozes[i]) - (finalSnow[i]-initialSnow[i]) + ups[i] + irr[i] + upsub[i] - (finalSurfStor[i]-initialSurfStor[i]) 
    area = (ofeLengths[i]*width[i])/1000
    idx = str(0)
    f.write("\n-------------------------------------------------------------------------\n\n")
    str2 = "OFE: " + str(i+1) + " Area(m^2)=" + str(ofeLengths[i]*width[i]) + " Length(m)=" + str(ofeLengths[i]) + " Width(m)=" + str(width[i])
    print(str2)
    f.write(str2 + "\n")
    if (shed == 1):
      str2 = "+Precip(mm):        %12.2f   %12.2f (m^3) (This channel (#%d) area only)" % (precips[i], precips[i]*area,i+1)
    else:
      str2 = "+Precip(mm):        %12.2f   %12.2f (m^3)" % (precips[i], precips[i]*area)
    print(str2)
    f.write(str2 + "\n")
    if (shed == 1):
      str2 = "-Runoff(mm):        %12.2f   %12.2f (m^3) (This channel (#%d) area only)" % (runoffs[i], runoffs[i]*area,i+1)
    else:
      str2 = "-Runoff(mm):        %12.2f   %12.2f (m^3)   %12.2f%%" % (runoffs[i], runoffs[i]*area,(runoffs[i]/waterAvail)*100)
    print(str2)
    f.write(str2 + "\n")
    if (shed == 1):
      str2 = "-Soil Evap(mm):     %12.2f   %12.2f (m^3) (This channel (#%d) area only)" % (ess[i], ess[i]*area,i+1)
    else:
      str2 = "-Soil Evap(mm):     %12.2f   %12.2f (m^3)   %12.2f%%" % (ess[i], ess[i]*area, (ess[i]/waterAvail)*100)
    print(str2)
    f.write(str2 + "\n")
    if (shed == 1):
       str2 = "-Plant Evap(mm):    %12.2f   %12.2f (m^3) (This channel (#%d) area only)" % (eps[i], eps[i]*area,i+1)
    else:
       str2 = "-Plant Evap(mm):    %12.2f   %12.2f (m^3)   %12.2f%%" % (eps[i], eps[i]*area, (eps[i]/waterAvail)*100)
    print(str2)
    f.write(str2 + "\n")
    if (shed == 1):
       str2 = "-Residue Evap(mm):  %12.2f   %12.2f (m^3) (This channel (#%d) area only)" % (ers[i],ers[i]*area,i+1)
    else:
       str2 = "-Residue Evap(mm):  %12.2f   %12.2f (m^3)   %12.2f%%" % (ers[i],ers[i]*area, (ers[i]/waterAvail)*100)
    print(str2)
    f.write(str2 + "\n")
    if (shed == 1):
       str2 = "-Deep seep(mm):     %12.2f   %12.2f (m^3)  (This channel (#%d) area only)" % (dps[i], dps[i]*area,i+1)
    else:
       str2 = "-Deep seep(mm):     %12.2f   %12.2f (m^3)   %12.2f%%" % (dps[i], dps[i]*area, (dps[i]/waterAvail)*100)
    print(str2)
    f.write(str2 + "\n")
    if (shed == 1):
       str2 = "-Lat Flow(mm):      %12.2f   %12.2f (m^3) (This channel (#%d) area only)" % (lats[i], lats[i]*area,i+1)
    else:
       str2 = "-Lat Flow(mm):      %12.2f   %12.2f (m^3)   %12.2f%%" % (lats[i], lats[i]*area, (lats[i]/waterAvail)*100)
    print(str2)
    f.write(str2 + "\n")
    if (shed == 1):
      str2 = "-Tile Drainage(mm): %12.2f   %12.2f (m^3) (This channel (#%d) area only)" % (drainq[i], drainq[i]*area,i+1)
    else:
      str2 = "-Tile Drainage(mm): %12.2f   %12.2f (m^3)   %12.2f%%" % (drainq[i], drainq[i]*area, (drainq[i]/waterAvail)*100)
    print(str2)
    f.write(str2 + "\n")
    if (shed == 1):
      str2 = "+Initial Soil Water(mm): %12.2f   %12.2f (m^3) (This channel (#%d) area only)" % (initialH2Os[i], initialH2Os[i]*area,i+1)
    else:
      str2 = "+Initial Soil Water(mm): %12.2f   %12.2f (m^3)" % (initialH2Os[i], initialH2Os[i]*area)
    print(str2)
    f.write(str2 + "\n")
    if (shed == 1):
       str2 = "-Final Soil Water(mm): %12.2f   %12.2f (m^3) (This channel (#%d) area only)" % (finalH2Os[i], finalH2Os[i]*area,i+1)
    else:
       str2 = "-Final Soil Water(mm): %12.2f   %12.2f (m^3)" % (finalH2Os[i], finalH2Os[i]*area)
    print(str2)
    f.write(str2 + "\n")
    if (shed == 1):
       str2 = "+Initial Frozen Soil Water(mm): %12.2f   %12.2f (m^3) (This channel (#%d) area only)" % (initialFrozes[i], initialFrozes[i]*area,i+1)
    else:
       str2 = "+Initial Frozen Soil Water(mm): %12.2f   %12.2f (m^3)" % (initialFrozes[i], initialFrozes[i]*area)
    print(str2)
    f.write(str2 + "\n")
    if (shed == 1):
       str2 = "-Final Frozen Soil Water(mm): %12.2f %12.2f (m^3) (This channel (#%d) area only)" % (finalFrozes[i], finalFrozes[i]*area,i+1)
    else:
       str2 = "-Final Frozen Soil Water(mm): %12.2f %12.2f (m^3)" % (finalFrozes[i], finalFrozes[i]*area)
    print(str2)
    f.write(str2 + "\n")
    if (shed == 1):
      str2 = "+Initial Snow Water(mm): %12.2f %12.2f (m^3) (This channel (#%d) area only)" % (initialSnow[i], initialSnow[i]*area,i+1)
    else:
      str2 = "+Initial Snow Water(mm): %12.2f %12.2f (m^3)" % (initialSnow[i], initialSnow[i]*area) 
    print(str2)
    f.write(str2 + "\n")
    if (shed == 1):
      str2 = "-Final Snow Water(mm): %12.2f %12.2f (m^3) (This channel (#%d) area only)" % (finalSnow[i], finalSnow[i]*area,i+1)
    else:
      str2 = "-Final Snow Water(mm): %12.2f %12.2f (m^3)" % (finalSnow[i], finalSnow[i]*area)
    print(str2)
    f.write(str2 + "\n")
    str2 = "+Upstream surface runon(mm): %12.2f  %12.2f (m^3)" % (ups[i]-baseFlow[i], (ups[i]-baseFlow[i])*area)
    print(str2)
    print("     * above does not include baseflow\n")
    f.write(str2 + "\n")
    f.write("     * above does not include baseflow\n")
    str2 = "+Upstream subsurface runon(mm): %12.2f   %12.2f (m^3)" % (upsub[i], upsub[i]*area)
    print(str2)
    f.write(str2 + "\n")
    if (shed == 1):
      str2 = "+Irrigation Water(mm): %12.2f   %12.2f (m^3) (This channel (#%d) area only)" % (irr[i], irr[i]*area,i+1)
    else:
      str2 = "+Irrigation Water(mm): %12.2f   %12.2f (m^3)" % (irr[i], irr[i]*area)
    print(str2)
    f.write(str2 + "\n")
    str2 = "+Initial Surface Storage(mm): %12.2f  %12.2f (m^3)" % (initialSurfStor[i], initialSurfStor[i]*area)
    print(str2)
    f.write(str2 + "\n")
    str2 = "-Final Surface Storage(mm): %12.2f   %12.2f (m^3)" % (finalSurfStor[i], finalSurfStor[i]*area)
    print(str2)
    f.write(str2 + "\n")
    str2 = "+Baseflow External (mm): %12.2f   %12.2f (m^3)" % (baseFlow[i], baseFlow[i]*area)
    print(str2)
    f.write(str2 + "\n")

#     ups includes the baseflow    
    balance = precips[i] + ups[i] + upsub[i]- runoffs[i] - ess[i] - eps[i] - ers[i] - dps[i] - lats[i] + initialH2Os[i] - finalH2Os[i] + \
        initialFrozes[i] - finalFrozes[i] + initialSnow[i] - finalSnow[i] +  irr[i] - drainq[i] + initialSurfStor[i] - finalSurfStor[i]
        
    str2 = "Final Water Balance Error (mm):  %8.2f\n" % (balance)
    fbalance[i] = balance
    print(str2)
    f.write(str2)
    str2 = "   Maximum surplus balance error occurred on day %d-%d: %8.2f\n" % (maxDay[i], maxYr[i], maxBalance[i])
    print(str2)
    f.write(str2)
    str2 = "   First day with surplus > 3mm: %d-%d: %8.2f\n" % (firstMaxDay[i], firstMaxYr[i], firstMaxBal[i])
    print(str2)
    f.write(str2)
    str2 = "   Maximum missing balance error occurred on day %d-%d: %8.2f\n" % (minDay[i], minYr[i], minBalance[i])
    print(str2)
    f.write(str2)
    str2 = "   First day with missing > 3mm: %d-%d: %8.2f\n" % (firstMinDay[i], firstMinYr[i], firstMinBal[i])
    print(str2)
    f.write(str2)

print("\n\n")
f.write("\n\n")

for i in range(ofes):
    str2 = "Final Water Balance Error for OFE %d:  %8.2f (mm)" % (i+1,fbalance[i])
    print(str2)
    f.write(str2 + "\n")
    
f.close()    
