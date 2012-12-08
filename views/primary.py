# copyright 2012 CreaLibre (Monterrey, MEXICO), all rights reserved.
# contact http://www.crealibre.com/ -- mailto:info@crealibre.com
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

from cubicweb.web.views import tabs, primary

class PrimaryViewOrbui(primary.PrimaryView):
    """overwrites the original PrimaryView de cubicweb to remove
     unnecessary tables
    """

    def render_entity(self, entity):
        """overwrites the original method of the primary view to display
         entity in orbui format
        """
        self.render_entity_toolbox(entity)
        self.render_entity_title(entity)
        # entity's attributes and relations, excluding meta data
        # if the entity isn't meta itself
        if self.is_primary():
            boxes = self._prepare_side_boxes(entity)
        else:
            boxes = None
        self.w(u'<div class="container-fluid">'
               u'<div class="row">'
               u'<div class="span12">'
               u'<div class="row-fluid">'
               u'<div class="span8">')
        if hasattr(self, 'render_entity_summary'):
            warn('[3.10] render_entity_summary method is deprecated (%s)' %
                 self, DeprecationWarning)
            self.render_entity_summary(entity) # pylint: disable=E1101
        summary = self.summary(entity)
        if summary:
            warn('[3.10] summary method is deprecated (%s)' % self,
                 DeprecationWarning)
            self.w(u'<div class="summary">%s</div>' % summary)
        self.content_navigation_components('navcontenttop')
        self.w(u'<div class="primary_entities">')
        self.render_entity_attributes(entity)
        if self.main_related_section:
            self.render_entity_relations(entity)
        self.w(u'</div>')
        self.content_navigation_components('navcontentbottom')
        self.w(u'</div>'
               u'<div class="span4">')
        # side boxes
        if boxes or hasattr(self, 'render_side_related'):
            self.render_side_boxes(boxes)
        self.w(u'</div>'
               u'</div>'
               u'</div>'
               u'</div>'
               u'</div>')

    def render_entity_attributes(self, entity):
        """overwrites the original method to use list instead of table
        to display attributes.
        """
        display_attributes = []
        for rschema, _, role, dispctrl in self._section_def(entity,
                                                            'attributes'):
            vid = dispctrl.get('vid', 'reledit')
            if rschema.final or vid == 'reledit' or dispctrl.get('rtypevid'):
                value = entity.view(vid, rtype=rschema.type, role=role,
                                    initargs={'dispctrl': dispctrl})
            else:
                rset = self._relation_rset(entity, rschema, role, dispctrl)
                if rset:
                    value = self._cw.view(vid, rset)
                else:
                    value = None
            if value is not None and value != '':
                display_attributes.append( (rschema, role, dispctrl, value) )
        if display_attributes:
            self.w(u'<div>')
            for rschema, role, dispctrl, value in display_attributes:
                # pylint: disable=E1101
                if not hasattr(self, '_render_attribute'):
                    label = self._rel_label(entity, rschema, role, dispctrl)
                    self.render_attribute(label, value, table=True)
                else:
                    warn('[3.9] _render_attribute prototype has changed and '
                         'renamed to render_attribute, please update %s'
                         % self.__class__, DeprecationWarning)
                    self._render_attribute(dispctrl, rschema, value, role=role,
                                           table=True)
            self.w(u'</div>')

    def render_attribute(self, label, value, table=False):
        """overwrites the original method to use list instead of table
        to display attributes.
        """
        self.w(u'<div class="row-fluid"> '
            u'<h6 class="span4">%s</h6>'
            u'<div class="span8">%s</div></div>' % (label, value))

class TabbedPrimaryViewOrbui(tabs.TabsMixin, PrimaryViewOrbui):
    __abstract__ = True # don't register

    tabs = [_('main_tab')]
    default_tab = 'main_tab'

    def cell_call(self, row, col):
        entity = self.cw_rset.complete_entity(row, col)
        self.render_entity_toolbox(entity)
        self.w(u'<div class="tabbedprimary"></div>')
        self.render_entity_title(entity)
        self.render_tabs(self.tabs, self.default_tab, entity)

class PrimaryTabOrbui(PrimaryViewOrbui):
    __regid__ = 'main_tab'
    title = None # should not appear in possible views

    def is_primary(self):
        return True

    def render_entity_title(self, entity):
        pass
    def render_entity_toolbox(self, entity):
        pass

def registration_callback(vreg):
    orbui_components = ((PrimaryViewOrbui, primary.PrimaryView),
                        (PrimaryTabOrbui, tabs.PrimaryTab),
                        )
    vreg.register_all(globals().values(), __name__, [new for (new,old) in orbui_components])
    for new, old in orbui_components:
        vreg.register_and_replace(new, old)
