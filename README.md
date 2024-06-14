# Geoimporter

## About

Tool to import raster/shapefile layers into the Geoserver using Python package for Geoserver REST API. The interface is built with
tkinter GUI package. The tool allows users to set a directory for the layers to import and streamline the process of publishing the layers
on to the Geoserver application. The tool will go into every subdirectory and import only files with .shp or .tif extension. Shapefiles
are imported into a PostgreSQL/PostGIS DB, and then they are published on Geoserver. Therefore, the tool will need to be able to connect
to a PostgreSQL/PostGIS DB. The tool has been created to have a graphical interface for the importing scripts.

## Packages Used

- [tkinter](https://docs.python.org/3/library/tkinter.html)
- [geopandas](https://geopandas.org/en/stable/index.html)
- [sqlalchemy](https://www.sqlalchemy.org)
- [geoserver-rest](https://geoserver-rest.readthedocs.io/en/latest/)

## Requirements

Python 3.12 or higher
Anaconda 24.4.0 or higher

## Quick Setup

Install dependency packages including debian packages:
configuration.bat: windows
configuration.sh: debian linux


## Environment Setup

Use Anaconda to install environment for ease of setup. This also allows for cross platform envrionment setup with the corresponding environmnt yml files.

### Anaconda for Windows

`conda env create -f ./environments/win_environment.yml`

### Anaconda for Linux

`conda env create -f ./environments/linux_environment.yml`

## Instructions

![geoserver importer screenshot](geoimporter_screenshot.png)

### Add Geoserver and Postgres Environment Variables

- Inside .env, input geoserver information for default value for text input.(Makes workflow quicker)

### Connect to Geoserver

1. Insert geoserver URL
2. Insert geoserver username
3. Insert geoserver password
4. Click Connect button
5. Insert workspace name in Workspace field
6. Click "Dir" button
5a. Navigate to path that the raster files are stored and select files
7. Click Import

### Connect to PostgreSQL/PostGIS DB

1. Insert Postgres user in PG User
2. Insert Postgres password in PG Pass Field
3. Insert Postgres ip address or hostname in PG Host Field
4. Insert Postgres port in Port field
5. Insert Postgres DB into PG DB field
6. Click DB Connect
7. Click Dir
8. Navigate to path that the shapefiles are stored and select files
9. Click Import


## Upcoming 

- Geoserver deletion for Stores and Layers
- Geoserver publishing for Layers
- Uploading to PostGIS
- Deleting from PostGIS
- List Layers on PostGIS
