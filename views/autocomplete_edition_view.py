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
from cubicweb.web import controller, Redirect
from cubicweb.view import EntityView
from cubicweb.selectors import is_instance


class AutoCompleteEntityRetriever(startup.IndexView):
    """retrieves entity for autocomplete function using the main attribute.
    """
    # special search of autocomplete
    SPECIALSEARCH = {'EntityA|relation|EntityB': ', filters..',
                    '__ud': ' '}

    # special condition of autocomplete
    SPECIALCONDITION = {'EntityA|relation|EntityB': ', Conditions..',
                        }
    # Help messages and error messages if add any relation not valid
    HELP_MESSAGES = {}

    templatable = False
    content_type = 'text/html'
    cache_max_age = 0  # no cache
    __regid__ = 'autocomplete-entity-retriever'

    def call(self):
        """create query for autocomplete
        """
        subject = True
        relation = ''
        etype_search = ''
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
            search = form['q']
            main_attribute = self._cw.vreg.schema.eschema(etype_search).main_attribute()
            specialsearch = self.getSpecialSearch(self._cw, parent_entity, relation, etype_search, role)
            constraint = ', %s %s ILIKE "%%%s%%" %s' % (letter, main_attribute, search, specialsearch)
            unrelated = parent_entity.cw_unrelated_rql(relation, etype_search, role)
            rql = (unrelated[0] + constraint).replace('DESC WHERE', 'DESC LIMIT 30 WHERE').replace('Any ','DISTINCT Any ')
            rset = self._cw.execute(rql, unrelated[1])
            for entity in rset.entities():
                printable_value = entity.printable_value(entity.e_schema.main_attribute())
                self.w(u'%s||%s\n' % (printable_value, entity.eid))

    def getSpecialSearch(self, session, parent_entity, relation, etype_search, role):
        eid = parent_entity.eid
        paren_name = type(parent_entity).__name__

        target = '%(paren_name)s|%(relation)s%(role)s|%(etype_search)s' % {
                                            'paren_name': paren_name,
                                            'relation': relation,
                                            'role': ('' if role == 'subject' else '_object'),
                                            'etype_search': etype_search}
        SPECIALSEARCH = self.SPECIALSEARCH
        SPECIALCONDITION = self.SPECIALCONDITION

        #Evalua si existe una condicion especial
        if target in SPECIALSEARCH:
            specialsearch = SPECIALSEARCH[target]
        else:
            return SPECIALSEARCH['__ud']

        #Evalua si existe una condicion especial para hacer o no la busqueda
        if target in SPECIALCONDITION:
            specialcondition = SPECIALCONDITION[target]
        else:
            return specialsearch

        #En caso de que exista una condicion especial para la busqueda,
        #evaluar que exista informacion y regresa la condicion espadial
        rset = session.execute(specialcondition % {'eid': eid, })
        if rset.rowcount > 0:
            return specialsearch
        else:
            return SPECIALSEARCH['__ud']


class AutocompleteEditionView(EntityView):
    """generic autocomplete view.
    """
    templatable = False
    __regid__ = 'autocomplete-edition-view'
    __select__ = is_instance('Any')

    def cell_call(self, row, col, relation='', role='subject', etype_search='', showname="Y"):
        """display the autocomplete widget
        """
        self._cw.add_js('jquery.autocomplete.js')
        self._cw.add_js('orbui.autocomplete.js')
        if role == 'subject':
            subject = True
        else:
            subject = False
        entity = self.cw_rset.get_entity(row, col)
        eid = entity.eid

        target = ('%(entity)s|%(relation)s%(role)s|%(etype_search)s'
                % {'entity': type(entity).__name__,
                   'relation': relation,
                   'role': ('' if role == 'subject' else '_object'),
                   'etype_search': etype_search})
        helpmsg = ''
        if target in AutoCompleteEntityRetriever().HELP_MESSAGES:
            helpmsg = ('<p class="text-info">'
               u'<small>%(help)s</small>'
               u'</p>' % {'help': self._cw._(AutoCompleteEntityRetriever().HELP_MESSAGES[target])})

        jscode = (u'var params = new Array();'
                  u'params[\'subject\'] = \'%(subject)s\';'
                  u'params[\'etype_search\'] = \'%(etype_search)s\';'
                  u'params[\'relation\'] = \'%(relation)s\';'
                  u'params[\'eid_parent\'] = \'%(eid)s\';'
                  u'makeautocomplete("#entityname_%(relation)s_%(eid)s_%(role)s_%(etype_search)s",'
                  u'"autocomplete-entity-retriever",'
                  u'"#entityeid_%(relation)s_%(eid)s_%(role)s_%(etype_search)s", params);'
                  % {'eid': eid, 'relation': relation, 'subject': subject,
                     'etype_search': etype_search,
                     'role': role})
        self._cw.add_onload(jscode)

        if showname == "Y":
            namee = (u'<div class="muted">'
               u'<small>%(name)s</small>'
               u'</div>' % {'name': self._cw._(etype_search)})
            url = entity.rest_path() + '?vid=edition'
        elif showname == "E":
            namee = ''
            url = entity.rest_path() + '?vid=edition'
        else:
            namee = ''
            url = entity.rest_path()

        self.w(u'<fieldset>'
               u'%(name)s'
               u'<input id="entityname_%(relation)s_%(eid)s_%(role)s_%(etype_search)s" '
               u'name="entityname_%(relation)s_%(eid)s_%(role)s_%(etype_search)s" type="text" '
               u'class="input" placeholder="%(etype_searchT)s"/>'
               u'<input id="entityeid_%(relation)s_%(eid)s_%(role)s_%(etype_search)s" '
               u'name="entityeid_%(relation)s_%(eid)s_%(role)s_%(etype_search)s" type="hidden"/>'
               u'<button type="button" class="btn btn-micro btn-success" '
               u'id="btn-add-relation"'
               u'onclick="javascript:redirect_edit_controller(\'%(subject)s\','
               u'\'%(relation)s\',\'%(eid)s\',\'%(etype_search)s\',\'%(url)s\');">%(confirm)s</button>'
               u'</fieldset>%(helpmsg)s'
               u'' % {'name': namee, 'eid': eid,
                      'relation': relation, 'url': url,
                      'subject': subject, 'etype_search': etype_search,'etype_searchT': self._cw._(etype_search),
                      'confirm': '<i class="icon-white icon-ok"></i>',  # changed label "Confirm" by icon
                      'role': role, 'helpmsg': helpmsg})


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
        etype_search = frm['etype_search']

        if subject == 'True':
            related_eid = frm['entityeid_%s_%s_subject_%s' % (relation, frm['parent_eid'], etype_search)]
            subject_eid = frm['parent_eid']
            object_eid = related_eid
        else:
            related_eid = frm['entityeid_%s_%s_object_%s' % (relation, frm['parent_eid'], etype_search)]
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
        subject = form['subject']

        sr_RDR = '#RDR_' + form['relation'] + \
                   ('_subject_' if subject == 'True' else '_object_') + \
                   form['etype_search']

        if '__redirect' in form:
            return self._cw.build_url(form['__redirect']) + sr_RDR
        else:
            return entity.absolute_url() + '?vid=edition' + sr_RDR



