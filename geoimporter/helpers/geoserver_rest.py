from pathlib import Path
from geo.Geoserver import Geoserver
import geopandas as gpd
import sqlalchemy as sa
import logging


def upload_raster(geoserver: Geoserver, filepath: Path, workspace: str):
    """
    Upload Raster file to Geoserver
    Args:
        geoserver: The Geoserver Connection handle
        filepath: The full path to the Raster file
        workspace: Name of workspace on Geoserver to upload the Raster to

    Returns:
        Whether the upload is successful or not

    Raises:
        Exception to log error uploading to Geoserver
        
    """
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


def upload_postgis(filepath: Path, engine: sa.Engine):
    """
    Upload shapefile to PostGIS Database.
    Args:
        filepath: The full path to the shapefile
        engine: The SQL Engine used to execute uploading of shapefile to PostGIS Database

    Returns:
        Whether the upload is successful or not

    Raises:
        Exception to log error uploading to PostGIS Database
        
    """
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


def upload_shapefile(geoserver: Geoserver, filepath: Path, workspace: str, storename: str):
    """
    Upload Shapefile to Geoserver
    Args:
        geoserver: The Geoserver Connection handle
        filepath: The full path to the Raster file
        workspace: Name of workspace on Geoserver to upload the Raster to
        storename: Name to upload into a store on Geoserver

    Returns:
        Whether the upload is successful or not

    Raises:
        Exception to log error uploading to Geoserver
        
    """
    filename = filepath.stem
    print("Uploading " + filename)
    try:
        _ = geoserver.publish_featurestore(
            workspace=workspace, store_name=storename, pg_table=filename
        )
        print(filename + " upload completed to Geoserver!")
    except Exception:
        logging.exception("Error uploading " + filename + " to Geoserver")
        return False
    return True

def reset_cache(geoserver: Geoserver):
    print("reseting cache for geoserver")
    try:
        _ = geoserver.reset()
    except Exception:
        logging.exception("Error reseting Geoserver")

