# QGeoWEPP-demo

Welcome to QGeoWEPP, a geo-spatial interface for Water Erosion Prediction Project based on QGIS3. 

QGeoWEPP was written by Han Zhang. This interface was developed based on the GeoWEPP for ArcGIS developed by Chris S. Renschler (written in C++), migrated to QGIS using Python, with more functions to provide higher flexibility for soil erosion studies.

----------------------------------------------------------------------------

LICENSE. 

QGeoWEPP uses GNU Affero General Public License 3.0. 
         Please read it first. It is located in the LICENSE file.

----------------------------------------------------------------------------
INSTALLATION AND RUNNING.

Please install QGIS 3 or higher first, then follow the instruction below.

1. Download the QGeoWEPP-main as ZIP file.

2. Unzip the file, compress the 'QGeoWEPP-demo' folder to .ZIP file.

2. On the menu bar of QGIS, click Plugins --> Manage and Install Plugins. The Plugins manager will pop up.

3. Click 'Install from ZIP'. Click '...' to navigate to ZIP file you have justed compressed.

4. Go back to Plugins manager, click 'Installed', mark the QGeoWEPP plugin on (if it is not marked automatically). You should be able to see the menu bar for QGeoWEPP.

5. The plugin has 2 Python module dependencies that may require installation if not already installed. The modules pywinauto and pyqtgraph can be installed from a command window using the pip commands:
   ```
   pip install pywinauto
   pip install pyqtgraph
   ```



------------------------------------------------------------------------------
Validation Dataset ready.

1. A set of dataset that has been parameterized and validated for the Lucky Hills watershed in the Walnut Gulch Experimental Watershed (Renschler and Zhang, 2020; Zhang et al., 2021) is included. The dataset can be found under Measurement/ folder

2. Input data: select 'Lucky Hills' in the 'Input data' function to use the parameterized Lucky Hills dataset for soil erosion simulation.

3. Measurement data: corresponding measured values for runoff (1963 - 2017) and sediment yields (1995 - 2017) can be found at measurements/runoff_measurements_validation_dataset.csv; measurements/sediment_yield_measurements_validation_dataset.


--------------------------------------------------------------------------------

References

Renschler, C. S., & Zhang, H. (2020). Long-term, process-based, continuous simulations for a cluster of six smaller, nested rangeland watersheds near Tombstone, AZ (USA): Establishing a baseline for event-based runoff and sediment yields. Science of The Total Environment, 717, 137089. https://doi.org/10.1016/j.scitotenv.2020.137089 

Zhang, H., Renschler, C. S., Nichols, M. H., & Nearing, M. A. (2021). Long-term, process-based, continuous simulations for a small, nested rangeland watershed near Tombstone, AZ (USA): Extending model validity to include soil redistribution. Science of The Total Environment, 792, 148403. https://doi.org/10.1016/j.scitotenv.2021.148403 

Zhang, H., &amp; Renschler, C. S. (2023). Steps towards the validation of process-based long-term soil redistribution at the watershed scale using QGEOWEPP. Soil Erosion Research Under a Changing Climate, January 8-13, 2023, Aguadilla, Puerto Rico, USA. https://doi.org/10.13031/soil.23044 

Han Zhang, Chris S. Renschler (2024). QGeoWEPP: An open-source geospatial interface to enable high-resolution watershed-based soil erosion assessment. Environmental Modelling & Software, Volume 179, 2024, 106118, ISSN 1364-8152, https://doi.org/10.1016/j.envsoft.2024.106118.
