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
                                             BreadCrumbETypeVComponent,
                                             ibreadcrumb_adapter)
from cubicweb.web.views.navigation import (NavigationComponent,
                                          NextPrevNavigationComponent,
                                          SortedNavigation,
                                          PageNavigation,
                                          PageNavigationSelect)
from cubicweb.web.views.facets import FilterBox
from cubicweb.entity import Entity
from cubicweb.utils import UStringIO, wrap_on_write
from cubicweb.web import formwidgets as fw, component, htmlwidgets
from cubicweb.selectors import non_final_entity
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
    order = -100
    formdef = (u'<li>'
               u'<form action="%(action)s" class="navbar-search pull-left">'
               u'<input id="norql" type="text" accesskey="q" tabindex="%(tabindex1)s"'
               u'       title="search text" value="%(value)s" name="rql"'
               u'       class="search-query span2" placeholder="Search"/>'
               u'       <input type="hidden" name="__fromsearchbox" '
               u'              value="1" />'
               u'       <input type="hidden" name="subvid" '
               u'value="tsearch" />'
               #FIXME this commented html code is left because the string
               #replacement would fail unless the render method is modified
               #also
               u'<!--input tabindex="%(tabindex2)s" type="submit" id="rqlboxsubmit"'
               u'    class="rqlsubmit" value="" /-->'
               u'</form></li>')

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
                          'tabindex2': self._cw.next_tabindex()})


class AnonUserStatusLinkOrbui(AnonUserStatusLink):
    """overwrites the original AnonUserStatusLink of cubicweb to change
    the display format
    """
    #FIXME the selections of possible visible objects does not filter by context
    #for AnonUserStatusLinkOrbui object
    context = _('header-top-right')

    def render(self, w):
        # do nothing for now, what is the real use of it?
        pass


class CookieLoginComponentOrbui(CookieLoginComponent):
    """overwrites original CookieLoginComponent of cubicweb to change
    the display format
    """
    context = _('header-top-right')
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
          u'<b class="caret"></b>'
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
                w(u'<li>%s %s</li>' % (dlink, label))
        if self.can_edit:
            w(u'<li>%s</li>' % req._('manage bookmarks'))
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


class EditBoxOrbui(component.CtxComponent):
    """overwrites the original EditBox class for orbui template
    """
    __regid__ = 'edit_box'
    context = _('main-toolbar')

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
        for category in ('mainactions', 'moreactions','addrelated'):
            menu_options = self.menu_options(actions, category)
            if actions.get(category, ()):
                menu_actions = actions.get(category, ())
                # if the menu has just one option display it as a simple link
                if len(menu_actions) == 1:
                    w(u'<li><a href="%(url)s">%(action)s</a></li>' %
                      {'url': xml_escape(menu_actions[0].url()),
                       'action': menu_actions[0].title})
                elif len(menu_actions) > 1:
                    w(u'<li class="dropdown">'
                      u'<a class="dropdown-toggle" data-toggle="dropdown" '
                      u'href="#">%s'
                      u'<b class="caret"></b>'
                      u'</a>'
                      u'<ul class="dropdown-menu">' % self._cw._(category))
                    w(menu_options)
                    w(u'</ul>'
                      u'</li>')

    def menu_options(self, actions, category):
        """return html code or an empty string to display
        the toolbar menus of certain category given.
        """
        menu_label = u''
        menu_list = []
        for action in actions.get(category, ()):
            if action.submenu:
                menu = self._get_menu(action.submenu)
                if menu_label != menu.label:
                    menu_label = menu.label
                    menu_list.append(u'<li class="divider"></li>')
                    menu_list.append(u'<li><strong>%s</strong></li>' %
                                     menu.label)
                for subaction in action.actual_actions():
                    menu_list.append(u'<li><a href="%s">%s</a></li>' %
                                        (xml_escape(subaction.url()),
                                         self._cw._(subaction.title)))
            else:
                menu_list.append(u'<li><a href="%s">%s</a></li>' %
                                    (xml_escape(action.url()),
                                     self._cw._(action.title)))
        return u''.join(menu_list)


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
            self.w(u'<div class="message alert alert-info" id="%s">'
                   u'<a class="close" data-dismiss="alert">x</a>'
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
        adapter = ibreadcrumb_adapter(entity)
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
        if self.first_separator:
            w(u'<li><span class="divider">%s</span></li>' % self.separator)
        w(u'<li>%s</li>' % self._cw._('search'))
        w(u'</ul>')


class BreadCrumbETypeVComponentOrbui(BreadCrumbETypeVComponent,
                                     BreadCrumbEntityVComponentOrbui):
    """overwrites BreadCrumbETypeVComponent component for orbui template
    """


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

class NavigationOrbuiMixIn(object):
    page_link_templ = u'<li><a href="%s" title="%s">%s</a></li>'
    selected_page_link_templ = u'<li class="active"><a href="%s" title="%s">%s</a></li>'
    previous_page_link_templ = next_page_link_templ = page_link_templ

    @property
    def no_previous_page_link(self):
        return u'<li class="disabled"><a href="#">««</a></li>'

    @property
    def no_next_page_link(self):
        return u'<li class="disabled"><a href="#">»»</a></li>'

    @property
    def no_content_prev_link(self):
        return u'««'

    @property
    def no_content_next_link(self):
        return u'»»'

class NavigationComponentOrbui(NavigationOrbuiMixIn, NavigationComponent):
    pass

class SortedNavigationOrbui(NavigationOrbuiMixIn, SortedNavigation):
    def write_links(self, basepath, params, blocklist):
        """Return HTML for the whole navigation: `blocklist` is a list of HTML
        snippets for each page, `basepath` and `params` will be necessary to
        build previous/next links.
        """
        self.w(u'<div class="pagination">')
        self.w(u'<ul>')
        self.w(u'%s&#160;' % self.previous_link(basepath, params))
        self.w(u'%s' % u''.join(blocklist))
        self.w(u'&#160;%s' % self.next_link(basepath, params))
        self.w(u'</ul>')
        self.w(u'</div>')


class PageNavigationOrbui(NavigationOrbuiMixIn, PageNavigation):
    def call(self):
        """displays a resultset by page"""
        params = dict(self._cw.form)
        self.clean_params(params)
        basepath = self._cw.relative_path(includeparams=False)
        self.w(u'<div class="pagination">')
        self.w(u'<ul>')
        self.w(u'%s&#160;' % self.previous_link(basepath, params))
        self.w(u'&#160;'.join(self.iter_page_links(basepath, params)))
        self.w(u'&#160;%s' % self.next_link(basepath, params))
        self.w(u'</ul>')
        self.w(u'</div>')

class NextPrevNavigationComponentOrbui(NextPrevNavigationComponent):
    """overwrites navigation Next and Previous on single entities
    """

    @property
    def prev_icon(self):
        return u'&#8592;'

    @property
    def next_icon(self):
        return u'&#8594;'

    # Should be better done, but this works
    def render_body(self, w):
        w(u'<div class="prevnext row">')
        w(u'<ul class="pager">')
        self.prevnext(w)
        w(u'</ul>')
        w(u'</div>')
        #w(u'<div class="clear"></div>')

    def prevnext_div(self, w, type, cssclass, url, title, content):
        cssclass = u'span6'

        w(u'<li class="%s">' % cssclass)
        w(u'<a href="%s" title="%s">%s</a>' % (xml_escape(url),
                                               xml_escape(title),
                                               content))
        w(u'</li>')
        self._cw.html_headers.add_raw('<link rel="%s" href="%s" />' % (
              type, xml_escape(url)))

def do_paginate(view, rset=None, w=None, show_all_option=True, page_size=None):
    """write pages index in w stream (default to view.w) and then limit the
    result set (default to view.rset) to the currently displayed page if we're
    not explicitly told to display everything (by setting __force_display in
    req.form)
    """
    req = view._cw
    if rset is None:
        rset = view.cw_rset
    if w is None:
        w = view.w
    nav = req.vreg['components'].select_or_none(
        'navigation', req, rset=rset, page_size=page_size, view=view)
    if nav:
        if w is None:
            w = view.w
        if req.form.get('__force_display'):
            # allow to come back to the paginated view
            params = dict(req.form)
            basepath = req.relative_path(includeparams=False)
            del params['__force_display']
            url = nav.page_url(basepath, params)
            w(u'<div class="displayAllLink btn btn-small">'
              u'<a href="%s">%s</a></div>\n'
              % (xml_escape(url), req._('back to pagination (%s results)')
                                  % nav.page_size))
        else:
            # get boundaries before component rendering
            start, stop = nav.page_boundaries()
            nav.render(w=w)
            params = dict(req.form)
            nav.clean_params(params)
            # make a link to see them all
            if show_all_option:
                basepath = req.relative_path(includeparams=False)
                params['__force_display'] = 1
                params['__fromnavigation'] = 1
                url = nav.page_url(basepath, params)
                w(u'<div class="displayAllLink btn btn-small">'
                  u'<a href="%s">%s</a></div>\n'
                  % (xml_escape(url), req._('show %s results') % len(rset)))
            rset.limit(offset=start, limit=stop-start, inplace=True)


def paginate(view, show_all_option=True, w=None, page_size=None, rset=None):
    """paginate results if the view is paginable
    """
    if view.paginable:
        do_paginate(view, rset, w, show_all_option, page_size)

# monkey patch base View class to add a .paginate([...])
# method to be called to write pages index in the view and then limit the result
# set to the current page
from cubicweb.view import View
View.do_paginate = do_paginate
View.paginate = paginate
View.handle_pagination = False

class PageNavigationSelectOrbui(NavigationOrbuiMixIn, PageNavigationSelect):
    """This pagination component displays a result-set by page as
    :class:`PageNavigation` but in a <select>, which is better when there are a
    lot of results.

    By default it will be selected when there are more than 4 pages to be
    displayed.
    """
    page_link_templ = u'<option value="%s" title="%s">%s</option>'
    selected_page_link_templ = u'<option value="%s" selected="selected" title="%s">%s</option>'

    def call(self):
        params = dict(self._cw.form)
        self.clean_params(params)
        basepath = self._cw.relative_path(includeparams=False)
        w = self.w
        w(u'<div class="pagination">')
        w(u'<ul>')
        w(self.previous_link(basepath, params))
        w(u'<li><select onchange="javascript: document.location=this.options[this.selectedIndex].value">')
        for option in self.iter_page_links(basepath, params):
            w(option)
        w(u'</select></li>')
        w(u'&#160;%s' % self.next_link(basepath, params))
        w(u'</ul>')
        w(u'</div>')


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
        w(u'<div class="modal-body">')
        if showmessage and self._cw.message:
            w(u'<div class="alert">%s'
              u'<a class="close" data-dismiss="alert">x</a></div>' % self._cw.message)
        config = self._cw.vreg.config
        if config['auth-mode'] != 'http':
            self.login_form(id) # Cookie authentication
        w(u'</div>')
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
                        (NextPrevNavigationComponentOrbui, NextPrevNavigationComponent),
                        (NavigationComponentOrbui, NavigationComponent),
                        (SortedNavigationOrbui, SortedNavigation),
                        (PageNavigationOrbui, PageNavigation),
                        (PageNavigationSelectOrbui, PageNavigationSelect),
                        (LogFormViewOrbui, LogFormView),
                        )
    vreg.register_all(globals().values(), __name__, [new for (new,old) in orbui_components])
    for new, old in orbui_components:
        vreg.register_and_replace(new, old)
