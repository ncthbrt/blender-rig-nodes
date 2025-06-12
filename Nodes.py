import bpy
from bpy.types import Node
from bl_ui import node_add_menu


# Mix-in class for all custom nodes in this tree type.
# Defines a poll function to enable instantiation.
class ArmatureNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "GeometryNodeTree" 


# Derived from the Node base type.
class EdgesToArmatureNode(ArmatureNode, Node):
    # === Basics ===
    # Description string
    '''Converts edges to an armature'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'EdgesToArmatureNodeType'
    # Label for nice name display
    bl_label = "Edges to Armature"
    # Icon identifier
    bl_icon = 'ARMATURE_DATA'

    # === Custom Properties ===
    # These work just like custom properties in ID data blocks
    # Extensive information can be found under
    # https://docs.blender.org/api/current/bpy.props.html
    # my_string_prop: bpy.props.StringProperty()
    # my_float_prop: bpy.props.FloatProperty(default=3.1415926)

    # === Optional Functions ===
    # Initialization function, called when a new node is created.
    # This is the most common place to create the sockets for a node, as shown below.
    # NOTE: this is not the same as the standard __init__ function in Python, which is
    #       a purely internal Python method and unknown to the node system!
    def init(self, context):
        self.inputs.new('NodeSocketGeometry', "Geometry")
        self.outputs.new('NodeSocketGeometry', "Geometry")        

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        pass

    # Free function to clean up on removal.
    def free(self):
        pass

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
#        layout.label(text="Node settings")
#        layout.prop(self, "my_float_prop")
        pass

    # Detail buttons in the sidebar.
    # If this function is not defined, the draw_buttons function is used instead
    def draw_buttons_ext(self, context, layout):
#        layout.prop(self, "my_float_prop")
        # my_string_prop button will only be visible in the sidebar
#        layout.prop(self, "my_string_prop")
        pass

    # Optional: custom label
    # Explicit user label overrides this, but here we can define a label dynamically
    def draw_label(self):
        return "Edge to Armature"


# Add custom nodes to the Add menu.
def draw_add_menu(self, context):
    layout = self.layout
    if context.space_data.tree_type != 'GeometryNodeTree':
        # Avoid adding nodes to other node trees
        return
    node_add_menu.draw_assets_for_catalog(layout, "Armature")
    layout = self.layout
    # Add nodes to the layout. Can use submenus, separators, etc. as in any other menu.
    node_add_menu.add_node_type(layout, "EdgesToArmatureNodeType")


classes = (
    EdgesToArmatureNode,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.NODE_MT_add.append(draw_add_menu)


def unregister():
    bpy.types.NODE_MT_add.remove(draw_add_menu)

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    register()
