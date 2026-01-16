"""Reusable tkinter/ttk stubs for GUI tests."""

from __future__ import annotations

from collections.abc import Iterable
from types import ModuleType
from typing import Any


class DummyTtkWidget:
    """Base stub for ttk widgets that exposes layout/no-op APIs."""

    instances: list[DummyTtkWidget] = []

    def __init__(
        self,
        *args: object,
        **kwargs: object,
    ) -> None:
        """Initialize the dummy widget and record its args/kwargs.

        Args:
            *args: Positional arguments passed to the widget.
            **kwargs: Keyword arguments passed to the widget.
        """
        self.args = args
        self.kwargs = kwargs
        self.operations: list[tuple[str, tuple[object, ...], dict[str, object]]] = []
        DummyTtkWidget.instances.append(self)

    def pack(
        self,
        *args: object,
        **kwargs: object,
    ) -> None:
        """Pack the widget and record the call.

        Args:
            *args: Positional arguments for pack.
            **kwargs: Keyword arguments for pack.
        """
        self.operations.append(("pack", args, kwargs))

    def pack_forget(
        self,
        *args: object,
        **kwargs: object,
    ) -> None:
        """Pack forget the widget and record the call.

        Args:
            *args: Positional arguments for pack_forget.
            **kwargs: Keyword arguments for pack_forget.
        """
        self.operations.append(("pack_forget", args, kwargs))

    def grid(
        self,
        *args: object,
        **kwargs: object,
    ) -> None:
        """Grid the widget and record the call.

        Args:
            *args: Positional arguments for grid.
            **kwargs: Keyword arguments for grid.
        """
        self.operations.append(("grid", args, kwargs))

    def configure(
        self,
        *args: object,
        **kwargs: object,
    ) -> None:
        """Configure the widget and record the call.

        Args:
            *args: Positional arguments for configure.
            **kwargs: Keyword arguments for configure.
        """
        self.operations.append(("configure", args, kwargs))

    def bind(self, *args: object, **kwargs: object) -> None:
        self.operations.append(("bind", args, kwargs))

    def yview(self, *args: object, **kwargs: object) -> None:
        self.operations.append(("yview", args, kwargs))

    def add(self, *args: object, **kwargs: object) -> None:
        self.operations.append(("add", args, kwargs))

    def heading(self, *args: object, **kwargs: object) -> None:
        self.operations.append(("heading", args, kwargs))

    def column(self, *args: object, **kwargs: object) -> None:
        self.operations.append(("column", args, kwargs))

    def insert(self, *args: object, **kwargs: object) -> None:
        self.operations.append(("insert", args, kwargs))

    def destroy(self, *args: object, **kwargs: object) -> None:
        self.operations.append(("destroy", args, kwargs))


class DummyCanvas(DummyTtkWidget):
    """Minimal canvas stub that records draw calls."""

    def delete(self, *args: object, **kwargs: object) -> None:
        self.operations.append(("delete", args, kwargs))

    def create_line(self, *args: object, **kwargs: object) -> None:
        self.operations.append(("create_line", args, kwargs))

    def create_text(self, *args: object, **kwargs: object) -> None:
        self.operations.append(("create_text", args, kwargs))

    def create_window(self, *args: object, **kwargs: object) -> str:
        self.operations.append(("create_window", args, kwargs))
        return "window-id"

    def bbox(self, *args: object, **kwargs: object) -> tuple[int, int, int, int]:
        self.operations.append(("bbox", args, kwargs))
        return (0, 0, 0, 0)

    def itemconfig(self, *args: object, **kwargs: object) -> None:
        self.operations.append(("itemconfig", args, kwargs))

    def configure(self, *args: object, **kwargs: object) -> None:
        super().configure(*args, **kwargs)

    def bind(self, *args: object, **kwargs: object) -> None:
        super().bind(*args, **kwargs)


class DummyLabel(DummyTtkWidget):
    """Stub for ttk.Label instances used in helper functions."""


class DummyTreeview(DummyTtkWidget):
    """Stub treeview that records layout configuration."""

    def __init__(
        self, *args: object, columns: Iterable[str] | None = None, **kwargs: object,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.columns = tuple(columns or ())
        self.show = kwargs.get("show")
        self.height = kwargs.get("height")
        self.headings: dict[str, str] = {}
        self.column_configs: dict[str, dict[str, object]] = {}

    def heading(self, column: str, text: str) -> None:
        self.headings[column] = text
        super().heading(column=column, text=text)

    def column(self, column: str, **kwargs: object) -> None:
        self.column_configs[column] = kwargs
        super().column(column=column, **kwargs)


class DummyCommandWidget(DummyTtkWidget):
    """Widget that exposes a command for buttons and radiobuttons."""

    def __init__(self, *args: object, command: Any | None = None, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.command = command


class DummyButton(DummyCommandWidget):
    """Stub button that captures the command it should run."""

    instances: list[DummyButton] = []

    def __init__(self, *args: object, command: Any | None = None, **kwargs: object) -> None:
        super().__init__(*args, command=command, **kwargs)
        DummyButton.instances.append(self)


class DummyRadiobutton(DummyCommandWidget):
    """Stub radiobutton that stores its value/command."""

    def __init__(
        self,
        *args: object,
        value: object | None = None,
        variable: object | None = None,
        **kwargs: object,
    ) -> None:
        command = kwargs.pop("command", None)
        super().__init__(*args, command=command, **kwargs)
        self.value = value
        self.variable = variable


class DummyScrollbar(DummyCommandWidget):
    """Stub scrollbar that remembers orient and command."""

    def __init__(self, *args: object, orient: object | None = None, **kwargs: object) -> None:
        command = kwargs.pop("command", None)
        super().__init__(*args, command=command, **kwargs)
        self.orient = orient

    def set(self, *args: object, **kwargs: object) -> None:
        self.operations.append(("set", args, kwargs))


class DummyStyle(DummyTtkWidget):
    """Stub style for configuring fonts/colors."""

    def lookup(self, *args: object, **kwargs: object) -> str:
        return ""


def create_tkinter_stub() -> ModuleType:
    """Create a tkinter module stub that exposes Canvas, ttk, filedialog, and messagebox."""

    module = ModuleType("tkinter")
    module.Canvas = DummyCanvas
    module.Misc = object
    module.SW = "sw"
    module.N = "n"
    module.S = "s"
    module.E = "e"
    module.W = "w"
    module.LEFT = "left"
    module.RIGHT = "right"
    module.X = "x"
    module.Y = "y"
    module.NW = "nw"
    module.CENTER = "center"
    module.BOTH = "both"
    module.SUNKEN = "sunken"
    module.HORIZONTAL = "horizontal"
    module.VERTICAL = "vertical"
    module.Label = DummyLabel

    module.ttk = ModuleType("tkinter.ttk")
    module.ttk.Frame = DummyTtkWidget
    module.ttk.LabelFrame = DummyTtkWidget
    module.ttk.Label = DummyLabel
    module.ttk.Button = DummyButton
    module.ttk.Entry = DummyTtkWidget
    module.ttk.Checkbutton = DummyTtkWidget
    module.ttk.Separator = DummyTtkWidget
    module.ttk.Treeview = DummyTreeview
    module.ttk.Scrollbar = DummyScrollbar
    module.ttk.Radiobutton = DummyRadiobutton
    module.ttk.Notebook = DummyTtkWidget
    module.ttk.Style = DummyStyle

    module.filedialog = ModuleType("tkinter.filedialog")
    module.filedialog.asksaveasfilename = lambda *args, **kwargs: ""
    module.filedialog.askopenfilename = lambda *args, **kwargs: ""
    module.messagebox = ModuleType("tkinter.messagebox")
    for name in ("showinfo", "showwarning", "showerror"):
        setattr(module.messagebox, name, lambda *args, **kwargs: None)

    return module


__all__ = [
    "DummyButton",
    "DummyCanvas",
    "DummyCommandWidget",
    "DummyLabel",
    "DummyRadiobutton",
    "DummyScrollbar",
    "DummyStyle",
    "DummyTreeview",
    "DummyTtkWidget",
    "create_tkinter_stub",
]
