from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, MutableSequence

import dearpygui.core as dpgcore
from dearpygui_obj import _register_item_type
from dearpygui_obj.data import ColorRGBA, ConfigPropertyColorRGBA
from dearpygui_obj.wrapper import PyGuiWidget, ConfigProperty

if TYPE_CHECKING:
    from typing import Optional, Iterable, Sequence, List
    from dearpygui_obj.wrapper import ItemConfigData

## Basic Content

@_register_item_type('mvAppItemType::Text')
class Text(PyGuiWidget):
    """A basic element that displays some text."""

    value: str

    #: Wrap after this many characters. Set to -1 to disable.
    wrap: int = ConfigProperty()

    #: Display a bullet point with the text.
    bullet: bool = ConfigProperty()

    color: ColorRGBA = ConfigPropertyColorRGBA()

    def __init__(self, value: str = '', *, name_id: str = None, **config):
        super().__init__(default_value=value, name_id=name_id, **config)

    def _setup_add_widget(self, dpg_args) -> None:
        dpgcore.add_text(self.id, **dpg_args)


@_register_item_type('mvAppItemType::LabelText')
class LabelText(PyGuiWidget):
    """Adds text with a label. Useful for output values when used with a data_source."""

    value: str
    label: str = ConfigProperty()
    color: ColorRGBA = ConfigPropertyColorRGBA()

    def __init__(self, label: str = None, value: str = '', *, name_id: str = None, **config):
        super().__init__(label=label, default_value=value, name_id=name_id, **config)

    def _setup_add_widget(self, dpg_args) -> None:
        dpgcore.add_label_text(self.id, **dpg_args)


@_register_item_type('mvAppItemType::Separator')
class Separator(PyGuiWidget):
    """Adds a horizontal line."""
    def __init__(self, *, name_id: str = None, **config):
        super().__init__(name_id=name_id, **config)

    def _setup_add_widget(self, dpg_args) -> None:
        dpgcore.add_separator(name=self.id, **dpg_args)

## Buttons

class ButtonArrow(Enum):
    """Specifies direction for arrow buttons."""
    Left    = 0
    Right   = 1
    Up      = 2
    Down    = 3

@_register_item_type('mvAppItemType::Button')
class Button(PyGuiWidget):
    """A simple button."""

    label: str = ConfigProperty()
    
    #: If ``True``, makes the button a small button. Useful for embedding in text.
    small: bool = ConfigProperty()

    @ConfigProperty()
    def arrow(self) -> Optional[ButtonArrow]:
        """Configure the button as an arrow button.

        If the button is an arrow button, the value will be the arrow direction.
        Otherwise the value will be ``None``.

        Assigning to this property will enable/disable the arrow and/or set the direction."""
        config = self.get_config()
        if not config['arrow']:
            return None
        return ButtonArrow(config['direction'])

    @arrow.getconfig
    def arrow(self, adir: Optional[ButtonArrow]):
        if adir is None:
            return {'arrow': False}
        return {'arrow': True, 'direction': adir.value}

    def __init__(self, label: str = None, *, name_id: str = None, **config):
        super().__init__(label=label, name_id=name_id, **config)

    def _setup_add_widget(self, dpg_args) -> None:
        dpgcore.add_button(self.id, **dpg_args)


@_register_item_type('mvAppItemType::Checkbox')
class Checkbox(PyGuiWidget):
    """Simple checkbox widget."""

    value: bool

    label: str = ConfigProperty()

    def __init__(self, label: str = None, value: bool = False, *, name_id: str = None, **config):
        super().__init__(label=label, default_value=value, name_id=name_id, **config)

    def _setup_add_widget(self, dpg_args) -> None:
        dpgcore.add_checkbox(self.id, **dpg_args)


@_register_item_type('mvAppItemType::RadioButtons')
class RadioButtons(PyGuiWidget, MutableSequence[str]):
    """A set of radio buttons.

    This widget can be used as a mutable sequence of labels. Changing the sequence will
    change the radio buttons in the group and their labels. The value of this widget is the index
    of the selected button.
    """
    value: int

    horizontal: bool = ConfigProperty()

    @ConfigProperty()
    def items(self) -> Sequence[str]:
        """Get or set this widget's items as a sequence."""
        return tuple(self._get_items())

    @items.getconfig
    def items(self, items: Sequence[str]):
        return {'items':list(items)}

    def __init__(self, labels: Iterable[str], value: int = 0, *, name_id: str = None, **config):
        super().__init__(items=labels, default_value=value, name_id=name_id, **config)

    def _setup_add_widget(self, dpg_args) -> None:
        dpgcore.add_radio_button(self.id, **dpg_args)

    def _get_items(self) -> List[str]:
        return self.get_config()['items']

    def __len__(self) -> int:
        return len(self._get_items())

    def __getitem__(self, idx: int) -> str:
        return self._get_items()[idx]

    def __setitem__(self, idx: int, label: str) -> None:
        items = self._get_items()
        items[idx] = label
        self.set_config(items=items)

    def __delitem__(self, idx: int) -> None:
        items = self._get_items()
        del items[idx]
        self.set_config(items=items)

    def insert(self, idx: int, label: str) -> None:
        items = self._get_items()
        items.insert(idx, label)
        self.set_config(items=items)


@_register_item_type('mvAppItemType::ProgressBar')
class ProgressBar(PyGuiWidget):
    """A progress bar.
    Displays a value given between 0.0 and 1.0."""

    value: float

    overlay_text: str = ConfigProperty(key='overlay') #: Overlayed text.

    def __init__(self, value: float = 0.0, *, name_id: str = None, **config):
        super().__init__(default_value=value, name_id=name_id, **config)

    def _setup_add_widget(self, dpg_args) -> None:
        dpgcore.add_progress_bar(self.id, **dpg_args)
