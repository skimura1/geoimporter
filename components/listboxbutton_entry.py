import os

import tkinter as tk
from tkinter import ttk, filedialog

__shapefile__ = "SHAPEFILE"
__raster__ = "RASTER"


class ListBoxandButtons(tk.Frame):
    def __init__(
        self,
        master=None,
        label_text="",
        type="",
        import_files=[],
        import_func=lambda: None,
        **kwargs
    ):
        super().__init__(master, **kwargs)

        # Shapefile directory path field
        self.listbox = tk.Listbox(self, width=20)
        self.label = tk.Label(self, width=12, text=label_text)

        # button to open fileexporer
        self.dir_button = ttk.Button(
            self,
            text="Dir",
            command=lambda: self.get_files(type, self.listbox, import_files),
        )
        self.import_button = ttk.Button(
            self, text="Import", command=lambda: import_func(import_files)
        )

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
        if type == __shapefile__:
            files = filedialog.askopenfilenames(filetypes=[("Shapefiles", "*.shp")])
        else:
            files = filedialog.askopenfilenames(
                filetypes=[("Raster", "*.tif"), ("Raster", "*.tiff")]
            )
        import_files += files
        for file in files:
            filename = os.path.basename(file)
            listbox.insert(tk.END, filename)
