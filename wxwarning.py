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
from requests.models import ChunkedEncodingError
import streamlit as st
import folium as fl
from folium.plugins import FastMarkerCluster,MarkerCluster,MiniMap
import streamlit_folium as sf
import branca.colormap as cm
import os as os
import pathlib
import re
import random
import json
import requests
import tarfile
import wget
import datetime as dt

#st.write('loaded 9 modules')

HOME = os.getcwd()

#st.write('HOME:',HOME)

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response,destination):
    CHUNK_SIZE=32768
    i = 1
    with open(destination,"wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:
#                st.write('Chunk:',i)
                f.write(chunk)
                i += 1

#newdata: set to False for streamlit app which cannot download data
newdata = False
newdata = True

#streamlit message size (doesn't work, need to change server_utils.py)
MESSAGE_SIZE_LIMIT = 750.*(1e6) #750 MB

STREAMLIT_STATIC_PATH = pathlib.Path(st.__path__[0]) / "static"
#st.write('STR_STATIC_PATH:',STREAMLIT_STATIC_PATH)
print('STREAMLIT_STATIC:',STREAMLIT_STATIC_PATH)

# We create a downloads directory within the streamlit static asset directory
# and we write output files to it
DOWNLOADS_PATH = STREAMLIT_STATIC_PATH / "downloads"
if not DOWNLOADS_PATH.is_dir():
    DOWNLOADS_PATH.mkdir()

#st.write(str(DOWNLOADS_PATH))
#get latest wx warnings from NWS
#os.chdir(DOWNLOADS_PATH)
#os.chdir('current_all')
os.system('rm -rf ' + str(DOWNLOADS_PATH) + '/current_* ' + str(DOWNLOADS_PATH) + '/wget*')
url='https://tgftp.nws.noaa.gov/SL.us008001/DF.sha/DC.cap/DS.WWA/current_all.tar.gz'
#st.write('downloading NWS file')

session = requests.Session()

response = session.get(url,stream=True)
token = get_confirm_token(response)

if token:
    params = {'confirm':token}
    response = session.get(URL,params=params,stream=True)

destination =  str(DOWNLOADS_PATH)+'/current_all.tar.gz'

#st.write(destination)

save_response_content(response,destination)

#st.write(destination)

#wxfile = wget.download(url)
#st.write('wxfile=',wxfile)

command = 'tar -xvzf '+ destination
#st.write(command)
#os.system(command)
#st.write('type=',type(destination))

wxdata = tarfile.open(name=destination)

#st.write('type=',type(wxdata))

wxdata.list(verbose=True)

#st.write('contents:',wxdata.list(verbose=True))

os.mkdir(str(DOWNLOADS_PATH)+'/current_all')

wxdata.extractall(path=str(DOWNLOADS_PATH)+'/current_all/')

#os.remove(str(DOWNLOADS_PATH)+'/current_all.tar.gz')
files = os.system('ls -l '+ str(DOWNLOADS_PATH))
#st.write(files)

#os.chdir(HOME)
os.getcwd()


# get the current time in UTC (constant reference timezone)
timestamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec='minutes')
#st.write(timestamp[0:10], timestamp[11:16],'UTC')
#st.write('DOWNLOADS_PATH',DOWNLOADS_PATH)

#Read in weather info

infile = str(DOWNLOADS_PATH) + '/current_all/current_all.shp'
#st.write(infile)

weatherdf = gpd.read_file(infile)

#weatherdf = gpd.read_file('current_warnings/current_warnings.shp')

weatherdf = weatherdf.drop(columns=['PHENOM','SIG','WFO','EVENT','ONSET','ENDS','CAP_ID','MSG_TYPE','VTEC'])

#st.write(weatherdf.head())


st.title('Current U.S. Weather Statements')

if (newdata == True):
    st.header(timestamp[0:10]+' '+timestamp[11:16]+' UTC')
else:
    st.header('Sample Map')

#os.chdir(HOME)
os.getcwd()
os.system('ls -lh')

#Assign an integer value to each unique warning
#so they will plot in different colors later

#Assign an integer value to each unique warning
#so they will plot in different colors later

wxwarnings = {}
k = 0
for w in weatherdf['PROD_TYPE'].unique():
    wxwarnings[w]=k
#    print(w,k)
    k += 10

#st.write(wxwarnings)

#Get min and max values of wxwarning id codes
all_values = wxwarnings.values()

max_wxwarnings = max(all_values)
min_wxwarnings = min(all_values)

#st.write('wxwarnings:',min_wxwarnings,max_wxwarnings)

# Now create an column PROD_ID which duplicates PROD_TYPE
weatherdf["PROD_ID"]=weatherdf['PROD_TYPE']

# and fill with values from the dictionary wxwarnings
weatherdf['PROD_ID'].replace(wxwarnings,inplace=True)

#st.write(weatherdf.head())

#verify no missing/Nan
weatherdf.isnull().sum().sum()

#explicitly create an index column with each entry having a unique value for indexing
weatherdf['UNIQUE_ID']=weatherdf.index

#st.write(weatherdf.head(10))

# write weatherdf to a geoJson file
#weatherdf.to_file("weatherdf.geojson", driver='GeoJSON')
#st.write('wrote GeoJSON file')

# Use branca.colormap instead of choropleth


#create a b/w map of CONUS
mbr = fl.Map(location=[40.0,-95.0],zoom_start=4,tiles="Stamen Toner")

colormap = cm.linear.Set1_09.scale(min_wxwarnings,max_wxwarnings).to_step(len(set(weatherdf['PROD_ID'])))

sf.folium_static(colormap)

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

# Add minimap
MiniMap(tile_layer='stamenterrain',zoom_level_offset=-5).add_to(mbr)



sf.folium_static(mbr)
st.header('Source: National Weather Service, USA')

#save the map to an HTML file

if os.path.exists('wxwarning.html'):
    os.remove('wxwarning.html')
    
mbr.save('wxwarning.html')

#st.write('Done')

#os.system('ls -lh')
