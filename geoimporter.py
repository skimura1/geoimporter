import os
import re

from tkinter import *
from tkinter import ttk
import geopandas as gpd
import sqlalchemy as sa
from geo.Geoserver import Geoserver


def tiff_walk(geoserver, tiff_dir, workspace):
    error_layer = []
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

    return error_layer


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

        # Can I implement a file finder?
        self.path = StringVar()
        path_entry = ttk.Entry(mainframe, width=10, textvariable=self.path)
        ttk.Label(mainframe, text="Path:").grid(column=1, row=4, sticky=E)
        path_entry.grid(column=2, row=4, sticky=(W, E))
        ttk.Button(mainframe, text="Import", command=self.tiffimport).grid(column=3, row=4, sticky=E)

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

    def tiffimport(self):
        tiff_dir = self.path.get()
        path_exists = os.path.exists(tiff_dir)

        if not path_exists:
            return "Could not find path"
        # Eventually need to change workspace for user's choice
        return tiff_walk(self.geo, tiff_dir, workspace="CRC")


root = Tk()
GeoImporter(root)
root.mainloop()
