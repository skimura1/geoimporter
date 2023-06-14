import os
import logging

import tkinter as tk
from tkinter import ttk, filedialog
from typing import List
from geoserver_rest import upload_raster, upload_postgis, upload_shapefile
import sqlalchemy as sa
import sqlalchemy.exc
from geo.Geoserver import Geoserver

class LabeledEntry(tk.Frame):
    def __init__(self, master=None, label_text="", default_text="", show="", **kwargs):
        super().__init__(master, **kwargs)
        self.label = tk.Label(self, width=10, text=label_text)
        self.label.pack(side=tk.LEFT)

        default = tk.StringVar()
        default.set(default_text)

        if show == "*":
            self.entry = tk.Entry(self, width=20, textvariable=default, show="*")
            self.entry.pack(side=tk.LEFT)
        else:
            self.entry = tk.Entry(self, width=20, textvariable=default)
            self.entry.pack(side=tk.LEFT)


        def get_text(self):
            return self.entry.get()

class ListBoxandButtons(tk.Frame):
    def __init__(self, master=None, label_text="", type="", files=[], import_func=None,**kwargs):
        super().__init__(master, **kwargs)

        # Shapefile directory path field
        self.listbox = tk.Listbox(self, width=20)
        self.label = tk.Label(self, width=10, text=label_text)
        
        # button to open fileexporer
        self.dir_button = ttk.Button(self, text="Dir", command=lambda: self.get_files(type, self.listbox))
        self.import_button = ttk.Button(self, text="Import", command= lambda: import_func(self.files))

        self.label.pack(side=tk.LEFT)
        self.listbox.pack(side=tk.LEFT)
        self.dir_button.pack(side=tk.LEFT)
        self.import_button.pack(side=tk.LEFT)

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
        LabeledEntry(mainframe, label_text="URL:", default_text=self.geo_host.get()).grid(column=1, row=1, sticky="W")

        # # geoserver username field
        self.geo_user = tk.StringVar()
        self.geo_user.set("admin")
        LabeledEntry(mainframe, label_text="Username:", default_text=self.geo_user.get()).grid(column=1, row=2, sticky="W")

        # geoserver password field
        self.geo_pass = tk.StringVar()
        LabeledEntry(mainframe, label_text="Password:", default_text=self.geo_pass.get(), show="*").grid(column=1, row=3, sticky="W")

        # geoserver connection button
        self.connected = tk.StringVar()
        ttk.Button(mainframe, text="Connect", command=self.geoconnect).grid(column=1, row=3, sticky="E")
        # display if the geoserver was successfully connected to
        ttk.Label(mainframe, textvariable=self.connected).grid(column=3, row=3)

        # geoserver workspace field
        self.workspace = tk.StringVar()
        # default value is "CRC"
        self.workspace.set("CRC")
        LabeledEntry(mainframe, label_text="Workspace:", default_text=self.workspace.get()).grid(column=1, row=4, sticky="W")

        # button to create workspace on the geoserver
        ttk.Button(mainframe, text="Create", command=self.create_workspace).grid(column=1, row=4, sticky="E")

        # TODO: Combined these components into one
        # tiff/raster path field
        self.tiff_files: List[str] = [] 
        ListBoxandButtons(mainframe, label_text="Raster Path:", type="raster", files=self.tiff_files, import_func=self.tiffimport).grid(column=1, row=5, sticky="W")

        # display if the layers have been imported
        self.tiff_comp = tk.StringVar()
        ttk.Label(mainframe, textvariable=self.tiff_comp).grid(column=5, row=5, sticky="W")

        # POSTGIS DB user field
        self.pg_user = tk.StringVar()
        self.pg_user.set("docker")
        LabeledEntry(mainframe, "PG User:", self.pg_user.get()).grid(column=1, row=6, sticky="W")

        # POSTGIS DB password field
        self.pg_pass = tk.StringVar()
        LabeledEntry(mainframe, "PG Pass:", self.pg_pass.get()).grid(column=1, row=7, sticky="W")

        # POSTGIS hostname field
        self.pg_host = tk.StringVar()
        self.pg_host.set("128.171.159.31")
        LabeledEntry(mainframe, "PG Host:", self.pg_host.get()).grid(column=1, row=8, sticky="W")

        # POSTGIS port field
        self.pg_port = tk.StringVar()
        self.pg_port.set("32767")
        LabeledEntry(mainframe, "Port:", self.pg_port.get()).grid(column=1, row=9, sticky="W")

        # POSTGIS database name field
        self.pg_database = tk.StringVar()
        self.pg_database.set("PUC_SLR_Viewer")
        LabeledEntry(mainframe, "PG DB:", self.pg_database.get()).grid(column=1, row=10, sticky="W")

        # geoserver storename field
        self.storename = tk.StringVar()
        self.storename.set("SLR Viewer")
        LabeledEntry(mainframe, "Storename:", self.storename.get()).grid(column=1, row=11, sticky="W")

        self.engine = None
        # Button to check connection to database
        ttk.Button(mainframe, text="DB Connect", command=lambda: self.set_engine(self.pg_connect())).grid(column=1, row=10, sticky="E")
        # Display if the connection is good
        self.dbconnected = tk.StringVar()
        ttk.Label(mainframe, textvariable=self.dbconnected).grid(column=3, row=10)

        # Shapefile directory path field
        self.shp_files: List[str] = [] 
        ListBoxandButtons(mainframe, label_text="Shapefile Path:", type="shape", files=self.shp_files, import_func=self.shpimport).grid(column=1, row=11, sticky="W")

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




if __name__ == "__main__":
    root = tk.Tk()
    GeoImporter(root)
    root.mainloop()
