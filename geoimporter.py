import os
import logging

import tkinter as tk
from tkinter import ttk, filedialog
from typing import List
from geoserver_rest import upload_raster, upload_postgis, upload_shapefile
import sqlalchemy as sa
import sqlalchemy.exc
from geo.Geoserver import Geoserver

class GeoImporter(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # initiate the tkinter frame to hold widgets
        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # geoserver hostname field
        self.geo_host = tk.StringVar()
        self.geo_host.set("https://crcgeo.soest.hawaii.edu/geoserver")
        ttk.Entry(mainframe, width=20, textvariable=self.geo_host).grid(column=2, row=1, sticky="W")
        ttk.Label(mainframe, text="Geoserver Url:").grid(column=1, row=1, sticky="E")

        # geoserver username field
        self.geo_user = tk.StringVar()
        self.geo_user.set("admin")
        ttk.Entry(mainframe, width=20, textvariable=self.geo_user).grid(column=2, row=2, sticky="W")
        ttk.Label(mainframe, text="Username:").grid(column=1, row=2, sticky="E")

        # geoserver password field
        self.geo_pass = tk.StringVar()
        ttk.Entry(mainframe, width=20, textvariable=self.geo_pass, show="*").grid(column=2, row=3, sticky="W")
        ttk.Label(mainframe, text="Password:").grid(column=1, row=3, sticky="E")

        # geoserver connection button
        self.connected = tk.StringVar()
        ttk.Button(mainframe, text="Connect", command=self.geoconnect).grid(column=3, row=3, sticky="E")
        # display if the geoserver was successfully connected to
        ttk.Label(mainframe, textvariable=self.connected).grid(column=4, row=3)

        # geoserver workspace field
        self.workspace = tk.StringVar()
        # default value is "CRC"
        self.workspace.set("CRC")
        ttk.Label(mainframe, text="Workspace:").grid(column=1, row=4, sticky="E")
        ttk.Entry(mainframe, width=20, textvariable=self.workspace).grid(column=2, row=4, sticky="W")

        # button to create workspace on the geoserver
        ttk.Button(mainframe, text="Create", command=self.create_workspace).grid(column=3, row=4, sticky="E")

        # tiff/raster path field
        self.tiff_files: List[str] = [] 
        tiff_listbox = tk.Listbox(mainframe, width=20)
        ttk.Label(mainframe, text="Raster/TIFF Path:").grid(column=1, row=5, sticky="E")
        tiff_listbox.grid(column=2, row=5, sticky="W")

        # file explorer button
        ttk.Button(mainframe, text="Dir", command= lambda: self.get_files("tiff", tiff_listbox)).grid(column=3, row=5, sticky="E")

        # import into geoserver button
        ttk.Button(mainframe, text="Import", command= lambda: self.tiffimport(self.tiff_files)).grid(column=4, row=5, sticky="W")

        # display if the layers have been imported
        self.tiff_comp = tk.StringVar()
        ttk.Label(mainframe, textvariable=self.tiff_comp).grid(column=5, row=5, sticky="W")

        # POSTGIS DB user field
        self.pg_user = tk.StringVar()
        self.pg_user.set("docker")
        ttk.Entry(mainframe, width=20, textvariable=self.pg_user).grid(column=2, row=6, sticky="W")
        ttk.Label(mainframe, text="PG User:").grid(column=1, row=6, sticky="E")

        # POSTGIS DB password field
        self.pg_pass = tk.StringVar()
        ttk.Entry(mainframe, width=20, textvariable=self.pg_pass, show="*").grid(column=2, row=7, sticky="W")
        ttk.Label(mainframe, text="PG Pass:").grid(column=1, row=7, sticky="E")

        # POSTGIS hostname field
        self.pg_host = tk.StringVar()
        self.pg_host.set("128.171.159.31")
        ttk.Entry(mainframe, width=20, textvariable=self.pg_host).grid(column=2, row=8, sticky="W")
        ttk.Label(mainframe, text="PG Host:").grid(column=1, row=8, sticky="E")

        # POSTGIS port field
        self.pg_port = tk.StringVar()
        self.pg_port.set("32767")
        ttk.Label(mainframe, text="Port:", width=10).grid(column=3, row=8, sticky="E")
        ttk.Entry(mainframe, width=5, textvariable=self.pg_port).grid(column=4, row=8, sticky="W")

        # POSTGIS database name field
        self.pg_database = tk.StringVar()
        self.pg_database.set("PUC_SLR_Viewer")
        ttk.Label(mainframe, text="PG DB:").grid(column=1, row=9, sticky="E")
        ttk.Entry(mainframe, width=20, textvariable=self.pg_database).grid(column=2, row=9, sticky="W")

        # geoserver storename field
        self.storename = tk.StringVar()
        self.storename.set("SLR Viewer")
        ttk.Label(mainframe, text="Storename:").grid(column=1, row=10, sticky="E")
        ttk.Entry(mainframe, width=20, textvariable=self.storename).grid(column=2, row=10, sticky="W")

        self.engine = None
        # Button to check connection to database
        ttk.Button(mainframe, text="DB Connect", command=lambda: self.set_engine(self.pg_connect())).grid(column=3, row=10, sticky="W")
        # Display if the connection is good
        self.dbconnected = tk.StringVar()
        ttk.Label(mainframe, textvariable=self.dbconnected).grid(column=4, row=10)

        # Shapefile directory path field
        self.shp_files: List[str] = [] 
        shp_listbox = tk.Listbox(mainframe, width=20)
        ttk.Label(mainframe, text="Shapefile Path:").grid(column=1, row=11, sticky="E")
        shp_listbox.grid(column=2, row=11, sticky="W")
        # button to open fileexporer
        ttk.Button(mainframe, text="Dir", command=lambda: self.get_files("shape", shp_listbox)).grid(column=3, row=11, sticky="W")
        ttk.Button(mainframe, text="Import", command= lambda: self.shpimport(self.shp_files)).grid(column=4, row=11, sticky="W")

        # display if the shapefiles succesfully imported
        self.shp_comp = tk.StringVar()
        ttk.Label(mainframe, textvariable=self.shp_comp).grid(column=5, row=11)

        # add x and y padding to every component
        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)
    
    def set_engine(self, engine):
        self.engine = engine


    def geoconnect(self):
        """
        Connect to the geoserver
        :return:
        """
        host = self.geo_host.get()
        username = self.geo_user.get()
        password = self.geo_pass.get()
        try:
            self.geo = Geoserver(host, username=username, password=password)
            self.geo.get_version()['about']
            self.connected.set('Connected!')
        except Exception:
            logging.exception("Error Connecting to Geoserver!")
            self.connected.set('Error Connection failed!')
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

    def tiffimport(self, tiff_files: List[str] ):
        """
        Create workspace if exists, and import TIFF/Raster layers on to geoserver
        :return:
        """
        count = 0
        for file in tiff_files:
            if not os.path.isfile(file):
                self.tiff_comp.set('Error! Could not find raster file.')
                return False
            else:
                if upload_raster(geoserver=self.geo, filepath=file, workspace=self.workspace.get()):
                    count += 1
                    print('Successfully uploaded ' + os.path.basename(file))
        self.tiff_comp.set('Successfully uploaded ' + str(count) + ' Raster Files!')

    def upload_sequence(self, file, count, error):
        """
        Abstract away the nested upload sequence for easier readability.  
        :return:
        """
        if not os.path.isfile(file):
            self.shp_comp.set('Error! Could not find shape file.')
        else:
            # Uploading to POSTGIS succeeds, we can upload to Geoserver
            if upload_postgis(file, self.engine):
                if upload_shapefile(geoserver=self.geo, filepath=file, workspace=self.workspace.get(), storename=self.storename.get()):
                    count += 1
                    print('Successfully uploaded ' + os.path.basename(file))
            else:
                error.append(os.path.basename(file))
                print(error)


    def shpimport(self, shp_files: List[str]):
        """
        Create workspace if doesn't exists, and import shape files onto PG DB and publish on geoserver
        :return:
        """
        count = 0
        error = []
        for file in shp_files:
            # Upload to file to Geoserver
            self.upload_sequence(file, count, error)
        if count == len(shp_files):
            self.shp_comp.set('Successfully uploaded all Shapefiles!')
        else:
            error_layers = ' '.join(error)
            self.shp_comp.set('There was an error in ' + error_layers)


    def pg_connect(self):
        """
        Create featurestore and connect to PG DB
        :return: DB engine for further access/manipulation
        """
        user = self.pg_user.get()
        passw = self.pg_pass.get()
        host = self.pg_host.get()
        port = str(self.pg_port.get())
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
                                               port=int(port), pg_user=user,
                                               pg_password=passw, schema="public")
            print("Feature store created!")
        else:
            print("Feature store exists!")

        try: 
            engine.connect()
            print('Database Connected!')
            self.dbconnected.set('Database connected!')
        except sqlalchemy.exc.OperationalError:
            logging.exception("Error connecting to database")
            self.dbconnected.set('Failed to connect to database!')
        return engine

    def get_files(self, type: str, listbox: tk.Listbox):
        """
        Set the path for shapefile or tiff
        :param shp: binary option to set to the shape file or tiff
        :return:
        """
        listbox.delete(0, tk.END)
        if type == "shape":            
            self.shp_files = []
            files = filedialog.askopenfilenames(filetypes=[('Shapefiles', '*.shp')])
            self.shp_files += files
            for file in self.shp_files:
                filename = os.path.basename(file)
                listbox.insert(tk.END, filename)
        else:
            self.tiff_files = []
            files = filedialog.askopenfilenames(filetypes=[('Raster', '*.tif'), ('Raster', '*.tiff')])
            self.tiff_files += files
            for file in self.tiff_files:
                filename = os.path.basename(file)
                listbox.insert(tk.END, filename)



if __name__ == "__main__":
    root = tk.Tk()
    GeoImporter(root)
    root.mainloop()
