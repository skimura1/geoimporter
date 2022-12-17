# Geoimporter v1

## About
Tool to import raster/shapefile layers into the Geoserver using Python package for Geoserver REST API. The interface is built with 
tkinter GUI package. The tool allows users to set a directory for the layers to import and streamline the process of publishing the layers
on to the Geoserver application. The tool will go into every subdirectory and import only files with .shp or .tif extension. Shapefiles
are imported into a PostgreSQL/PostGIS DB, and then they are published on Geoserver. Therefore, the tool will need to be able to connect
to a PostgreSQL/PostGIS DB. The tool has been created to have a graphical interface for the importing scripts. 

## Geoserver-rest.py
Barebones script that is the precursor to the GUI. Feel free to use the barebones script.

## Packages Used
[tkinter](https://docs.python.org/3/library/tkinter.html)
[geopandas](https://geopandas.org/en/stable/index.html)
[sqlalchemy](https://www.sqlalchemy.org)
[geoserver](https://geoserver.org)
[os](https://docs.python.org/3/library/os.html)
[re](https://docs.python.org/3/library/re.html)

## Notes
Unfortunately, due to limited will power and effort in implementing features into tkinter, there is no way to import a single layer.
There will be no further development for this current iteration of the tool because there are alternative user interface frameworks that
are more powerful and could be a good reimplemntation for this tool.

## Installation
Execute ```python -m pip install -r requirements.txt``` to install requirements
Run the Python script, ```python geoimporter.py```

## Instructions
![geoserver importer screenshot](geo_importer_screenshot.png)

Connect to Geoserver
1. Insert Geoserver URL
2. Insert geoserver username
3. Insert geoserver password
4. Click connect
Create Workspace if necessary
4a. Insert workspace name in Workspace field
4b. Click Create
Import Raster Layer
5. Insert path inside field
5a. Click "Dir" button
5b. Navigate to path that the raster files are stored
6. Click Import
Connect to PostgreSQL/PostGIS DB
7. Insert Postgres user
8. Insert Postgres Password
9. Insert Postgres host
10. Insert Postgres Port
11. Insert name of DB into storename field
12. Click DB Connect (Will Confirm connection)
13. Insert Shapefile Path
13a. Click Dir
13b. Navigate to path that the shapefiles are stored
14. Click Import
