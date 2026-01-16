"""Tests for the shared GUI helper utilities."""

from __future__ import annotations

from tests.gui_stubs import DummyLabel, DummyTtkWidget


def test_add_input_creates_entries_and_binds_callbacks(reload_gui_module: callable) -> None:
    """inputs get a label + entry, and the entry hooks the provided callbacks."""

    helpers = reload_gui_module("refi_calculator.gui.builders.helpers")
    DummyTtkWidget.instances.clear()
    parent = DummyTtkWidget()
    var = object()

    helpers.add_input(parent, "Test Label", var, row=2, on_change=lambda: None)

    labels = [w for w in DummyTtkWidget.instances if isinstance(w, DummyLabel)]
    entry = next(w for w in DummyTtkWidget.instances if w.kwargs.get("textvariable") is var)

    assert any(label.kwargs.get("text") == "Test Label" for label in labels)
    assert any(op[0] == "grid" for op in entry.operations)
    assert sum(1 for op in entry.operations if op[0] == "bind") == 2


def test_add_option_appends_tooltip_label(reload_gui_module: callable) -> None:
    """Options rows add the tooltip text beside the entry value."""

    helpers = reload_gui_module("refi_calculator.gui.builders.helpers")
    DummyTtkWidget.instances.clear()
    parent = DummyTtkWidget()
    var = object()

    helpers.add_option(parent, "Option Label", var, row=1, tooltip="Tooltip text")

    tooltips = [
        w for w in DummyTtkWidget.instances if isinstance(w, DummyLabel) and w.kwargs.get("text") == "Tooltip text"
    ]
    assert tooltips
    assert any(op[0] == "grid" for op in tooltips[0].operations)


def test_result_block_returns_label_and_arranges(reload_gui_module: callable) -> None:
    """Result blocks create a titled area and return the label that shows values."""

    helpers = reload_gui_module("refi_calculator.gui.builders.helpers")
    DummyTtkWidget.instances.clear()
    parent = DummyTtkWidget()
    label = helpers.result_block(parent, "Title", 0)

    assert isinstance(label, DummyLabel)
    assert label.kwargs.get("text") == "—"
    assert any(op[0] == "pack" for op in label.operations)
