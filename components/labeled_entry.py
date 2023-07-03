import tkinter as tk
from tkinter import ttk


class LabeledEntry(tk.Frame):
    def __init__(
        self,
        master=None,
        label_text="",
        entry_text=None,
        show="",
        button_func=None,
        button_label="",
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.label = tk.Label(self, width=12, text=label_text)
        self.label.pack(side=tk.LEFT)

        if show == "*":
            self.entry = tk.Entry(
                self, width=20, textvariable=entry_text, show="*"
            ).pack(side=tk.LEFT)
        else:
            self.entry = tk.Entry(self, width=20, textvariable=entry_text).pack(
                side=tk.LEFT
            )

        if button_func is not None:
            self.button = ttk.Button(self, text=button_label, command=button_func).pack(
                side=tk.LEFT
            )
        else:
            tk.Label(self, width=10).pack(side=tk.LEFT)

        tk.Label(self, width=10).pack(side=tk.LEFT)
