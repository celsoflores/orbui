
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

from logilab.mtconverter import xml_escape
from cubicweb import Unauthorized, neg_role
from cubicweb.utils import json_dumps
from cubicweb.web import formwidgets
from cubicweb.web.views import formrenderers
from cubicweb.web.views.autoform import (AutomaticEntityForm, get_pending_deletes, relation_id,
                                         GenericRelationsField, toggleable_relation_link)
from cubicweb.web.views.forms import FieldsForm

FieldsForm.needs_css = ()
FieldsForm.cssclass = 'form-horizontal'


class GenericRelationsWidgetOrbui(formwidgets.FieldWidget):
    """override the GenericRelation default widget.
       CubicWeb builds a table, in orbui, we build a simple list of divs :
    """

    def render(self, form, field, renderer):
        stream = []
        w = stream.append
        req = form._cw
        _ = req._
        __ = _
        entity = form.edited_entity
        eid = entity.eid
        etype = entity.e_schema
        relative_url = '%s' % eid
        w(u'<div class="accordion form-relation" id="accordion_%s">'
           % eid)
        w_num_rel = 0
        for label, rschema, role in field.relations:
            # FIXME should be a more optimized way to get the name of
            # the target entity.
            relation = req.entity_from_eid(rschema.eid)
            targets = rschema.targets(etype, role)
      
        #----
        #    Agregar ciclo sobre targets
        #----
            for target in targets:
                if w_num_rel == 0:
                    w(u'<div class="row-fluid">')
                w_num_rel = w_num_rel+1
                
                linkto = '%s:%s:%s' % (rschema, eid, neg_role(role))
                link_label = u'%s %s' % (req._('add'), req._(target))
                lsearch = u'%s %s' % (req._('search'), req._(target))

                relate_entity = (u'<div class="relate-entity">%(relate_entity)s</div>'%
                                 {'relate_entity': entity.view('autocomplete-edition-view', relation=rschema,
                                            role=role, etype_search=target,showname="E")})

                search_url = ('<a href="?__mode=%(role)s:%(eid)s:%(rschema)s:'
                           '%(target)s&vid=search-associate"'
                           'class="btn btn-micro btn-link">'
                           '%(link_label)s'
                           '</a>'
                            %
                           {'role': role,
                           'rschema': rschema, 'eid': eid,
                            'link_label': lsearch, 'target': target})

                add_new = ('<a href="/add/%(target)s?__linkto=%(linkto)s'
                           '&__redirectpath=%(url)s&__redirectvid=edition "'
                           'class="btn btn-micro btn-link">'
                           '%(link_label)s'
                           '</a>'
                            %
                           {'linkto': linkto, 'url': relative_url,
                            'link_label': link_label, 'target': target})

                w(u'<div class="span4"><div class="accordion-group">'
                  u'<div class="accordion-heading container-fluid">'
                  u'    <div id="RDR_%(relation_name)s_%(role)s_%(target)s">'
                  u'        <a class="accordion-toggle" data-toggle="collapse" '
                  u'            data-parent="# accordion_%(eid)s" '
                  u'             href="#collapse_%(relation_name)s">'
                  u'             %(label)s'
                  u'        </a>'
                  u'    </div>'             # </div> de id_RDR.. 
                  u'    <div id="add-relation-combo">%(search)s %(add_new)s</div>'
                  u'</div>'             # </div> de accordion-heading 
                   % {'eid': eid, 'relation_name': rschema, 'target': target,
                      'label': label, 'search': search_url,
                      'add_new': add_new, 'role': role,
                      'relate-entity': relate_entity})
                w(u'<div id="collapse_%(relation)s" class="accordion-body collapse in">'
                  u'    <div class="accordion-inner">'
                  u'        <ul class="thumbnails">%(relate-entity)s' %
                      {'relation': rschema, 'relate-entity':relate_entity})
        #----
        # Reemplazar los widgets desordenados de la vid=edition por tablas tipo any_rset
        #----
                if role == "subject":
                    subject_eid=eid
                    target_eid='eid-objeto'
                    rql = ('Any X,X WHERE X is %(target)s,Y is %(entity)s,'
                           ' Y %(relate)s X, Y eid %(eid)s ' %
                              {'relate':rschema,
                               'target':target,
                               'entity':etype,
                               'eid':eid} )
                else:
                    subject_eid='eid-objeto'
                    target_eid=eid
                    rql = ('Any X,X WHERE X is %(target)s,Y is %(entity)s,'
                           ' X %(relate)s Y, Y eid %(eid)s' %
                              {'relate':rschema,
                               'target':target,
                               'entity':etype,
                               'eid':eid} )

                rset = form._cw.execute(rql)
        #----
        #    Incluir el activador ([x]) de borrado de relaciones en la tabla preentada. 
        #        + cellvid redf-del-rel para el activador de borrado
        #        + cellvid pending_del para que las relaciones seleccionadas se marquen  visualmente 
        #----
                pending_deletes = get_pending_deletes(form._cw, eid)
                ea_relation = rschema.type
                param_but = '%s|%s|%s|%s|%s'%('Y',eid,ea_relation,role,str(pending_deletes))

                kwargs={'ea_rel_entity': target,
                    'ea_relation': rschema,
                    'role':role,
                    'headers':(' ',''),
                    'cellvids':{0:'rdef-del-rel','_0':param_but,1:'pending-del','_1':param_but},
                    'limit':10,
                    'rdefkwargs':{},
                    'title':u'no-widget-title',
                    }

                w(form._cw.view('w-table', rset, 'null',**kwargs))
        #----
                w(u'    </div>'             # </div> de accordion-inner
                  u'</div></div>'        # </div> de accordion-body-collapse  -- </div> accordion-group           
                  u'</div>')         # </div> de span4  

                if w_num_rel == 3:  # controlar el cambio de row de los widgets 
                    w(u'</div>')
                    w_num_rel = 0
        if w_num_rel > 0:
            w(u'</div>')
        w(u'</div>'     
          u'</div>')

        # FIXME try to change this table with a fancy html code.

        pendings = list(field.restore_pending_inserts(form))

        w(u'<table id="relatedEntities">')
        if not pendings:
            w(u'<tr><th>&#160;</th><td>&#160;</td></tr>')
        else:
            for row in pendings:
                # soon to be linked to entities
                w(u'<tr id="tr%s">' % row[1])
                w(u'<th>%s</th>' % row[3])
                w(u'<td>')
                w(u'<a class="handle" title="%s" href="%s">[x]</a>' %
                  (_('cancel this insert'), row[2]))
                w(u'<a id="a%s" class="editionPending" href="%s">%s</a>'
                  % (row[1], row[4], xml_escape(row[5])))
                w(u'</td>')
                w(u'</tr>')
        w(u'<tr id="relationSelectorRow_%s" class="separator">' % eid)
        w(u'<th class="labelCol">')
        w(u'<select id="relationSelector_%s" tabindex="%s" '
          u'onchange="javascript:showMatchingSelect'
          u'(this.options[this.selectedIndex].value,%s);">'
          % (eid, req.next_tabindex(), xml_escape(json_dumps(eid))))
        w(u'<option value="">%s</option>' % _('select a relation'))
        for i18nrtype, rschema, role in field.relations:
            # more entities to link to
            w(u'<option value="%s_%s">%s</option>' % (rschema, role, i18nrtype))
        w(u'</select>')
        w(u'</th>')
        w(u'<td id="unrelatedDivs_%s"></td>' % eid)
        w(u'</tr>')
        w(u'</table>')
        return '\n'.join(stream)


GenericRelationsField.widget = GenericRelationsWidgetOrbui
GenericRelationsField.control_field = False


class FormRendererOrbui(formrenderers.FormRenderer):
    """form renderer class
    """
    button_bar_class = u'form-actions'

    def render_content(self, w, form, values):
        if self.display_progress_div:
            w(u'<div id="progress">%s</div>' % self._cw._('validating...'))
        w(u'<fieldset>')

        if '__redirectpath' not in self._cw.form:
            if hasattr(form, 'edited_entity'):
                entity = form.edited_entity
                if hasattr(entity, 'has_eid'):
                    if entity.has_eid():
                        redirect_path = entity.rest_path()
                        w(u'<input name="__redirectpath" type="hidden" value="%s" />'
                                 % redirect_path)
                        w(u'<input name="__redirectparams" type="hidden" value="" />')

        self.render_fields(w, form, values)
        self.render_buttons(w, form)
        w(u'</fieldset>')

    def render_help(self, form, field):
        """display help in the form
        """
        help = []
        descr = field.help
        if callable(descr):
            if support_args(descr, 'form', 'field'):
                descr = descr(form, field)
            else:
                warn("[3.10] field's help callback must now take form "
                     "and field as argument (%s)" % field, DeprecationWarning)
                descr = descr(form)
        if descr:
            help.append('<p class="muted"><small>%s</small></p>' % self._cw._(descr))
        example = field.example_format(self._cw)
        if example:
            help.append('<p class="muted"><small>(%s: %s)</small></p>'
                        % (self._cw._('sample format'), example))
        return u'&#160;'.join(help)

    def error_message(self, form):
        """return formatted error message

        This method should be called once inlined field errors has been consumed
        """
        req = self._cw
        errex = form.form_valerror
        # get extra errors
        if errex is not None:
            errormsg = req._('please correct the following errors:')
            errors = form.remaining_errors()
            if errors:
                if len(errors) > 1:
                    templstr = u'<li>%s</li>'
                else:
                    templstr = u'&#160;%s'
                for field, err in errors:
                    if field is None:
                        errormsg += templstr % err
                    else:
                        errormsg += templstr % '%s: %s' % (req._(field), err)
                if len(errors) > 1:
                    errormsg = '<ul>%s</ul>' % errormsg
            return u'<div class="errorMessage alert">%s</div>' % errormsg
        return u''

    def _render_fields(self, fields, w, form):
        """render form fields
        """
        byfieldset = {}
        for field in fields:
            byfieldset.setdefault(field.fieldset, []).append(field)
        if form.fieldsets_in_order:
            fieldsets = form.fieldsets_in_order
        else:
            fieldsets = byfieldset.keys()
        for fieldset in fieldsets:
            try:
                fields = byfieldset.pop(fieldset)
            except KeyError:
                self.warning('no such fieldset: %s (%s)', fieldset, form)
                continue
            w(u'<fieldset class="%s">' % (fieldset or u'default'))
            if fieldset:
                w(u'<legend>%s</legend>' % self._cw._(fieldset))
            for field in fields:
                error = form.field_error(field)
                control = not hasattr(field, 'control_field') or field.control_field
                w(u'<div class="control-group %s-%s_row %s">' %
                                    (field.name, field.role, 'error' if error else ''))
                if self.display_label and field.label is not None:
                    w(u'%s' % self.render_label(form, field))
                if control:
                    w(u'<div class="controls">')
                else:
                    w(u'<div class="controls no-margin">')
                w(field.render(form, self))
                if error:
                    self.render_error(w, error)
                if self.display_help:
                    w(self.render_help(form, field))
                w(u'</div>')
                w(u'</div>')
            w(u'</fieldset>')
        if byfieldset:
            self.warning('unused fieldsets: %s', ', '.join(byfieldset))

    def render_buttons(self, w, form):
        """render form's buttons
        """
        if not form.form_buttons:
            return
        w(u'<div class="%s">' % self.button_bar_class)
        for button in form.form_buttons:
            w(u'%s' % button.render(form))
        w(u'</div>')


class EntityFormRendererOrbui(FormRendererOrbui, formrenderers.EntityFormRenderer):
    """This is the 'default' renderer for entity's form.

    You can still use form_renderer_id = 'base' if you want base FormRenderer
    layout even when selected for an entity.
    """

    def open_form(self, form, values):
        """creates the form's title
        """
        attrs_fs_label = ''
        if self.main_form_title:
            attrs_fs_label = (u'<legend>%s</legend>' %
                              self._cw._(self.main_form_title))
        open_form = u'%s%s' % (attrs_fs_label,
                               super(formrenderers.EntityFormRenderer,
                                     self).open_form(form, values))
        return open_form

    def close_form(self, form, values):
        """seems dumb but important for consistency w/ close form, and necessary
        for form renderers overriding open_form to use something else or
        more than
        and <form>
        """
        return super(formrenderers.EntityFormRenderer, self).close_form(form, values) + ''

    def render_buttons(self, w, form):
        """let the form buttons be inside a div
        """
        if len(form.form_buttons) == 3:
            w(u'<div class="form-actions"> %s %s %s </div>' %
              tuple(button.render(form) for button in form.form_buttons))
        else:
            super(formrenderers.EntityFormRenderer, self).render_buttons(w, form)


class EntityInlinedFormRendererOrbui(EntityFormRendererOrbui,
                                        formrenderers.EntityInlinedFormRenderer):
    def open_form(self, w, form, values):
        try:
            w(u'<div id="div-%(divid)s" onclick="%(divonclick)s">' % values)
        except KeyError:
            w(u'<div id="div-%(divid)s">' % values)
        else:
            w(u'<div id="notice-%s" class="notice">%s</div>' % (
                values['divid'], self._cw._('click on the box to cancel the deletion')))
        w(u'<div class="iformBody">')

    def close_form(self, w, form, values):
        w(u'</div></div>')

    def render_fields(self, w, form, values):
        w(u'<fieldset id="fs-%(divid)s">' % values)
        fields = self._render_hidden_fields(w, form)
        w(u'</fieldset>')
        if fields:
            self._render_fields(fields, w, form)
        self.render_child_forms(w, form, values)


class AutomaticEntityFormOrbui(AutomaticEntityForm):
    """overwrites the original Automatic Entity Form class
    """
    cssclass = 'form-horizontal'

# replace FormRenderer
def registration_callback(vreg):
    """register new primary view for orbui project
    """
    orbui_components = ((FormRendererOrbui, formrenderers.FormRenderer),
                        (EntityFormRendererOrbui, formrenderers.EntityFormRenderer),
                        (EntityInlinedFormRendererOrbui, formrenderers.EntityInlinedFormRenderer),
                        (AutomaticEntityFormOrbui, AutomaticEntityForm),
                        )
    vreg.register_all(globals().values(), __name__,
                        [new for (new, old) in orbui_components])
    for new, old in orbui_components:
        vreg.register_and_replace(new, old)
