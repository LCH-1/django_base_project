from functools import partial
from typing import Any

from django.contrib import admin
from django.contrib.admin import helpers, StackedInline, display
from django.contrib.admin.options import InlineModelAdmin
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.utils import flatten_fieldsets, unquote
from django.contrib.admin.options import get_content_type_for_model
from django.db import models
from django.db.models import OneToOneField, ForeignKey
from django.forms import ModelForm
from django.forms.formsets import all_valid
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.urls import reverse
from django.utils.html import format_html
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe
from django.core.exceptions import PermissionDenied, FieldDoesNotExist


class ReadonlyMixin:
    set_all_fields_readonly = True

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class ReadonlyInlineMixin(ReadonlyMixin):
    can_delete = False

    def __init__(self, *args, **kwargs):
        self._readonly_fields = []
        self.template = f'custom/tabular.html'

        super().__init__(*args, **kwargs)

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        self._readonly_fields = fields

        return fields

    def get_readonly_fields(self, request, obj=None):
        # readonly_fields = super().get_readonly_fields(request, obj)
        # return set(readonly_fields) | set(self._readonly_fields)

        return self._readonly_fields


class AdminMixin:
    disable_auto_readonly_fields = False
    disable_ordering_fields = False
    disable_setup_fields = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fields = []

    def _get_related_link(self, obj, str_field=None, verbose=None):
        app_label = obj._meta.app_label
        model_name = obj._meta.model_name
        verbose = verbose or (getattr(obj, str_field, "-") if str_field else str(obj))

        link = reverse(f"admin:{app_label}_{model_name}_change", args=[obj.pk,])
        return format_html(f'<a href="{link}">{verbose}</a>')

    def get_inlines(self, request, obj):
        if not obj:
            inlines = super().get_inlines(request, obj)
            return [x for x in inlines if not issubclass(x, ReadonlyInlineMixin)]

        return super().get_inlines(request, obj)

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)

        if not self.fields and not self.disable_ordering_fields:
            model_fields = self.model._meta.fields
            orderd_fields = [name for x in model_fields if (name := x.name) in fields]
            remain_fields = [x for x in fields if x not in orderd_fields]
            fields = orderd_fields + remain_fields

        return fields

    def add_view(self, request, form_url="", extra_context=None):
        fields = self.get_fields(request)

        if not self.disable_setup_fields:
            model = self.model
            model_pk_name = model._meta.pk.name
            model_fields = model._meta.fields
            model_field_names = [name for x in model_fields if (name := x.name) not in ["pk", model_pk_name]]
            self.fields = [x for x in fields if x in model_field_names]

        return self.changeform_view(request, None, form_url, extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        obj = self.get_object(request, unquote(object_id))
        self._fields = flatten_fieldsets(self.get_fieldsets(request, obj))
        return self.changeform_view(request, object_id, form_url, extra_context)

    def get_readonly_fields(self, request, obj=None):
        if not obj:
            return super().get_readonly_fields(request, obj)

        readonly_fields = list(super().get_readonly_fields(request, obj))
        if not self.disable_auto_readonly_fields:
            model_fields = self.model._meta.fields
            model_field_names = [field.name for field in model_fields]

            auto_readonly_fields = [obj._meta.pk.name]
            auto_readonly_fields += [field.name for field in model_fields if not getattr(field, 'editable', True)]
            auto_readonly_fields += [field for field in self._fields
                                     if field not in model_field_names + auto_readonly_fields]

            readonly_fields += auto_readonly_fields

        return readonly_fields


class ModelAdmin(AdminMixin, admin.ModelAdmin):
    pass


class TabularInline(AdminMixin, admin.TabularInline):
    pass


class SingletonModelAdmin(ModelAdmin):
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False

        return super().has_add_permission(request)


class AdminSite(admin.AdminSite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._registry_order = []

    def register(self, model_or_iterable, admin_class=ModelAdmin, **options):
        super().register(model_or_iterable, admin_class, **options)
        if isinstance(model_or_iterable, (list, tuple)):
            for model in model_or_iterable:
                self._registry_order.append(model)
        else:
            self._registry_order.append(model_or_iterable)

    def get_app_list(self, request):
        app_dict = self._build_app_dict(request)
        # # app_list를 원하는 순서로 재구성
        # app_list = sorted(
        #     app_dict.values(),
        #     key=lambda x: x['name'].lower()
        # )
        app_list = app_dict.values()

        for app in app_list:
            app['models'].sort(key=lambda x: self._registry_order.index(x['model']))

        return app_list


site = AdminSite()


# https://github.com/daniyalzade/django_reverse_admin
class ReverseInlineFormSet(BaseModelFormSet):
    '''
    A formset with either a single object or a single empty
    form. Since the formset is used to render a required OneToOne
    relation, the forms must not be empty.
    '''
    parent_fk_name = ''

    def __init__(self,
                 data=None,
                 files=None,
                 instance=None,
                 prefix=None,
                 queryset=None,
                 save_as_new=False):
        object_ = getattr(instance, self.parent_fk_name, None)
        if object_:
            qs = self.model.objects.filter(pk=object_.pk)
        else:
            qs = self.model.objects.none()
            self.extra = 1
        super().__init__(data, files,
                         prefix=prefix,
                         queryset=qs)
        for form in self.forms:
            form.empty_permitted = False


def _get_parent_fk_field(obj, formset):
    return next((f for f in obj._meta.fields if f.name == formset.parent_fk_name), None)


def _remove_blank_reverse_inlines(obj, formset_inline_tuples):
    """
    Hacky implementation, but for some reasons blank inlines are being treated
    as invalid. So, let's remove them from validation, since we know that they are
    actually valid.
    """
    def to_filter(formset):
        if not isinstance(formset, ReverseInlineFormSet):
            return True
        field = _get_parent_fk_field(obj, formset)
        return not (field.blank and not formset.has_changed())
    return [a for a in filter(lambda t: to_filter(t[0]), formset_inline_tuples)]


def reverse_inlineformset_factory(parent_model,
                                  model,
                                  parent_fk_name,
                                  form=ModelForm,
                                  fields=None,
                                  exclude=None,
                                  formfield_callback=lambda f: f.formfield()):

    if fields is None and exclude is None:
        related_fields = [f for f in model._meta.get_fields() if
                          (f.one_to_many or f.one_to_one or f.many_to_many) and f.auto_created and not f.concrete]
        fields = [f.name for f in model._meta.get_fields() if f not in
                  related_fields]  # ignoring reverse relations
    kwargs = {
        'form': form,
        'formfield_callback': formfield_callback,
        'formset': ReverseInlineFormSet,
        'extra': 0,
        'can_delete': True,
        'can_order': False,
        'fields': fields,
        'exclude': exclude,
        'max_num': 1,
    }
    FormSet = modelformset_factory(model, **kwargs)
    FormSet.parent_fk_name = parent_fk_name
    return FormSet


class ReverseInlineModelAdmin(InlineModelAdmin):
    '''
    Use the name and the help_text of the owning models field to
    render the verbose_name and verbose_name_plural texts.
    '''

    def __init__(self,
                 parent_model,
                 parent_fk_name,
                 model, admin_site,
                 inline_type):
        self.template = f'admin/edit_inline/{inline_type}.html'
        self.parent_fk_name = parent_fk_name
        self.model = model
        field_descriptor = getattr(parent_model, self.parent_fk_name)
        field = field_descriptor.field

        self.verbose_name_plural = field.verbose_name.title()
        self.verbose_name = field.help_text
        if not self.verbose_name:
            self.verbose_name = self.verbose_name_plural
        super(ReverseInlineModelAdmin, self).__init__(parent_model, admin_site)

    def get_formset(self, request, obj=None, **kwargs):
        if 'fields' in kwargs:
            fields = kwargs.pop('fields')
        elif self.get_fieldsets(request, obj):
            fields = flatten_fieldsets(self.get_fieldsets(request, obj))
        else:
            fields = None

        # want to combine exclude arguments - can't do that if they're None
        # also, exclude starts as a tuple - need to make it a list
        exclude = list(kwargs.get("exclude", []))
        exclude_2 = self.exclude or []
        exclude.extend(self.get_readonly_fields(request, obj))
        non_editable_fields = [f for f in self.model._meta.fields if not f.editable]
        exclude.extend(list(exclude_2))
        exclude.extend(non_editable_fields)
        # but need exclude to be None if result is an empty list
        exclude = exclude or None

        defaults = {
            "form": self.form,
            "fields": fields,
            "exclude": exclude,
            "formfield_callback": partial(self.formfield_for_dbfield, request=request),
        }
        kwargs.update(defaults)
        return reverse_inlineformset_factory(self.parent_model,
                                             self.model,
                                             self.parent_fk_name,
                                             **kwargs)


class ReverseModelAdmin(admin.ModelAdmin):
    '''
    Patched ModelAdmin class. The add_view method is overridden to
    allow the reverse inline formsets to be saved before the parent
    model.
    '''
    inline_reverse = []
    inline_type = ""

    def __init__(self, model, admin_site):
        if not self.inline_reverse or not self.inline_type:
            raise ValueError(
                f'At least one inline_reverse and inline_type must be specified for {self.__class__.__name__}')

        super().__init__(model, admin_site)
        if self.exclude is None:
            self.exclude = []
        self.exclude = list(self.exclude)

        inline_instances = []
        for field_name in self.inline_reverse:

            kwargs = {}
            admin_class = None
            if isinstance(field_name, tuple):
                kwargs = field_name[1]
                field_name = field_name[0]
            elif isinstance(field_name, dict):
                kwargs = field_name.get('kwargs', kwargs)
                admin_class = field_name.get('admin_class', admin_class)
                field_name = field_name['field_name']

            field = model._meta.get_field(field_name)
            if isinstance(field, (OneToOneField, ForeignKey)):
                if admin_class:
                    admin_class_to_use = type(
                        f'DynamicReverseInlineModelAdmin_{admin_class.__name__}',
                        (admin_class, ReverseInlineModelAdmin),
                        {},
                    )
                else:
                    admin_class_to_use = ReverseInlineModelAdmin

                name = field.name
                parent = field.remote_field.model
                inline = admin_class_to_use(model,
                                            name,
                                            parent,
                                            admin_site,
                                            self.inline_type)
                if kwargs:
                    inline.__dict__.update(kwargs)
                inline_instances.append(inline)
                self.exclude.append(name)

        # These are the inline reverse instances for ReverseModelAdmin
        self.tmp_inline_instances = inline_instances

    def get_inline_instances(self, request, obj=None):
        own = list(filter(
            lambda inline: inline.has_view_or_change_permission(request, obj) or
            inline.has_add_permission(request, obj) or
            inline.has_delete_permission(request, obj), self.tmp_inline_instances))
        return own + super(ReverseModelAdmin, self).get_inline_instances(request, obj)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        return self._changeform_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        return self._changeform_view(request, None, form_url, extra_context)

    def _save_object(self, request, new_object, form, formsets, add):
        self.save_model(request, new_object, form, change=not add)
        self.save_related(request, form, formsets, change=not add)
        form.save_m2m()
        change_message = self.construct_change_message(request, form, formsets, add)
        if add:
            self.log_addition(request, new_object, change_message)
        else:
            self.log_change(request, new_object, change_message)

    def _changeform_view(self, request, object_id, form_url, extra_context):
        add = object_id is None

        model = self.model
        opts = model._meta

        if add:
            if not self.has_add_permission(request):
                raise PermissionDenied
            obj = None

        else:
            obj = self.get_object(request, unquote(object_id))

            if request.method == 'POST':
                if not self.has_change_permission(request, obj):
                    raise PermissionDenied
            else:
                if not self.has_view_or_change_permission(request, obj):
                    raise PermissionDenied

            if obj is None:
                return self._get_obj_does_not_exist_redirect(request, opts, object_id)

        formsets = []
        model_form = self.get_form(request, obj=obj, change=not add)
        if request.method == 'POST':
            form = model_form(request.POST, request.FILES, instance=obj)
            form_validated = form.is_valid()
            if form_validated:
                new_object = self.save_form(request, form, change=not add)
            else:
                new_object = form.instance
            formsets, _ = self._create_formsets(request, new_object, change=not add)
            formset_inline_tuples = zip(formsets, self.get_inline_instances(request))
            formset_inline_tuples = _remove_blank_reverse_inlines(new_object, formset_inline_tuples)
            formsets = [t[0] for t in formset_inline_tuples]
            if form_validated and not formsets:
                self._save_object(request, new_object, form, formsets, add)
                return self.response_add(request, new_object)
            elif form_validated and all_valid(formsets):
                # Here is the modified code.
                for formset, inline in formset_inline_tuples:
                    if not isinstance(inline, ReverseInlineModelAdmin):
                        continue
                    # The idea or this piece is coming from https://stackoverflow.com/questions/50910152/inline-formset-returns-empty-list-on-save.
                    # Without this, formset.save() was returning None for forms that
                    # haven't been modified
                    forms = [f for f in formset]
                    if not forms:
                        continue
                    obj = forms[0].save()
                    setattr(new_object, inline.parent_fk_name, obj)
                self._save_object(request, new_object, form, formsets, add)
                for formset in formsets:
                    self.save_formset(request, form, formset, change=not add)

                # self.log_addition(request, new_object)
                return self.response_add(request, new_object)
        else:
            # Prepare the dict of initial data from the request.
            # We have to special-case M2Ms as a list of comma-separated PKs.
            initial = dict(request.GET.items())
            for k in initial:
                try:
                    f = opts.get_field(k)
                except FieldDoesNotExist:
                    continue
                if isinstance(f, models.ManyToManyField):
                    initial[k] = initial[k].split(",")
            if add:
                form = model_form(initial=initial)
                prefixes = {}
                for FormSet, inline in self.get_formsets_with_inlines(request):
                    prefix = FormSet.get_default_prefix()
                    prefixes[prefix] = prefixes.get(prefix, 0) + 1
                    if prefixes[prefix] != 1:
                        prefix = "{prefix}-{prefixes[prefix]}"
                    formset = FormSet(instance=self.model(), prefix=prefix)
                    formsets.append(formset)
            else:
                form = model_form(instance=obj)
                formsets, _ = self._create_formsets(request, obj, change=True)

        if not add and not self.has_change_permission(request, obj):
            readonly_fields = flatten_fieldsets(
                self.get_fieldsets(request, obj))
        else:
            readonly_fields = self.get_readonly_fields(request, obj)

        adminForm = helpers.AdminForm(form,
                                      list(self.get_fieldsets(request)),
                                      self.prepopulated_fields,
                                      readonly_fields=readonly_fields,
                                      model_admin=self
                                      )
        media = self.media + adminForm.media

        inline_admin_formsets = self.get_inline_formsets(request, formsets, self.get_inline_instances(request), obj)
        for inline_formset in inline_admin_formsets:
            media = media + inline_formset.media

        # Inherit the default context from admin_site
        context = self.admin_site.each_context(request)
        reverse_admin_context = {
            'title': ('Change %s', 'Add %s')[add] % force_str(opts.verbose_name),
            'adminform': adminForm,
            # 'is_popup': '_popup' in request.REQUEST,
            'is_popup': False,
            'object_id': object_id,
            'original': obj,
            'media': mark_safe(media),
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            # 'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
        }
        context.update(reverse_admin_context)
        context.update(extra_context or {})
        return self.render_change_form(request, context, form_url=form_url,
                                       add=add,
                                       change=not add,
                                       obj=obj,
                                       )
