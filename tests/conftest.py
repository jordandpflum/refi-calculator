"""Pytest fixtures for shared GUI testing utilities."""

from __future__ import annotations

import importlib
import sys
from types import ModuleType

import pytest

from tests.gui_stubs import DummyButton, DummyTtkWidget, create_tkinter_stub
from tests.streamlit_stubs import StreamlitStub, create_streamlit_stub


@pytest.fixture
def tkinter_stub(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Inject a fake tkinter/ttk module before each GUI-focused test.

    Args:
        monkeypatch: Pytest fixture for modifying sys.modules.
    """

    stub = create_tkinter_stub()
    DummyButton.instances.clear()
    DummyTtkWidget.instances.clear()
    monkeypatch.setitem(sys.modules, "tkinter", stub)
    monkeypatch.setitem(sys.modules, "tkinter.ttk", stub.ttk)
    monkeypatch.setitem(sys.modules, "tkinter.filedialog", stub.filedialog)
    monkeypatch.setitem(sys.modules, "tkinter.messagebox", stub.messagebox)
    yield stub


@pytest.fixture
def streamlit_stub(monkeypatch: pytest.MonkeyPatch) -> StreamlitStub:
    """Inject a fake streamlit module for web-focused tests.

    Args:
        monkeypatch: Pytest fixture for modifying sys.modules.

    Returns:
        The stubbed Streamlit module.
    """

    stub = create_streamlit_stub()
    stub.session_state.setdefault("chart_horizon_years", 10)
    stub.session_state.setdefault("sensitivity_max_reduction", 2.0)
    stub.session_state.setdefault("sensitivity_step", 0.25)
    stub.session_state.setdefault("opportunity_rate", 5.0)
    stub.session_state.setdefault("marginal_tax_rate", 0.0)
    stub.session_state.setdefault("npv_window_years", 5)
    stub.session_state.setdefault("maintain_payment", False)
    stub.secrets.setdefault("FRED_API_KEY", "test-key")
    monkeypatch.setitem(sys.modules, "streamlit", stub)
    yield stub


@pytest.fixture
def reload_web_module(
    monkeypatch: pytest.MonkeyPatch,
    streamlit_stub: StreamlitStub,
) -> callable:
    """Reload a Streamlit module so it uses the stubbed implementation.

    Args:
        monkeypatch: Pytest fixture for modifying sys.modules.
        streamlit_stub: The stubbed Streamlit module.

    Returns:
        A callable that reloads the specified module name.
    """

    def _reload(name: str) -> ModuleType:
        """Reload the specified module name.

        Args:
            name: The module name to reload.

        Returns:
            The reloaded module.
        """
        monkeypatch.delitem(sys.modules, name, raising=False)
        return importlib.import_module(name)

    return _reload


@pytest.fixture
def reload_gui_module(
    monkeypatch: pytest.MonkeyPatch,
    tkinter_stub: ModuleType,
) -> callable:
    """Reload a GUI module so it uses the stubbed tkinter implementation.

    Args:
        monkeypatch: Pytest fixture for modifying sys.modules.
        tkinter_stub: The stubbed tkinter module.

    Returns:
        A callable that reloads the specified module name.
    """

    def _reload(name: str) -> ModuleType:
        """Reload the specified module name.

        Args:
            name: The module name to reload.

        Returns:
            The reloaded module.
        """
        monkeypatch.delitem(sys.modules, name, raising=False)
        return importlib.import_module(name)

    return _reload
