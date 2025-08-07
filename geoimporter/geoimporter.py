import logging
import os
import re
import tkinter as tk
import warnings
from pathlib import Path
from tkinter import ttk
from typing import Optional

import sqlalchemy as sa
import sqlalchemy.exc
from dotenv import load_dotenv
from geo.Geoserver import Geoserver, GeoserverException
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import declarative_base

try:
    from .helpers.labeled_entry import LabeledEntry
    from .helpers.listboxbutton_entry import ListBoxandButtons
    from .helpers.geoserver_rest import upload_postgis, upload_raster, upload_shapefile
except ImportError:
    from helpers.labeled_entry import LabeledEntry
    from helpers.listboxbutton_entry import ListBoxandButtons
    from helpers.geoserver_rest import upload_postgis, upload_raster, upload_shapefile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('geoimporter.log'),
        logging.StreamHandler()
    ]
)

load_dotenv()
__shapefile__ = "SHAPEFILE"
__raster__ = "RASTER"


class GeoImporter(tk.Frame):
    """ 
    This class create the instance of Geoimporter on a TKinter Frame

    Attributes:
        parent: Set the parent frame to the initial TKinter Frame
        args: Additonal Arguments passed to app if needed
        kwargs: Additional positional args passed to app if needed
    """
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        tab_control = ttk.Notebook(parent)

        # initiate the tkinter frame to hold widgets
        import_frame = ttk.Frame(tab_control, padding="3 3 12 12")
        # TODO: Fix Deletion
        delete_frame = ttk.Frame(tab_control, padding="3 3 12 12")
        tab_control.add(import_frame, text="Import")
        tab_control.add(delete_frame, text="Delete")
        tab_control.grid(column=0, row=0)
        parent.title("Geoimporter")
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

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
        self.engine: Optional[Engine] = None
        self.dbconnected = tk.StringVar()
        self.search_layername = tk.StringVar()
        self.search_tablename = tk.StringVar()
        self.layers = []
        self.table_names = []
        self.filtered_layers = self.layers
        self.filtered_tables = self.table_names

        host_label = LabeledEntry(import_frame, self.geo_host, label_text="URL:")
        username_label = LabeledEntry(import_frame, self.geo_user, label_text="Username:")
        password_label = LabeledEntry(
            import_frame,
            self.geo_pass,
            label_text="Password:",
            show="*",
            button_label="Connect",
            button_func=self.geoconnect,
        )
        geo_connect_label = tk.Label(import_frame, textvariable=self.connected)
        workspace_label = LabeledEntry(import_frame, self.workspace, label_text="Workspace:")
        rasterpath_label = ListBoxandButtons(
            master=import_frame,
            import_files=self.tiff_files,
            label_text="Raster Path:",
            type=__raster__,
            import_func=self.tiff_import,
        )
        pguser_label = LabeledEntry(import_frame, self.pg_user, label_text="PG User:")
        pgpass_label = LabeledEntry(import_frame, self.pg_pass, label_text="PG Pass:", show="*")
        pghost_label = LabeledEntry(import_frame, self.pg_host, label_text="PG Host:")
        pgport_label = LabeledEntry(import_frame, self.pg_port, "Port:", )
        pgdb_label = LabeledEntry(import_frame, self.pg_database, "PG DB:")
        pgstore_label = LabeledEntry(
            import_frame,
            self.storename,
            label_text="Storename:",
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
            command=lambda: self.search_item(
                pattern=self.search_layername.get(), 
                listbox=self.layer_listbox, 
                original_list=self.layers, 
                list_name="filtered_layers"
            ),
        ).grid(column=2, row=1)
        self.layer_listbox.grid(column=1, row=2)
        tk.Button(
            delete_frame,
            text="delete",
            command=lambda: self.delete_layer(
                self.layer_listbox.curselection()
            ),
        ).grid(column=2, row=2)



        tk.Label(delete_frame, width=12, text="Tables:").grid(column=0, row=3)
        tk.Entry(delete_frame, width=50, textvariable=self.search_tablename).grid(
            column=1, row=3
        )
        ttk.Button(
            delete_frame,
            text="search",
            command=lambda: self.search_item(
                pattern=self.search_tablename.get(), 
                listbox=self.table_listbox, 
                original_list=self.table_names, 
                list_name="filtered_tables"
            ),
        ).grid(column=2, row=3)
        self.table_listbox = tk.Listbox(delete_frame, width=50, selectmode=tk.MULTIPLE)
        self.table_listbox.grid(column=1, row=4)
        tk.Button(
            delete_frame,
            text="Delete",
            command=lambda: self.delete_tables(self.table_listbox.curselection()),
        ).grid(column=2, row=4)

        # Reset Cache Button (Probably not gonna enable this one)
        # tk.Button(
        #     delete_frame,
        #     text="Reset",
        #     command=lambda: reset_cache(self.geo),
        # ).grid(column=1, row=5)

        # Drop Table Operations



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
        """
        Setter function for sql engine

        Args:
            engine: engine we want to update to

        """
        self.engine = engine

    # TODO: Extract this function
    def populate_listbox(self, listbox: tk.Listbox, items: list[str]) -> None:
        """
        Populate the list box with given items

        Args:
            listbox: the listbox we want to populate items with
            items: the items that we want to add to listbox

        """
        for item in items:
            listbox.insert("end", item)


    def geoconnect(self):
        """
        Connect to the Geoserver
        Args:
            Void

        Returns:
            Void

        Raises:
            Exception to log error connecting to Geoserver
            
        """
        host = self.geo_host.get()
        username = self.geo_user.get()
        password = self.geo_pass.get()
        workspace = self.workspace.get()
        
        # Attempt to Connect to the geoserver
        try:
            self.geo = Geoserver(host, username=username, password=password)
            self.geo.get_version()["about"]
            self.connected.set("Connected!")
            print("Connected to Geoserver")

        except GeoserverException:
            logging.exception("Error Connecting to Geoserver!")
            self.connected.set("Error Connection failed!")

        # Clear list if listbox is already populated, then clear the listbox
        if self.layers:
            self.layer_listbox.delete(0, tk.END)

        # Attempt to get the layers from Geoserver
        try:
            layers = self.geo.get_layers(workspace)["layers"]["layer"]
        except GeoserverException:
            logging.exception("Unable to get the layers from " + workspace)
            self.connected.set("Unable to obtain layer name")
        else:
            self.layers = [obj["name"] for obj in layers]
            self.filtered_layers = self.layers
            # If everything works, populate the appropriate listbox
            self.populate_listbox(listbox=self.layer_listbox, items=self.layers)


    def create_workspace(self):
        """
        Check if the workspace exists, if not, create a workspace
        Args:
            Void

        Return:
            Void

        Raises:
        """
        if self.geo.get_workspace(self.workspace.get()):
            print("Workspace exists")
        else:
            self.geo.create_workspace(self.workspace.get())
            print("Workspace created")

    def tiff_import(self, paths: list[Path]):
        """
        Importer Raster files

        Args:
            The list of paths of the raster files

        Return:
            Void

        Raises:
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
                filename = path.name
                print("Successfully uploaded " + filename)
                self.layers.append(filename)
        self.tiff_comp.set("Successfully uploaded " + str(count) + " Raster Files!")

    # TODO: Fix Error Action + better name for function
    def upload_sequence(self, path: Path) -> bool:
        """
        Abstract away the nested upload sequence for easier readability.

        Args:
            path: The path to each file to upload
            
        Return:
            bool: If uploading to PostGIS and Geoserver is successful
        """
        if not path.is_file():
            self.shp_comp.set(f"Error! Could not find shapefile: {path}")
            return False
            
        if self.engine is None:
            self.shp_comp.set("Error! Database not connected.")
            return False
            
        try:
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
                    self.table_names.append(path.stem)
                    self.layers.append(path.stem)
                    return True
        except Exception as e:
            logging.error("Error in upload sequence for %s: %s", path.name, e)
            self.shp_comp.set(f"Error uploading {path.name}: {str(e)}")
            
        return False

    def shpimport(self, shp_files: list[Path]) -> None:
        """
        Create workspace if doesn't exist, and import shape files
        onto PG DB and publish on geoserver

        Args:
            shp_files: List of paths for the shape files to upload
        """
        if not shp_files:
            self.shp_comp.set("No files selected for import.")
            return
            
        print("Importing Shape Files")
        count = 0
        failed_files: list[str] = []
        
        for file_path in shp_files:
            if self.upload_sequence(file_path):
                count += 1
            else:
                failed_files.append(file_path.name)
                
        if count == len(shp_files):
            self.shp_comp.set(f"Successfully uploaded all {count} Shapefiles!")
        elif count > 0:
            self.shp_comp.set(f"Uploaded {count}/{len(shp_files)} files. Failed: {', '.join(failed_files)}")
        else:
            self.shp_comp.set("Failed to upload any files.")

    def pg_connect(self) -> None:
        """
        Create featurestore and connect to PG DB
        """
        user = self.pg_user.get().strip()
        password = self.pg_pass.get().strip()
        host = self.pg_host.get().strip()
        port = self.pg_port.get().strip()
        db = self.pg_database.get().strip()
        store = self.storename.get().strip()
        workspace = self.workspace.get().strip()
        
        # Validate required fields
        if not all([user, password, host, port, db, store, workspace]):
            self.dbconnected.set("Error: All fields are required!")
            return
            
        try:
            port_int = int(port)
        except ValueError:
            self.dbconnected.set("Error: Port must be a number!")
            return
            
        try:
            connection_string = f"postgresql://{user}:{password}@{host}:{port}/{db}"
            engine = sa.create_engine(connection_string)
            
            # Test the connection
            with engine.connect() as conn:
                conn.execute(sa.text("SELECT 1"))
                
            print("Database Connected!")
            self.dbconnected.set("Database connected!")
            self.set_engine(engine)
            
            # Handle featurestore creation
            store_exists = self.is_store_exists(self.geo, self.storename, self.workspace)
            if store_exists is None:
                try:
                    self.geo.create_featurestore(
                        store_name=store,
                        workspace=workspace,
                        db=db,
                        host=host,
                        port=port_int,
                        pg_user=user,
                        pg_password=password,
                        schema="public",
                    )
                    print("Feature store created!")
                except Exception as e:
                    logging.error("Error creating featurestore: %s", e)
                    self.dbconnected.set(f"Connected to DB but featurestore creation failed: {e}")
            else:
                print("Feature store exists!")
                
            # Populate table list
            insp = sa.inspect(self.engine)
            self.table_names = insp.get_table_names()
            self.filtered_tables = self.table_names
            self.populate_listbox(listbox=self.table_listbox, items=self.table_names)
            
        except sqlalchemy.exc.OperationalError as e:
            logging.error("Database connection error: %s", e)
            self.dbconnected.set(f"Failed to connect: {str(e)}")
        except Exception as e:
            logging.error("Unexpected error during database connection: %s", e)
            self.dbconnected.set(f"Connection error: {str(e)}")

    def is_store_exists(self, geoserver: Geoserver, store: tk.StringVar, workspace: tk.StringVar):
        """
        Check if the store exists already on the Geoserver

        Args:
            geoserver: The Geoserver handle to execute operations
            store: The specific store that we want to check on Geoserver
            workspace: The workspace on the Geoserver that the store exists on

        Return:
            TODO Fix this to be guarantee that we get a boolean
           Unknown | None: Whether the store exists ore not
        """
        # Could maybe have another function for the geoserver functions
        if geoserver.get_version():
            return geoserver.get_featurestore(
                store_name=store.get(), workspace=workspace.get()
            )
        else:
            print("Geoserver not connected")
            return None

    def search_item(self, pattern: str, listbox: tk.Listbox, original_list: list[str], list_name: str) -> None:
        """ 
        Update filtered_list based on search pattern

        Args:
            pattern: search pattern
            listbox: the listbox we want to update
            original_list: static list of original items
            list_name: name of the attribute to update with filtered results

        """
        filtered_list: list[str] = []

        if pattern == "":
            filtered_list = original_list
        else:
            filtered_list = [
                table for table in original_list if re.search(pattern.lower(), table.lower())
            ]

        setattr(self, list_name, filtered_list)

        listbox.delete(0, tk.END)
        self.populate_listbox(listbox=listbox, items=filtered_list)

    def delete_layer(self, indexes: tuple[int, ...]) -> None:
        """ 
        Delete each layer from GeoServer based on TK Listbox selection

        Args:
            indexes: tuple of the indexes relative to filtered_layers 

        """
        for i in indexes:
            print("Deleting " + self.filtered_layers[i])
            try:
                self.geo.delete_layer(
                    layer_name=self.filtered_layers[i],
                    workspace=self.workspace.get(),
                )
            except GeoserverException as e:
                logging.error("Geoserver Error: %s", e)
            else:
                self.layers.remove(self.filtered_layers[i])
        self.layer_listbox.delete(0, tk.END)
        self.populate_listbox(listbox=self.layer_listbox, items=self.layers)

    def drop_table(self, table_name: str) -> None:
        """ 
        Drop table from Postgres Database

        Args:
            table_name: name of table we drop

        Raises:
            SQLAlchemyError: If table doesn't exist or engine is None
        """
        if self.engine is None:
            raise sqlalchemy.exc.SQLAlchemyError("Database engine not initialized")
            
        base = declarative_base()
        metadata = sa.MetaData()
        warnings.filterwarnings("ignore", category=sqlalchemy.exc.SAWarning)
        metadata.reflect(bind=self.engine)
        
        if table_name in metadata.tables:
            table = metadata.tables[table_name]
            print(f'Deleting {table_name} table from PostGIS')
            base.metadata.drop_all(self.engine, [table], checkfirst=True)
        else:
            raise sqlalchemy.exc.SQLAlchemyError(f"Table '{table_name}' does not exist in PostGIS")

    def delete_tables(self, indexes: tuple[int, ...]) -> None:
        """ 
        Delete each table from PostGIS based on TK Listbox selection

        Args:
            indexes: tuple of the indexes relative to filtered_tables 

        """
        print(self.filtered_tables)

        for i in indexes:
            print(self.filtered_tables[i])
            try: 
                self.drop_table(self.filtered_tables[i])
            except sqlalchemy.exc.SQLAlchemyError as e:
                logging.error("Error: %s", e)
            else:
                self.table_names.remove(self.filtered_tables[i])

        self.table_listbox.delete(0, tk.END)
        self.populate_listbox(listbox=self.table_listbox, items=self.table_names)


def main() -> None:
    """Main entry point for the GeoImporter application."""
    try:
        root = tk.Tk()
        root.geometry("800x600")
        root.resizable(True, True)
        
        app = GeoImporter(root)
        app.grid(column=0, row=0, sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        logging.info("GeoImporter application started")
        root.mainloop()
        
    except Exception as e:
        logging.error("Fatal error starting application: %s", e)
        raise


if __name__ == "__main__":
    main()
