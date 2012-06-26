
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

from cubicweb.web.views.formrenderers import FormRenderer, EntityFormRenderer
from cubicweb.web.views.autoform import AutomaticEntityForm


class FormRendererOrbui(FormRenderer):
    """form renderer class
    """
    button_bar_class = u'form-actions'

    def render_content(self, w, form, values):
        if self.display_progress_div:
            w(u'<div id="progress">%s</div>' % self._cw._('validating...'))
        w(u'<fieldset class="form-horizontal">')
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
            help.append('<p class="help-block">%s</p>' % self._cw._(descr))
        example = field.example_format(self._cw)
        if example:
            help.append('<p class="help-block">(%s: %s)</p>'
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
            w(u'<fieldset class="form-horizontal %s">\n' % (fieldset or
                                                            u'default'))
            if fieldset:
                w(u'<legend>%s</legend>' % self._cw._(fieldset))
            for field in fields:
                w(u'<div class="control-group %s_%s_row">' % (field.name,
                                                              field.role))
                if self.display_label and field.label is not None:
                    w(u'%s' %
                      self.render_label(form, field))
                w(u'<div')
                if field.label is None:
                    w(u' colspan="2"')
                error = form.field_error(field)
                if error:
                    w(u' class="error"')
                w(u' class="controls">')
                w(field.render(form, self))
                w(u'')
                if error:
                    self.render_error(w, error)
                if self.display_help:
                    w(self.render_help(form, field))
                w(u'</div></div>')
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


class EntityFormRendererOrbui(EntityFormRenderer):
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
                               super(EntityFormRenderer,
                                     self).open_form(form, values))
        return open_form

    def close_form(self, form, values):
        """seems dumb but important for consistency w/ close form, and necessary
        for form renderers overriding open_form to use something else or
        more than
        and <form>
        """
        return super(EntityFormRenderer, self).close_form(form, values) + ''

    def render_buttons(self, w, form):
        """let the form buttons be inside a div
        """
        if len(form.form_buttons) == 3:
            w(u'<div class="form-actions"> %s %s %s </div>' %
              tuple(button.render(form) for button in form.form_buttons))
        else:
            super(EntityFormRenderer, self).render_buttons(w, form)

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
            w(u'<fieldset class="form-horizontal %s">' % (fieldset or
                                                          u'default'))
            if fieldset:
                w(u'<legend>%s</legend>' % self._cw._(fieldset))
            for field in fields:
                w(u'<div class="control-group %s_%s_row">' % (field.name,
                                                              field.role))
                if self.display_label and field.label is not None:
                    w(u'%s' %
                      self.render_label(form, field))
                w(u'<div')
                if field.label is None:
                    w(u' colspan="2"')
                error = form.field_error(field)
                if error:
                    w(u' class="error"')
                w(u' class="controls">')
                w(field.render(form, self))
                w(u'')
                if error:
                    self.render_error(w, error)
                if self.display_help:
                    w(self.render_help(form, field))
                w(u'</div></div>')
            w(u'</fieldset>')
        if byfieldset:
            self.warning('unused fieldsets: %s', ', '.join(byfieldset))


class AutomaticEntityFormOrbui(AutomaticEntityForm):
    """overwrites the original Automatic Entity Form class
    """
    cssclass = 'form-horizontal'


# replace FormRenderer
def registration_callback(vreg):
    """register new primary view for orbui project
    """
    orbui_components = ((FormRendererOrbui, FormRenderer),
                        (EntityFormRendererOrbui, EntityFormRenderer),
                        (AutomaticEntityFormOrbui, AutomaticEntityForm),
                        )
    vreg.register_all(globals().values(), __name__, [new for (new,old) in orbui_components])
    for new, old in orbui_components:
        vreg.register_and_replace(new, old)
