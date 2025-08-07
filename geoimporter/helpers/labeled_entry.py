import tkinter as tk
from tkinter import Variable, ttk
from typing import Callable


class LabeledEntry(tk.Frame):
    """ 
    This class bundles the entry component and button component

    Attributes:
        label_text (str): The label of the input text box
        entry_text (Variable): Variable text that holds the input of the input text box 
        show (str): Shows this text instead of the actual text in case of hiding purposes (password)
        button_func (Callable): Anonymous function to be carried out when the button is clicked
        button_label: (str): Label of the button
    """
    def __init__(
        self,
        master: ttk.Frame,
        entry_text: Variable,
        label_text: str ="",
        show: str="",
        button_func: Callable[[], None] | None = None,
        button_label: str="",
    ):
        super().__init__(master)
        self.label = tk.Label(self, width=12, text=label_text)
        self.label.pack(side=tk.LEFT)

        if show == "*":
            self.entry = tk.Entry(
                self, width=20, textvariable=entry_text, show="*"
            )
            self.entry.pack(side=tk.LEFT)
        else:
            self.entry = tk.Entry(self, width=20, textvariable=entry_text)
            self.entry.pack(side=tk.LEFT)

        if button_func is not None:
            self.button = ttk.Button(self, text=button_label, command=button_func)
            self.button.pack(side=tk.LEFT)
        else:
            tk.Label(self, width=10).pack(side=tk.LEFT)

        tk.Label(self, width=10).pack(side=tk.LEFT)
