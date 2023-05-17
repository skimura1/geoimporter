import os

import sqlalchemy as sa
import geopandas as gpd

def upload_raster(geoserver, filepath, workspace):
    filename = os.path.basename(filepath)

    print("Importing " + filename)
    try:
        geoserver.create_coveragestore(layer_name=filename[:-4], path=filepath, workspace=workspace)
    except Exception as e:
        print('Error with ' + filename + ' with ' + e)
        return False
    return True

def upload_postgis(filepath, engine):
    filename = os.path.basename(filepath)
    try:
        shp_file = gpd.read_file(filepath)
        insp = sa.inspect(engine)
        if not insp.has_table(filename[:-4], schema="public"):
            shp_file.to_postgis(filename[:-4], engine, index=True, index_lable='index')
        else:
            print(filename[:-4] + " already exists in PostgreSQL database!")
    except Exception as e:
        print("Error uploading shapefile to PostgreSQL database with " + filename + " with " + e)
        return False
    print(filename + " uploaded to PostgreSQL database!")
    return True

def upload_shapefile(geoserver, filepath, workspace, storename):
    filename = os.path.basename(filepath)
    print("Uploading " + filename)
    try:
        geoserver.publish_featurestore(workspace=workspace, store_name=storename, pg_table=filename[:-4])
    except Exception as e:
        print("Something went wrong with uploading Geoserver")
        return False
    print(filename + " upload completed to Geoserver!")
    return True

