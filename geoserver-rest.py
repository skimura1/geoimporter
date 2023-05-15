import re
import geopandas as gpd

def tiff_walk(geoserver, files, workspace):
    """
    Walk through all the directories looking for TIFF/Raster files and uploading to Geoserver
    :param geoserver: the geoserver that we want to publish the files onto
    :param tiff_dir: the directory that we are trying to "walk through"
    :param workspace: the workspace on geoserver that will hold the layer
    :return: the status of the operation; whether it has failed or succeeded
    """
    error_layer = []
    import_num = 0
    print("Tiff file importing initialized...")
    for (root_dir, dirs, files) in os.walk(tiff_dir):
        for file in files:
            if re.search(r'.tif$', file):
                filename = file[:-4]
                print('Uploading ' + filename)
                try:
                    geoserver.create_coveragestore(layer_name=filename, path=root_dir + '/' + file, workspace=workspace)
                    import_num += 1
                except Exception as e:
                    error_tuple = (filename, e)
                    error_layer.append(filename)
                    print('Error with ' + filename)
                    continue
    status = 'Successfully imported ' + str(import_num) + ' layers!'
    print(status)
    if len(error_layer):
        status += 'There was an error in' + ''.join(error_layer)
    return status

def upload_raster(file, path, workspace):
    


def shp_walk(geoserver, engine, shp_dir, workspace, storename):
    """
    Walk through all the directories looking for shapefiles and uploading them to the PostgreSQL/POSTGIS DB.
    Then make a connection the geoserver, so the layers on PostgreSQL/POSTGIS DB can be published on Geoserver.
    :param geoserver: the geoserver that we want to publish the files onto
    :param engine: the database connection that we want to upload the files from
    :param shp_dir: the directory that the shapefiles are stored
    :param workspace: the workspace on geoserver that will hold the layer
    :param storename: the storename on geoserver that will be basis of connection to POSTGIS DB
    :return: the status of the operation; whether it has failed or succeeded
    """
    error_layer = []
    import_num = 0
    insp = sa.inspect(engine)
    print("Shape file importing initialized...")
    for (root_dir, dirs, files) in os.walk(shp_dir):
        for file in files:
            filename = file[:-4]
            if re.search(r'.shp$', file):
                print("Uploading " + filename)
                shp_file = gpd.read_file(root_dir + "/" + file)
                if not insp.has_table(filename, schema="public"):
                    try:
                        shp_file.to_postgis(filename, engine, index=True, index_label='Index')
                    except Exception as e:
                        error_tuple = (filename, e)
                        error_layer.append(filename)
                        print("Error with " + filename)
                        continue
                else:
                    print(filename + ' exists already in PostgreSQL database!')
                if geoserver.publish_featurestore(workspace=workspace, store_name=storename, pg_table=filename) is None:
                    print(filename + " upload completed to Geoserver!")
                    import_num += 1
    status = 'Successfully imported ' + str(import_num) + ' layers!'
    if len(error_layer):
        status += "There was an error in" + ''.join(error_layer)
    return status

