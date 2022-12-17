import os
import re

import geopandas as gpd
import sqlalchemy as sa
from geo.Geoserver import Geoserver

# Variables
geo_user = 'INSERT GEO USERNAME'
geo_pass = 'INSERT GEO PASS'
geo_host = 'INSERT GEO HOSTNAME'
geo_workspace = 'INSERT GEO WORKSPACE'
geo_storename = 'INSERT GEO STORENAME'
pg_user = 'INSERT PG USERNAME'
pg_passw = 'INSERT PG PASSWORD'
pg_host = 'INSERT PG HOST IP ADDRESS'
pg_port = 'INSERT PG PORT'
pg_db = 'INSERT PG DB'


# Create connection to Geoserver and starting workspace
geo = Geoserver(geo_host, username=geo_user, password=geo_pass)

geo.create_workspace(workspace=geo_workspace)

# Create connection to the postgresql database
geo.create_featurestore(store_name=geo_storename, workspace=geo_workspace, db=pg_db, host=pg_host,
                        port=pg_port, pg_user=pg_user,
                        pg_password=pg_passw, schema='public')

# Create interface to handle/manage database
engine = sa.create_engine('postgresql://' + pg_user + ':' + pg_passw + '@' + pg_host + ':' + pg_port + '/' + pg_db)
insp = sa.inspect(engine)

# Import Shapefiles into the PostgreSQLDB, then publish on Geoserver
shp_dir = 'SHAPE FILE DIRECTORY'
errorLayer = []
for (root, dirs, files) in os.walk(shp_dir):
    for file in files:
        filename = file[:-4]
        if re.search(r'.shp$', file):
            print('Uploading ' + filename)
            shp_file = gpd.read_file(root + "/" + file)
            if not insp.has_table(filename, schema='public'):
                try:
                    shp_file.to_postgis(filename, engine, index=True, index_label='Index')
                except Exception as e:
                    errorTuple = (filename, e)
                    errorLayer.append(filename)
                    print("Error with " + filename)
                    continue
            else:
                print(filename + ' exists already in PostgreSQL database!')
            geo.publish_featurestore(workspace='CRC', store_name='PUC_SLR_Viewer', pg_table=filename)
            print(filename + ' upload completed!')

# Import and publish Raster (TIF Data) onto Geoserver 
tiff_dir = 'TIFF DIRECTORY'
for (root, dirs, files) in os.walk(tiff_dir):
    for file in files:
        if re.search(r'.tif$', file):
            filename = file[:-4]
            print('Uploading ' + filename)
            try:
                geo.create_coveragestore(layer_name=filename, path=root + '/' + file, workspace='CRC')
            except Exception as e:
                errorTuple = (filename, e)
                errorLayer.append(filename)
                print('Error with ' + filename)
                continue

print(errorLayer)
