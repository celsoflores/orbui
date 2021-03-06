# -*- coding: iso-8859-15 -*-
from logilab.mtconverter import xml_escape

from cubicweb.web.views.navigation import (NavigationComponent,
                                          NextPrevNavigationComponent,
                                          SortedNavigation,
                                          PageNavigation,
                                          PageNavigationSelect)


class NavigationOrbuiMixIn(object):
    page_link_templ = u'<li><a href="%s" title="%s">%s</a></li>'
    selected_page_link_templ = u'<li class="active"><a href="%s" title="%s">%s</a></li>'
    previous_page_link_templ = next_page_link_templ = page_link_templ

    @property
    def no_previous_page_link(self):
        return u'<li class="disabled"><a href="#">&laquo;</a></li>'

    @property
    def no_next_page_link(self):
        return u'<li class="disabled"><a href="#">&raquo;</a></li>'

    @property
    def no_content_prev_link(self):
        return u'&laquo;'

    @property
    def no_content_next_link(self):
        return u'&raquo;'


class SortedNavigationOrbui(NavigationOrbuiMixIn, SortedNavigation):
    def write_links(self, basepath, params, blocklist):
        """Return HTML for the whole navigation: `blocklist` is a list of HTML
        snippets for each page, `basepath` and `params` will be necessary to
        build previous/next links.
        """
        self.w(u'<div class="pagination pagination-small">')
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
        self.w(u'<div class="pagination pagination-small">')
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
        w(u'<div class="pagination pagination-small">')
        w(u'<ul>')
        w(self.previous_link(basepath, params))
        w(u'<li><select onchange="javascript: document.location=this.options[this.selectedIndex].value">')
        for option in self.iter_page_links(basepath, params):
            w(option)
        w(u'</select></li>')
        w(u'&#160;%s' % self.next_link(basepath, params))
        w(u'</ul>')
        w(u'</div>')


def registration_callback(vreg):
    """register new components for orbui
    """
    orbui_components = ((NextPrevNavigationComponentOrbui, NextPrevNavigationComponent),
                        (SortedNavigationOrbui, SortedNavigation),
                        (PageNavigationOrbui, PageNavigation),
                        (PageNavigationSelectOrbui, PageNavigationSelect),
                        )
    vreg.register_all(globals().values(), __name__, [new for (new,old) in orbui_components])
    for new, old in orbui_components:
        vreg.register_and_replace(new, old)
