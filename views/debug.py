"""Orbui views that replace base debug views

:organization: Logilab
:copyright: 2012 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"
_ = unicode

from time import strftime, localtime

from logilab.mtconverter import xml_escape

from cubicweb import BadConnectionId
from cubicweb.predicates import none_rset, match_user_groups
from cubicweb.view import StartupView
from cubicweb.web.views import debug

def dict_to_html(w, dict):
    # XHTML doesn't allow emtpy <ul> nodes
    if dict:
        w(u'<dl>')
        for key in sorted(dict):
            w(u'<dt>%s</dt><dd>%s</dd>' % (
                xml_escape(str(key)), xml_escape(repr(dict[key]))))
        w(u'</dl>')

class ProcessInformationViewOrbui(debug.ProcessInformationView):

    def call(self, **kwargs):
        req = self._cw
        dtformat = req.property_value('ui.datetime-format')
        _ = req._
        w = self.w
        # generic instance information
        w(u'<h2>%s</h2>' % _('Instance'))
        w(u'<table class="table table-striped table-condensed">')
        for key,value in ((_('config type'), self._cw.vreg.config.name),
                          (_('config mode'), self._cw.vreg.config.mode),
                          (_('instance home'), self._cw.vreg.config.apphome)):
            w(u'<tr><th>%s</th><td>%s</td></tr>' % (key,value))
        w(u'</table>')
        vcconf = req.vreg.config.vc_config()
        w(u'<h3>%s</h3>' % _('versions configuration'))
        w(u'<table class="table table-striped table-condensed">')
        w(u'<tr><th>%s</th><td>%s</td></tr>' % (
            'CubicWeb', vcconf.get('cubicweb', _('no version information'))))
        for cube in sorted(self._cw.vreg.config.cubes()):
            cubeversion = vcconf.get(cube, _('no version information'))
            w(u'<tr><th>%s</th><td>%s</td></tr>' % (
                cube, cubeversion))
        w(u'</table>')
        # repository information
        repo = req.vreg.config.repository(None)
        w(u'<h2>%s</h2>' % _('Repository'))
        w(u'<h3>%s</h3>' % _('resources usage'))
        w(u'<table class="table table-striped table-condensed">')
        stats = repo.stats()
        for element in sorted(stats):
            w(u'<tr><th>%s</th><td>%s %s</td></tr>'
                   % (element, xml_escape(unicode(stats[element])),
                      element.endswith('percent') and '%' or '' ))
        w(u'</table>')
        if req.cnx.is_repo_in_memory and req.user.is_in_group('managers'):
            w(u'<h3>%s</h3>' % _('opened sessions'))
            sessions = repo._sessions.values()
            if sessions:
                w(u'<ul>')
                for session in sessions:
                    w(u'<li>%s (%s: %s)<br/>' % (
                        xml_escape(unicode(session)),
                        _('last usage'),
                        strftime(dtformat, localtime(session.timestamp))))
                    dict_to_html(w, session.data)
                    w(u'</li>')
                w(u'</ul>')
            else:
                w(u'<p>%s</p>' % _('no repository sessions found'))
        # web server information
        w(u'<h2>%s</h2>' % _('Web server'))
        w(u'<table class="table table-striped table-condensed">')
        w(u'<tr><th>%s</th><td>%s</td></tr>' % (
            _('base url'), req.base_url()))
        w(u'<tr><th>%s</th><td>%s</td></tr>' % (
            _('data directory url'), req.datadir_url))
        w(u'</table>')
        if req.user.is_in_group('managers'):
            from cubicweb.web.application import SESSION_MANAGER
            sessions = SESSION_MANAGER.current_sessions()
            w(u'<h3>%s</h3>' % _('opened web sessions'))
            if sessions:
                w(u'<ul>')
                for session in sessions:
                    last_usage_time = session.mtime
                    w(u'<li>%s (%s: %s)<br/>' % (
                        session.sessionid,
                        _('last usage'),
                        strftime(dtformat, localtime(last_usage_time))))
                    dict_to_html(w, session.data)
                    w(u'</li>')
                w(u'</ul>')
            else:
                w(u'<p>%s</p>' % _('no web sessions found'))


class RegistryViewOrbui(debug.RegistryView):

    def call(self, **kwargs):
        self.w(u'<h2>%s</h2>' % self._cw._("Registry's content"))
        keys = sorted(self._cw.vreg)
        url = xml_escape(self._cw.url())
        self.w(u'<p>%s</p>\n' % ' - '.join('<a href="%s#%s">%s</a>'
                                           % (url, key, key) for key in keys))
        for key in keys:
            if key in ('boxes', 'contentnavigation'): # those are bw compat registries
                continue
            self.w(u'<h3 id="%s">%s</h3>' % (key, key))
            if self._cw.vreg[key]:
                values = sorted(self._cw.vreg[key].iteritems())
                self.wview('pyvaltable', pyvalue=[(key, xml_escape(repr(val)))
                                                  for key, val in values])
            else:
                self.w(u'<p>Empty</p>\n')

# class GCView(StartupView):
#     """display garbage collector information"""
#     __regid__ = 'gc'
#     __select__ = StartupView.__select__ & match_user_groups('managers')
#     title = _('memory leak debugging')
#     cache_max_age = 0

#     def call(self, **kwargs):
#         from cubicweb._gcdebug import gc_info
#         from rql.stmts import Union
#         from cubicweb.appobject import AppObject
#         from cubicweb.rset import ResultSet
#         from cubicweb.dbapi import Connection, Cursor
#         from cubicweb.web.request import CubicWebRequestBase
#         lookupclasses = (AppObject,
#                          Union, ResultSet,
#                          Connection, Cursor,
#                          CubicWebRequestBase)
#         try:
#             from cubicweb.server.session import Session, InternalSession
#             lookupclasses += (InternalSession, Session)
#         except ImportError:
#             pass # no server part installed
#         self.w(u'<h2>%s</h2>' % _('Garbage collection information'))
#         counters, ocounters, garbage = gc_info(lookupclasses,
#                                                viewreferrersclasses=())
#         self.w(u'<h3>%s</h3>' % self._cw._('Looked up classes'))
#         values = sorted(counters.iteritems(), key=lambda x: x[1], reverse=True)
#         self.wview('pyvaltable', pyvalue=values)
#         self.w(u'<h3>%s</h3>' % self._cw._('Most referenced classes'))
#         values = sorted(ocounters.iteritems(), key=lambda x: x[1], reverse=True)
#         self.wview('pyvaltable', pyvalue=values[:self._cw.form.get('nb', 20)])
#         if garbage:
#             self.w(u'<h3>%s</h3>' % self._cw._('Unreachable objects'))
#             values = sorted(xml_escape(repr(o)) for o in garbage)
#             self.wview('pyvallist', pyvalue=values)

def registration_callback(vreg):
    orbui_components = ((ProcessInformationViewOrbui, debug.ProcessInformationView),
                        (RegistryViewOrbui, debug.RegistryView),
                        )
    vreg.register_all(globals().values(), __name__, [new for (new,old) in orbui_components])
    for new, old in orbui_components:
        vreg.register_and_replace(new, old)
