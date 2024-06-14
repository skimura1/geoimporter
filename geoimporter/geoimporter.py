import logging
import os
import re
import tkinter as tk
import warnings
from pathlib import Path
from tkinter import ttk

import sqlalchemy as sa
import sqlalchemy.exc
from dotenv import load_dotenv
from geo.Geoserver import Geoserver
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import declarative_base

from helpers.labeled_entry import LabeledEntry
from helpers.listboxbutton_entry import ListBoxandButtons
from helpers.geoserver_rest import upload_postgis, upload_raster, upload_shapefile, reset_cache

_= load_dotenv()
__shapefile__ = "SHAPEFILE"
__raster__ = "RASTER"


class GeoImporter(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        tab_control = ttk.Notebook(root)

        # initiate the tkinter frame to hold widgets
        import_frame = ttk.Frame(tab_control, padding="3 3 12 12")
        delete_frame = ttk.Frame(tab_control, padding="3 3 12 12")
        tab_control.add(import_frame, text="Import")
        tab_control.add(delete_frame, text="Delete")
        tab_control.grid(column=0, row=0)
        root.title("Geoimporter")
        _ = root.columnconfigure(0, weight=1)
        _ = root.rowconfigure(0, weight=1)

        self.geo: Geoserver = Geoserver()
        self.geo_host = tk.StringVar(value=os.getenv("GEOSERVER"))
        self.geo_user = tk.StringVar(value=os.getenv("GEOSERVER_USER"))
        self.geo_pass = tk.StringVar(value=os.getenv("GEOSERVER_PASS"))
        self.connected = tk.StringVar()
        self.workspace = tk.StringVar(value=os.getenv("GEOSERVER_WORKSPACE"))
        self.tiff_files = []
        self.tiff_comp = tk.StringVar()
        self.pg_user = tk.StringVar(value=os.getenv("PG_USER"))
        self.pg_pass = tk.StringVar(value=os.getenv("PG_PASS"))
        self.pg_host = tk.StringVar(value=os.getenv("PG_HOST"))
        self.pg_port = tk.StringVar(value=os.getenv("PG_PORT"))
        self.pg_database = tk.StringVar(value=os.getenv("PG_DATABASE"))
        self.shp_files = []
        self.shp_comp = tk.StringVar()
        self.storename = tk.StringVar(value=os.getenv("STORENAME"))
        self.engine: Engine = sa.create_engine(
            "postgresql://test:testpassword@localhost:5432/data"
        )
        self.dbconnected = tk.StringVar()
        self.search_layername = tk.StringVar()
        self.search_tablename = tk.StringVar()
        self.layers = []
        self.table_names = []
        self.filtered_layers = self.layers
        self.filtered_tables = self.table_names

        host_label = LabeledEntry(
            import_frame, label_text="URL:", entry_text=self.geo_host
        )
        username_label = LabeledEntry(
            import_frame, label_text="Username:", entry_text=self.geo_user
        )
        password_label = LabeledEntry(
            import_frame,
            label_text="Password:",
            entry_text=self.geo_pass,
            show="*",
            button_label="Connect",
            button_func=self.geoconnect,
        )
        geo_connect_label = tk.Label(import_frame, textvariable=self.connected)
        workspace_label = LabeledEntry(
            import_frame, label_text="Workspace:", entry_text=self.workspace
        )
        rasterpath_label = ListBoxandButtons(
            master=import_frame,
            import_files=self.tiff_files,
            label_text="Raster Path:",
            type=__raster__,
            import_func=self.tiff_import,
        )
        pguser_label = LabeledEntry(
            import_frame, label_text="PG User:", entry_text=self.pg_user
        )
        pgpass_label = LabeledEntry(
            import_frame, label_text="PG Pass:", entry_text=self.pg_pass, show="*"
        )
        pghost_label = LabeledEntry(
            import_frame, label_text="PG Host:", entry_text=self.pg_host
        )
        pgport_label = LabeledEntry(import_frame, "Port:", entry_text=self.pg_port)
        pgdb_label = LabeledEntry(import_frame, "PG DB:", entry_text=self.pg_database)
        pgstore_label = LabeledEntry(
            import_frame,
            label_text="Storename:",
            entry_text=self.storename,
            button_label="Connect",
            button_func=self.pg_connect,
        )
        shape_listbox = ListBoxandButtons(
            master=import_frame,
            import_files=self.shp_files,
            label_text="Shapefile Path:",
            type=__shapefile__,
            import_func=self.shpimport,
        )
        dbconnected_label = tk.Label(import_frame, textvariable=self.dbconnected)
        shp_comp_label = tk.Label(import_frame, textvariable=self.shp_comp)

        ### Delete tab
        tk.Label(delete_frame, width=12, text="Layers:").grid(column=0, row=1)
        tk.Entry(delete_frame, width=50, textvariable=self.search_layername).grid(
            column=1, row=1
        )
        self.layer_listbox = tk.Listbox(delete_frame, width=50, selectmode=tk.MULTIPLE)
        ttk.Button(
            delete_frame,
            text="search",
            command=lambda: search_item(
                self, pattern=self.search_layername.get(), listbox=self.layer_listbox, filtered_list=self.filtered_layers
            ),
        ).grid(column=2, row=1)
        self.layer_listbox.grid(column=1, row=2)
        tk.Button(
            delete_frame,
            text="Delete",
            command=lambda: delete_layer(
                self, indexes=self.layer_listbox.curselection()
            ),
        ).grid(column=2, row=2)


        def search_item(self, pattern: str, listbox: tk.Listbox, filtered_list: list[str]):
            filtered_list = [
                table for table in filtered_list if re.search(pattern, table)
            ]
            listbox.delete(0, tk.END)
            self.populate_listbox(
                listbox=listbox, items=filtered_list
            )

        def delete_layer(self, indexes):
            for i in indexes:
                print("Deleting " + self.filtered_layers[i])
                print(
                    self.geo.delete_layer(
                        layer_name=self.filtered_layers[i],
                        workspace=self.workspace.get(),
                    )
                )
                self.layers.remove(self.filtered_layers[i])
            self.layer_listbox.delete(0, tk.END)
            self.populate_listbox(listbox=self.layer_listbox, items=self.layers)

        tk.Label(delete_frame, width=12, text="Tables:").grid(column=0, row=3)
        tk.Entry(delete_frame, width=50, textvariable=self.search_tablename).grid(
            column=1, row=3
        )
        ttk.Button(
            delete_frame,
            text="search",
            command=lambda: search_item(
                self, pattern=self.search_tablename.get(), listbox=self.table_listbox, filtered_list=self.filtered_tables 
            ),
        ).grid(column=2, row=3)
        self.table_listbox = tk.Listbox(delete_frame, width=50, selectmode=tk.MULTIPLE)
        self.table_listbox.grid(column=1, row=4)
        tk.Button(
            delete_frame,
            text="Delete",
            command=lambda: delete_table(self, self.table_listbox.curselection()),
        ).grid(column=2, row=4)

        tk.Button(
            delete_frame,
            text="Reset",
            command=lambda: reset_cache(self.geo),
        ).grid(column=1, row=5)

        def delete_table(self, table_arr):
            for i in table_arr:
                print("Deleting " + self.filtered_tables[i])
                print(drop_table(self, self.filtered_tables[i]))
                self.table_names.remove(self.filtered_tables[i])
            self.table_listbox.delete(0, tk.END)
            self.populate_listbox(listbox=self.table_listbox, items=self.table_names)

        def drop_table(self, table_name):
            base = declarative_base()
            metadata = sa.MetaData()
            warnings.filterwarnings("ignore", category=sqlalchemy.exc.SAWarning)
            metadata.reflect(bind=self.engine)
            table = metadata.tables[table_name]
            if table is not None:
                base.metadata.drop_all(self.engine, [table], checkfirst=True)

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
        for child in import_frame.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def set_engine(self, engine):
        self.engine = engine

    def populate_listbox(self, listbox: tk.Listbox, items: list[str]) -> None:
        for item in items:
            listbox.insert("end", item)

    def populate_tablebox(self):
        if self.engine is None:
            print("Something went wrong")
        insp = sa.inspect(self.engine)
        self.table_names = self.filtered_tables = insp.get_table_names()
        self.populate_listbox(listbox=self.table_listbox, items=self.table_names)


    def geoconnect(self):
        """
        Connect to the geoserver
        :return:
        """
        host = self.geo_host.get()
        username = self.geo_user.get()
        password = self.geo_pass.get()
        workspace = self.workspace.get()
        try:
            self.geo = Geoserver(host, username=username, password=password)
            self.geo.get_version()["about"]
            self.connected.set("Connected!")
            print("Connected to Geoserver")
            layers = self.geo.get_layers(workspace)
            if layers["layers"] != '':
                self.layers = [obj["name"] for obj in layers["layers"]["layer"]]
                self.filtered_layers = self.layers
                self.populate_listbox(listbox=self.layer_listbox, items=self.layers)
        except Exception:
            logging.exception("Error Connecting to Geoserver!")
            self.connected.set("Error Connection failed!")

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

    def tiff_import(self, paths: list[Path]):
        """
        Create workspace if exists, and import TIFF/Raster layers on to geoserver
        :return:
        """
        print("Importing Raster Files")
        count = 0
        for path in paths:
            if not path.is_file():
                self.tiff_comp.set("Error! Could not find raster file.")
            if upload_raster(
                geoserver=self.geo, filepath=path, workspace=self.workspace.get()
            ):
                count += 1
                filename = path.stem
                print("Successfully uploaded " + filename)
                self.layers.append(filename)
        self.tiff_comp.set("Successfully uploaded " + str(count) + " Raster Files!")

    def upload_sequence(self, path: Path):
        """
        Abstract away the nested upload sequence for easier readability.
        :return bool:
        """
        if not path.is_file():
            self.shp_comp.set("Error! Could not find shapefile.")
        else:
            # Uploading to POSTGIS succeeds, we can upload to Geoserver
            if upload_postgis(path, self.engine):
                if upload_shapefile(
                    geoserver=self.geo,
                    filepath=path,
                    workspace=self.workspace.get(),
                    storename=self.storename.get(),
                ):
                    print("Successfully uploaded " + path.name)
                    # Update table to include new shapefile uploaded
                    self.table_names.append(path.name)
                    self.layers.append(path.name)
                    return True
        return False


    def shpimport(self, shp_files: list[str]):
        """
        Create workspace if doesn't exists, and import shape files
        onto PG DB and publish on geoserver
        :return bool:
        """
        print("Importing Shape Files")
        count = 0
        error: list[str] = []
        for file in shp_files:
            file_path = Path(file)
            # Upload to file to Geoserver
            if self.upload_sequence(file_path):
                count += 1
                error.append(file_path.name)
        if count == len(shp_files):
            self.shp_comp.set("Successfully uploaded all Shapefiles!")
        else:
            error_layers = " ".join(error)
            self.shp_comp.set("There was an error in " + error_layers)

    def pg_connect(self):
        """
        Create featurestore and connect to PG DB
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
        store_exists = self.is_store_exists(self.geo, self.storename, self.workspace)

        if store_exists is None:
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
        self.populate_tablebox()

    def is_store_exists(self, geoserver: Geoserver, store: tk.StringVar, workspace: tk.StringVar):
        # Could maybe have another function for the geoserver functions
        if geoserver.get_version():
            return geoserver.get_featurestore(
                store_name=store.get(), workspace=workspace.get()
            )
        else:
            print("Geoserver not connected")
            return None


if __name__ == "__main__":
    root = tk.Tk()
    GeoImporter(root)
    root.mainloop()
