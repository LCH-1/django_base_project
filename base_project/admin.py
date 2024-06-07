from functools import partial

from django.contrib import admin
from django.contrib.admin import helpers, StackedInline, display
from django.contrib.admin.options import InlineModelAdmin
from django.contrib.admin.utils import flatten_fieldsets, unquote
from django.contrib.admin.options import get_content_type_for_model
from django.db.models import OneToOneField, ForeignKey
from django.forms import ModelForm
from django.forms.formsets import all_valid
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.urls import reverse
from django.utils.html import format_html
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe
from django.core.exceptions import PermissionDenied, FieldDoesNotExist

from adminsortable2.admin import SortableAdminMixin as BaseSortableAdminMixin
from adminsortable2.admin import SortableTabularInline, SortableInlineAdminMixin

from base_project import models
from base_project.utils import get_client_ip
from base_project.forms import OrderForm


class LogMixin:
    def __init__(self, model, admin_site):
        self.origin_obj = None
        super().__init__(model, admin_site)

    def save_model(self, request, obj, form, change):
        if change:
            self.origin_obj = obj.__class__.objects.get(pk=obj.pk)
        return super().save_model(request, obj, form, change)

    def log_addition(self, request, obj, message):
        adds = []

        for field in obj._meta.fields:
            adds.append(f"{field.name}: {getattr(obj, field.name)}")

        message = "\n".join(adds)

        return super().log_addition(request, obj, message)

    def log_change(self, request, obj, message):
        original_object = self.origin_obj

        if not original_object:
            return super().log_change(request, obj, message)

        changes = [f"ip : {get_client_ip(request)}\n"]

        for field in obj._meta.fields:
            if getattr(original_object, field.name) != getattr(obj, field.name):
                changes.append(f"{field.name}: {getattr(original_object, field.name)} -> {getattr(obj, field.name)}")

        message = "\n".join(changes)

        return super().log_change(request, obj, message)


class DefaultOrderingAdminMixin:
    ordering = ['-pk']


class OrderInlineMixin:
    # form = OrderForm
    ordering = ['order', 'pk']

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'order':
            field.widget.attrs['style'] = 'width: 60px;'
        return field


class SortableAdminMixin(BaseSortableAdminMixin):
    # form = OrderForm
    ordering = ['order', 'pk']

    def get_form(self, request, obj=None, **kwargs):
        if not getattr(self.form, "is_order_form", None):
            self.form = type(self.form.__name__, (OrderForm, self.form), {})

        return super().get_form(request, obj, **kwargs)

    def get_fields(self, request, obj=None):
        return super(BaseSortableAdminMixin, self).get_fields(request, obj)

    def save_model(self, request, obj, form, change):
        return super(BaseSortableAdminMixin, self).save_model(request, obj, form, change)

    def delete_queryset(self, request, queryset):
        for i, obj in enumerate(queryset):
            obj.delete(idx=i)

    def get_ordering(self, request):
        return self.ordering


class DynamicOrderInheritanceMixin:
    def __init__(self, *args, model, class_, **kwargs):
        class_obj = self.set_inherit_class(model, class_)
        super(*class_obj).__init__(*args, **kwargs)

    def set_inherit_class(self, model, class_):
        if not issubclass(model, models.OrderModelMixin) or issubclass(self.__class__, class_):
            return []

        class_name = self.__class__.__name__
        new_bases = (class_, self.__class__)
        new_class = type(class_name, new_bases, {"ordering": ['order', 'pk']})
        self.__class__ = new_class

        return [new_class, self]


class DynamicOrderInheritanceAdminMixin(DynamicOrderInheritanceMixin):
    def __init__(self, model, admin_site):
        # new_class = self.set_inherit_class(model, SortableAdminMixin)

        super().__init__(model, admin_site, model=model, class_=SortableAdminMixin)


class DynamicOrderInheritanceInlineMixin(DynamicOrderInheritanceMixin):
    def __init__(self, parent_model, admin_site):
        # new_class = self.set_inherit_class(self.model, SortableInlineAdminMixin)

        super().__init__(parent_model, admin_site, model=self.model, class_=SortableInlineAdminMixin)


class ReadOnlyMixin:
    """

    model을 admin에서 수정할 수 없도록 함
    """
    set_all_fields_readonly = True

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class ReadOnlyInlineMixin(ReadOnlyMixin):
    """
    Inline model을 admin에서 수정할 수 없도록 함
    """
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
    """
    admin에 기본적으로 사용되는 mixin
    """

    disable_auto_readonly_fields = False
    disable_ordering_fields = False
    disable_setup_fields = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fields = []

    def _get_related_link(self, obj, str_field=None, verbose=None):
        """
        admin 페이지에서 보여지는 field에 fk, m2m, o2o 관계를 가진 model의 링크를 생성
        """
        app_label = obj._meta.app_label
        model_name = obj._meta.model_name
        verbose = verbose or (getattr(obj, str_field, "-") if str_field else str(obj))

        link = reverse(f"admin:{app_label}_{model_name}_change", args=[obj.pk,])
        return format_html(f'<a href="{link}">{verbose}</a>')

    def get_inlines(self, request, obj):
        """
        데이터 생성 시 readonly로 지정된 mixin을 작성할 수 없도록 함
        """
        if not obj:
            inlines = super().get_inlines(request, obj)
            return [x for x in inlines if not issubclass(x, ReadOnlyInlineMixin)]

        return super().get_inlines(request, obj)

    def get_fields(self, request, obj=None):
        """
        admin 페이지에서 보여지는 field의 순서를 models.py에 정의된 순서대로 변경
        """
        fields = super().get_fields(request, obj)

        if not self.fields and not self.disable_ordering_fields:
            model_fields = self.model._meta.fields
            orderd_fields = [name for x in model_fields if (name := x.name) in fields]
            remain_fields = [x for x in fields if x not in orderd_fields]
            fields = orderd_fields + remain_fields

        return fields

    def add_view(self, request, form_url="", extra_context=None):
        """
        특정 상황에서 admin add 페이지에서 pk가 추가되는 문제 방지
        """
        fields = self.get_fields(request)

        if not self.disable_setup_fields:
            model = self.model
            model_pk_name = model._meta.pk.name
            model_fields = model._meta.fields
            model_field_names = [name for x in model_fields if (name := x.name) not in ["pk", model_pk_name]]
            self.fields = [x for x in fields if x in model_field_names]

        return self.changeform_view(request, None, form_url, extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        """
        get_readonly_fields에서 사용될 _fields 저장
        """
        obj = self.get_object(request, unquote(object_id))
        self._fields = flatten_fieldsets(self.get_fieldsets(request, obj))
        return self.changeform_view(request, object_id, form_url, extra_context)

    def get_readonly_fields(self, request, obj=None):
        """
        ModelAdmin에서 model field에 존재하지 않는 field를 추가해서 사용할 경우
        자동으로 read_only_fields하여 에러가 발생하는 것을 방지
        """
        if not obj:
            return super().get_readonly_fields(request, obj)

        readonly_fields = list(super().get_readonly_fields(request, obj))

        if not self.disable_auto_readonly_fields:
            model_fields = self.model._meta.fields
            model_mtm_fields = self.model._meta.many_to_many
            model_field_names = [field.name for field in model_fields]
            model_field_names += [field.name for field in model_mtm_fields]

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
    """
    admin 페이지에서 record를 하나만 생성할 수 있도록 함
    """

    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False

        return super().has_add_permission(request)


class AdminSite(admin.AdminSite):
    """
    admin 페이지에서 보여지는 model 순서 변겅
     - 기존 : a~z
     - 변경 : admin.site.register()에 등록된 순서
    """

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
        app_list = list(app_dict.values())

        for app in app_list:
            app['models'].sort(key=lambda x: self._registry_order.index(x['model']))

        # app_list.append({
        #     "name": "",
        #     "app_label": "",
        #     "app_url": "",
        #     "models": [
        #         {"admin_url": "",
        #          "name": "", },
        #     ],
        # })

        return app_list


site = AdminSite()
