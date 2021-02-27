from __future__ import annotations

from typing import TYPE_CHECKING

import dearpygui.core as dpgcore
from dearpygui_obj.wrapper import PyGuiObject, dearpygui_wrapper, ConfigProperty

if TYPE_CHECKING:
    from typing import Optional, Tuple, Callable
    from dearpygui_obj.wrapper import ItemConfigData


class MainWindow:
    """Container for static functions used to manipulate the main window.

    Attempting to instantiate this class will raise a :class:`TypeError`.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError('this class may not be instantiated')

    @staticmethod
    def set_title(title: str) -> None:
        dpgcore.set_main_window_title(title)

    @staticmethod
    def set_pos(x: int, y: int) -> None:
        dpgcore.set_main_window_pos(x, y)

    @staticmethod
    def allow_resize(enabled: bool):
        dpgcore.set_main_window_resizable(enabled)

    @staticmethod
    def set_size(width: int, height: int):
        dpgcore.set_main_window_size(width, height)

    @staticmethod
    def get_size() -> Tuple[int, int]:
        return tuple(dpgcore.get_main_window_size())

    @staticmethod
    def set_primary_window(window: Optional[Window]) -> None:
        """Set a window as the primary window, or remove the primary window.

        When a window is set as the primary window it will fill the entire viewport.

        If any other window was already set as the primary window, it will be unset.
        """
        if window is not None:
            dpgcore.set_primary_window(window.id, True)
        else:
            dpgcore.set_primary_window('', False)

    @staticmethod
    def set_resize_callback(callback: Callable):
        """Set a callback for when the main viewport is resized."""
        dpgcore.set_resize_callback(callback, handler='')

    @staticmethod
    def enable_docking(**kwargs):
        """Enable docking and set docking options.

        Note:
            Once docking is enabled, it cannot be disabled.

        Keyword Arguments:
            shift_only: if ``True``, hold down shift for docking.
                If ``False``, dock by dragging window titlebars.
            dock_space: if ``True``, windows will be able to dock
                with the main window viewport.
        """
        dpgcore.enable_docking(**kwargs)


@dearpygui_wrapper('mvAppItemType::Window')
class Window(PyGuiObject):
    """Creates a new window.

    This is a container item that should be used as a context manager. For example:

    .. code-block:: python

        with Window('Example Window'):
            TextInput('Child Input')
            Button('Child Button')

    """

    label: str = ConfigProperty()
    x_pos: int = ConfigProperty()
    y_pos: int = ConfigProperty()
    autosize: bool = ConfigProperty()

    no_resize: bool = ConfigProperty()
    no_title_bar: bool = ConfigProperty()
    no_move: bool = ConfigProperty()
    no_collapse: bool = ConfigProperty()
    no_focus_on_appearing: bool = ConfigProperty()
    no_bring_to_front_on_focus: bool = ConfigProperty()
    no_close: bool = ConfigProperty()
    no_background: bool = ConfigProperty()

    menubar: bool = ConfigProperty()

    #: Disable scrollbars (can still scroll with mouse or programmatically).
    no_scrollbar: bool = ConfigProperty()

    #: Allow horizontal scrollbar to appear.
    horizontal_scrollbar: bool = ConfigProperty()

    @ConfigProperty()
    def pos(self) -> Tuple[int, int]:
        """Get or set (x_pos, y_pos) as a tuple."""
        config = self.get_config()
        return config['x_pos'], config['y_pos']

    @pos.getconfig
    def pos(self, value: Tuple[int, int]) -> ItemConfigData:
        width, height = value
        return {'x_pos': width, 'y_pos' : height}

    _on_close: Optional[Callable] = None

    def __init__(self, label: str = '', *, name_id: str = None, **config):
        super().__init__(label=label, name_id=name_id, **config)

    def _setup_add_widget(self, dpg_args) -> None:
        dpgcore.add_window(self.id, **dpg_args)

    def __enter__(self) -> Window:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        dpgcore.end()

    def _handle_on_close(self, sender, data) -> None:
        if self._on_close is not None:
            self._on_close(sender, data)

    def on_close(self, callback: Callable) -> Callable:
        """Set on_close callback, can be used as a decorator."""
        self._on_close = callback
        return callback

    def resized(self, callback: Callable) -> Callable:
        """Set resized callback, can be used as a decorator."""
        dpgcore.set_resize_callback(callback, handler=self.id)
        return callback

if __name__ == '__main__':
    from dearpygui.core import *

    from dearpygui_obj import iter_all_windows

    for win in iter_all_windows():
        print(win.id, win.is_container())

    start_dearpygui()

