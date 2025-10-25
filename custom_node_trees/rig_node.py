import bpy


class RigNodeTree(bpy.types.NodeTree):
    bl_idname="RigNodeTree"
    category = "ANIMATION"
    def init(self, context):
        pass

    @classmethod
    def poll(cls, context):
        return True

