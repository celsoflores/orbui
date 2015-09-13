# -*- coding: utf-8 -*-
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

# enable with statement for python < 2.6
from __future__ import with_statement

from logilab.mtconverter import xml_escape

from cubicweb.web.views.boxes import (SearchBox, EditBox, ContextualBoxLayout,
                                      ContextFreeBoxLayout)
from cubicweb.web.views.basecomponents import (ApplLogo, CookieLoginComponent,
                                               AnonUserStatusLink,
                                               AuthenticatedUserStatus,
                                               ApplicationMessage,
                                               ApplicationName)
from cubicweb.web.views.bookmark import BookmarksBox
from cubicweb.web.views.basetemplates import LogForm, LogFormView
from cubicweb.web.views.basecontrollers import JSonController
from cubicweb.web.views.formrenderers import (FormRenderer,
                                              EntityCompositeFormRenderer)
from cubicweb.web.views.formrenderers import field_label, checkbox
from cubicweb.web.views.ibreadcrumbs import (BreadCrumbEntityVComponent,
                                             BreadCrumbAnyRSetVComponent,
                                             BreadCrumbETypeVComponent)
#                                             ibreadcrumb_adapter)
from cubicweb.web.views.facets import FilterBox
from cubicweb.entity import Entity
from cubicweb.utils import UStringIO, wrap_on_write
from cubicweb.web import formwidgets as fw, component, htmlwidgets
from cubicweb.predicates import non_final_entity, match_context
from cubicweb.uilib import toggle_action
from cubicweb import tags, uilib

class ApplLogoOrbui(ApplLogo):
    """build the instance logo, usually displayed in the header
    """
    context = _('header-left')

    def render(self, w):
        w(u'<h1>')
        super(ApplLogoOrbui, self).render(w)
        w(u'</h1>')


class SearchBoxOrbui(SearchBox):
    """display a box with a simple search form
    """
    context = _('header-top-right')
    # make search box appear as first element (left to right) in navbar
    #order = 100
    formdef = (u'<div class="btn btn-small" id="search-box">'
               u'<form action="%(action)s"'
               u' class="navbar-search form-search pull-left">'
               u'<input id="norql" type="text" accesskey="q" tabindex="%(tabindex1)s"'
               u'       title="%(search_text)s" value="%(value)s" name="rql"'
               u'       class="input-medium search-query span2" placeholder="%(Search)s"/>'
               u'       <input type="hidden" name="__fromsearchbox" '
               u'              value="1" />'
               u'       <input type="hidden" name="subvid" '
               u'value="tsearch" />'
               #FIXME this commented html code is left because the string
               #replacement would fail unless the render method is modified
               #also
               u'<!--input tabindex="%(tabindex2)s" type="submit" id="rqlboxsubmit"'
               u'    class="rqlsubmit" value="" /-->'
               u'</form></div>')

    def render(self, w):
        """overwrites SearchBox component for orbui template
        """
        # Don't display search box title, just display the search box body
        if self._cw.form.pop('__fromsearchbox', None):
            rql = self._cw.form.get('rql', '')
        else:
            rql = ''
        w(self.formdef % {'action': self._cw.build_url('view'),
                          'tabindex1': self._cw.next_tabindex(),
                          'value': xml_escape(rql),
                          'tabindex2': self._cw.next_tabindex(),
                          'search_text': self._cw._("search text"),
                          'Search': self._cw._("Search")})


class AnonUserStatusLinkOrbui(AnonUserStatusLink):
    """overwrites the original AnonUserStatusLink of cubicweb to change
    the display format
    """
    # FIXME the selections of possible visible objects does not filter by context
    # for AnonUserStatusLinkOrbui object
    context = _('header-top-right')

    def render(self, w):
        # do nothing for now, what is the real use of it?
        pass

class CookieLoginComponentOrbui(CookieLoginComponent):
    """overwrites original CookieLoginComponent of cubicweb to change
    the display format
    """
    context = _('header-top-right')
    _html = (u'''<!--%s-->
             <li><a title="%s" data-toggle="modal"
             href="#loginModal">%s</a></li>''')

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
    context = _('header-top-right')

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
        w(u'<li id="user-name" class="btn btn-small"><small><a>%s</a></small></li>' % name)
        for action in actions.get('useractions', ())[2:]:
            w(u'<li id="logout" class="btn btn-small"><small>')
            self.action_link(action).render(w=w)
            w(u'</small></li>')
#        w(u'''<li class="dropdown"><a href="#" class="dropdown-toggle"
#              data-toggle="dropdown">%s <span class="caret"></span></a>
#              <ul class="dropdown-menu">''' % name)
#        for action in actions.get('useractions', ())[-1]:
#            w(u'<li>')
#            self.action_link(action).render(w=w)
#            w(u'</li>')
#        for action in actions.get('siteactions', ()):
#            w(u'<li>')
#            self.action_link(action).render(w=w)
#            w(u'</li>')


class LogFormOrbui(LogForm):
    """overwrites the original LogForm class to change look and functionality
    of buttons
    """
    needs_css = ()
    form_buttons = [fw.ResetButton(label=_('cancel'),
                                   attrs={'class': 'btn',
                                          'data-dismiss': 'modal'}),
                    fw.SubmitButton(label=_('log in'),
                                    attrs={'class': 'btn btn-primary'})]

class BookmarksBoxOrbui(component.CtxComponent):
    """overwrites the original BookmarksBox class for orbui template
    """
    __regid__ = 'bookmarks_box'
    context = _('main-toolbar')
    title = _('bookmarks')
    rql = ('Any B,T,P ORDERBY lower(T) '
           'WHERE B is Bookmark,B title T, B path P, B bookmarked_by U, '
           'U eid %(x)s')
    order = 1

    def render(self, w, cw_rset):
        """render bookmarks
        """
        self.init_rendering(w)

    def init_rendering(self, w):
        ueid = self._cw.user.eid
        self.bookmarks_rset = self._cw.execute(self.rql, {'x': ueid})
        rschema = self._cw.vreg.schema.rschema('bookmarked_by')
        eschema = self._cw.vreg.schema.eschema('Bookmark')
        self.can_delete = rschema.has_perm(self._cw, 'delete', toeid=ueid)
        self.can_edit = (eschema.has_perm(self._cw, 'add') and
                         rschema.has_perm(self._cw, 'add', toeid=ueid))
        if self.bookmarks_rset or self.can_edit:
            self.render_menu(w)

    def render_menu(self, w):
        ueid = self._cw.user.eid
        req = self._cw
        if self.can_delete:
            req.add_js('cubicweb.ajax.js')
        w(u'<li class="dropdown">'
          u'<a class="dropdown-toggle" data-toggle="dropdown" href="#">'
          u'%s'
          u'<span class="caret"></span>'
          u'</a>'
          u'<ul class="dropdown-menu">' % self._cw._('bookmarks'))
        for bookmark in self.bookmarks_rset.entities():
            label = self.link(bookmark.title, bookmark.action_url())
            if self.can_delete:
                #FIXME dropdown menu won't work having 2 links on the same menu
                dlink = (u'<a class="action" '
                         u'href="javascript:removeBookmark(%s)" '
                         u'title="%s">[-]</a>' % (bookmark.eid,
                                                 req._('delete this bookmark')))
                dlink = u''
                w(u'<li><span class="action-category">%s %s</span></li>' % (dlink, label))
        if self.can_edit:
            w(u'<li><span class="action-category">%s</span></li>' % req._('manage bookmarks'))
            linkto = 'bookmarked_by:%s:subject' % ueid
            # use a relative path so that we can move the instance without
            # loosing bookmarks
            path = req.relative_path()
            # XXX if vtitle specified in params, extract it and use it as
            # default value for bookmark's title
            url = req.vreg['etypes'].etype_class('Bookmark').cw_create_url(
                req, __linkto=linkto, path=path)
            w(u'<li>%s</li>' % self.link(req._('bookmark this page'), url))
            if self.bookmarks_rset:
                if req.user.is_in_group('managers'):
                    bookmarksrql = (u'Bookmark B WHERE B bookmarked_by U,'
                                    u'U eid %s' % ueid)
                    erset = self.bookmarks_rset
                else:
                    # we can't edit shared bookmarks we don't own
                    bookmarksrql = (u'Bookmark B WHERE B bookmarked_by U,'
                                    u'B owned_by U, U eid %(x)s')
                    erset = req.execute(bookmarksrql, {'x': ueid},
                                        build_descr=False)
                    bookmarksrql %= {'x': ueid}
                if erset:
                    url = req.build_url(vid='muledit', rql=bookmarksrql)
                    w(u'<li>%s</li>' % self.link(req._('edit bookmarks'), url))
            url = req.user.absolute_url(vid='xaddrelation', rtype='bookmarked_by',
                                        target='subject')
            w(u'<li>%s</li>' % self.link(req._('pick existing bookmarks'), url))
        w(u'</ul>'
          u'</li>')



class MainToolbarBoxMenu(htmlwidgets.BoxMenu):

    def _start_li(self):
        return u'<li class="dropdown">'

    def _begin_menu(self):
        self.w(u'<ul class="dropdown-menu">')

    def _render(self):
        if self.isitem:
            self.w(self._start_li())
        ident = self.ident
        self.w(u'<a href="#" class="dropdown-toggle" data-toggle="dropdown">%s' % (
            self.label))
        self.w(u'<span class="caret"></span></a>')
        self._begin_menu()
        for item in self.items:
            _bwcompatible_render_item(self.w, item)
        self._end_menu()
        if self.isitem:
            self.w(u'</li>')

class Separator(object):
    """a menu separator.

    Use this rather than `cw.web.htmlwidgets.BoxSeparator`.
    """
    newstyle = True

    def render(self, w):
        w(u'<li class="divider"></li>')


def _bwcompatible_render_item(w, item):
    if hasattr(item, 'render'):
        if getattr(item, 'newstyle', False):
            if isinstance(item, Separator):
                item.render(w)
            else:
                w(u'<li>')
                item.render(w)
                w(u'</li>')
        else:
            item.render(w) # XXX displays <li> by itself
    else:
        w(u'<li>%s</li>' % item)


class EditBoxOrbui(EditBox): #component.CtxComponent):
    """overwrites the original EditBox class for orbui template
    """
    # __regid__ = 'edit_box'

    context = _('main-toolbar')
    contextual = False
    order = 0

    def _get_menu(self, id, title=None, label_prefix=None):
        try:
            return self._menus_by_id[id]
        except KeyError:
            if title is None:
                title = self._cw._(id)
            self._menus_by_id[id] = menu = MainToolbarBoxMenu(title)
            menu.label_prefix = label_prefix
            self._menus_in_order.append(menu)
            return menu

    def render_items(self, w, items=None):
        if items is None:
            items = self.items
        assert items
        for item in items:
            _bwcompatible_render_item(w, item)

    def init_rendering(self):
        super(EditBox, self).init_rendering()
        _ = self._cw._
        self._menus_in_order = []
        self._menus_by_id = {}
        # build list of actions
        actions = self._cw.vreg['actions'].possible_actions(self._cw, self.cw_rset,
                                                            **self.cw_extra_kwargs)
        other_menu = self._get_menu('moreactions', _('more actions'))
        for category, defaultmenu in (('re-selection', self),
                                      ('mainactions', self),
                                      ('moreactions', other_menu),
                                      ('addrelated', other_menu)):
            for action in actions.get(category, ()):
                if action.submenu and not defaultmenu:
                    menu = self._get_menu(action.submenu)
                else:
                    menu = defaultmenu
                action.fill_menu(self, menu)
        # if we've nothing but actions in the other_menu, add them directly into the box
        if not self.items and len(self._menus_by_id) == 1 and not other_menu.is_empty():
            self.items = other_menu.items
        else: # ensure 'more actions' menu appears last
            self._menus_in_order.remove(other_menu)
            self._menus_in_order.append(other_menu)
            for submenu in self._menus_in_order:
                self.add_submenu(self, submenu)
        if not self.items:
            raise component.EmptyComponent()

class ApplicationMessageOrbui(ApplicationMessage):
    """overwrites application message class for orbui
    """
    def call(self, msg=None):
        if msg is None:
            msgs = []
            if self._cw.cnx:
                srcmsg = self._cw.get_shared_data('sources_error', pop=True)
                if srcmsg:
                    msgs.append(srcmsg)
            reqmsg = self._cw.message # XXX don't call self._cw.message twice
            if reqmsg:
                msgs.append(reqmsg)
        else:
            msgs = [msg]
        for msg in msgs:
            # XXX should we prefer alert-info to alert- -success as default value
            self.w(u'<div class="alert alert-success" id="%s">'
                   u'<button class="close" data-dismiss="alert" type="button">x</button>'
                   u' %s</div>' % (self.domid, msg))


class JSonControllerOrbui(JSonController):
    """overwrites JSonController for orbui template
    """
    def _call_view(self, view, paginate=False, **kwargs):
        divid = self._cw.form.get('divid')
        # we need to call pagination before with the stream set
        try:
            stream = view.set_stream()
        except AttributeError:
            stream = UStringIO()
            kwargs['w'] = stream.write
            assert not paginate
        if divid == 'pageContent':
            # ensure divid isn't reused by the view (e.g. table view)
            del self._cw.form['divid']
            # mimick main template behaviour
            stream.write(u'<div class="span9 pull-right" id="pageContent">')
            vtitle = self._cw.form.get('vtitle')
            if vtitle:
                stream.write(u'<h1 class="vtitle">%s</h1>\n' % vtitle)
            paginate = True
        nav_html = UStringIO()
        if paginate and not view.handle_pagination:
            view.paginate(w=nav_html.write)
        stream.write(nav_html.getvalue())
        if divid == 'pageContent':
            stream.write(u'<div id="contentmain">')
        view.render(**kwargs)
        extresources = self._cw.html_headers.getvalue(skiphead=True)
        if extresources:
            stream.write(u'<div class="ajaxHtmlHead">\n') # XXX use a widget ?
            stream.write(extresources)
            stream.write(u'</div>\n')
        if divid == 'pageContent':
            stream.write(u'</div>%s</div>' % nav_html.getvalue())
        return stream.getvalue()

class EntityCompositeFormRendererOrbui(EntityCompositeFormRenderer):
    """Multiple Edition Table for orbui template 'muledit' HTML5
    """
    def render_fields(self, w, form, values):
        if form.parent_form is None:
            # We should probably take those CSS classes to uiprops.py
            w(u'<table class="table table-striped table-bordered table-condensed">')
            # get fields from the first subform with something to display (we
            # may have subforms with nothing editable that will simply be
            # skipped later)
            for subform in form.forms:
                subfields = [field for field in subform.fields
                             if field.is_visible()]
                if subfields:
                    break
            if subfields:
                # main form, display table headers HTML5
                w(u'<thead>')
                w(u'<tr>')
                w(u'<th>%s</th>' %
                  tags.input(type='checkbox',
                             title=self._cw._('toggle check boxes'),
                             onclick="setCheckboxesState('eid', null, this.checked)"))
                for field in subfields:
                    w(u'<th>%s</th>' % field_label(form, field))
                w(u'</tr>')
                w(u'</thead>')
        super(EntityCompositeFormRenderer, self).render_fields(w, form, values)
        if form.parent_form is None:
            w(u'</table>')
            if self._main_display_fields:
                super(EntityCompositeFormRenderer, self)._render_fields(
                    self._main_display_fields, w, form)


class ApplicationNameOrbui(ApplicationName):
    """overwrites ApplicationName component for orbui template
    """
    context = _('header-top-left-dont-hide')

    # XXX support kwargs for compat with other components
    # which gets the view as argument
    def render(self, w, **kwargs):
        title = self._cw.property_value('ui.site-title')
        if title:
            w(u'<a class="brand" href="%s">%s</a>' % (self._cw.base_url(),
                                                      xml_escape(title)))


class BreadCrumbEntityVComponentOrbui(BreadCrumbEntityVComponent):
    """overwrites ApplicationName component for orbui template
    """
    context = _('header-main')

    # XXX support kwargs for compat with other components which gets
    # the view as argument
    def render(self, w, **kwargs):
        #XXX we do not need first sepator for this breadcrumb style
        self.first_separator = False
        try:
            entity = self.cw_extra_kwargs['entity']
        except KeyError:
            entity = self.cw_rset.get_entity(0, 0)
    #### CHECAR
        adapter = entity.cw_adapt_to('IBreadCrumbs')
    ####
        view = self.cw_extra_kwargs.get('view')
        path = adapter.breadcrumbs(view)
        if path:
            w(u'<ul class="breadcrumb">')
            if self.first_separator:
                w(u'<li><span class="divider">%s</span></li>' % self.separator)
            self.render_breadcrumbs(w, entity, path)
            w(u'</ul>')

    def render_breadcrumbs(self, w, contextentity, path):
        root = path.pop(0)
        if isinstance(root, Entity):
            w(u'<li>%s<span class="divider">%s</span></li>' %
              (self.link_template % (self._cw.build_url(root.__regid__),
                                     root.dc_type('plural')), self.separator))
        self.wpath_part(w, root, contextentity, not path)
        for i, parent in enumerate(path):
            w(u'<li><span class="divider">%s</span></li>' % self.separator)
            self.wpath_part(w, parent, contextentity, i == len(path) - 1)


class BreadCrumbAnyRSetVComponentOrbui(BreadCrumbAnyRSetVComponent,
                                       BreadCrumbEntityVComponentOrbui):
    """overwrites BreadCrumbAnyRSetVComponent component for orbui template
    """
    # XXX support kwargs for compat with other components which gets the view as
    # argument
    def render(self, w, **kwargs):
        #XXX we do not need first sepator for this breadcrumb style
        self.first_separator = False
        w(u'<ul class="breadcrumb">')
        #~ if self.first_separator:
            #~ w(u'<li><span class="divider">%s</span></li>' % self.separator)
        w(u'<li id="search">%s</li>' % self._cw._('search'))
        w(u'</ul>')


class BreadCrumbETypeVComponentOrbui(BreadCrumbETypeVComponent,
                                     BreadCrumbEntityVComponentOrbui):
    """overwrites BreadCrumbETypeVComponent component for orbui template
    """

class MainToolbar(component.Layout):
   __select__ = match_context('main-toolbar',)
   cssclass = 'section'

   def render(self, w):
        if self.init_rendering():
            view = self.cw_extra_kwargs['view']
            view.render_body(w)

class ContextualBoxLayoutOrbui(ContextualBoxLayout):
    #__select__ = match_context('incontext', 'left', 'right') & contextual()
    # predefined class in cubicweb.css: contextualBox | contextFreeBox
    cssclass = 'contextualBox'

    def render(self, w):
        if self.init_rendering():
            view = self.cw_extra_kwargs['view']
            w(u'<div class="%s %s" id="%s">' % (self.cssclass, view.cssclass,
                                                view.domid))
            with wrap_on_write(w, u'<h3 class="boxTitle">',
                               u'</h3>') as wow:
                view.render_title(wow)
            w(u'<div class="boxBody">')
            view.render_body(w)
            # We dissapear the boxFooter CSS place holder, as shadows
            # or effect will be made with CSS
            w(u'</div></div>\n')


class ContextFreeBoxLayoutOrbui(ContextFreeBoxLayout):
    cssclass = 'contextFreeBox'
    def render(self, w):
        if self.init_rendering():
            view = self.cw_extra_kwargs['view']
            w(u'<div class="%s %s" id="%s">' % (self.cssclass, view.cssclass,
                                                view.domid))
            with wrap_on_write(w, u'<h3 class="boxTitle">',
                               u'</h3>') as wow:
                view.render_title(wow)
            w(u'<div class="boxBody">')
            view.render_body(w)
            # We dissapear the boxFooter CSS place holder, as shadows
            # or effect will be made with CSS
            w(u'</div></div>\n')


class FilterBoxOrbui(FilterBox):
    bk_linkbox_template = u'<p class="btn btn-small btn-facet">%s</p>'

class LogFormViewOrbui(LogFormView):
    """overwrites LogFormView for orbui project
    """

    def call(self, id, klass, title=True, showmessage=True):
        w = self.w
        w(u'<div id="%s" class="modal %s">' % (id, klass))
        if title:
            stitle = self._cw.property_value('ui.site-title')
            if stitle:
                stitle = xml_escape(stitle)
            else:
                stitle = u'&#160;'
            w(u'<div class="modal-header">'
              u'<h2>%s</h2>'
              u'</div>' % stitle)
            w(u'<div class="modal-header2">'
              u'<h2>  </h2>'
              u'</div>')
        w(u'<div class="modal-body">')
        if showmessage and self._cw.message:
            w(u'<div class="alert alert-error">%s'
              u'<button class="close" data-dismiss="alert">x</button></div>' % self._cw.message)
        config = self._cw.vreg.config
        if config['auth-mode'] != 'http':
            self.login_form(id) # Cookie authentication
        w(u'<div class="modal-links span3">'
          u'<h4>  </h4>'
          u'</div>'
          u'</div>')
        if self._cw.https and config.anonymous_user()[0]:
            path = xml_escape(config['base-url'] + self._cw.relative_path())
            w(u'<div class="loginMessage alert"><a href="%s">%s</a></div>\n'
              % (path, self._cw._('No account? Try public access at %s') % path))
        w(u'</div>')

def registration_callback(vreg):
    """register new components for orbui
    """
    orbui_components = ((ApplLogoOrbui, ApplLogo),
                        (SearchBoxOrbui, SearchBox),
                        (AnonUserStatusLinkOrbui, AnonUserStatusLink),
                        (CookieLoginComponentOrbui, CookieLoginComponent),
                        (AuthenticatedUserStatusOrbui, AuthenticatedUserStatus),
                        (LogFormOrbui, LogForm),
                        (BookmarksBoxOrbui, BookmarksBox),
                        (EditBoxOrbui, EditBox),
                        (ApplicationMessageOrbui, ApplicationMessage),
                        (JSonControllerOrbui, JSonController),
                        (EntityCompositeFormRendererOrbui, EntityCompositeFormRenderer),
                        (ApplicationNameOrbui, ApplicationName),
                        (BreadCrumbEntityVComponentOrbui, BreadCrumbEntityVComponent),
                        (BreadCrumbAnyRSetVComponentOrbui, BreadCrumbAnyRSetVComponent),
                        (BreadCrumbETypeVComponentOrbui, BreadCrumbETypeVComponent),
                        (ContextualBoxLayoutOrbui, ContextualBoxLayout),
                        (ContextFreeBoxLayoutOrbui, ContextFreeBoxLayout),
                        (FilterBoxOrbui, FilterBox),
                        (LogFormViewOrbui, LogFormView),
                        )
    vreg.register_all(globals().values(), __name__, [new for (new,old) in orbui_components])
    for new, old in orbui_components:
        vreg.register_and_replace(new, old)
