from pathlib import Path
from geo.Geoserver import Geoserver

import geopandas as gpd
import sqlalchemy as sa
import logging


def upload_raster(geoserver: Geoserver, filepath: Path, workspace: str):
    filename = filepath.name

    print("Importing " + filename)
    try:
        geoserver.create_coveragestore(
            layer_name=filepath.stem, path=str(filepath), workspace=workspace
        )
    except Exception:
        logging.exception("Error uploading " + filename + " to Geoserver")
        return False
    return True


def upload_postgis(filepath, engine):
    filename = filepath.stem

    try:
        shp_file = gpd.read_file(filepath)
        insp = sa.inspect(engine)
        if not insp.has_table(filename, schema="public"):
            shp_file.to_postgis(filename, engine, index=True, index_label="index")
            print(filename + " uploaded to PostgreSQL database!")
        else:
            print("Table already exists")
            return False
    except Exception:
        logging.exception(
            "Error uploading " + filename + " shapefile to PostgreSQL database"
        )
        return False
    return True


def upload_shapefile(geoserver, filepath, workspace, storename):
    filename = filepath.stem
    print("Uploading " + filename)
    try:
        geoserver.publish_featurestore(
            workspace=workspace, store_name=storename, pg_table=filename
        )
        print(filename + " upload completed to Geoserver!")
    except Exception as e:
        logging.exception("Error uploading " + filename + " to Geoserver")
        return False
    return True

def reset_cache(geoserver: Geoserver):
    print("reseting cache for geoserver")
    try:
        geoserver.reset()
    except Exception as e:
        logging.exception("Error reseting Geoserver")

