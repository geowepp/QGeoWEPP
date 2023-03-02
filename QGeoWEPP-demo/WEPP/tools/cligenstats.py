import os, sys
import subprocess, shutil, signal, time, math


def getAvg(arr):
    ct = float(len(arr))
    tot = sum(arr)
    if (ct > 0):
        av = tot / ct
    else:
        av = 0
    return av

def calcTimePeakDist(tot,count,allMonths):
   bins = []
   tct = 0
   for i in range(0,12):
      bins.append(0)
      
   for i in range(0,12):
      if (count[i] > 0):
        ct = len(allMonths[i])
        for j in range(0,ct):
          val = int(allMonths[i][j]/0.083333333)
          bins[val] = bins[val] + 1
          tct = tct + 1
          
   for i in range(0,12):
       bins[i] = float(bins[i])/float(tct)
   for i in range(1,12):
     bins[i] = bins[i] + bins[i-1]
     
   return bins      
      
def calcStandDev(tot,count,allMonths):

  sds = [] 
  for i in range(0,12):
      if (count[i] > 0):
        mean = (tot[i]/count[i])
        ct = len(allMonths[i])
        sd2 = 0
        for j in range(0,ct):
          val = allMonths[i][j]
          sd2 = sd2 + ((val - mean) * (val - mean))
        sd = math.sqrt(sd2 / float(ct))
      else:
        sd = -1
      sds.append(sd)

  return sds      

def doStats(clifile,years):
    
    wetDays = [0,0,0,0,0,0,0,0,0,0,0,0]
    precip = [0,0,0,0,0,0,0,0,0,0,0,0]

    daysMon = [31,28,31,30,31,30,31,31,30,31,30,31]

    durations1 = []
    durations2 = []
    durations3 = []
    durations4 = []
    durations5 = []
    durations6 = []
    durations7 = []
    durations8 = []
    durations9 = []
    durations10 = []
    durations11 = []
    durations12 = []

    allDurs = [durations1,durations2,durations3,durations4,durations5,durations6,durations7,durations8,durations9,durations10,durations11,durations12]

    ip1 = []
    ip2 = []
    ip3 = []
    ip4 = []
    ip5 = []
    ip6 = []
    ip7 = []
    ip8 = []
    ip9 = []
    ip10 = []
    ip11 = []
    ip12 = []

    allIps = [ip1,ip2,ip3,ip4,ip5,ip6,ip7,ip8,ip9,ip10,ip11,ip12]    

    mx1 = []
    mx2 = []
    mx3 = []
    mx4 = []
    mx5 = []
    mx6 = []
    mx7 = []
    mx8 = []
    mx9 = []
    mx10 = []
    mx11 = []
    mx12 = []

    allMxs = [mx1,mx2,mx3,mx4,mx5,mx6,mx7,mx8,mx9,mx10,mx11,mx12]

    tp1 = []
    tp2 = []
    tp3 = []
    tp4 = []
    tp5 = []
    tp6 = []
    tp7 = []
    tp8 = []
    tp9 = []
    tp10 = []
    tp11 = []
    tp12 = []
    tpTotal = []
    
    allTps = [tp1,tp2,tp3,tp4,tp5,tp6,tp7,tp8,tp9,tp10,tp11,tp12]    

    avgm = []        
    
    try:
        fpe = file(clifile,"r")
    except:
        print("Could not open: " + clifile)
        return;
    try:
        outfp = file("output.txt","w")
    except:
        print("Could not open: cligenstats.txt")
        return;
              
    firstYear = -1
    lastYear = -1
    lineno = 1
    verst = ""

    for i in range(0,12):
        tpTotal.append(0)
     
    for line in fpe:
        line = line.strip()
        if (lineno == 3):
            outfp.write(line + " YEARS: " + str(years))
        if (lineno >= 16):
            tokens = line.split()
            if (len(tokens) == 13):
                yr = int(tokens[2])
                if (yr <= years):
                   month = int(tokens[1])
                   dur = float(tokens[4])
                   ipeak = float(tokens[6])
                   tp = float(tokens[5])
                   amt = float(tokens[3])
                   if (firstYear == -1):
                      firstYear = int(tokens[2])
                   lastYear = int(tokens[2])
                
                   if (amt > 0.0):
                     wetDays[month-1] = wetDays[month-1] + 1
                     precip[month-1] = precip[month-1] + amt
                     mx30 = ((amt/dur) * ipeak)
                     allDurs[month-1].append(dur)
                     allIps[month-1].append(ipeak)
                     allMxs[month-1].append(mx30)
                     allTps[month-1].append(tp)
                     tpTotal[month-1] = tpTotal[month-1] + tp
                
        lineno = lineno + 1
    for i in range(0,12):
      avgm.append(getAvg(allDurs[i]))

    str2 = ""
    
    for i in range(0,12):
       if (i==0):
           str2 = '%8.2f' % (avgm[i])
       else:
           str2 = str2 + "  " + '%8.2f' % (avgm[i])

    str1 = "%-45s" % ("[1] " + verst + " \"CLI AVG DUR (HR)\"")       
    outfp.write("\n" + str1 + str2)

    del avgm[:]
    for i in range(0,12):
      avgm.append(getAvg(allMxs[i]))

    str2 = ""
    
    for i in range(0,12):
      if (i==0):
        str2 = '%8.2f' % (avgm[i]/25.4)   
      else:
       str2 = str2 + "  " + '%8.2f' % (avgm[i]/25.4)

    str1 = "%-45s" % ("[2] " + verst + " \"CLI AVG IP(in/hr)\"")
    
    outfp.write("\n" + str1 + str2)

    del avgm[:]
    for i in range(0,12):
      avgm.append(getAvg(allTps[i]))

    str2 = ""
    for i in range(0,12):
      if (i==0):
        str2 = '%8.2f' % (avgm[i])   
      else:
       str2 = str2 + "  " + '%8.2f' % (avgm[i])

    str1 = "%-45s" % ("[36] " + verst + " \"CLI AVG PEAK LOC\"")
    outfp.write("\n" + str1 + str2)    

    sdTp = calcStandDev(tpTotal,wetDays,allTps)
    tpDist = calcTimePeakDist(tpTotal,wetDays,allTps)

    str2 = ""
    for i in range(0,12):
      if (i==0):
        str2 = '%8.2f' % (sdTp[i])   
      else:
       str2 = str2 + "  " + '%8.2f' % (sdTp[i])
       
    str1 = "%-45s" % ("[37] " + verst + " \"CLI SD PEAK LOC\"")
    outfp.write("\n" + str1 + str2)        

    str2 = ""
    for i in range(0,12):
      if (i==0):
        str2 = '%8.2f' % (tpDist[i])   
      else:
       str2 = str2 + "  " + '%8.2f' % (tpDist[i])
       
    str1 = "%-45s" % ("[38] " + verst + " \"CLI PEAK DIST\"")
    outfp.write("\n" + str1 + str2)

    del avgm[:]
    for i in range(0,12):
        if (len(allMxs[i]) > 0):
           avgm.append(max(allMxs[i]))
        else:
           avgm.append(0)
    str2 = ""
    
    for i in range(0,12):

       if (i==0):
         str2 = '%8.2f' % (avgm[i]/25.4)
       else:
         str2 = str2 + "  " + '%8.2f' % (avgm[i]/25.4)

    str1 = "%-45s" % ("[14] " + verst + " \"CLI MAX IP(in/hr)\"")       
    outfp.write("\n" + str1 + str2)

    str2 = ""
    years = (lastYear-firstYear) + 1
    for i in range(0,12):

       if (i==0):
         str2 = '%8.2f' % (float(wetDays[i])/years)
       else:
         str2 = str2 + "  " + '%8.2f' % (float(wetDays[i])/years)

    str1 =  "%-45s" % ("[16] " + verst + " \"CLI WET DAYS\"")      
    outfp.write("\n" + str1 + str2)
    for i in range(0,12):

       if (i==0):
         if (wetDays[i] > 0):
            str2 = '%8.2f' % ((precip[i]/float(wetDays[i]))/25.4)
         else:
            str2 = '%8.2f' % (zero)   
       else:
         if (wetDays[i] > 0):
            str2 = str2 + "  " + '%8.2f' % ((precip[i]/float(wetDays[i]))/25.4)
         else:
            str2 = str2 + "  " + '%8.2f' % (zero)

    str1 = "%-45s" % ("[18] " + verst + " \"CLI MEAN P /Storm (in)\"")           
    outfp.write("\n" + str1 + str2)
    
    outfp.close()
#
#
#
print("----------Starting cligenstats--------------\n")

if (len(sys.argv) != 4):
    print("Usage: cligenstats runfile clifile 0|1\n")
    print("--------------Done with cligenstats--------------\n")
    exit()

clifile = sys.argv[2]
runfile = sys.argv[1]
ty = sys.argv[3]

try:
    fpe = file(runfile,"r")
except:
    print("Could not open: " +runfile)
    exit

isShed = int(ty)

lastLine = ""
prevline = ""
# hillslope version has years on second to last line
for line in fpe:
    lastLine = prevline
    line = line.strip()
    prevline = line
# watershed version has years on last line
if (isShed == 1):
    lastLine = prevline
    
fpe.close()
years = int(lastLine)
isShed = int(ty)
print("Statistics for " + str(years) + " years.")
doStats(clifile,years)
