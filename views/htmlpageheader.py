# copyright 2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
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

from cubicweb.web.views.basetemplates import HTMLPageHeader
from cubicweb.web.views.basecomponents import ApplLogo


class HTMLPageHeaderOrbui(HTMLPageHeader):
    """default html page header"""

    def main_header(self, view):
        """overwrites cubicweb HTMLPageHeader, so can be change to orbuit format.
        rigth now we split the header in two columns: header-left and header-right
        """
        w = self.w
        logo_componets = []
        left_components = []
        right_components = []
        headers = self.headers + (('header-logo', 'header-logo'),)
        for colid, context in headers:
            components = self._cw.vreg['ctxcomponents'].poss_visible_objects(
                self._cw, rset=self.cw_rset, view=view, context=context)
            if context == 'header-left':
                left_components = components
            elif context == 'header-right':
                right_components = components
            # Strange CW functionality, go to mailing list some time
            elif context == 'header-logo':
                logo_components = components
        self.w(u'<div id="header_left" class="three columns">')
        if logo_components:
            for logo in logo_components:
                logo.render(w=w)
        self.w(u'</div>'
               u'<div id="header_center" class="seven columns">')
        for component in left_components:
            component.render(w=w)
        self.w(u'</div>'
               u'<div id="header_right" class="two columns">')
        for component in right_components:
            component.render(w=w)
        self.w(u'</div>')


class ApplLogoOrbui(ApplLogo):
    """build the instance logo, usually displayed in the header"""
    context = _('header-logo')


def registration_callback(vreg):
    """register new elements for cw_minimum_css
    """
    vreg.register_all(globals().values(), __name__, (HTMLPageHeaderOrbui, ApplLogoOrbui))
    vreg.register_and_replace(HTMLPageHeaderOrbui, HTMLPageHeader)
    vreg.register_and_replace(ApplLogoOrbui, ApplLogo)
