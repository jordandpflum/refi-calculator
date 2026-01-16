"""Streamlit stubs used during web-focused tests."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from types import ModuleType
from typing import Any


class DummyColumn:
    """Minimal column stub that records metric invocations."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.metrics: list[tuple[str, str | float]] = []

    def metric(self, label: str, value: str | float, **kwargs: Any) -> None:
        self.metrics.append((label, value))


class DummyTab:
    """Simple context manager that mimics Streamlit tab objects."""

    def __init__(self, label: str, stub: StreamlitStub) -> None:
        self.label = label
        self.stub = stub

    def __enter__(self) -> DummyTab:
        self.stub.calls.append(("enter_tab", self.label))
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        self.stub.calls.append(("exit_tab", self.label))
        return False


class StreamlitStub(ModuleType):
    """Module-like stub that records Streamlit API interactions."""

    def __init__(self) -> None:
        super().__init__("streamlit")
        self.calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []
        self.session_state: dict[str, Any] = {}
        self.secrets: dict[str, Any] = {}

    def _record(self, name: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> None:
        self.calls.append((name, args, kwargs))

    def tabs(self, labels: Sequence[str]) -> tuple[DummyTab, ...]:
        self._record("tabs", (tuple(labels),), {})
        return tuple(DummyTab(label, self) for label in labels)

    def columns(self, count: int) -> list[DummyColumn]:
        self._record("columns", (count,), {})
        return [DummyColumn(f"col{i}") for i in range(count)]

    def subheader(self, text: str) -> None:
        self._record("subheader", (text,), {})

    def title(self, text: str) -> None:
        self._record("title", (text,), {})

    def write(self, message: str) -> None:
        self._record("write", (message,), {})

    def divider(self) -> None:
        self._record("divider", (), {})

    def markdown(self, message: str) -> None:
        self._record("markdown", (message,), {})

    def info(self, message: str) -> None:
        self._record("info", (message,), {})

    def warning(self, message: str) -> None:
        self._record("warning", (message,), {})

    def error(self, message: str) -> None:
        self._record("error", (message,), {})

    def caption(self, message: str) -> None:
        self._record("caption", (message,), {})

    def metric(self, label: str, value: str | float) -> None:
        self._record("metric", (label, value), {})

    def line_chart(self, data: Any, **kwargs: Any) -> None:
        self._record("line_chart", (data,), kwargs)

    def plotly_chart(self, data: Any, **kwargs: Any) -> None:
        self._record("plotly_chart", (data,), kwargs)

    def dataframe(self, data: Any, **kwargs: Any) -> None:
        self._record("dataframe", (data,), kwargs)

    def radio(
        self,
        label: str,
        options: Iterable[str],
        horizontal: bool | None = None,
        key: str | None = None,
    ) -> str:
        self._record("radio", (label, tuple(options)), {"horizontal": horizontal, "key": key})
        return next(iter(options))

    def number_input(
        self,
        label: str,
        min_value: float | int,
        max_value: float | int | None = None,
        value: float | int = 0,
        step: float | int = 1,
        key: str | None = None,
        **kwargs: Any,
    ) -> float | int:
        self._record(
            "number_input",
            (label, min_value, max_value, value, step),
            {"key": key, **kwargs},
        )
        return value

    def checkbox(
        self,
        label: str,
        value: bool,
        key: str | None = None,
    ) -> bool:
        self._record("checkbox", (label, value), {"key": key})
        return value

    def set_page_config(self, **kwargs: Any) -> None:
        self._record("set_page_config", (), kwargs)

    def cache_data(self, ttl: int | None = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Simulate the cache_data decorator that Streamlit exposes."""

        def decorator(func: callable) -> callable:
            def wrapper(*args: object, **kwargs: Any) -> Any:
                return func(*args, **kwargs)

            return wrapper

        return decorator


def create_streamlit_stub() -> StreamlitStub:
    """Create a fresh Streamlit stub module."""

    return StreamlitStub()


__all__ = [
    "StreamlitStub",
    "create_streamlit_stub",
]
