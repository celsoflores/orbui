# -*- coding: utf-8 -*-

from cubicweb.web.views import actions

class SelectActionOrbui(actions.SelectAction):
    category = 're-selection'

class CancelSelectActionOrbui(actions.CancelSelectAction):
    category = 're-selection'


def registration_callback(vreg):
    """register new components for orbui
    """
    orbui_components = ((SelectActionOrbui, actions.SelectAction),
                        (CancelSelectActionOrbui, actions.CancelSelectAction),)
    vreg.register_all(globals().values(), __name__, [new for (new,old) in orbui_components])
    for new, old in orbui_components:
        vreg.register_and_replace(new, old)
