import tkinter as tk
from tkinter import  ttk, filedialog
from pathlib import Path
from typing import Callable

__shapefile__ = "SHAPEFILE"
__raster__ = "RASTER"


class ListBoxandButtons(ttk.Frame):
    """ 
    This class bundle the listbox and button components

    Attributes:
        import_files (list[Path]): An array that holds the paths to the files
        master (ttk.Frame): The frame that we want to list this component
        label_text (str): The label of the list box
        type (str): Type of the file that is being listed
        import_func (Callable): Anonymous function to be carried out when button is clicked
    """
    def __init__(
        self,
        import_files: list[Path],
        import_func: Callable[[list[Path]], None],
        master: ttk.Frame|None = None,
        label_text: str="",
        type: str="",
    ):
        super().__init__(master)
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
        Get files from the file dialog
        Args:
            type: Type of file for the file dialog
            listbox: Listbox to populate the file with

        Returns:
            Void

        """
        self.import_files: list[Path] = []
        files = []

        # Clear Listbox before populating
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
    """ 
    This class bundle the listbox and button components for deletion

    Attributes:
        import_files (list[Path]): An array that holds the paths to the files
        master (ttk.Frame): The frame that we want to list this component
        label_text (str): The label of the delete box
        type (str): Type of the file that is being listed
        import_func (Callable): Anonymous function to be carried out when button is clicked
    """
    def __init__(
        self,
        master: ttk.Frame,
        label_text,
    ):
        super().__init__(master)
        # Shapefile directory path field
        self.listbox: tk.Listbox = tk.Listbox(self, width=20, selectmode=tk.MULTIPLE)
        self.label = tk.Label(self, width=12, text=label_text)
        self.delete_files: list[int] = self.listbox.curselection()

        self.label.pack(side=tk.LEFT)
        self.listbox.pack(side=tk.LEFT)

    def populate_listbox(self, items: list[str]) -> None: 
        """
        Get files from the file dialog
        Args:
            items: List of paths to populate the listbox
        Returns:
            Void

        """
        for i in items:
            self.listbox.insert("end", i)
