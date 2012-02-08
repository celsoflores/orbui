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

"""cubicweb-cw-minimum-css views/forms/actions/components for web ui"""
from logilab.mtconverter import xml_escape
from cubicweb.utils import UStringIO
from cubicweb.web.views.basetemplates import TheMainTemplate, templatable_view

class TheMainTemplateOrbui(TheMainTemplate):
    """the main template for orbui
    """

    def call(self, view):
        """
        """
        # html head info
        self.set_request_content_type()
        self.template_header(self.content_type, view)
        self.wview('htmlheader', rset=self.cw_rset)
        # body
        self.w(u'<body>\n')
        self.w(u'<div id="header" class="row">')
        self.wview('header', rset=self.cw_rset, view=view)
        self.w(u'</div>\n')
        # top row
        self.w(u'<div id="top" class="row">')
        self.w(u'</div>\n')
        self.w(u'<div id="main" class="row">')
        # boxes
        self.w(u'<div class="leftCol three columns">')
        self.nav_column(view, 'left')
        self.w(u'</div>\n')
        self.w(u'<div class="mainCol nine columns">')
        # components
        components = self._cw.vreg['components']
        rqlcomp = components.select_or_none('rqlinput', self._cw, rset=self.cw_rset)
        if rqlcomp:
            rqlcomp.render(w=self.w, view=view)
        msgcomp = components.select_or_none('applmessages', self._cw, rset=self.cw_rset)
        if msgcomp:
            msgcomp.render(w=self.w)
        # contentheader
        self.wview('contentheader', rset=self.cw_rset, view=view)
        # vtitle
        vtitle = self._cw.form.get('vtitle')
        if vtitle:
            self.w(u'<div class="vtitle">%s</div>\n' % xml_escape(vtitle))
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
        # close mainCol
        self.w(u'</div>\n')
        # close main
        self.w(u'</div>\n')
        # bottom row
        self.w(u'<div id="bottom" class="row">')
        self.w(u'</div>\n')
        # footer row
        self.w(u'<div id="footer" class="row">')
        self.template_footer(view)
        self.w(u'</div>\n')
        # close body
        self.w(u'</body>\n')

    def template_header(self, content_type, view=None, page_title='', additional_headers=()):
        page_title = page_title or view.page_title()
        additional_headers = additional_headers or view.html_headers()
        self.template_html_header(content_type, page_title, additional_headers)

    def template_html_header(self, content_type, page_title, additional_headers=()):
        w = self.whead
        lang = self._cw.lang
        self.write_doctype()
        # explictly close the <base> tag to avoid IE 6 bugs while browsing DOM
        self._cw.html_headers.define_var('BASE_URL', self._cw.base_url())
        w(u'<meta http-equiv="content-type" content="%s; charset=%s"/>\n'
          % (content_type, self._cw.encoding))
        w(u'\n'.join(additional_headers) + u'\n')
        if page_title:
            w(u'<title>%s</title>\n' % xml_escape(page_title))

    def template_footer(self, view=None):
        self.wview('contentfooter', rset=self.cw_rset, view=view)
        self.wview('footer', rset=self.cw_rset)

    def nav_column(self, view, context):
        boxes = list(self._cw.vreg['ctxcomponents'].poss_visible_objects(
            self._cw, rset=self.cw_rset, view=view, context=context))
        if boxes:
            getlayout = self._cw.vreg['components'].select
            self.w(u'<div class="navboxes">\n')
            for box in boxes:
                box.render(w=self.w, view=view)
            self.w(u'</div>\n')


# replace TheMainTemplate
def registration_callback(vreg):
    """register new elements for cw_minimum_css
    """
    vreg.register_and_replace(TheMainTemplateOrbui, TheMainTemplate)
