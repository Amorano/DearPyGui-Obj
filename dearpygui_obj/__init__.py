"""An object-oriented Wrapper around DearPyGui 0.6"""

from __future__ import annotations

from warnings import warn
from typing import TYPE_CHECKING

import dearpygui.core as dpgcore

if TYPE_CHECKING:
    from typing import Dict, Iterable, Optional, Callable, Any
    from dearpygui_obj.wrapper import PyGuiBase

# DearPyGui's widget name scope is global, so I guess it's okay that this is too.
_ITEM_LOOKUP: Dict[str, PyGuiBase] = {}

# Used to construct the correct type when getting an item
# that was created outside the object wrapper library
_ITEM_TYPES: Dict[str, Callable[..., PyGuiBase]] = {}

# Fallback constructor used when getting a type that isn't registered in _ITEM_TYPES
_default_ctor: Optional[Callable[..., PyGuiBase]] = None


def get_item_by_id(name: str) -> PyGuiBase:
    """Retrieve an item using its unique name.

    If the item was created by instantiating a :class:`PyGuiBase` object, this will return that
    object. Otherwise, a new wrapper object will be created for that item and returned. Future calls
    for the same ID will return the same object.

    Raises:
        KeyError: if name refers to an item that is invalid (deleted) or does not exist.
    """
    if not dpgcore.does_item_exist(name):
        raise KeyError(f"'{name}' item does not exist")

    item = _ITEM_LOOKUP.get(name)
    if item is not None:
        return item

    item_type = dpgcore.get_item_type(name)
    ctor = _ITEM_TYPES.get(item_type, _default_ctor)
    if ctor is None:
        raise ValueError(f"could not create wrapper for '{name}': no constructor for item type '{item_type}'")

    return ctor(name = name)

def iter_all_items() -> Iterable[PyGuiBase]:
    """Iterate all items (*NOT* windows) and yield their wrapper objects."""
    for name in dpgcore.get_all_items():
        yield get_item_by_id(name)

def iter_all_windows() -> Iterable[PyGuiBase]:
    """Iterate all windows and yield their wrapper objects."""
    for name in dpgcore.get_windows():
        yield get_item_by_id(name)

def get_active_window() -> PyGuiBase:
    """Get the active window."""
    active = dpgcore.get_active_window()
    return get_item_by_id(active)

def _register_item(name: str, instance: PyGuiBase) -> None:
    if name in _ITEM_LOOKUP:
        warn(f"item with name '{name}' already exists in global item registry, overwriting")
    _ITEM_LOOKUP[name] = instance

def _unregister_item(name: str, unregister_children: bool = True) -> None:
    _ITEM_LOOKUP.pop(name, None)
    if unregister_children:
        children = dpgcore.get_item_children(name)
        if children is not None:
            for child_name in children:
                _unregister_item(child_name, True)

## Start/Stop DearPyGui

def start_gui() -> None:
    """Starts the GUI engine (DearPyGui)."""
    dpgcore.start_dearpygui()

def stop_gui() -> None:
    """Stop the GUI engine and exit the main window."""
    dpgcore.stop_dearpygui()

def is_running() -> bool:
    """Get the status of the GUI engine."""
    return dpgcore.is_dearpygui_running()

def set_start_callback(callback: Callable) -> None:
    """Fires when the main window is started."""
    dpgcore.set_start_callback(callback)

def set_exit_callback(callback: Callable) -> None:
    """Fires when the main window is exited."""
    dpgcore.set_exit_callback(callback)

def set_render_callback(callback: Callable) -> None:
    """Fires after rendering each frame."""
    dpgcore.set_render_callback(callback)

def get_delta_time() -> float:
    """Get the time elapsed since the last frame."""
    return dpgcore.get_delta_time()

def get_total_time() -> float:
    """Get the time elapsed since the application started."""
    return dpgcore.get_total_time()

def enable_vsync(enabled: bool) -> None:
    """Enable or disable vsync"""
    return dpgcore.set_vsync(enabled)

## Value Storage System

VALUEREF = object()  #: Sentinel used to create :class:`GuiData` objects that reference existing values.

class GuiData:
    """Manipulate DearPyGui Value Storage.

    For example:

    .. code-block:: python

        linked_text = GuiData('')

        with Window('Data Example'):
            TextInput('Text1', data_source = linked_text)
            TextInput('Text2', data_source = linked_text)
    """

    name: str  #: The unique name identifying the value in the Value Storage system.

    def __init__(self, value: Any = VALUEREF, *, name: Optional[str] = None):
        """
        Note:
            If the GuiData's name does not reference a value that exists, attempts to
            manipulate the value will also fail silently, and attempts to retrieve the value will
            produce ``None``.

            DearPyGui does not provide a function like :func:`does_item_exist` for values so it is
            impossible to detect this.

        Parameters:
            value: the value to store. If the :attr:`ALIAS` sentinel value is provided, the
                GuiData object will instead act as a reference to an existing value instead of
                creating a new value.
            name: The name of the value in the Value Storage system.
                If not provided, a name will be autogenerated.
                This argument is required if :attr:`ALIAS` is passed to **value**.
        """
        if value is VALUEREF:
            # reference an existing value
            if not name:
                raise ValueError("a name is required to create a value reference")
            self.name = name

        else:
            # create a new value
            self.name = name or f'{id(self):x}'
            if dpgcore.get_value(self.name) is not None:
                raise ValueError(f"a value with name '{self.name}' already exists")
            dpgcore.add_value(self.name, value)


    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name!r})"

    def __str__(self) -> str:
        return self.name

    @property
    def value(self) -> Any:
        """Get or set the value's... value."""
        return dpgcore.get_value(self.name)

    @value.setter
    def value(self, new_value: Any) -> None:
        dpgcore.set_value(self.name, new_value)