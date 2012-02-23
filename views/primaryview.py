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

from cubicweb.web.views.primary import PrimaryView

class PrimaryViewOrbui(PrimaryView):
    """overwrites the original PrimaryView de cubicweb to remove unnecessary tables
    """

    def render_entity(self, entity):
        """overwrites the original method of the primary view to display entity in orbui format
        """
        self.render_entity_toolbox(entity)
        self.render_entity_title(entity)
        # entity's attributes and relations, excluding meta data
        # if the entity isn't meta itself
        if self.is_primary():
            boxes = self._prepare_side_boxes(entity)
        else:
            boxes = None
        self.w(u'<div class="well row-fluid">'
               u'<div class="span9">')
        if hasattr(self, 'render_entity_summary'):
            warn('[3.10] render_entity_summary method is deprecated (%s)' % self,
                 DeprecationWarning)
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
               u'<div class="span3">')
        # side boxes
        if boxes or hasattr(self, 'render_side_related'):
            self.render_side_boxes(boxes)
        self.w(u'</div>'
               u'</div>')

# replace PrimaryView
def registration_callback(vreg):
    """register new primary view for orbui project
    """
    vreg.register_all(globals().values(), __name__, (PrimaryViewOrbui,))
    vreg.register_and_replace(PrimaryViewOrbui, PrimaryView)
