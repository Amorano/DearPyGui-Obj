from __future__ import annotations

from enum import Enum
from warnings import warn
from typing import TYPE_CHECKING, NamedTuple, overload

from dearpygui import core as dpgcore

from dearpygui_obj import _register_item_type, try_get_item_by_id, wrap_callback
from dearpygui_obj.wrapper.widget import PyGuiWidget, ConfigProperty

if TYPE_CHECKING:
    from typing import Optional, Iterable, Callable
    from dearpygui_obj import PyGuiCallback


class NodeLinkError(Exception):
    """Raised when a link cannot be created."""

class NodeLink(NamedTuple):
    """Holds info about a link between two :class:`.NodeAttribute` objects."""
    input: NodeAttribute   #: The input end of the link.
    output: NodeAttribute  #: The output end of the link.

    @classmethod
    def from_endpoints(cls, end1: NodeAttribute, end2: NodeAttribute) -> NodeLink:
        """Creates a NodeLink from an input and an output node.

        Raises:
            NodeLinkError: if exactly 1 input node and 1 output node was not provided.
        """
        endpoints = end1, end2

        inputs = [ end for end in endpoints if end.is_input() ]
        if len(inputs) != 1:
            raise NodeLinkError('did not provide exactly 1 input endpoint')

        outputs = [ end for end in endpoints if end.is_output() ]
        if len(outputs) != 1:
            raise NodeLinkError('did not provide exactly 1 output endpoint')

        return cls(input=inputs[0], output=outputs[0])


def _get_link_from_ids(id1: str, id2: str) -> NodeLink:
    end1 = try_get_item_by_id(id1)
    end2 = try_get_item_by_id(id2)
    if not isinstance(end1, NodeAttribute) or not isinstance(end2, NodeAttribute):
        raise NodeLinkError('given id does not reference a NodeAttribute')
    return NodeLink.from_endpoints(end1, end2)


@_register_item_type('mvAppItemType::NodeEditor')
class NodeEditor(PyGuiWidget):
    """A canvas specific to graph node workflow.

    Should only contain :class:`.Node` objects. Any other kind of widget will not be displayed.
    """

    def __init__(self, *, name_id: str = None, **config):
        super().__init__(name_id=name_id, **config)

    def _setup_add_widget(self, dpg_args) -> None:
        dpgcore.add_node_editor(
            self.id, link_callback=self._on_link, delink_callback=self._on_delink, **dpg_args,
        )

    def __enter__(self) -> NodeEditor:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        dpgcore.end()

    ## Links

    def get_all_links(self) -> Iterable[NodeLink]:
        """Get all linkages between any :class:`.NodeAttribute` objects in the editor."""
        for id1, id2 in dpgcore.get_links(self.id):
            try:
                yield _get_link_from_ids(id1, id2)
            except NodeLinkError:
                warn('dearpygui.core.get_links() produced an invalid link, this is likely due to a bug in DPG')

    def add_link(self, end1: NodeAttribute, end2: NodeAttribute) -> NodeLink:
        """Adds a link between two :class:`.NodeAttribute` objects.

        Raises:
            NodeLinkError: if exactly 1 input node and 1 output node was not provided.
        """
        dpgcore.add_node_link(self.id, end1.id, end2.id)
        return NodeLink.from_endpoints(end1, end2)

    @overload
    def delete_link(self, link: NodeLink) -> None:
        ...
    @overload
    def delete_link(self, end1: NodeAttribute, end2: NodeAttribute) -> None:
        ...
    def delete_link(self, end1, end2 = None) -> None:
        """Deletes a link between two :class:`.NodeAttribute` objects if a link exists."""
        if end2 is None:
            link = end1
            dpgcore.delete_node_link(self.id, link.input.id, link.output.id)
        else:
            dpgcore.delete_node_link(self.id, end1.id, end2.id)

    ## Node and Link Selection

    def get_selected_links(self) -> Iterable[NodeLink]:
        """Get all links in the selected state."""
        for id1, id2 in dpgcore.get_selected_links(self.id):
            try:
                yield _get_link_from_ids(id1, id2)
            except NodeLinkError:
                warn('dearpygui.core.get_selected_links() produced an invalid link, this is likely due to a bug in DPG')

    def clear_link_selection(self) -> None:
        """Clears all links from being in the selection state."""
        dpgcore.clear_selected_links(self.id)

    def get_selected_nodes(self) -> Iterable[Node]:
        """Get all nodes in the selected state."""
        for node_id in dpgcore.get_selected_nodes(self.id):
            node = try_get_item_by_id(node_id)
            if node is not None:
                yield node

    def clear_node_selection(self) -> None:
        """Clears all nodes from being in the selection state."""
        dpgcore.clear_selected_nodes(self.id)

    ## Callbacks

    ## workaround for the fact that you can't set the link_callback or delink_callback properties in DPG
    _on_link_callback: Optional[Callable] = None
    _on_delink_callback: Optional[Callable] = None

    def _on_link(self, sender, data) -> None:
        if self._on_link_callback is not None:
            self._on_link_callback(sender, data)

    def _on_delink(self, sender, data) -> None:
        if self._on_delink_callback is not None:
            self._on_delink_callback(sender, data)

    def link_callback(self, callback: Optional[PyGuiCallback]) -> Callable:
        """Set the link callback, can be used as a decorator."""
        if callback is not None:
            callback = wrap_callback(callback)
        self._on_link_callback = callback
        return callback

    def delink_callback(self, callback: Optional[PyGuiCallback]) -> Callable:
        """Set the delink callback, can be used as a decorator."""
        if callback is not None:
            callback = wrap_callback(callback)
        self._on_delink_callback = callback
        return callback


@_register_item_type('mvAppItemType::Node')
class Node(PyGuiWidget):
    """A :class:`.NodeEditor` node.

    Should only contain :class:`.NodeAttribute` objects, any other kind of widget will not be
    displayed. Note that :class:`.NodeAttribute` objects may contain any kind or number of widget
    though."""

    label: str = ConfigProperty()
    draggable: bool = ConfigProperty()

    def __init__(self, label: str = None, *, name_id: str = None, **config):
        super().__init__(label=label, name_id=name_id, **config)

    def _setup_add_widget(self, dpg_args) -> None:
        dpgcore.add_node(self.id, **dpg_args)

    def __enter__(self) -> Node:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        dpgcore.end()


class NodeAttributeType(Enum):
    """Specifies how a :class:`.NodeAttribute` will link to other nodes."""
    Input  = None  #: Input nodes may only link to Output nodes.
    Output = 'output'  #: Output nodes may only link to Input nodes.
    Static = 'static'  #: Static nodes do not link. They are still useful as containers to place widgets inside a node.

def input_attribute(*, name_id: str = None) -> NodeAttribute:
    """Shortcut constructor for ``NodeAttribute(NodeAttributeType.Input)``"""
    return NodeAttribute(NodeAttributeType.Input, name_id=name_id)

def output_attribute(*, name_id: str = None) -> NodeAttribute:
    """Shortcut constructor for ``NodeAttribute(NodeAttributeType.Output)``"""
    return NodeAttribute(NodeAttributeType.Output, name_id=name_id)

def static_attribute(*, name_id: str = None) -> NodeAttribute:
    """Shortcut constructor for ``NodeAttribute(NodeAttributeType.Static)``"""
    return NodeAttribute(NodeAttributeType.Static, name_id=name_id)

@_register_item_type('mvAppItemType::NodeAttribute')
class NodeAttribute(PyGuiWidget):
    """An attachment point for a :class:`.Node`."""

    type: NodeAttributeType
    @ConfigProperty()
    def type(self) -> NodeAttributeType:
        config = self.get_config()
        for mode in NodeAttributeType:
            if mode.value is not None and config.get(mode.value):
                return mode
        return NodeAttributeType.Input

    @type.getconfig
    def type(self, value: NodeAttributeType):
        return {
            mode.value : (mode == value)  for mode in NodeAttributeType if mode.value is not None
        }

    def __init__(self, type: NodeAttributeType = NodeAttributeType.Input, *, name_id: str = None, **config):
        super().__init__(type=type, name_id=name_id, **config)

    def _setup_add_widget(self, dpg_args) -> None:
        dpgcore.add_node_attribute(self.id, **dpg_args)

    def __enter__(self) -> NodeAttribute:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        dpgcore.end()

    def is_input(self) -> bool:
        """Shortcut for ``self.type == NodeAttributeType.Input``."""
        return self.type == NodeAttributeType.Input

    def is_output(self) -> bool:
        """Shortcut for ``self.type == NodeAttributeType.Output``."""
        return self.type == NodeAttributeType.Output

    def is_static(self) -> bool:
        """Shortcut for ``self.type == NodeAttributeType.Static``."""
        return self.type == NodeAttributeType.Static


__all__ = [
    'NodeEditor',
    'Node',
    'NodeAttribute',
    'NodeLink',
    'NodeLinkError',
    'NodeAttributeType',
    'input_attribute',
    'output_attribute',
    'static_attribute',
]
