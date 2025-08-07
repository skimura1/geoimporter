from pathlib import Path
from geo.Geoserver import Geoserver
import geopandas as gpd
import sqlalchemy as sa
import logging


def upload_raster(geoserver: Geoserver, filepath: Path, workspace: str) -> bool:
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
    if not filepath.exists():
        logging.error("Raster file does not exist: %s", filepath)
        return False
        
    filename = filepath.name
    print(f"Importing {filename}")
    
    try:
        geoserver.create_coveragestore(
            layer_name=filepath.stem, path=str(filepath), workspace=workspace
        )
        logging.info("Successfully uploaded raster %s to workspace %s", filename, workspace)
        return True
    except Exception as e:
        logging.error("Error uploading %s to Geoserver: %s", filename, e)
        return False


def upload_postgis(filepath: Path, engine: sa.Engine) -> bool:
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
    if not filepath.exists():
        logging.error("Shapefile does not exist: %s", filepath)
        return False
        
    filename = filepath.stem

    try:
        shp_file = gpd.read_file(filepath)
        insp = sa.inspect(engine)
        
        if insp.has_table(filename, schema="public"):
            logging.warning("Table '%s' already exists in database", filename)
            return False
            
        shp_file.to_postgis(filename, engine, index=True, index_label="index")
        logging.info("Successfully uploaded shapefile %s to PostgreSQL database", filename)
        print(f"{filename} uploaded to PostgreSQL database!")
        return True
        
    except Exception as e:
        logging.error("Error uploading %s shapefile to PostgreSQL database: %s", filename, e)
        return False


def upload_shapefile(geoserver: Geoserver, filepath: Path, workspace: str, storename: str) -> bool:
    """
    Upload Shapefile to Geoserver
    Args:
        geoserver: The Geoserver Connection handle
        filepath: The full path to the Shapefile
        workspace: Name of workspace on Geoserver to upload the Shapefile to
        storename: Name to upload into a store on Geoserver

    Returns:
        Whether the upload is successful or not

    Raises:
        Exception to log error uploading to Geoserver
        
    """
    filename = filepath.stem
    print(f"Uploading {filename} to GeoServer")
    
    try:
        geoserver.publish_featurestore(
            workspace=workspace, store_name=storename, pg_table=filename
        )
        logging.info("Successfully uploaded shapefile %s to GeoServer workspace %s", filename, workspace)
        print(f"{filename} upload completed to Geoserver!")
        return True
    except Exception as e:
        logging.error("Error uploading %s to Geoserver: %s", filename, e)
        return False

def reset_cache(geoserver: Geoserver):
    print("reseting cache for geoserver")
    try:
        _ = geoserver.reset()
    except Exception:
        logging.exception("Error reseting Geoserver")

