"""Common helpers for building UI tabs."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk


def add_input(
    parent: tk.Misc,
    label: str,
    var: tk.StringVar,
    row: int,
    on_change: Callable[[], None],
) -> None:
    """Add a labeled entry bound to the provided StringVar.

    Args:
        parent: Parent frame hosting the entry row.
        label: Text displayed next to the entry.
        var: StringVar that stores the entry value.
        row: Grid row for the label/entry pair.
        on_change: Callback invoked when the value changes.
    """
    ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, pady=3)
    entry = ttk.Entry(parent, textvariable=var, width=14)
    entry.grid(row=row, column=1, sticky=tk.E, pady=3, padx=(10, 0))
    entry.bind("<Return>", lambda e: on_change())
    entry.bind("<FocusOut>", lambda e: on_change())


def add_option(
    parent: tk.Misc,
    label: str,
    var: tk.StringVar,
    row: int,
    tooltip: str,
) -> None:
    """Add a labeled option input with descriptive tooltip.

    Args:
        parent: Parent frame used for the input row.
        label: Label text describing the option.
        var: StringVar associated with the option entry.
        row: Row index inside the grid layout.
        tooltip: Supplemental explanation shown alongside input.
    """
    ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, pady=6)
    entry = ttk.Entry(parent, textvariable=var, width=10)
    entry.grid(row=row, column=1, sticky=tk.W, pady=6, padx=(10, 15))
    ttk.Label(parent, text=tooltip, font=("Segoe UI", 8), foreground="#666").grid(
        row=row,
        column=2,
        sticky=tk.W,
    )


def result_block(
    parent: ttk.Frame,
    title: str,
    col: int,
) -> ttk.Label:
    """Create a title + value display block within a row.

    Args:
        parent: Parent frame that hosts the result block.
        title: Title text displayed above the value.
        col: Column index used for layout (unused but maintained for parity).

    Returns:
        The label that shows the numeric value.
    """
    frame = ttk.Frame(parent)
    frame.pack(side=tk.LEFT, expand=True, fill=tk.X)
    ttk.Label(frame, text=title, style="Header.TLabel").pack()
    label = ttk.Label(frame, text="—", style="Result.TLabel")
    label.pack(pady=2)
    return label


__all__ = [
    "add_input",
    "add_option",
    "result_block",
]

__description__ = """
Shared helpers for building Tkinter tabs.
"""
