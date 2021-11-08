# Program wxwarning
# by Todd Arbetter (todd.e.arbetter@gmail.com)
# Software Engineer, IXMap, Golden, CO

# collects latests National Weather Service Warnings, Watches, Advisories,
# and Statements, plots shapefiles on an interactive map in various colors.
# The map is able to pan and zoom, and on mouseover will give the type of
# weather statement, start, and expiry.

# created with streamlit and folium

# import some libraries
import numpy as np
import pandas as pd
import geopandas as gpd
import streamlit as str
import folium as fl
import streamlit_folium as sf
import branca.colormap as cm
import os as os
import pathlib as path
import datetime as dt

#newdata: set to False for streamlit app which cannot download data
newdata = False
#newdata = True

#streamlit message size
MESSAGE_SIZE_LIMIT = 300.*int(1e6) #300 MB

# get the current time in UTC (constant reference timezone)
timestamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec='minutes')

str.title('Current U.S. Weather Statements')

if (newdata == True):
    str.header(timestamp[0:10]+' '+timestamp[11:16]+' UTC')
else:
    str.header('Sample Map')

#get latest wx warnings from NWS
home = path.PurePath('.')
#os.chdir(home)
#str.write('home:',home)
#str.write('os files home:',os.listdir('.'))

#list files
p = path.Path(home).glob('current_all/*')
files = [x for x in p if x.is_file()]
#str.write('pathlib files current_all:',files)

if (newdata == True):
# Get latest wx warnings from NWS
# Check for existence of current_all directory; if it doesn't exist, create it
    if (os.path.isdir('current_all') == False ):
        os.mkdir('./current_all')
        str.write('created current_all')
# cd into current_all and clear it out
    #str.write('os files current_all:',os.listdir('current_all/'))
    os.chdir('current_all')
    os.system('rm -rf current_*')
    url='https://tgftp.nws.noaa.gov/SL.us008001/DF.sha/DC.cap/DS.WWA/current_all.tar.gz'
    os.system('wget -q https://tgftp.nws.noaa.gov/SL.us008001/DF.sha/DC.cap/DS.WWA/current_all.tar.gz')
    os.system('tar -xzf current_all.tar.gz')
    os.system('rm -rf current_all.tar.gz')
#   str.write('os files current_all:',os.listdir('current_all/'))
else:
    #str.write('os files:',os.listdir('current_all/'))
    os.chdir('current_all')

#    os.system('ls -lh')

# Read in weather info.  Read in current_warnings to test with a small shapefile
filepath = './current_all.shp'
if path.Path(filepath).exists():
    #str.write(filepath,' exists')
    weatherdf = gpd.read_file(filepath)
#   str.write(weatherdf.head())
else:
    str.write(filepath,' not found')
    exit()
     

os.chdir('..')

# drop unnecessary columns from geodataframe
weatherdf = weatherdf.drop(columns=['PHENOM','SIG','WFO','EVENT','ONSET','ENDS','CAP_ID','MSG_TYPE','VTEC'])

#str.write(weatherdf.head())

#Assign an integer value to each unique warning
#so they will plot in different colors later

wxwarnings = {}
k = 0
for w in weatherdf['PROD_TYPE'].unique():
    wxwarnings[w]=k
#    print(w,k)
    k += 10

#str.write(wxwarnings)

#Get min and max values of wxwarning id codes
all_values = wxwarnings.values()

max_wxwarnings = max(all_values)
min_wxwarnings = min(all_values)

#str.write('wxwarnings:',min_wxwarnings,max_wxwarnings)

# Now create an column PROD_ID which duplicates PROD_TYPE
weatherdf["PROD_ID"]=weatherdf['PROD_TYPE']

# and fill with values from the dictionary wxwarnings
weatherdf['PROD_ID'].replace(wxwarnings,inplace=True)

#str.write(weatherdf.head())

#verify no missing/Nan
missing = weatherdf.isnull().sum().sum()
#str.write('Number of missing values:',missing)

#explicitly create an index column with each entry having a unique value for indexing
weatherdf['UNIQUE_ID']=weatherdf.index

#str.write(weatherdf.head(10))

# write weatherdf to a geoJson file
weatherdf.to_file("wxwarning.geojson", driver='GeoJSON')

#str.write('wrote GeoJSON file')

# Use branca.colormap instead of choropleth


#create a b/w map of CONUS
mbr = fl.Map(location=[50.0,-120.0],zoom_start=3,tiles="Stamen Toner")

# create a color map that spans the range of weather product ids
colormap = cm.linear.YlGnBu_09.scale(min_wxwarnings,max_wxwarnings)

#colormap

#Add weather data to map with mouseover (this will take a few minutes), include tooltip

fl.GeoJson(weatherdf,
               style_function = lambda x: {"weight":0.5, 
                            'color':'red',
                            'fillColor':colormap(x['properties']['PROD_ID']), 
                            'fillOpacity':0.5
               },
           
               highlight_function = lambda x: {'fillColor': '#000000', 
                                'color':'#000000', 
                                'fillOpacity': 0.25, 
                                'weight': 0.1
               },
               
               tooltip=fl.GeoJsonTooltip(
                   fields=['PROD_TYPE','ISSUANCE','EXPIRATION'], 
                   aliases=['Hazard', 'Starts','Expires'],
                   labels=True,
                   localize=True
               ),
              ).add_to(mbr)

sf.folium_static(mbr)
str.header('Source: National Weather Service, USA')

# Save weather map to an HTML fle
mbr.save('wxwarning.html')

#str.write('Done')

#os.system('ls -lh')
