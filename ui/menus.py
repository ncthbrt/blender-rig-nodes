# SPDX-FileCopyrightText: 2025 Natalie Cuthbert <natalie@cuthbert.co.za>
# SPDX-FileCopyrightText: 2025 BD3D DIGITAL DESIGN (Dorian B.)
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy

import os


# NOTE we automatically register the submenus from that list below.
# TODO auto registration of submenus could be improved
# - we could use the _GN_, _SH_, _CP_ notations perhaps.
# - we could use an attribute per node class for submenu appartenance.
# - we could also use the poll classmethod to avoid rendundancy.

from ..customnodes import (
    GN_CustomNodes,
)


class DynaMenu:
    """Base class for menus that automatically draws node items"""

    node_items = []  # This will be overridden by subclasses
    tree_type = ""

    def draw(self, context):

        layout = self.layout
        been_drawn = []

        for item in self.node_items:

            # Case ['Submenu', (NodeClass1, NodeClass2, ...)]
            if isinstance(item, tuple) or isinstance(item, list):
                if (
                    (len(item) > 1)
                    and isinstance(item[0], str)
                    and isinstance(item[1], tuple)
                ):
                    submenu_name = item[0]
                    submenu_id = f"RIG_NODES_MT_{submenu_name}" + self.tree_type

                    if submenu_id not in been_drawn:
                        layout.menu(submenu_id)
                        been_drawn.append(submenu_id)

            # Case separator
            elif item is None:
                layout.separator()

            # Case NodeClass
            elif hasattr(item, "bl_label") and hasattr(item, "bl_idname"):
                op = layout.operator("node.add_node", text=item.bl_label)
                op.type = item.bl_idname
                op.use_transform = True

        return None


class RIG_NODES_MT_GeometryNodeTree(DynaMenu, bpy.types.Menu):
    bl_idname = "RIGNODES_MT_GeometryNodeTree"
    bl_label = "Armature"
    node_items = GN_CustomNodes
    tree_type = "GeometryNodeTree"


def rig_nodes_templatemenu_append(self, context):
    layout = self.layout
    layout.separator()
    layout.menu(
        "RIG_NODES_MT_textemplate",
        text="Rig Nodes Scripts",
    )
    return None


def rig_nodes_addmenu_append(
    self,
    context,
):
    tree_type = context.space_data.tree_type
    menu_id = f"RIGNODES_MT_{tree_type}"
    self.layout.menu(menu_id)
    return None


def rig_nodes_nodemenu_append(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(
        "rig_nodes.node_purge_unused",
        text="Purge Unused Nodes",
    )
    return None


MENUS = (
    bpy.types.NODE_MT_add,
    bpy.types.NODE_MT_node,
    bpy.types.TEXT_MT_templates,
)
DRAWFUNCS = (
    rig_nodes_addmenu_append,
    rig_nodes_nodemenu_append,
    rig_nodes_templatemenu_append,
)


DYNAMIC_MENUS = {}


def register_submenus(custom_nodes, shadertype):
    """Register all submenus found in the custom_nodes list"""

    def create_submenu(menu_name, user_name, menu_items):
        """Create submenu classes"""

        # Define a new menu class that inherits from the base menu
        menu_cls = type(
            f"RIG_NODES_MT_{menu_name}",
            (DynaMenu, bpy.types.Menu),
            {
                "bl_idname": f"RIG_NODES_MT_{menu_name}",
                "bl_label": user_name,
                "node_items": menu_items,
            },
        )
        return menu_cls

    # Process all items in the custom_nodes list
    for item in custom_nodes:

        # ('Submenu', (NodeClass1, NodeClass2, ...))
        if (
            isinstance(item, tuple)
            and len(item) > 1
            and isinstance(item[0], str)
            and isinstance(item[1], tuple)
        ):
            user_name = item[0]
            submenu_name = user_name + shadertype
            submenu_items = item[1]

            if submenu_name not in DYNAMIC_MENUS:
                # Create and register the submenu
                submenu_cls = create_submenu(submenu_name, user_name, submenu_items)
                DYNAMIC_MENUS[submenu_name] = submenu_cls
                try:
                    bpy.utils.register_class(submenu_cls)
                except Exception as e:
                    print(f"Failed to register {submenu_name}: {e}")

    return None


def append_menus():

    # append draw functions to existing menus.
    for menu, fct in zip(MENUS, DRAWFUNCS):
        menu.append(fct)

    # Register the main menus
    for cls in {
        RIG_NODES_MT_GeometryNodeTree        
    }:
        bpy.utils.register_class(cls)
        continue

    # Register submenus for all tree types
    register_submenus(GN_CustomNodes, "GeometryNodeTree")
    return None


def remove_menus():
    # remove draw functions from existing menus.
    for menu in MENUS:
        for f in menu._dyn_ui_initialize().copy():
            if f in DRAWFUNCS:
                menu.remove(f)

    # Unregister the main menu classes
    for cls in {
        RIG_NODES_MT_GeometryNodeTree,
    }:
        bpy.utils.unregister_class(cls)
        continue

    # Unregister all dynamic menus
    for menu_name, menu_cls in DYNAMIC_MENUS.items():
        try:
            bpy.utils.unregister_class(menu_cls)
        except Exception as e:
            print(f"Failed to unregister {menu_name}: {e}")

    DYNAMIC_MENUS.clear()

    return None
