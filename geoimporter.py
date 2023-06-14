import os
import logging

import tkinter as tk
from tkinter import ttk, filedialog
from typing import List
from geoserver_rest import upload_raster, upload_postgis, upload_shapefile
import sqlalchemy as sa
import sqlalchemy.exc
from geo.Geoserver import Geoserver

__shapefile__ = "SHAPEFILE"
__raster__ = "RASTER"

class LabeledEntry(tk.Frame):
    def __init__(self, master=None, label_text="", entry_text="", show="", button_func=None, button_label="", **kwargs):
        super().__init__(master, **kwargs)
        self.label = tk.Label(self, width=12, text=label_text)
        self.label.pack(side=tk.LEFT)

        if show == "*":
            self.entry = tk.Entry(self, width=20, textvariable=entry_text, show="*").pack(side=tk.LEFT)
        else:
            self.entry = tk.Entry(self, width=20, textvariable=entry_text).pack(side=tk.LEFT)

        if button_func != None:
            self.button = ttk.Button(self, text=button_label, command=button_func).pack(side=tk.LEFT)
        else:
            tk.Label(self, width=10).pack(side=tk.LEFT)

        tk.Label(self, width=10).pack(side=tk.LEFT)

        def get_text(self):
            return self.text_value.get()

class ListBoxandButtons(tk.Frame):
    def __init__(self, master=None, label_text="", type="", import_files=[], import_func=None,**kwargs):
        super().__init__(master, **kwargs)

        # Shapefile directory path field
        self.listbox = tk.Listbox(self, width=20)
        self.label = tk.Label(self, width=12, text=label_text)
        
        # button to open fileexporer
        self.dir_button = ttk.Button(self, text="Dir", command=lambda: self.get_files(type, self.listbox, import_files))
        self.import_button = ttk.Button(self, text="Import", command= lambda: import_func(import_files))

        self.label.pack(side=tk.LEFT)
        self.listbox.pack(side=tk.LEFT)
        self.dir_button.pack(side=tk.LEFT)
        self.import_button.pack(side=tk.LEFT)

    def get_files(self, type: str, listbox: tk.Listbox, import_files: list):
        """
        Set the path for shapefile or tiff
        :param shp: binary option to set to the shape file or tiff
        :return:
        """
        listbox.delete(0, tk.END)
        files = []
        if type == __shapefile__:
            files = filedialog.askopenfilenames(filetypes=[('Shapefiles', '*.shp')])
        else:
            files = filedialog.askopenfilenames(filetypes=[('Raster', '*.tif'), ('Raster', '*.tiff')])
        import_files += files
        for file in files:
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
        host_label = LabeledEntry(mainframe, label_text="URL:", entry_text=self.geo_host).grid(column=0, row=1)

        # geoserver username field
        self.geo_user = tk.StringVar()
        self.geo_user.set("admin")
        username_label = LabeledEntry(mainframe, label_text="Username:", entry_text=self.geo_user).grid(column=0, row=2)

        # # geoserver password field
        self.geo_pass = tk.StringVar()
        self.connected = tk.StringVar()
        password_label = LabeledEntry(mainframe, label_text="Password:", entry_text=self.geo_pass, show="*", button_label="Connect", button_func=self.geoconnect).grid(column=0, row=3)
        tk.Label(mainframe, textvariable=self.connected).grid(column=1, row=3)

        # geoserver workspace field
        self.workspace = tk.StringVar()
        self.workspace.set("CRC")
        workspace_label = LabeledEntry(mainframe, label_text="Workspace:", entry_text=self.workspace).grid(column=0, row=4)

        # tiff/raster path field
        self.tiff_files: List[str] = [] 
        self.tiff_comp = tk.StringVar()
        rasterpath_label = ListBoxandButtons(mainframe, label_text="Raster Path:", type=__raster__, import_files=self.tiff_files, import_func=self.tiffimport).grid(column=0, row=5)

        # POSTGIS DB user field
        self.pg_user = tk.StringVar()
        self.pg_user.set("docker")
        pguser_label = LabeledEntry(mainframe, label_text="PG User:", entry_text=self.pg_user).grid(column=0, row=6)

        # POSTGIS DB password field
        self.pg_pass = tk.StringVar()
        pgpass_label = LabeledEntry(mainframe, label_text="PG Pass:", entry_text=self.pg_pass, show="*").grid(column=0, row=7)

        # POSTGIS hostname field
        self.pg_host = tk.StringVar()
        self.pg_host.set("128.171.159.31")
        pghost_label = LabeledEntry(mainframe, label_text="PG Host:", entry_text=self.pg_host).grid(column=0, row=8)

        # POSTGIS port field
        self.pg_port = tk.StringVar()
        self.pg_port.set("32767")
        pgport_label = LabeledEntry(mainframe, "Port:", entry_text=self.pg_port).grid(column=0, row=9)

        # POSTGIS database name field
        self.pg_database = tk.StringVar()
        self.pg_database.set("PUC_SLR_Viewer")
        pgdb_label = LabeledEntry(mainframe, "PG DB:", entry_text=self.pg_database).grid(column=0, row=10)

        # geoserver storename field
        self.storename = tk.StringVar()
        self.engine = None
        self.storename.set("SLR Viewer")
        self.dbconnected = tk.StringVar()
        pgstore_label = LabeledEntry(mainframe, label_text="Storename:", entry_text=self.storename, button_label="Connect", button_func=lambda: self.set_engine(self.pg_connect())).grid(column=0, row=11)
        tk.Label(mainframe, textvariable=self.dbconnected).grid(column=1, row=11)

        # Shapefile directory path field
        self.shp_files: List[str] = [] 
        shape_listbox = ListBoxandButtons(mainframe, label_text="Shapefile Path:", type=__shapefile__, import_files=self.shp_files, import_func=self.shpimport).grid(column=0, row=12)
        # display if the shapefiles succesfully imported
        self.shp_comp = tk.StringVar()
        shpcomp_label = tk.Label(mainframe, textvariable=self.shp_comp).grid(column=0, row=13)

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
            print("Connected to Geoserver")
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
        print("Importing Raster Files")
        print(tiff_files)
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
        print("Importing Shape Files")
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
