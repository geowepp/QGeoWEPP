@echo off
del bluebook.f80
del bluebook.sum
F:\GeoWEPP_10_1_0_1\GeoWEPP_10_1_0_1\Projects\gwpp8\utms.exe <utms.inp
F:\GeoWEPP_10_1_0_1\GeoWEPP_10_1_0_1\Projects\gwpp8\convdem.exe
F:\GeoWEPP_10_1_0_1\GeoWEPP_10_1_0_1\Projects\gwpp8\dednm.exe <one.inp
F:\GeoWEPP_10_1_0_1\GeoWEPP_10_1_0_1\Projects\gwpp8\raspro.exe
F:\GeoWEPP_10_1_0_1\GeoWEPP_10_1_0_1\Projects\gwpp8\rasfor.exe
del subwta.asc
copy SUBWTA.ARC subwta.asc
del NotDone2.txt
exit
@cls
