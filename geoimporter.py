import os

from tkinter import *
from tkinter import ttk, filedialog
from typing import List
import sqlalchemy as sa
import sqlalchemy.exc
from geo.Geoserver import Geoserver

class GeoImporter:

    def __init__(self, root):
        self.geo = Geoserver()
        root.title("GeoImporter")

        # initiate the tkinter frame to hold widgets
        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # geoserver hostname field
        self.geo_host = StringVar()
        self.geo_host.set("https://crcgeo.soest.hawaii.edu/geoserver")
        host_entry = ttk.Entry(mainframe, width=20, textvariable=self.geo_host)
        ttk.Label(mainframe, text="Geoserver Url:").grid(column=1, row=1, sticky=E)
        host_entry.grid(column=2, row=1, sticky=W)

        # geoserver username field
        self.geo_user = StringVar()
        self.geo_user.set("admin")
        user_entry = ttk.Entry(mainframe, width=20, textvariable=self.geo_user)
        ttk.Label(mainframe, text="Username:").grid(column=1, row=2, sticky=E)
        user_entry.grid(column=2, row=2, sticky=W)

        # geoserver password field
        self.geo_pass = StringVar()
        pass_entry = ttk.Entry(mainframe, width=20, textvariable=self.geo_pass, show="*")
        ttk.Label(mainframe, text="Password:").grid(column=1, row=3, sticky=E)
        pass_entry.grid(column=2, row=3, sticky=W)

        # geoserver connection button
        self.connected = StringVar()
        ttk.Button(mainframe, text="Connect", command=self.geoconnect).grid(column=3, row=3, sticky=E)
        # display if the geoserver was successfully connected to
        ttk.Label(mainframe, textvariable=self.connected).grid(column=4, row=3)

        # geoserver workspace field
        self.workspace = StringVar()
        # default value is "CRC"
        self.workspace.set("CRC")
        workspace_entry = ttk.Entry(mainframe, width=20, textvariable=self.workspace)
        ttk.Label(mainframe, text="Workspace:").grid(column=1, row=4, sticky=E)
        workspace_entry.grid(column=2, row=4, sticky=W)

        # button to create workspace on the geoserver
        ttk.Button(mainframe, text="Create", command=self.create_workspace).grid(column=3, row=4, sticky=E)

        # tiff/raster path field
        self.tiff_files: List[str] = [] 
        tiff_path_entry = Listbox(mainframe, width=20)
        for file in self.tiff_files:
            tiff_path_entry.insert("end", file)
        ttk.Label(mainframe, text="Raster/TIFF Path:").grid(column=1, row=5, sticky=E)
        tiff_path_entry.grid(column=2, row=5, sticky=W)
        # file explorer button
        ttk.Button(mainframe, text="Dir", command= lambda: self.get_files("tiff")).grid(column=3, row=5, sticky=E)
        # import into geoserver button
        ttk.Button(mainframe, text="Import", command=self.tiffimport).grid(column=4, row=5, sticky=W)

        # display if the layers have been imported
        self.tiff_comp = StringVar()
        ttk.Label(mainframe, textvariable=self.tiff_comp).grid(column=6, row=5)

        # POSTGIS DB user field
        self.pg_user = StringVar()
        self.pg_user.set("docker")
        pg_usr_entry = ttk.Entry(mainframe, width=20, textvariable=self.pg_user)
        ttk.Label(mainframe, text="PG User:").grid(column=1, row=6, sticky=E)
        pg_usr_entry.grid(column=2, row=6, sticky=W)

        # POSTGIS DB password field
        self.pg_pass = StringVar()
        pg_pass_entry = ttk.Entry(mainframe, width=20, textvariable=self.pg_pass, show="*")
        ttk.Label(mainframe, text="PG Pass:").grid(column=1, row=7, sticky=E)
        pg_pass_entry.grid(column=2, row=7, sticky=W)

        # POSTGIS hostname field
        self.pg_host = StringVar()
        self.pg_host.set("128.171.159.31")
        pg_host_entry = ttk.Entry(mainframe, width=20, textvariable=self.pg_host)
        ttk.Label(mainframe, text="PG Host:").grid(column=1, row=8, sticky=E)
        pg_host_entry.grid(column=2, row=8, sticky=W)

        # POSTGIS port field
        self.pg_port = StringVar()
        self.pg_port.set("32767")
        pg_port = ttk.Entry(mainframe, width=20, textvariable=self.pg_port)
        ttk.Label(mainframe, text="Port:").grid(column=3, row=8, sticky=W)
        pg_port.grid(column=4, row=8, sticky=W)

        # POSTGIS database name field
        self.pg_database = StringVar()
        self.pg_database.set("PUC_SLR_Viewer")
        pg_db_entry = ttk.Entry(mainframe, width=20, textvariable=self.pg_database)
        ttk.Label(mainframe, text="PG DB:").grid(column=1, row=9, sticky=E)
        pg_db_entry.grid(column=2, row=9, sticky=W)

        # geoserver storename field
        self.storename = StringVar()
        self.storename.set("SLR Viewer")
        storename_entry = ttk.Entry(mainframe, width=20, textvariable=self.storename)
        ttk.Label(mainframe, text="Storename:").grid(column=1, row=10, sticky=E)
        storename_entry.grid(column=2, row=10, sticky=W)

        # Button to check connection to database
        ttk.Button(mainframe, text="DB Connect", command=self.pg_connect).grid(column=3, row=10, sticky=W)
        # Display if the connection is good
        self.dbconnected = StringVar()
        ttk.Label(mainframe, textvariable=self.dbconnected).grid(column=4, row=10)

        # Possible output field...
        # output = Text(mainframe, width=40, height=10, state='disabled')
        # output.grid(column=2, row=5)

        # Shapefile directory path field
        self.shp_files: List[str] = [] 
        shp_path_entry = Listbox(mainframe, width=20)
        for filepath in self.shp_files:
            shp_path_entry.insert("end", filepath)
        ttk.Label(mainframe, text="Shapefile Path:").grid(column=1, row=11, sticky=E)
        shp_path_entry.grid(column=2, row=11, sticky=W)
        # button to open fileexporer
        ttk.Button(mainframe, text="Dir", command=lambda: self.get_files("shape")).grid(column=3, row=11, sticky=W)
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
        tiff_dir = self.tiff_files.get()
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

    def get_files(self, shp: str):
        """
        Set the path for shapefile or tiff
        :param shp: binary option to set to the shape file or tiff
        :return:
        """
        if shp == "shape":            
            files = filedialog.askopenfilenames(filetypes=[('Shapefiles', '*.shp')])
            self.shp_files += files
        else:
            files = filedialog.askopenfilenames(filetypes=[('Raster', '*.tif'), ('Raster', '*.tiff')])
            self.tiff_files += files

root = Tk()
GeoImporter(root)
root.mainloop()
