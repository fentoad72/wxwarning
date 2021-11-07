Sample streamlit python program
todd arbetter (todd.e.arbetter@gmail.com)
Software Engineer
IXMap, Golden, Colorado

This is an alpha release


README.md -this file
wxwarning.py - python file with folium and streamlit commands. run this file with "streamlit run wxwarning.py"
requirements.txt - package requirements to run this code
environment.yml - conda environment geo_env yml file
current_all/ - directory containing ArcGIS type information for NWS warnings, watches, and advisories (may be large); scrubbed and updated at runtime; if streamlit cannot find this directory it will create one in the directory it runs in
current_warning/ - directory containing ArcGIS info for NWS warnings only (much smaller); use for testing
weatherdf.geoson - geojson file created by wxwarning.py, contains weatherdf geodataframe
wxwarning.html - html page created by wxwarning.py contaning the interactive map

In wxwarning.py, set warnings = True to only plot NWS weather warnings, not all statements.  Note: this may not work if there are no current warnings.

In wxwarning.ph, newdata is set to False by default because Streamlit.io won't allow downloading data.  Set to true to get latest NWS updates (but not on Streamlit App)
