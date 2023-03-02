#
#  Modified:  Fri Nov 08 10:32:16 AM 2013
#
model = 98.4
project  =  "default.prj"
template = "default.prj"
set = none
maxChannels = 1000
soilVersion = 97.5
units = english
grid = yes
weppdos = no
cligendos = no
wepsview = yes
erosion = yes
startScreen = yes
limitred = no
limitgreen = no
3D = yes
graphics = {
   Y,Y,Y,Y,Y,Y,Y,Y,Y,Y,Y,Y
   Y,Y,Y,Y,Y,Y,Y,Y,Y,Y
   Y,Y,Y,Y,Y,Y,Y,Y,Y,Y
   Y,Y,Y,Y,Y,Y,Y,Y,Y,Y
   Y,Y,Y,Y,Y,Y,Y,Y,Y,Y
   Y,Y,Y,Y,Y,Y,Y,Y,Y,Y
   Y,Y,Y,Y,Y,Y,Y,Y,Y,Y
   Y,Y,Y,Y,Y,Y,Y,Y,Y,Y
   Y,Y,Y,Y,Y,Y,Y,Y
}
shading = {{
   watershed_soil_loss = {
       ff,0,0
    }
   watershed_sediment = {
       ff,0,0
    }
   watershed_runoff = {
       ff,0,0
    }
}}
watershed_option_ask_keep_length = yes
watershed_option_keep_length = yes
watershed_option_warn_hillshape_change = yes
zoomlevel = 1.0000
hillborderthickness = 1
channelborderthickness = 3
layout_slope_use_normalized_scale = no
soilRestrictKsat = {360,0.36,0.09,3.6e-005,0.00036,0.00036,3.6e-005,360,3.6,3.6,0.36,0.0036,0.00036,0,0,0,0,0,0,0}
