# -*- coding: utf-8 -*-
# Validation hook for relationship
# Author: Softtek - MLCS
# Date: Jun 2014
# Project: Platypus

from cubicweb import ValidationError
from cubicweb.server.hook import Hook, match_rtype
from cubes.orbui.views.autocomplete_edition_view import AutoCompleteEntityRetriever


class Validate_Autocomplete_RulesHook(Hook):
    """
    Validate the correct application of the autocomplete rules
    """
    __regid__ = 'validateAutocompleteRules'
    __select__ = Hook.__select__ & ~match_rtype('created_by', 'owned_by')
    events = ('before_add_relation',)

    def __call__(self):
        #print 'eidfrom: %s, eidto: %s, rtype: %s' % (self.eidfrom, self.eidto, self.rtype)
        #Cuando ya existe la relación no se evaluan las condiciones especiales
        srql = 'Any X, Y WHERE X %s Y, X eid %s, Y eid %s' % (self.rtype, self.eidfrom, self.eidto)
        if self._cw.execute(srql).rowcount > 0:
            return

        eidfrom = self._cw.entity_from_eid(self.eidfrom)
        eidto = self._cw.entity_from_eid(self.eidto)

        #Evaluate the direct relation
        target = ''
        specialsearch = AutoCompleteEntityRetriever().getSpecialSearch(self._cw, eidfrom, self.rtype, type(eidto).__name__, 'subject')
        if specialsearch != ' ':
            unrelated = eidfrom.cw_unrelated_rql(self.rtype, type(eidto).__name__, 'subject')
            srql = ((unrelated[0] % unrelated[1]) + specialsearch + ', O eid ' + str(self.eidto))
            if self._cw.execute(srql).rowcount < 1:
                target = ('%(entity)s|%(relation)s%(role)s|%(etype_search)s'
                % {'entity': type(eidfrom).__name__,
                   'relation': self.rtype, 'role': '',
                   'etype_search': type(eidto).__name__})
                helpmsg = self._cw._('Validation error, relation not valid')
                if target in AutoCompleteEntityRetriever().HELP_MESSAGES:
                    helpmsg = self._cw._(AutoCompleteEntityRetriever().HELP_MESSAGES[target])
                raise ValidationError(self.eidfrom, {self.rtype: helpmsg})

        #Evaluate the reverse relation
        target = ''
        specialsearch = AutoCompleteEntityRetriever().getSpecialSearch(self._cw, eidto, self.rtype, type(eidfrom).__name__, 'object')
        if specialsearch != ' ':
            unrelated = eidto.cw_unrelated_rql(self.rtype, type(eidfrom).__name__, 'object')
            srql = ((unrelated[0] % unrelated[1]) + specialsearch + ', S eid ' + str(self.eidfrom))
            if self._cw.execute(srql).rowcount < 1:
                target = ('%(entity)s|%(relation)s%(role)s|%(etype_search)s'
                % {'entity': type(eidto).__name__,
                   'relation': self.rtype, 'role': '_object',
                   'etype_search': type(eidfrom).__name__})
                helpmsg = self._cw._('Validation error, relation not valid')
                if target in AutoCompleteEntityRetriever().HELP_MESSAGES:
                    helpmsg = self._cw._(AutoCompleteEntityRetriever().HELP_MESSAGES[target])
                raise ValidationError(self.eidto, {self.rtype: helpmsg})


