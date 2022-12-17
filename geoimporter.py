import os
import re

from tkinter import *
from tkinter import ttk, filedialog
import geopandas as gpd
import sqlalchemy as sa
import sqlalchemy.exc
from geo.Geoserver import Geoserver

def tiff_walk(geoserver, tiff_dir, workspace):
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

class GeoImporter:

    def __init__(self, root):
        self.geo = Geoserver()
        root.title("GeoImporter")

        # initiate the tkinter frame to hold widgets
        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # geoserver hostname field
        self.geo_host = StringVar()
        self.geo_host.set("https://crcgeo.soest.hawaii.edu/geoserver")
        host_entry = ttk.Entry(mainframe, width=20, textvariable=self.geo_host)
        ttk.Label(mainframe, text="Geoserver Url:").grid(column=1, row=1, sticky=E)
        host_entry.grid(column=2, row=1, sticky=(W, E))

        # geoserver username field
        self.geo_user = StringVar()
        self.geo_user.set("admin")
        user_entry = ttk.Entry(mainframe, width=10, textvariable=self.geo_user)
        ttk.Label(mainframe, text="Username:").grid(column=1, row=2, sticky=E)
        user_entry.grid(column=2, row=2, sticky=(W, E))

        # geoserver password field
        self.geo_pass = StringVar()
        pass_entry = ttk.Entry(mainframe, width=10, textvariable=self.geo_pass, show="*")
        ttk.Label(mainframe, text="Password:").grid(column=1, row=3, sticky=E)
        pass_entry.grid(column=2, row=3, sticky=(W, E))

        # geoserver connection button
        self.connected = StringVar()
        ttk.Button(mainframe, text="Connect", command=self.geoconnect).grid(column=3, row=3, sticky=E)
        # display if the geoserver was successfully connected to
        ttk.Label(mainframe, textvariable=self.connected).grid(column=4, row=3)

        # geoserver workspace field
        self.workspace = StringVar()
        # default value is "CRC"
        self.workspace.set("CRC")
        workspace_entry = ttk.Entry(mainframe, width=10, textvariable=self.workspace)
        ttk.Label(mainframe, text="Workspace:").grid(column=1, row=4, sticky=E)
        workspace_entry.grid(column=2, row=4, sticky=(W, E))

        # button to create workspace on the geoserver
        ttk.Button(mainframe, text="Create", command=self.create_workspace).grid(column=3, row=4, sticky=E)

        # tiff/raster path field
        self.tiff_path = StringVar()
        tiff_path_entry = ttk.Entry(mainframe, width=10, textvariable=self.tiff_path)
        ttk.Label(mainframe, text="Raster/TIFF Path:").grid(column=1, row=5, sticky=E)
        tiff_path_entry.grid(column=2, row=5, sticky=(W, E))
        # file explorer button
        ttk.Button(mainframe, text="Dir", command= lambda: self.get_dir(0)).grid(column=3, row=5, sticky=E)
        # import into geoserver button
        ttk.Button(mainframe, text="Import", command=self.tiffimport).grid(column=4, row=5, sticky=W)

        # display if the layers have been imported
        self.tiff_comp = StringVar()
        ttk.Label(mainframe, textvariable=self.tiff_comp).grid(column=6, row=5)

        # POSTGIS DB user field
        self.pg_user = StringVar()
        self.pg_user.set("docker")
        pg_usr_entry = ttk.Entry(mainframe, width=10, textvariable=self.pg_user)
        ttk.Label(mainframe, text="PG User:").grid(column=1, row=6, sticky=E)
        pg_usr_entry.grid(column=2, row=6, sticky=(W, E))

        # POSTGIS DB password field
        self.pg_pass = StringVar()
        pg_pass_entry = ttk.Entry(mainframe, width=10, textvariable=self.pg_pass, show="*")
        ttk.Label(mainframe, text="PG Pass:").grid(column=1, row=7, sticky=E)
        pg_pass_entry.grid(column=2, row=7, sticky=(W, E))

        # POSTGIS hostname field
        self.pg_host = StringVar()
        self.pg_host.set("128.171.159.31")
        pg_host_entry = ttk.Entry(mainframe, width=10, textvariable=self.pg_host)
        ttk.Label(mainframe, text="PG Host:").grid(column=1, row=8, sticky=E)
        pg_host_entry.grid(column=2, row=8, sticky=(W, E))

        # POSTGIS port field
        self.pg_port = StringVar()
        self.pg_port.set("32767")
        pg_port = ttk.Entry(mainframe, width=10, textvariable=self.pg_port)
        ttk.Label(mainframe, text="Port:").grid(column=3, row=8, sticky=W)
        pg_port.grid(column=4, row=8, sticky=(W, E))

        # POSTGIS database name field
        self.pg_database = StringVar()
        self.pg_database.set("PUC_SLR_Viewer")
        pg_db_entry = ttk.Entry(mainframe, width=10, textvariable=self.pg_database)
        ttk.Label(mainframe, text="PG DB:").grid(column=1, row=9, sticky=E)
        pg_db_entry.grid(column=2, row=9, sticky=(W, E))

        # geoserver storename field
        self.storename = StringVar()
        self.storename.set("SLR Viewer")
        storename_entry = ttk.Entry(mainframe, width=10, textvariable=self.storename)
        ttk.Label(mainframe, text="Storename:").grid(column=1, row=10, sticky=E)
        storename_entry.grid(column=2, row=10, sticky=(W, E))

        # Button to check connection to database
        ttk.Button(mainframe, text="DB Connect", command=self.pg_connect).grid(column=3, row=10, sticky=W)
        # Display if the connection is good
        self.dbconnected = StringVar()
        ttk.Label(mainframe, textvariable=self.dbconnected).grid(column=4, row=10)

        # Possible output field...
        # output = Text(mainframe, width=40, height=10, state='disabled')
        # output.grid(column=2, row=5)

        # Shapefile directory path field
        self.shp_path = StringVar()
        shp_path_entry = ttk.Entry(mainframe, width=10, textvariable=self.shp_path)
        ttk.Label(mainframe, text="Shapefile Path:").grid(column=1, row=11, sticky=E)
        shp_path_entry.grid(column=2, row=11, sticky=(W, E))
        # button to open fileexporer
        ttk.Button(mainframe, text="Dir", command=lambda: self.get_dir(1)).grid(column=3, row=11, sticky=W)
        ttk.Button(mainframe, text="Import", command=self.shpimport).grid(column=4, row=11, sticky=W)

        # display if the shapefiles succesfully imported
        self.shp_comp = StringVar()
        ttk.Label(mainframe, textvariable=self.shp_comp).grid(column=5, row=11)

        # add x and y padding to every component
        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def geoconnect(self):
        """
        Connect to the geoserver
        :return:
        """
        host = self.geo_host.get()
        username = self.geo_user.get()
        password = self.geo_pass.get()
        self.geo = Geoserver(host, username=username, password=password)
        try:
            self.geo.get_version()['about']
            self.connected.set('Connected!')
        except TypeError:
            self.connected.set('Error, Connection failed!')
            pass

    def create_workspace(self):
        """
        Check if the workspace exists, if not, create a workspace
        :return:
        """
        if self.geo.get_workspace(self.workspace.get()):
            print("Workspace exists")
        else:
            self.geo.create_workspace(self.workspace.get())
            print("Workspace created")

    def tiffimport(self):
        """
        Create workspace if exists, and import TIFF/Raster layers on to geoserver
        :return:
        """
        tiff_dir = self.tiff_path.get()
        path_exists = os.path.exists(tiff_dir)
        if not path_exists:
            self.tiff_comp.set('Could not find path')
        else:
            self.tiff_comp.set('Path could be found!')
            self.create_workspace()
            self.tiff_comp.set(tiff_walk(self.geo, tiff_dir, workspace=self.workspace.get()))

    def shpimport(self):
        """
        Create workspace if doesn't exists, and import shape files onto PG DB and publish on geoserver
        :return:
        """
        shp_dir = self.shp_path.get()
        engine = self.pg_connect()
        path_exists = os.path.exists(shp_dir)
        if not path_exists:
            self.shp_comp.set('Error! Could not access path:' + shp_dir)
        else:
            self.create_workspace()
            self.shp_comp.set('Path could be found! Importing from ' + shp_dir)
            self.shp_comp.set(shp_walk(self.geo, engine, shp_dir, workspace=self.workspace.get(), storename=self.storename.get()))

    def pg_connect(self):
        """
        Create featurestore and connect to PG DB
        :return: DB engine for further access/manipulation
        """
        user = self.pg_user.get()
        passw = self.pg_pass.get()
        host = self.pg_host.get()
        port = self.pg_port.get()
        db = self.pg_database.get()
        store = self.storename.get()
        workspace = self.workspace.get()
        engine = sa.create_engine('postgresql://' + user + ':' + passw + '@' + host + ":" + port + '/' + db)

        # Could maybe have another function for the geoserver functions
        if self.geo.get_version():
            store_exists = self.geo.get_featurestore(store_name=store, workspace=workspace)
        else:
            print("Geoserver not connected")

        if type(store_exists) is str:
            self.geo.create_featurestore(store_name=store, workspace=workspace, db=db,
                                               host=host,
                                               port=port, pg_user=user,
                                               pg_password=passw, schema="public")
            print("Feature store created!")
        else:
            print("Feature store exists!")
        try:
            engine.connect()
            print('Database connected!')
            self.dbconnected.set('Database connected!')
        except sqlalchemy.exc.OperationalError:
            print('Failed to connect to Database')
            self.dbconnected.set('Failed to connect to database!')

        return engine

    def get_dir(self, shp):
        """
        Set the path for shapefile or tiff
        :param shp: binary option to set to the shape file or tiff
        :return:
        """
        if shp:
            self.shp_path.set(filedialog.askdirectory())
        else:
            self.tiff_path.set(filedialog.askdirectory())

root = Tk()
GeoImporter(root)
root.mainloop()
