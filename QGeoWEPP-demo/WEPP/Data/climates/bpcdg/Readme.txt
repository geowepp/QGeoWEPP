
October 24, 2004

The program BPCDG.EXE is the BreakPoint Climate Data Generator
developed by Zeleke Gete of the Center for Development and
Environment, Institute of Geography, University of Bern, Bern,
Switzerland, and Thomas Winter, Department of Civil Engineering,
University of Darmstadt, Darmstadt, Germany.  Dennis Flanagan,
USDA-Agricultural Research Service, National Soil Erosion Research
Laboratory, West Lafayette, Indiana, United States has assisted
Gete and Winter in development of the program, compatibility
with WEPP, and documentation.


The BPCDG program can be used to convert precipitation data
obtained from recording raingauges to breakpoint precipitation
climate input files that can be used to run WEPP (Water Erosion
Prediction Project) erosion model simulations.

The BPCDG program is a DOS executable, that is run in a single
directory on an IBM-compatible personal computer, with the
following files:

    BPCDG.EXE -  executable program file
 xxyyyyPL.CSV -  rainfall data input file for BPCDG
 xxyyyyCS.CSV -  temperature & wind data input file for BPCDG
 xxyyyyCL.DAT -  wind tables, radiation, dew point input for BPCDG
 xxyyyyST.DAT -  station data input file for BPCDG

When executed with the properly constructed files, the program will
create the following output files:

   xxyyyy.CLI -  WEPP climate file
   xxyyyy.ERR -  BPCDG run time messages and error messages file
 xxyyyyCS.CTL -  control file used by BPCDG for rainfall data
 xxyyyyPL.CTL -  control file used by BPCDG for temperature and wind

In the above file names, the "xx" stands for a two-digit letter
code identifying a precipitation station, and the "yyyy" stands for
the four digit year of the data.  Currently the BPCDG program can
only handle input data files containing information for single
years.

Please refer to the BPCDG model documentation for a complete
description of the input and output files.

Changes in this version (5.00):
   1. Fixed bug where preciptation times in xxyyyyPL.CSV were not being converted
      to hours only. The times in xxyyyyPL.CSV should be in hours and minutes. 
      For example: 30 minutes past 6 AM would be 06.30 in the xxyyyyPL.CSV file. The
      output climate file xxyyyy.CLI for wepp will have a time of 06.50 to indicate hours and 
      fraction of an hour.

   2. Fixed bug where precipitation events on 1/1 where not being output.


WEPP Technical Support
USDA-ARS NSERL
1196 Building SOIL
West Lafayette, IN 47907-1196
USA

email:  wepp@ecn.purdue.edu
phone:  (765) 494-8673
FAX  :  (765) 494-5948
WWW  :  http://topsoil.nserl.purdue.edu
