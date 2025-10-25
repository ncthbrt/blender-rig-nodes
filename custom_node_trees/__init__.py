# SPDX-FileCopyrightText: 2025 Natalie Cuthbert <natalie@cuthbert.co.za>
# SPDX-FileCopyrightText: 2025 BD3D DIGITAL DESIGN (Dorian B.)
# SPDX-License-Identifier: GPL-3.0-or-later

from ..__init__ import get_addon_prefs, dprint
from .rig_node import RigNodeTree

classes = (
    RigNodeTree   
)

#for utility. handlers.py module will use this list.
allcustomtrees = tuple(
    cls for cls in classes if (('NodeTree' in cls.__name__))
)