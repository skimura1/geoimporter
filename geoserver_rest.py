import os

import geopandas as gpd
import sqlalchemy as sa
import logging

def upload_raster(geoserver, filepath, workspace):
    filename = os.path.basename(filepath)

    print("Importing " + filename)
    try:
        geoserver.create_coveragestore(layer_name=filename[:-4], path=filepath, workspace=workspace)
    except Exception:
        logging.exception("Error uploading " +  filename + " to Geoserver")
        return False
    return True

def upload_postgis(filepath, engine):
    filename = os.path.basename(filepath)
    try:
        shp_file = gpd.read_file(filepath)
        insp = sa.inspect(engine)
        if not insp.has_table(filename[:-4], schema="public"):
            shp_file.to_postgis(filename[:-4], engine, index=True, index_lable='index')
            print(filename + " uploaded to PostgreSQL database!")
        else:
            print("Table already exists")
            return False
    except Exception:
        logging.exception("Error uploading " + filename + " shapefile to PostgreSQL database")
        return False
    return True

def upload_shapefile(geoserver, filepath, workspace, storename):
    filename = os.path.basename(filepath)
    print("Uploading " + filename)
    try:
        geoserver.publish_featurestore(workspace=workspace, store_name=storename, pg_table=filename[:-4])
        print(filename + " upload completed to Geoserver!")
    except Exception as e:
        logging.exception("Error uploading " + filename + " to Geoserver")
        return False
    return True

