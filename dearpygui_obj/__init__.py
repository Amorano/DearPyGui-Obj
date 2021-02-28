"""An object-oriented Wrapper around DearPyGui 0.6"""

from __future__ import annotations

from warnings import warn
from typing import TYPE_CHECKING, NamedTuple

import dearpygui.core as dpgcore

if TYPE_CHECKING:
    from typing import Dict, Iterable, Optional, Callable, Any, List
    from dearpygui_obj.wrapper import PyGuiObject

# DearPyGui's widget name scope is global, so I guess it's okay that this is too.
_ITEM_LOOKUP: Dict[str, PyGuiObject] = {}

# Used to construct the correct type when getting an item
# that was created outside the object wrapper library
_ITEM_TYPES: Dict[str, Callable[..., PyGuiObject]] = {}

# Fallback constructor used when getting a type that isn't registered in _ITEM_TYPES
_default_ctor: Optional[Callable[..., PyGuiObject]] = None


def get_item_by_id(name: str) -> PyGuiObject:
    """Retrieve an item using its unique name.

    If the item was created by instantiating a :class:`PyGuiObject` object, this will return that
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

    return ctor(name_id = name)

def iter_all_items() -> Iterable[PyGuiObject]:
    """Iterate all items (*NOT* windows) and yield their wrapper objects."""
    for name in dpgcore.get_all_items():
        yield get_item_by_id(name)

def iter_all_windows() -> Iterable[PyGuiObject]:
    """Iterate all windows and yield their wrapper objects."""
    for name in dpgcore.get_windows():
        yield get_item_by_id(name)

def get_active_window() -> PyGuiObject:
    """Get the active window."""
    active = dpgcore.get_active_window()
    return get_item_by_id(active)

def _register_item(name: str, instance: PyGuiObject) -> None:
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

def _generate_id(o: Any) -> str:
    return f'{o.__class__.__name__}##{id(o):x}'

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

def create_value(init_value: Any) -> DataValue:
    """Create a data value

    This can be handy if you need to refer to a value before the widgets that supply the value
    have been added. For example:

    .. code-block:: python

        linked_text = create_value('')
        with Window('Data Example'):
            ## using created value
            TextInput('Text1', data_source = linked_text)
            TextInput('Text2', data_source = linked_text)

            ## directly assign a widget as data source
            text3 = TextInput('Text3', data_source = linked_text)
            TextInput('Text4', data_source = text3)

    """
    proxy = DataValue(None)
    proxy.id = _generate_id(proxy)
    dpgcore.add_value(proxy.id, init_value)
    return proxy


class DataValue:
    """Proxy object for working with Dear PyGui's Value Storage System"""

    id: str

    def __init__(self, data_source: Any):
        self.id = str(data_source)

    def __repr__(self) -> str:
        return f'<{self.__class__.__qualname__}({self.id!r})>'

    def __str__(self) -> str:
        return self.id

    @property
    def value(self) -> Any:
        return dpgcore.get_value(self.id)

    @value.setter
    def value(self, new_value: Any) -> None:
        dpgcore.set_value(self.id, new_value)

