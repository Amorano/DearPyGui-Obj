"""Widgets for controlling layout."""

from __future__ import annotations
from typing import TYPE_CHECKING

import dearpygui.core as dpgcore
from dearpygui_obj.wrapper import PyGuiBase, dearpygui_wrapper, ConfigProperty

if TYPE_CHECKING:
    pass

@dearpygui_wrapper('mvAppItemType::Spacing')
class VSpacing(PyGuiBase):
    """Adds vertical spacing."""

    space: int = ConfigProperty(key='count') #: The amount of vertical space.

    def _setup_add_widget(self, config) -> None:
        dpgcore.add_spacing(name=self.id, **config)


@dearpygui_wrapper('mvAppItemType::SameLine')
class HAlignNext(PyGuiBase):
    """Places a widget on the same line as the previous widget.
    Can also be used for horizontal spacing."""

    xoffset: float = ConfigProperty() #: offset from containing window
    spacing: float = ConfigProperty() #: offset from previous widget

    def _setup_add_widget(self, config) -> None:
        dpgcore.add_same_line(name=self.id, **config)


@dearpygui_wrapper('mvAppItemType::Child')
class ScrollView(PyGuiBase):
    """Adds an embedded child window. Will show scrollbars when items do not fit.

    This is a container widget."""

    def _setup_add_widget(self, config) -> None:
        dpgcore.add_child(self.id, **config)

    def __enter__(self) -> ScrollView:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.is_container():
            dpgcore.end()


if __name__ == '__main__':
    from dearpygui.core import *
    from dearpygui_obj import *
    from dearpygui_obj.window import Window
    from dearpygui_obj.basic import Button
    from dearpygui_obj.devtools import *

    with DebugWindow():
        pass

    with DocumentationWindow():
        pass

    with Window('Window'):
        with ScrollView():
            Button()
            HAlignNext(spacing=15)
            Button()
            HAlignNext(spacing=15)
            Button()
            VSpacing(space=5)
            Button()
            Button()
            VSpacing(space=10)
            Button()


    for item in iter_all_items():
        print(item.id, get_item_type(item.id))


    # start_dearpygui()

