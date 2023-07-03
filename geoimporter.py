import os
import logging

import tkinter as tk
from tkinter import ttk
from typing import List

from geoserver_rest import upload_raster, upload_postgis, upload_shapefile
import sqlalchemy as sa
import sqlalchemy.exc
from geo.Geoserver import Geoserver
from components.labeled_entry import LabeledEntry
from components.listboxbutton_entry import ListBoxandButtons


__shapefile__ = "SHAPEFILE"
__raster__ = "RASTER"


class GeoImporter(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # initiate the tkinter frame to hold widgets
        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        self.geo_host = tk.StringVar(value="https://crcgeo.soest.hawaii.edu/geoserver")
        self.geo_user = tk.StringVar(value="admin")
        self.geo_pass = tk.StringVar()
        self.connected = tk.StringVar()
        self.workspace = tk.StringVar(value="CRC")
        self.tiff_files = []
        self.tiff_comp = tk.StringVar()
        self.pg_user = tk.StringVar(value="docker")
        self.pg_pass = tk.StringVar()
        self.pg_host = tk.StringVar(value="128.171.159.31")
        self.pg_port = tk.StringVar(value="32767")
        self.pg_database = tk.StringVar(value="PUC_SLR_Viewer")
        self.shp_files = []
        self.shp_comp = tk.StringVar()
        self.storename = tk.StringVar(value="SLR Viewer")
        self.engine = None
        self.dbconnected = tk.StringVar()

        host_label = LabeledEntry(
            mainframe, label_text="URL:", entry_text=self.geo_host
        )
        username_label = LabeledEntry(
            mainframe, label_text="Username:", entry_text=self.geo_user
        )
        password_label = LabeledEntry(
            mainframe,
            label_text="Password:",
            entry_text=self.geo_pass,
            show="*",
            button_label="Connect",
            button_func=self.geoconnect,
        )
        geo_connect_label = tk.Label(mainframe, textvariable=self.connected)
        workspace_label = LabeledEntry(
            mainframe, label_text="Workspace:", entry_text=self.workspace
        )
        rasterpath_label = ListBoxandButtons(
            mainframe,
            label_text="Raster Path:",
            type=__raster__,
            import_files=self.tiff_files,
            import_func=self.tiffimport,
        )
        pguser_label = LabeledEntry(
            mainframe, label_text="PG User:", entry_text=self.pg_user
        )
        pgpass_label = LabeledEntry(
            mainframe, label_text="PG Pass:", entry_text=self.pg_pass, show="*"
        )
        pghost_label = LabeledEntry(
            mainframe, label_text="PG Host:", entry_text=self.pg_host
        )
        pgport_label = LabeledEntry(mainframe, "Port:", entry_text=self.pg_port)
        pgdb_label = LabeledEntry(mainframe, "PG DB:", entry_text=self.pg_database)
        pgstore_label = LabeledEntry(
            mainframe,
            label_text="Storename:",
            entry_text=self.storename,
            button_label="Connect",
            button_func=lambda: self.pg_connect(),
        )
        shape_listbox = ListBoxandButtons(
            mainframe,
            label_text="Shapefile Path:",
            type=__shapefile__,
            import_files=self.shp_files,
            import_func=self.shpimport,
        )
        dbconnected_label = tk.Label(mainframe, textvariable=self.dbconnected)
        shp_comp_label = tk.Label(mainframe, textvariable=self.shp_comp)

        # geoserver hostname field
        host_label.grid(column=0, row=1)

        # geoserver username field
        username_label.grid(column=0, row=2)

        # geoserver password field
        password_label.grid(column=0, row=3)

        # show connected to geoserver
        geo_connect_label.grid(column=1, row=3)

        # geoserver workspace field
        workspace_label.grid(column=0, row=4)

        # tiff/raster path field
        rasterpath_label.grid(column=0, row=5)

        # POSTGIS DB user field
        pguser_label.grid(column=0, row=6)

        # POSTGIS DB password field
        pgpass_label.grid(column=0, row=7)

        # POSTGIS hostname field
        pghost_label.grid(column=0, row=8)

        # POSTGIS port field
        pgport_label.grid(column=0, row=9)

        # POSTGIS database name field
        pgdb_label.grid(column=0, row=10)

        # geoserver storename field
        pgstore_label.grid(column=0, row=11)

        # show connected to postgis db
        dbconnected_label.grid(column=1, row=11)

        # Shapefile directory path field
        shape_listbox.grid(column=0, row=12)
        # display if the shapefiles succesfully imported
        shp_comp_label.grid(column=0, row=13)

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
            self.geo.get_version()["about"]
            self.connected.set("Connected!")
            print("Connected to Geoserver")
        except Exception:
            logging.exception("Error Connecting to Geoserver!")
            self.connected.set("Error Connection failed!")
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

    def tiffimport(self, tiff_files: List[str]):
        """
        Create workspace if exists, and import TIFF/Raster layers on to geoserver
        :return:
        """
        print("Importing Raster Files")
        print(tiff_files)
        count = 0
        for file in tiff_files:
            if not os.path.isfile(file):
                self.tiff_comp.set("Error! Could not find raster file.")
                return False
            else:
                if upload_raster(
                    geoserver=self.geo, filepath=file, workspace=self.workspace.get()
                ):
                    count += 1
                    print("Successfully uploaded " + os.path.basename(file))
        self.tiff_comp.set("Successfully uploaded " + str(count) + " Raster Files!")

    def upload_sequence(self, file, count, error):
        """
        Abstract away the nested upload sequence for easier readability.
        :return:
        """
        if not os.path.isfile(file):
            self.shp_comp.set("Error! Could not find shape file.")
        else:
            # Uploading to POSTGIS succeeds, we can upload to Geoserver
            if upload_postgis(file, self.engine):
                if upload_shapefile(
                    geoserver=self.geo,
                    filepath=file,
                    workspace=self.workspace.get(),
                    storename=self.storename.get(),
                ):
                    count += 1
                    print("Successfully uploaded " + os.path.basename(file))
            else:
                error.append(os.path.basename(file))
                print(error)

    def shpimport(self, shp_files: List[str]):
        """
        Create workspace if doesn't exists, and import shape files
        onto PG DB and publish on geoserver
        :return:
        """
        print("Importing Shape Files")
        count = 0
        error: List[str] = []
        for file in shp_files:
            # Upload to file to Geoserver
            self.upload_sequence(file, count, error)
        if count == len(shp_files):
            self.shp_comp.set("Successfully uploaded all Shapefiles!")
        else:
            error_layers = " ".join(error)
            self.shp_comp.set("There was an error in " + error_layers)

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
        engine = sa.create_engine(
            "postgresql://" + user + ":" + passw + "@" + host + ":" + port + "/" + db
        )
        store_exists = False

        # Could maybe have another function for the geoserver functions
        if self.geo.get_version():
            store_exists = self.geo.get_featurestore(
                store_name=store, workspace=workspace
            )
        else:
            print("Geoserver not connected")

        if type(store_exists) is str:
            self.geo.create_featurestore(
                store_name=store,
                workspace=workspace,
                db=db,
                host=host,
                port=int(port),
                pg_user=user,
                pg_password=passw,
                schema="public",
            )
            print("Feature store created!")
        else:
            print("Feature store exists!")

        try:
            engine.connect()
            print("Database Connected!")
            self.dbconnected.set("Database connected!")
        except sqlalchemy.exc.OperationalError:
            logging.exception("Error connecting to database")
            self.dbconnected.set("Failed to connect to database!")
        self.set_engine(engine)


if __name__ == "__main__":
    root = tk.Tk()
    GeoImporter(root)
    root.mainloop()
