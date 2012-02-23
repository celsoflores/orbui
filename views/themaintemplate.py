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

"""cubicweb-cw-minimum-css views/forms/actions/components for web ui"""
from logilab.mtconverter import xml_escape
from cubicweb.utils import UStringIO
from cubicweb.web.views.basetemplates import TheMainTemplate, templatable_view

class TheMainTemplateOrbui(TheMainTemplate):
    """the main template for orbui

    This class creates the main structure of the cubicweb front page.

    The sections are:

    * header
    * toolbar
    * main
    * footer

    Each section has more inner sections according to its related components.
    """

    def call(self, view):
        """call all methods to build the main template
        """
        # html head info
        self.set_request_content_type()
        self.template_header(self.content_type, view)
        # writes all css & js needed for Cubicweb
        self.wview('htmlheader', rset=self.cw_rset)
        self.w(u'<body>')
        self.page_header(view)
        self.page_toolbar(view)
        self.page_main(view)
        self.page_footer(view)
        self.w(u'</body>')

    def page_header(self, view):
        """display the header of the main template
        """
        ctxcomponents =  self._cw.vreg['ctxcomponents']
        self.w(u'<header id="pageheader">'
               u'<div class="navbar navbar-top">'
               u'<div class="navbar-inner">'
               u'<div class="container">'
               u' <a class="btn btn-navbar" data-toggle="collapse"'
               u'    data-target=".nav-collapse">'
               u'<span class="icon-bar"></span>'
               u'<span class="icon-bar"></span>'
               u'<span class="icon-bar"></span>'
               u'</a>')
        components_top_left = ctxcomponents.poss_visible_objects(self._cw,
                              rset=self.cw_rset, view=view,
                              context='header-top-left')
        components_top_right = ctxcomponents.poss_visible_objects(self._cw,
                               rset=self.cw_rset, view=view,
                               context='header-top-right')
        # Anything placed here will be hidden on mobile devices and
        # small screens in general. It can be show by clicking the button
        # above this comment.
        self.w(u'<div class="nav-collapse">'
               u'<ul class="nav">')
        for component in components_top_left:
            component.render(w=self.w)
        self.w(u'</ul>'
               u'<ul class="nav pull-right">')
        for component in components_top_right:
            component.render(w=self.w)
        self.w(u'</ul>'
               u'</div>')
        components_header_left = ctxcomponents.poss_visible_objects(self._cw,
                                 rset=self.cw_rset, view=view,
                                 context='header-left')
        components_header_main = ctxcomponents.poss_visible_objects(self._cw,
                                 rset=self.cw_rset,
                                 view=view, context='header-main')
        components_header_right = ctxcomponents.poss_visible_objects(self._cw,
                                  rset=self.cw_rset,
                                  view=view, context='header-right')
        # get seach box component
        #search_box = ctxcomponents.select('search_box', self._cw)
        self.w(u'</div>'
               u'</div>'
               u'</div>'
               u'<div class="container">'
               u'<div class="row">'
               u'<div class="span2">')
        for component in components_header_left:
            component.render(w=self.w)
        self.w(u'</div>'
               u'<div class="span8">')
        for component in components_header_main:
            component.render(w=self.w)
        self.w(u'</div>'
               u'<div class="span2">')
        for component in components_header_right:
            component.render(w=self.w)
        self.w(u'</div>'
               u'</div>'
               u'</div>'
               u'</header>')
        # close header
        # get login form to display it as modal window
        login = self._cw.vreg['forms'].select('logform', self._cw)
        self.w(u'<div id="loginModal" class="modal hide fade in">'
               u'<div class="modal-header">'
               u'<a class="close" data-dismiss="modal">x</a>'
               u'<h3>%s</h3>'
               u'</div>'
               u'<div class="modal-body">' % self._cw._('log in'))
        login.render(w=self.w)
        self.w(u'</div>'
               u' <div class="modal-footer"></div>'
               u'</div>')

    def page_toolbar(self, view):
        """display contextual toolbar
        """
        ctxcomponents = self._cw.vreg['ctxcomponents']
        self.w(u'<nav id="toolbar" class="container">'
               u'<div class="row">'
               u'<div class="span12">')
        components_toolbar = ctxcomponents.poss_visible_objects(self._cw,
                             rset=self.cw_rset,
                             view=view, context='main-toolbar')
        self.w(u'<ul class="nav nav-pills pull-right">')
        for component in components_toolbar:
            component.render(w=self.w, cw_rset=self.cw_rset)
        self.w(u'</ul>')
        #FIXME right now we are not displaying this section
        # writes ctxcomponents for this element
        #self.wview('contentheader', rset=self.cw_rset, view=view)
        self.w(u'</div>'
               u'</div>'
               u'</nav>')

    def page_main(self, view):
        """display main section of the main template
        """
        components = self._cw.vreg['components']
        rqlcomp = components.select_or_none('rqlinput', self._cw,
                                            rset=self.cw_rset)
        #FIXME this is a trick to find out if boxes exists for this element
        context = 'left'
        boxes = list(self._cw.vreg['ctxcomponents'].poss_visible_objects(
                self._cw, rset=self.cw_rset, view=view, context=context))
        if boxes:
            columns = 9
        else:
            columns = 12
        self.w(u'<section id="main">'
               u'<div class="container">'
               u'<div class="row">'
               u'<div class="span%i pull-right" id="pageContent">' % columns)
        if rqlcomp:
            rqlcomp.render(w=self.w, view=view)
        msgcomp = components.select_or_none('applmessages', self._cw,
                                            rset=self.cw_rset)
        if msgcomp:
            msgcomp.render(w=self.w)
        # vtitle
        vtitle = self._cw.form.get('vtitle')
        if vtitle:
            self.w(u'<div class="vtitle">%s</div>' % xml_escape(vtitle))
        # display entity type restriction component
        etypefilter = self._cw.vreg['components'].select_or_none(
            'etypenavigation', self._cw, rset=self.cw_rset)
        if etypefilter and etypefilter.cw_propval('visible'):
            etypefilter.render(w=w)
        nav_html = UStringIO()
        if view and not view.handle_pagination:
            view.paginate(w=nav_html.write)
        self.w(nav_html.getvalue())
        view.render(w=self.w)
        self.w(nav_html.getvalue())
        self.w(u'</div>')
        # aside section - write boxes for this element
        self.nav_column(view, 'left')
        self.w(u'</div>'
               u'</div>'
               u'</section>')

    def page_footer(self, view):
        """display page footer
        """
        self.w(u'<footer id="pagefooter">'
               u'<div class="container">'
               u'<div class="row">'
               u'<div class="span12">'
               u'<hr />')
        self.template_footer(view)
        self.w(u'</div>'
               u'</div>'
               u'</div>'
               u'</footer>')

    def template_header(self, content_type, view=None, page_title='',
                        additional_headers=()):
        page_title = page_title or view.page_title()
        additional_headers = additional_headers or view.html_headers()
        self.template_html_header(content_type, page_title, additional_headers)

    def template_html_header(self, content_type, page_title,
                             additional_headers=()):
        w = self.whead
        lang = self._cw.lang
        self.write_doctype()
        # explictly close the <base> tag to avoid IE 6 bugs while browsing DOM
        self._cw.html_headers.define_var('BASE_URL', self._cw.base_url())
        w(u'<meta http-equiv="content-type" content="%s; charset=%s"/>\n'
          % (content_type, self._cw.encoding))
        w(u'<meta name="viewport" content="initial-scale=1.0; '
          u'maximum-scale=1.0; width=device-width; "/>')
        w(u'\n'.join(additional_headers) + u'\n')
        # FIXME this is a quick option to make cw work in IE9
        # you'll lose all IE9 functionality, the browser will act as IE8.
        #w(u'<meta http-equiv="X-UA-Compatible" content="IE=8" />\n')
        w(u'<!-- Le HTML5 shim, for IE6-8 support of HTML elements -->\n'
          u'  <!--[if lt IE 9]>\n'
          u'        <script src="%s"></script>\n'
          u'  <![endif]-->\n' % self._cw.data_url('js/html5.js'))
        if page_title:
            w(u'<title>%s</title>\n' % xml_escape(page_title))

    def template_footer(self, view=None):
        self.wview('contentfooter', rset=self.cw_rset, view=view)
        self.wview('footer', rset=self.cw_rset)

    def nav_column(self, view, context):
        boxes = list(self._cw.vreg['ctxcomponents'].poss_visible_objects(
                self._cw, rset=self.cw_rset, view=view, context=context))
        if boxes:
            self.w(u'<aside class="span3">'
                   u'<div class="well">'
                   u'<div class="navboxes">')
            for box in boxes:
                box.render(w=self.w, view=view)
            self.w(u'</div>'
                   u'</div>'
                   u'</aside>')


# replace TheMainTemplate
def registration_callback(vreg):
    """register new elements for cw_minimum_css
    """
    vreg.register_and_replace(TheMainTemplateOrbui, TheMainTemplate)
