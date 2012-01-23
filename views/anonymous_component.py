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

from cubicweb.web.views.basecomponents import AnonUserStatusLink, CookieLoginComponent


class AnonUserStatusLinkOrbui(AnonUserStatusLink):
    """overwrites the original AnonUserStatusLink of cubicweb to change the display format
    """

    def render(self, w):
        # do nothing
        pass


class CookieLoginComponentOrbui(CookieLoginComponent):
    """ovewrites original CookieLoginComponent of cubicweb to change the display format
    """
    _html = (u'<a class="login_button" title="%s" '
             u'href="javascript:cw.htmlhelpers.popupLoginBox(\'%s\', \'__login\');">%s</a>')


def registration_callback(vreg):
    """register new elements for cw_minimum_css
    """
    vreg.register_all(globals().values(), __name__, (CookieLoginComponentOrbui,
                                                     AnonUserStatusLinkOrbui))
    vreg.register_and_replace(AnonUserStatusLinkOrbui, AnonUserStatusLink)
    vreg.register_and_replace(CookieLoginComponentOrbui, CookieLoginComponent)

