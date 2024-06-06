import os

import tkinter as tk
from tkinter import StringVar, ttk, filedialog
from pathlib import Path

from sqlalchemy.sql import delete

__shapefile__ = "SHAPEFILE"
__raster__ = "RASTER"


class ListBoxandButtons(tk.Frame):
    def __init__(
        self,
        master=None,
        label_text: str="",
        type: str="",
        import_files: list[Path]=[],
        import_func=lambda: None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.import_files = import_files
        self.import_func = import_func
        self.type = type
        self.label_text = label_text

        # Shapefile directory path field
        self.listbox = tk.Listbox(self, width=20)
        self.label = tk.Label(self, width=12, text=label_text)

        # button to open fileexporer
        self.dir_button = ttk.Button(
            self,
            text="Dir",
            command=lambda: self.get_files(type, self.listbox),
        )
        self.import_button = ttk.Button(
            self, text="Import", command=lambda: import_func(self.import_files)
        )

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
        self.import_files = []

        listbox.delete(0, tk.END)
        if type == __shapefile__:
            files = filedialog.askopenfilenames(filetypes=[("Shapefiles", "*.shp")])
        else:
            files = filedialog.askopenfilenames(
                filetypes=[("Raster", "*.tif"), ("Raster", "*.tiff")]
            )

        for file in files:
            self.import_files.append(Path(file))
            filename = Path(file).name
            listbox.insert(tk.END, filename)


class DeleteBoxandButtons(tk.Frame):
    def __init__(
        self,
        master=None,
        label_text="",
        listbox=None,
        type="",
        delete_func=lambda: None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        # Shapefile directory path field
        self.listbox = tk.Listbox(self, width=20, selectmode=tk.MULTIPLE)
        self.label = tk.Label(self, width=12, text=label_text)
        self.delete_files = self.listbox.curselection()

        self.label.pack(side=tk.LEFT)
        self.listbox.pack(side=tk.LEFT)

    def populate_listbox(self, items):
        for i in items:
            self.listbox.insert("end", i)
