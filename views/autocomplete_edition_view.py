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

from cubicweb.web.views import startup
from cubicweb import schema
from cubicweb.web import controller, Redirect
from cubicweb.view import EntityView
from cubicweb.selectors import is_instance


class AutoCompleteEntityRetriever(startup.IndexView):
    """retrieves entity for autocomplete function using the main attribute.
    """
    templatable = False
    content_type = 'text/html'
    cache_max_age = 0 # no cache
    __regid__ = 'autocomplete-entity-retriever'

    def call(self):
        """create query for autocomplete
        """
        subject = True
        relation = ''
        etype_search = ''
        eid_parent = 0
        form = self._cw.form
        if 'subject' in form:
            subject = True if form['subject'] == 'True' else False
        if 'etype_search' in form:
            etype_search = form['etype_search']
        if 'relation' in form:
            relation = form['relation']
        if 'eid_parent' in form:
            eid = form['eid_parent']
        if subject:
            letter = 'O'
            role = 'subject'
        else:
            letter = 'S'
            role = 'object'
        parent_entity = self._cw.entity_from_eid(eid)
        if 'q' in form:
            search =form['q']
            main_attribute = self._cw.vreg.schema.eschema(etype_search).main_attribute()
            constraint = ', %s %s ILIKE "%%%s%%"' % (letter, main_attribute, search)
            unrelated = parent_entity.cw_unrelated_rql(relation, etype_search, role)
            rql = unrelated[0] + constraint
            rset = self._cw.execute(rql, unrelated[1])
            for entity in rset.entities():
                printable_value = entity.printable_value(entity.e_schema.main_attribute())
                self.w(u'%s||%s\n' % (printable_value, entity.eid))


class AutocompleteEditionView(EntityView):
    """generic autocomplete view.
    """
    templatable = False
    __regid__ = 'autocomplete-edition-view'
    __select__ = is_instance('Any')

    def cell_call(self, row, col, relation='', role='subject', etype_search=''):
        """display the autocomplete widget
        """
        self._cw.add_js('jquery.autocomplete.js')
        self._cw.add_js('orbui.autocomplete.js')
        form = self._cw.form
        if role == 'subject':
            subject = True
        else:
            subject = False
        entity = self.cw_rset.get_entity(row, col)
        url = entity.rest_path() + '?vid=edition'
        eid = entity.eid
        jscode = (u'var params = new Array();'
                  u'params[\'subject\'] = \'%(subject)s\';'
                  u'params[\'etype_search\'] = \'%(etype_search)s\';'
                  u'params[\'relation\'] = \'%(relation)s\';'
                  u'params[\'eid_parent\'] = \'%(eid)s\';'
                  u'makeautocomplete("#entityname_%(relation)s_%(eid)s",'
                  u'"autocomplete-entity-retriever",'
                  u'"#entityeid_%(relation)s_%(eid)s", params);'
                  % {'eid': eid, 'relation': relation, 'subject': subject,
                     'etype_search': etype_search})
        self._cw.add_onload(jscode)
        self.w(u'<form method="get" action="/autocomplete-entity-controller" '
               u'name="entityname_%(relation)s_%(eid)s">'
               u'<fieldset>'
               u'<label class="span4 muted"><small class="pull-right">%(name)s</small>'
               u'</label>'
               u'<input id="entityname_%(relation)s_%(eid)s" '
               u'name="entityname_%(relation)s_%(eid)s" type="text" '
               u'class="input"/>'
               u'<input id="entityeid_%(relation)s_%(eid)s" '
               u'name="entityeid_%(relation)s_%(eid)s" type="hidden"/>'
               u'<input id="__redirectpath" value="%(url)s" '
               u'name="__redirectpath" type="hidden"/>'
               u'<input id="relation" value="%(relation)s" '
               u'name="relation" type="hidden"/>'
               u'<input id="subject" value="%(subject)s" '
               u'name="subject" type="hidden"/>'
               u'<input id="parent_eid" value="%(eid)s" '
               u'name="parent_eid" type="hidden"/>'
               u'<button type="submit" class="btn btn-success btn-small" '
               u'id="btn-add-relation" >+</button>'
               u'</fieldset>'
               u'</form>' % {'name': etype_search, 'eid': eid,
                            'relation': relation, 'url': url,
                            'subject': subject})


class AutocompleteEntityController(controller.Controller):
    """autocomplete entity controller
    """
    __regid__ = 'autocomplete-entity-controller'

    def publish(self, rset=None):
        raise Redirect(self.success_redirect_url(self.save_data()))

    def save_data(self):
        """check if tag exists or create a new one, then tag the entity
        """
        frm = self._cw.form
        subject = frm['subject']
        relation = frm['relation']
        related_eid = frm['entityeid_%s_%s' % (relation, frm['parent_eid'])]
        if subject == 'True':
            subject_eid = frm['parent_eid']
            object_eid = related_eid
        else:
            subject_eid = related_eid
            object_eid = frm['parent_eid']
        rql = ('SET X %(relation)s Y '
               'WHERE X eid %(subject_eid)s , Y eid %(object_eid)s')
        entity = self._cw.entity_from_eid(frm['parent_eid'])
        rql = rql % {'relation': relation, 'subject_eid': subject_eid,
                               'object_eid': object_eid}
        self._cw.execute(rql)
        return entity

    def success_redirect_url(self, entity):
        """success redirection
        """
        form = self._cw.form
        if '__redirectpath' in form:
            return self._cw.build_url(form['__redirectpath'])
        else:
            return entity.absolute_url()
