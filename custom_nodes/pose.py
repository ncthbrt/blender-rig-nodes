# SPDX-FileCopyrightText: 2025 Natalie Cuthbert <natalie@cuthbert.co.za>
# SPDX-FileCopyrightText: 2025 BD3D DIGITAL DESIGN (Dorian B.)
# SPDX-License-Identifier: GPL-3.0-or-later


import bpy 

from .. import get_addon_prefs
from ..utils.str_utils import word_wrap
from ..utils.node_utils import (
    create_new_nodegroup,
    set_ng_socket_defvalue,
    get_all_nodes,
)


class RIG_NODES_NG_GN_Pose(bpy.types.GeometryNodeCustomGroup):
    bl_idname = "RigNodesPose"
    bl_label = "Pose"
    bl_description = """"""
    auto_update = {'FRAME_PRE','DEPS_POST',}
    tree_type = "GeometryNodeTree"

    @classmethod
    def poll(cls, node_tree):
        """mandatory poll"""
        return True

    def init(self, context):
        """this fct run when appending the node for the first time"""

        name = f".{self.bl_idname}"

        ng = bpy.data.node_groups.get(name)
        if (ng is None):
            ng = create_new_nodegroup(name,
                tree_type=self.tree_type,
                out_sockets={
                    "Use Gravity": "NodeSocketBool",
                    "Gravity": "NodeSocketVector",
                    },
                )
        ng = ng.copy() #always using a copy of the original ng
        self.node_tree = ng

        return None

    def copy(self, node):
        """fct run when dupplicating the node"""
        
        self.node_tree = node.node_tree.copy()
        
        return None

    def update(self):
        """generic update function"""

        return None
        
    def sync_out_values(self):
        """sync output socket values with data"""

        scene = bpy.context.scene

        set_ng_socket_defvalue(self.node_tree, 0, value=scene.use_gravity)
        set_ng_socket_defvalue(self.node_tree, 1, value=scene.gravity)

        return None

    def draw_label(self,):
        """node label"""
        if (self.label==''):
            return 'Scene Info'
        return self.label

    def draw_buttons(self, context, layout):
        """node interface drawing"""

        return None

    def draw_panel(self, layout, context):
        """draw in the rig_nodes N panel 'Active Node'"""

        n = self

        header, panel = layout.panel("doc_panelid", default_closed=True,)
        header.label(text="Documentation",)
        if (panel):
            word_wrap(layout=panel, alert=False, active=True, max_char='auto',
                char_auto_sidepadding=0.9, context=context, string=n.bl_description,
                )
            panel.operator("wm.url_open", text="Documentation",).url = "https://github.com/ncthbrt/blender-rig-nodes/wiki/"

        header, panel = layout.panel("dev_panelid", default_closed=True,)
        header.label(text="Development",)
        if (panel):
            panel.active = False

            col = panel.column(align=True)
            col.label(text="NodeTree:")
            col.template_ID(n, "node_tree")
        
        return None

    @classmethod
    def update_all(cls, using_nodes=None, signal_from_handlers=False,):
        """search for all node instances of this type and refresh them. Will be called automatically if .auto_update's are defined"""

        if (using_nodes is None):
              nodes = get_all_nodes(exactmatch_idnames={cls.bl_idname},)
        else: nodes = [n for n in using_nodes if (n.bl_idname==cls.bl_idname)]

        for n in nodes:
            n.sync_out_values()
            
        return None 
