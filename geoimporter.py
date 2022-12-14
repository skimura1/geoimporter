import os
import re

from tkinter import *
from tkinter import ttk
import geopandas as gpd
import sqlalchemy as sa
from geo.Geoserver import Geoserver


def tiff_walk(geoserver, tiff_dir, workspace):
    error_layer = []
    status = "Importing layer successful!"
    for (root_dir, dirs, files) in os.walk(tiff_dir):
        for file in files:
            if re.search(r'.tif$', file):
                filename = file[:-4]
                print('Uploading ' + filename)
                try:
                    geoserver.create_coveragestore(layer_name=filename, path=root_dir + '/' + file, workspace=workspace)
                except Exception as e:
                    error_tuple = (filename, e)
                    error_layer.append(filename)
                    print('Error with ' + filename)
                    continue
    if len(error_layer):
        status = "There was an error in" + ''.join(error_layer)
    return status

# TODO: Create shp_walk(geoserver, engine, shp_dir, workspace)
def shp_walk(geoserver, shp_dir, workspace):
    error_layer = []
    insp = sa.inspect(engine)
    for (root_dir, dirs, files) in os.walk(shp_dir):
        for file in files:
            filename = file[:-4]
            if re.search(r'.shp$', file):
                print("Uploading " + filename)
                shp_file = gpd.read_file(root + "/" + file)
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
                geoserver.publish_featurestore(workspace=workspace, store_name='PUC_SLR_Viewer', pg_table=filename)
                print(filename + " upload completed!")


class GeoImporter:

    def __init__(self, root):
        self.geo = Geoserver()
        root.title("GeoImporter")

        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        self.geo_host = StringVar()
        host_entry = ttk.Entry(mainframe, width=20, textvariable=self.geo_host)
        ttk.Label(mainframe, text="Geoserver Url:").grid(column=1, row=1, sticky=W)
        host_entry.grid(column=2, row=1, sticky=(W, E))

        self.geo_user = StringVar()
        user_entry = ttk.Entry(mainframe, width=10, textvariable=self.geo_user)
        ttk.Label(mainframe, text="Username:").grid(column=1, row=2, sticky=E)
        user_entry.grid(column=2, row=2, sticky=(W, E))

        self.geo_pass = StringVar()
        pass_entry = ttk.Entry(mainframe, width=10, textvariable=self.geo_pass, show="*")
        ttk.Label(mainframe, text="Password:").grid(column=1, row=3, sticky=E)
        pass_entry.grid(column=2, row=3, sticky=(W, E))

        self.connected = StringVar()
        ttk.Button(mainframe, text="Connect", command=self.geoconnect).grid(column=3, row=3, sticky=E)
        ttk.Label(mainframe, textvariable=self.connected).grid(column=4, row=3)

        # TODO: Implement file finder
        self.path = StringVar()
        path_entry = ttk.Entry(mainframe, width=10, textvariable=self.path)
        ttk.Label(mainframe, text="Path:").grid(column=1, row=4, sticky=E)
        path_entry.grid(column=2, row=4, sticky=(W, E))
        ttk.Button(mainframe, text="Import", command=self.tiffimport).grid(column=3, row=4, sticky=E)

        self.tiff_comp = StringVar()
        ttk.Label(mainframe, textvariable=self.tiff_comp).grid(column=4, row=4)

        self.pg_user = StringVar()
        pg_usr_entry = ttk.Entry(mainframe, width=10, textvariable=self.pg_user)
        ttk.Label(mainframe, text="PG User:").grid(column=1, row=5, sticky=E)
        pg_usr_entry.grid(column=2, row=5, sticky=(W, E))

        self.pg_pass = StringVar()
        pg_pass_entry = ttk.Entry(mainframe, width=10, textvariable=self.pg_pass)
        ttk.Label(mainframe, text="PG Pass:").grid(column=1, row=6, sticky=E)
        pg_pass_entry.grid(column=2, row=6, sticky=(W, E))

        self.pg_host = StringVar()
        pg_host_entry = ttk.Entry(mainframe, width=10, textvariable=self.pg_host)
        ttk.Label(mainframe, text="PG Host:").grid(column=1, row=7, sticky=E)
        pg_host_entry.grid(column=2, row=7, sticky=(W, E))

        self.pg_database = StringVar()
        pg_db_entry = ttk.Entry(mainframe, width=10, textvariable=self.pg_database)
        ttk.Label(mainframe, text="PG DB:").grid(column=1, row=8, sticky=E)
        pg_db_entry.grid(column=2, row=8, sticky=(W, E))

        ttk.Button(mainframe, text="DB Connect", command=self.pg_connect).grid(column=3, row=8, sticky=E)

        # output = Text(mainframe, width=40, height=10, state='disabled')
        # output.grid(column=2, row=5)

        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def geoconnect(self):
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

    # TODO: Create pg_connect()
    def pg_connect(self):
        engine = sa.create_engine('postgresql://' + self.pg_user + ':' + self.pg_pass + '@' + self.pg_host + '/' + self.pg_database)
        store_created = False
        store_exists = self.geo.get_featurestore(store_name="PUC_SLR_Viewer", workspace="CRC")
        if not store_exists:
            self.geo.create_featurestore(store_name='PUC_SLR_Viewer', workspace='CRC', db='PUC_SLR_Viewer',
                                               host=self.pg_host,
                                               port=self.pg_port, pg_user=self.pg_user,
                                               pg_password=self.pg_user, schema=self.pg_schema)
            store_created = True




    # TODO: Create shpimport()

    # TODO: Possible implement multiple paths and single TIFF files
    def tiffimport(self):
        tiff_dir = self.path.get()
        path_exists = os.path.exists(tiff_dir)

        if not path_exists:
            self.tiff_comp.set('Could not find path')
        else:
            self.tiff_comp.set('Path Could be found!')
            # Eventually need to change workspace for user's choice
            self.tiff_comp.set(tiff_walk(self.geo, tiff_dir, workspace="CRC"))
    
    # TODO: Create Delete layer interface


root = Tk()
GeoImporter(root)
root.mainloop()
