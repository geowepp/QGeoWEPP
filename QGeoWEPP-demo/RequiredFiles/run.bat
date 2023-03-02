echo "Convert DEM to TOPAZ format and adjust control file"
demanly
echo "Run TOPAZ for channel delineation"
pause
dednm
rasfor
echo "NETFUL.ARC has channel grid"
pause
echo "Run TOPZ for watershed delineation"
convdem
echo 1 | dednm
raspro
rasfor
echo "SUBWTA.ARC has watershed subcatchment grid"
pause
echo "Running UTMS to get lat+long
utms < utms.inp
echo "Running climport to select climate"
climport
echo "Running topwepp2 to run WEPP"
topwepp2
echo "wepploss.arc, weppfloss.arc, ww2output.txt summary.txt are main output files
echo "Modifying hillslope 21 soil"
topwepp4 *.sol 32 1
echo "Modifying hillslope 21 management"
topwepp4 *.rot 32 1
echo "Redo WEPP run"
topwepp2
echo "Done"