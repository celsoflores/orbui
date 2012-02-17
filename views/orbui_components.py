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

from cubicweb.web.views.boxes import SearchBox, EditBox
from cubicweb.web.views.basecomponents import (ApplLogo, CookieLoginComponent,
                                               AnonUserStatusLink,
                                               AuthenticatedUserStatus)
from cubicweb.web.views.bookmark import BookmarksBox
from cubicweb.web.views.basetemplates import LogForm
from cubicweb.web import formwidgets as fw, component, htmlwidgets
from cubicweb.selectors import non_final_entity


class ApplLogoOrbui(ApplLogo):
    """build the instance logo, usually displayed in the header
    """
    context = _('no-where-for-now')


class SearchBoxOrbui(SearchBox):
    """display a box with a simple search form"""
    context = _('no-where-for-now')
    formdef = u"""<form action="%s" class="form-search">
                  <input id="norql" type="text" accesskey="q" tabindex="%s"
                         title="search text" value="%s" name="rql"
                         class="input-medium search-query"/>
                 <input type="hidden" name="__fromsearchbox" value="1" />
                 <input type="hidden" name="subvid" value="tsearch" />
                 <!--input tabindex="%s" type="submit" id="rqlboxsubmit"
                 class="rqlsubmit" value="" /-->
                 </form>"""


class AnonUserStatusLinkOrbui(AnonUserStatusLink):
    """overwrites the original AnonUserStatusLink of cubicweb to change
    the display format
    """
    def render(self, w):
        # do nothing for now
        pass


class CookieLoginComponentOrbui(CookieLoginComponent):
    """overwrites original CookieLoginComponent of cubicweb to change
    the display format
    """
    _html = (u'<li class="divider-vertical"></li><!--%s-->'
             u'<li><a title="%s" data-toggle="modal"'
             u' href="#loginModal">%s</a></li>')

    def call(self):
        self.w(self._html % (self._cw._('login / password'),
                             self.loginboxid, self._cw._('i18n_login_popup')))
        self._cw.view('logform', rset=self.cw_rset, id=self.loginboxid,
                      klass='%s hidden' % self.loginboxid, title=False,
                      showmessage=False, w=self.w)


class AuthenticatedUserStatusOrbui(AuthenticatedUserStatus):
    """overwrites the original AuthenticatedUserStatus to change the
    display format
    """

    def render(self, w):
        name = None
        # get a simple user name
        if self._cw.user.firstname:
            name = self._cw.user.firstname.split(' ')[0]
        if self._cw.user.surname:
            if name:
                name = u'%s %s' % (name, self._cw.user.surname.split(' ')[0])
            else:
                name = self._cw.user.surname.split(' ')[0]
        if not name:
            name = self._cw.user.login
        # display useractions and siteactions
        actions = self._cw.vreg['actions'].possible_actions(
            self._cw, rset=self.cw_rset)
        w(u'<li class="divider-vertical"></li>'
          u'<li class="dropdown"><a href="#" class="dropdown-toggle"'
          u' data-toggle="dropdown">%s <b class="caret"></b></a>'
          u'<ul class="dropdown-menu">' % name)
        for action in actions.get('useractions', ()):
            w(u'<li>')
            self.action_link(action).render(w=w)
            w(u'</li>')
        for action in actions.get('siteactions', ()):
            w(u'<li>')
            self.action_link(action).render(w=w)
            w(u'</li>')
        w(u'</ul>'
          u'</li>')


class LogFormOrbui(LogForm):
    """overwrites the original LogForm class to change look and functionality
    of buttons
    """
    form_buttons = [fw.ResetButton(label=_('cancel'),
                                   attrs={'class': 'btn',
                                          'data-dismiss': 'modal'}),
                    fw.SubmitButton(label=_('log in'),
                                    attrs={'class': 'btn btn-primary'})]

class BookmarksBoxOrbui(BookmarksBox):
    """overwrites the original BookmarksBox class for orbui template
    """
    context = _('no-where-for-now')


#class EditBoxOrbui(EditBox):
class EditBoxOrbui(component.CtxComponent):
    """overwrites the original EditBox class for orbui template
    """
    __regid__ = 'edit_box'
    #FIXME we should use the correct selectors
    __select__ = component.CtxComponent.__select__ & non_final_entity()

    title = _('actions')
    order = 2
    #contextual = True
    context = _('no-where-for-now')
    items = []

    def _get_menu(self, id, title=None, label_prefix=None):
        try:
            return self._menus_by_id[id]
        except KeyError:
            if title is None:
                title = self._cw._(id)
            self._menus_by_id[id] = menu = htmlwidgets.BoxMenu(title)
            menu.label_prefix = label_prefix
            self._menus_in_order.append(menu)
            return menu

    def render(self, w, cw_rset):
        """builds the menu in the toolbar for top navigations of the component
        """
        #FIXME this method is not compatible with the complete cubicweb
        #functionality, it is just a partial solution.
        _ = self._cw._
        self._menus_in_order = []
        self._menus_by_id = {}
        # build list of actions
        actions = self._cw.vreg['actions'].possible_actions(self._cw, cw_rset,
                  **self.cw_extra_kwargs)
        other_menu = self._get_menu('moreactions', _('more actions'))

        for category, defaultmenu in (('mainactions', self),
                                      ('moreactions', other_menu),
                                      ('addrelated', None)):
            if actions.get(category, ()):
                w(u'<li class="dropdown">'
                  u'<a class="dropdown-toggle" data-toggle="dropdown" href="#">'
                  u'%s'
                  u'<b class="caret"></b>'
                  u'</a>'
                  u'<ul class="dropdown-menu">' % self._cw._(category))
                for action in actions.get(category, ()):
                    if action.submenu:
                        menu = self._get_menu(action.submenu)
                        w(u'<li class="divider"></li>')
                        w(u'<li><strong>%s</strong></li>' % menu.label)
                        for subaction in action.actual_actions():
                            w(u'<li><a href="%s">%s</a></li>' %
                              (subaction.url(), self._cw._(subaction.title)))
                        w(u'<li class="divider"></li>')
                    else:
                        menu = defaultmenu
                        w(u'<li><a href="%s">%s</a></li>' %
                          (action.url(), self._cw._(action.title)))
                w(u'</ul>'
                  u'</li>')


def registration_callback(vreg):
    """register new elements for cw_minimum_css
    """
    vreg.register_and_replace(ApplLogoOrbui, ApplLogo)
    vreg.register_and_replace(SearchBoxOrbui, SearchBox)
    vreg.register_and_replace(AnonUserStatusLinkOrbui, AnonUserStatusLink)
    vreg.register_and_replace(CookieLoginComponentOrbui, CookieLoginComponent)
    vreg.register_and_replace(AuthenticatedUserStatusOrbui,
                              AuthenticatedUserStatus)
    vreg.register_and_replace(LogFormOrbui, LogForm)
    vreg.register_and_replace(BookmarksBoxOrbui, BookmarksBox)
    vreg.register_and_replace(EditBoxOrbui, EditBox)
