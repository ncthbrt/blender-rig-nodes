# SPDX-FileCopyrightText: 2025 Natalie Cuthbert <natalie@cuthbert.co.za>
# SPDX-FileCopyrightText: 2025 BD3D DIGITAL DESIGN (Dorian B.)
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from ..__init__ import get_addon_prefs, dprint
from ..custom_nodes import allcustomnodes
from collections.abc import Iterable


def register_msgbusses():
    return None


def unregister_msgbusses():
    return None


def on_plugin_installation():
    """is executed either right after plugin installation (when user click on install checkbox),
    or when blender is booting, it will also load plugin"""

    def wait_restrict_state_timer():
        """wait until bpy.context is not bpy_restrict_state._RestrictContext anymore
        BEWARE: this is a function from a bpy.app timer, context is trickier to handle
        """

        dprint(
            f"HANDLER: on_plugin_installation(): Still in restrict state?",
        )

        # don't do anything until context is cleared out
        if str(bpy.context).startswith("<bpy_restrict_state"):
            return 0.01

        dprint(
            f"HANDLER: on_plugin_installation(): Loading Plugin: Running few functions..",
        )

        return None

    bpy.app.timers.register(wait_restrict_state_timer)

    return None


def windows_changed():
    """check if a new window has been opened"""

    wincount = len(bpy.context.window_manager.windows)
    _f = windows_changed
    if not hasattr(_f, "wincount"):
        _f.wincount = wincount

    state = wincount != _f.wincount
    _f.wincount = wincount
    return state


def upd_all_custom_nodes(classes: list):
    """automatically run the update_all() function of all custom nodes passed"""

    # NOTE function below will simply collect all instances of 'NodeBooster' nodes.
    # NOTE there's a lot of classes, and this functions might loop over a lot of data.
    # for optimization purpose, instead of each cls using the function, we create it once
    # here, then pass the list to the update functions with the 'using_nodes' param.

    if not classes:
        return None

    sett_win = bpy.context.window_manager.nodebooster
    has_autorization = sett_win.authorize_automatic_execution

    matching_blid = [cls.bl_idname for cls in classes]

    nodes = get_all_nodes(
        exactmatch_idnames=matching_blid,
    )
    # print("upd_all_custom_nodes().nodes:", matching_blid, nodes, )

    for n in nodes:

        # cls with auto_update property are eligible for automatic execution.
        if (not hasattr(n, "update_all")) or (not hasattr(n, "auto_update")):
            continue

        # automatic re-evaluation of the Python Expression and Python Nex Nodes.
        # for security reasons, we update only if the user allows it expressively on each blender sess.
        if ("AUTORIZATION_REQUIRED" in n.auto_update) and (not has_autorization):
            continue

        n.update_all(signal_from_handlers=True, using_nodes=nodes)
        continue

    return None


DEPSPOST_UPD_NODES = [cls for cls in allcustomnodes if ("DEPS_POST" in cls.auto_update)]


@bpy.app.handlers.persistent
def nodebooster_handler_depspost(scene, desp):
    """update on depsgraph change"""

    if get_addon_prefs().debug_depsgraph:
        print("nodebooster_handler_depspost(): depsgraph signal")

    if get_addon_prefs().auto_launch_minimap_navigation:
        if windows_changed():
            win_sett = bpy.context.window_manager.nodebooster
            # we are forced to restart the modal navigation when a window is opened.
            # a modal op is tied per window, so if we need to support our nav widget
            # for this window, we need to relaunch our multi window modal.
            win_sett.minimap_modal_operator_is_active = False
            win_sett.minimap_modal_operator_is_active = True

    # updates for our custom nodes
    upd_all_custom_nodes(DEPSPOST_UPD_NODES)
    return None


FRAMEPRE_UPD_NODES = [cls for cls in allcustomnodes if ("FRAME_PRE" in cls.auto_update)]


@bpy.app.handlers.persistent
def nodebooster_handler_framepre(scene, desp):
    """update on frame change"""

    if get_addon_prefs().debug_depsgraph:
        print("nodebooster_handler_framepre(): frame_pre signal")

    # updates for our custom nodes
    upd_all_custom_nodes(FRAMEPRE_UPD_NODES)
    return None


LOADPOST_UPD_NODES = [cls for cls in allcustomnodes if ("LOAD_POST" in cls.auto_update)]


@bpy.app.handlers.persistent
def nodebooster_handler_loadpost(scene, desp):
    """Handler function when user is loading a file"""

    if get_addon_prefs().debug_depsgraph:
        print("nodebooster_handler_framepre(): frame_pre signal")

    # need to add message bus on each blender load
    register_msgbusses()

    # register gpu drawing functions
    register_gpu_drawcalls()

    # start the minimap navigation automatically? only if the user enabled it.
    if get_addon_prefs().auto_launch_minimap_navigation:
        bpy.context.window_manager.nodebooster.minimap_modal_operator_is_active = True

    # updates for our custom nodes
    upd_all_custom_nodes(LOADPOST_UPD_NODES)
    return None


# ooooooooo.
# `888   `Y88.
#  888   .d88'  .ooooo.   .oooooooo
#  888ooo88P'  d88' `88b 888' `88b
#  888`88b.    888ooo888 888   888
#  888  `88b.  888    .o `88bod8P'
# o888o  o888o `Y8bod8P' `8oooooo.
#                        d"     YD
#                        "Y88888P'


def all_handlers(name=False):
    """return a list of handler stored in .blend"""

    for oh in bpy.app.handlers:
        if isinstance(oh, Iterable):
            for h in oh:
                yield h


def load_handlers():

    # special timer 'handler' for plugin installation.
    # if we need to do things on plugin init, but there's an annoying restrict state.
    on_plugin_installation()

    handler_names = [h.__name__ for h in all_handlers()]

    if "nodebooster_handler_depspost" not in handler_names:
        bpy.app.handlers.depsgraph_update_post.append(nodebooster_handler_depspost)

    if "nodebooster_handler_framepre" not in handler_names:
        bpy.app.handlers.frame_change_pre.append(nodebooster_handler_framepre)

    if "nodebooster_handler_loadpost" not in handler_names:
        bpy.app.handlers.load_post.append(nodebooster_handler_loadpost)

    return None


def unload_handlers():

    for h in all_handlers():

        if h.__name__ == "nodebooster_handler_depspost":
            bpy.app.handlers.depsgraph_update_post.remove(h)

        if h.__name__ == "nodebooster_handler_framepre":
            bpy.app.handlers.frame_change_pre.remove(h)

        if h.__name__ == "nodebooster_handler_loadpost":
            bpy.app.handlers.load_post.remove(h)

    return None
