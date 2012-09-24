from cubicweb.web.views import tableview

class TableLayoutOrbui(tableview.TableLayout):
    cssclass = 'table table-striped table-bordered table-condensed'

def registration_callback(vreg):
    orbui_components = ((TableLayoutOrbui, tableview.TableLayout),
                        )
    vreg.register_all(globals().values(), __name__, [new for (new,old) in orbui_components])
    for new, old in orbui_components:
        vreg.register_and_replace(new, old)
