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

from cubicweb.view import EntityView
from cubicweb.schema import display_name


class EntityViewOrbui(EntityView):
    """overwrites the original EntityView de cubicweb to remove

    """
    def field(self, label, value, row=True, show_label=True, w=None, tr=True,
              table=False):
        """read-only field"""
        if w is None:
            w = self.w
        if not table:
            self._field_as_div(label, value, show_label=show_label, w=w)
        else:
            self.field_as_table(label, value, row=row, show_label=show_label, tr=tr, w=w)

    def _field_as_table(self, label, value, show_label=True,  tr=True, w=None):
        w(u'<tr class="entityfield">')
        if show_label and label:
            if tr:
                label = display_name(self._cw, label)
            w(u'<th>%s</th>' % label)
        if not (show_label and label):
            w(u'<td colspan="2">%s</td></tr>' % value)
        else:
            w(u'<td>%s</td></tr>' % value)

    def _field_as_div(self, label, value, show_label=True, w=None):
        self.w(u'<div class="row-fluid">')
        if show_label and label:
            self.w(u'<h6 class="span4">%s</h6>'% display_name(self._cw, label))
        self.w(u'<div class="span8">%s</div>' % value)
        self.w(u'</div>') # row_fluid
