# Table of Contents

* [admin](#admin)
  * [ReadonlyMixin](#admin.ReadonlyMixin)
  * [ReadonlyInlineMixin](#admin.ReadonlyInlineMixin)
  * [AdminMixin](#admin.AdminMixin)
    * [get\_inlines](#admin.AdminMixin.get_inlines)
    * [get\_fields](#admin.AdminMixin.get_fields)
    * [add\_view](#admin.AdminMixin.add_view)
    * [change\_view](#admin.AdminMixin.change_view)
    * [get\_readonly\_fields](#admin.AdminMixin.get_readonly_fields)
  * [SingletonModelAdmin](#admin.SingletonModelAdmin)
  * [AdminSite](#admin.AdminSite)
* [decorators](#decorators)
  * [caching\_view](#decorators.caching_view)
* [fields](#fields)
  * [DefaultErrorMessageMixin](#fields.DefaultErrorMessageMixin)
* [logger](#logger)
  * [DefaultLogHandler](#logger.DefaultLogHandler)
  * [ConsoleLogHandler](#logger.ConsoleLogHandler)
  * [NoOutputLogHandler](#logger.NoOutputLogHandler)
  * [TimedRotatingFileHandler](#logger.TimedRotatingFileHandler)
  * [LogFileHandler](#logger.LogFileHandler)
  * [CustomLogger](#logger.CustomLogger)
  * [DefaultFormatter](#logger.DefaultFormatter)
  * [ConsoleFormatter](#logger.ConsoleFormatter)
* [middleware](#middleware)
  * [RequestLogMiddleware](#middleware.RequestLogMiddleware)
  * [LoggedInUserMiddleware](#middleware.LoggedInUserMiddleware)
* [models](#models)
  * [Model](#models.Model)
  * [SingletonManager](#models.SingletonManager)
  * [SingletonModel](#models.SingletonModel)
  * [CheckVerboseNameAttributeMixin](#models.CheckVerboseNameAttributeMixin)
  * [CheckRelatedNameAttributeMixin](#models.CheckRelatedNameAttributeMixin)
  * [FileField](#models.FileField)
* [pagination](#pagination)
  * [PageNumberPagination](#pagination.PageNumberPagination)
* [parsers](#parsers)
  * [RemoveEmptyValueMixin](#parsers.RemoveEmptyValueMixin)
  * [RemoveEmptyValueMultiPartParser](#parsers.RemoveEmptyValueMultiPartParser)
* [permissions](#permissions)
  * [check\_login](#permissions.check_login)
  * [IsAuthenticated](#permissions.IsAuthenticated)
  * [IsAuthenticatedOrCreateOnly](#permissions.IsAuthenticatedOrCreateOnly)
  * [IsAdminUser](#permissions.IsAdminUser)
* [routers](#routers)
  * [UserRouter](#routers.UserRouter)
  * [CustomActionUrlRouter](#routers.CustomActionUrlRouter)
* [serializers](#serializers)
  * [ResponseErrorSerializerMixin](#serializers.ResponseErrorSerializerMixin)
  * [ModelSerializer](#serializers.ModelSerializer)
* [utils](#utils)
  * [FilenameObfusecate](#utils.FilenameObfusecate)
  * [get\_cached\_list](#utils.get_cached_list)
  * [clear\_cached\_view](#utils.clear_cached_view)
  * [clear\_all\_cache](#utils.clear_all_cache)
  * [get\_client\_ip](#utils.get_client_ip)
* [views](#views)
  * [static\_serve](#views.static_serve)
  * [static\_view](#views.static_view)
  * [list\_to\_string\_exception\_handler](#views.list_to_string_exception_handler)
* [viewsets](#viewsets)
  * [SearchQuerysetMixin](#viewsets.SearchQuerysetMixin)

<a id="admin"></a>

# admin

<a id="admin.ReadonlyMixin"></a>

## ReadonlyMixin Objects

```python
class ReadonlyMixin()
```

model�� admin���� ������ �� ������ ��

<a id="admin.ReadonlyInlineMixin"></a>

## ReadonlyInlineMixin Objects

```python
class ReadonlyInlineMixin(ReadonlyMixin)
```

Inline model�� admin���� ������ �� ������ ��

<a id="admin.AdminMixin"></a>

## AdminMixin Objects

```python
class AdminMixin()
```

admin�� �⺻������ ���Ǵ� mixin

<a id="admin.AdminMixin.get_inlines"></a>

#### get\_inlines

```python
def get_inlines(request, obj)
```

������ ���� �� readonly�� ������ mixin�� �ۼ��� �� ������ ��

<a id="admin.AdminMixin.get_fields"></a>

#### get\_fields

```python
def get_fields(request, obj=None)
```

admin ���������� �������� field�� ������ models.py�� ���ǵ� ������� ����

<a id="admin.AdminMixin.add_view"></a>

#### add\_view

```python
def add_view(request, form_url="", extra_context=None)
```

Ư�� ��Ȳ���� admin add ���������� pk�� �߰��Ǵ� ���� ����

<a id="admin.AdminMixin.change_view"></a>

#### change\_view

```python
def change_view(request, object_id, form_url="", extra_context=None)
```

get_readonly_fields���� ���� _fields ����

<a id="admin.AdminMixin.get_readonly_fields"></a>

#### get\_readonly\_fields

```python
def get_readonly_fields(request, obj=None)
```

ModelAdmin���� model field�� �������� �ʴ� field�� �߰��ؼ� ����� ���
�ڵ����� read_only_fields�Ͽ� ������ �߻��ϴ� ���� ����

<a id="admin.SingletonModelAdmin"></a>

## SingletonModelAdmin Objects

```python
class SingletonModelAdmin(ModelAdmin)
```

admin ���������� record�� �ϳ��� ������ �� �ֵ��� ��

<a id="admin.AdminSite"></a>

## AdminSite Objects

```python
class AdminSite(admin.AdminSite)
```

admin ���������� �������� model ���� ����
- ���� : a~z
- ���� : admin.site.register()�� ��ϵ� ����

<a id="decorators"></a>

# decorators

<a id="decorators.caching_view"></a>

#### caching\_view

```python
def caching_view(caching_request_data=True, alias=None)
```

view�� ������ ������ ��û�� ���� ������ ĳ���ϴ� ���ڷ�����

**Arguments**:

- `caching_request_data` _bool, optional_ - request.GET�� parameter�� ĳ�� Ű�� �������� ����. Defaults to True.
- `alias` _str, optional_ - ĳ�� Ű�� ���� ������ ��� ���. Defaults to None.
  

**Example**:

  class UserViewSet(viewsets.ModelViewSet):<br>
����...<br>
����@caching_view(alias="${some alias}", caching_request_data=False)<br>
����@action(detail=False, methods=["GET"])<br>
����def some_function(self, request):<br>
��������...<br>

<a id="fields"></a>

# fields

<a id="fields.DefaultErrorMessageMixin"></a>

## DefaultErrorMessageMixin Objects

```python
class DefaultErrorMessageMixin()
```

rest framework���� ���Ǵ� error message��
field�� verbose_name, capital_verbose_name, �ѱ� ���� �߰� ����

<a id="logger"></a>

# logger

<a id="logger.DefaultLogHandler"></a>

## DefaultLogHandler Objects

```python
class DefaultLogHandler(RichHandler)
```

�⺻������ ���Ǵ� �ڵ鷯

<a id="logger.ConsoleLogHandler"></a>

## ConsoleLogHandler Objects

```python
class ConsoleLogHandler(RichHandler)
```

�ֿܼ� �α׸� ����ϴ� �ڵ鷯

<a id="logger.NoOutputLogHandler"></a>

## NoOutputLogHandler Objects

```python
class NoOutputLogHandler(RichHandler)
```

�α׸� ������� �ʴ� �ڵ鷯

<a id="logger.TimedRotatingFileHandler"></a>

## TimedRotatingFileHandler Objects

```python
class TimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler)
```

�α� ������ ��¥���� �����ϴ� �ڵ鷯

<a id="logger.LogFileHandler"></a>

## LogFileHandler Objects

```python
class LogFileHandler(RichHandler)
```

���Ͽ� �α׸� ����ϴ� �ڵ鷯

<a id="logger.CustomLogger"></a>

## CustomLogger Objects

```python
class CustomLogger(logging.Logger)
```

�α׸� �α� ��� �� pretty format ����

<a id="logger.DefaultFormatter"></a>

## DefaultFormatter Objects

```python
class DefaultFormatter(logging.Formatter)
```

logging�� user ������ �߰��ϴ� formatter

<a id="logger.ConsoleFormatter"></a>

## ConsoleFormatter Objects

```python
class ConsoleFormatter(DefaultFormatter)
```

console�� ����ϴ� log�� color style ����

<a id="middleware"></a>

# middleware

<a id="middleware.RequestLogMiddleware"></a>

## RequestLogMiddleware Objects

```python
class RequestLogMiddleware()
```

Request / Response logging

<a id="middleware.LoggedInUserMiddleware"></a>

## LoggedInUserMiddleware Objects

```python
class LoggedInUserMiddleware()
```

user info�� logging �ϱ� ���� ���

<a id="models"></a>

# models

<a id="models.Model"></a>

## Model Objects

```python
class Model(models.Model)
```

__str__�� �ۼ����� ���� ��� raise
default ordering�� -pk�� ����

<a id="models.SingletonManager"></a>

## SingletonManager Objects

```python
class SingletonManager(models.Manager)
```

singleton model�� ��ü�� ��ȯ�ϰ� ���� ��� None�� ��ȯ

<a id="models.SingletonModel"></a>

## SingletonModel Objects

```python
class SingletonModel(Model)
```

record�� �Ѱ� �̻� �������� ���ϵ��� �ϴ� ��

<a id="models.CheckVerboseNameAttributeMixin"></a>

## CheckVerboseNameAttributeMixin Objects

```python
class CheckVerboseNameAttributeMixin()
```

�ʵ忡 verbose_name�� ���ǵǾ� �ִ��� üũ�ϴ� mixin

<a id="models.CheckRelatedNameAttributeMixin"></a>

## CheckRelatedNameAttributeMixin Objects

```python
class CheckRelatedNameAttributeMixin()
```

�ܷ� Ű �ʵ忡 related_name�� ���ǵǾ� �ִ��� üũ�ϴ� mixin

<a id="models.FileField"></a>

## FileField Objects

```python
class FileField(CheckVerboseNameAttributeMixin, models.FileField)
```

���� FileField���� Ȯ����, �뷮 ���� �ɼ� �߰�
Kwargs:
allowed_content_types (bool, optional) - list containing allowed content_types.

**Example**:

  - ['pdf', 'png', 'jpg', 'jpeg']
  
  max_upload_size (bool, optional) - a number indicating the maximum file size allowed for upload.

**Examples**:

  - 1024 # 1kb
  - 10 * 1024 # 10kb
  - 10 * 1024 * 1024 # 10mb
  - 1kb
  - 10mb
  - 1g or 10g

<a id="pagination"></a>

# pagination

<a id="pagination.PageNumberPagination"></a>

## PageNumberPagination Objects

```python
class PageNumberPagination(pagination.PageNumberPagination)
```

pagination ��� ����
get_pagination_class �Լ��� ���� �������� page_size�� �����Ͽ� ���

<a id="parsers"></a>

# parsers

<a id="parsers.RemoveEmptyValueMixin"></a>

## RemoveEmptyValueMixin Objects

```python
class RemoveEmptyValueMixin()
```

Json, Form parser�� empty value ���� mixin

<a id="parsers.RemoveEmptyValueMultiPartParser"></a>

## RemoveEmptyValueMultiPartParser Objects

```python
class RemoveEmptyValueMultiPartParser(MultiPartParser)
```

MultiPartParser�� empty value ����

<a id="permissions"></a>

# permissions

<a id="permissions.check_login"></a>

#### check\_login

```python
def check_login(*args, **kwargs)
```

������� �α��� ���θ� üũ�ϴ� decorator
kwargs:
safe_methods(optional): ���ѿ� ��� ���� ����� http method ����

<a id="permissions.IsAuthenticated"></a>

## IsAuthenticated Objects

```python
class IsAuthenticated(BasePermission)
```

�α��� �� ����ڸ� ��� ����

<a id="permissions.IsAuthenticatedOrCreateOnly"></a>

## IsAuthenticatedOrCreateOnly Objects

```python
class IsAuthenticatedOrCreateOnly(BasePermission)
```

�α��� �� ����ڰ� �ƴ϶�� ������ ����

<a id="permissions.IsAdminUser"></a>

## IsAdminUser Objects

```python
class IsAdminUser(BasePermission)
```

admin ����ڸ� ���� ����

<a id="routers"></a>

# routers

<a id="routers.UserRouter"></a>

## UserRouter Objects

```python
class UserRouter(DefaultRouter)
```

UserViewSet�� ���� router
����� ����(retrieve) ��ȸ �� request.user�� ���, pk ���ʿ�

<a id="routers.CustomActionUrlRouter"></a>

## CustomActionUrlRouter Objects

```python
class CustomActionUrlRouter(DefaultRouter)
```

action(detail=True)�� ���� �� url ���� ����
�⺻ url ����
- \${pk}/${action_url}/
������ url ����
- \${action_url}/${pk(optional)}/

<a id="serializers"></a>

# serializers

<a id="serializers.ResponseErrorSerializerMixin"></a>

## ResponseErrorSerializerMixin Objects

```python
class ResponseErrorSerializerMixin()
```

error response �� list�� �ƴ� string ���·� ��ȯ

<a id="serializers.ModelSerializer"></a>

## ModelSerializer Objects

```python
class ModelSerializer(ResponseErrorSerializerMixin,
                      serializers.ModelSerializer)
```

default error message �� Ŀ���� �ɼǵ��� �����ϱ� ���� serializer field mapping ������

<a id="utils"></a>

# utils

<a id="utils.FilenameObfusecate"></a>

## FilenameObfusecate Objects

```python
@deconstructible
class FilenameObfusecate()
```

filefield�� ���ε� �Ǵ� ������ ���ϸ��� �������� ������ �� ���

<a id="utils.get_cached_list"></a>

#### get\_cached\_list

```python
def get_cached_list(view_info)
```

Ư�� view�� ĳ�� ��� Ȯ��

<a id="utils.clear_cached_view"></a>

#### clear\_cached\_view

```python
def clear_cached_view(view_info)
```

Ư�� view�� ĳ�� ������ ����

<a id="utils.clear_all_cache"></a>

#### clear\_all\_cache

```python
def clear_all_cache()
```

��� ĳ�� ������ ����

<a id="utils.get_client_ip"></a>

#### get\_client\_ip

```python
def get_client_ip(request)
```

����� ip �ּ� ��ȯ

<a id="views"></a>

# views

<a id="views.static_serve"></a>

#### static\_serve

```python
async def static_serve(request, path, insecure=False, **kwargs)
```

async�� static_server �Լ� ������

<a id="views.static_view"></a>

#### static\_view

```python
async def static_view(request, path, document_root=None, show_indexes=False)
```

async�� static_view �Լ� ������

<a id="views.list_to_string_exception_handler"></a>

#### list\_to\_string\_exception\_handler

```python
def list_to_string_exception_handler(exc, context)
```

list ������ exception info�� string���� ��ȯ

<a id="viewsets"></a>

# viewsets

<a id="viewsets.SearchQuerysetMixin"></a>

## SearchQuerysetMixin Objects

```python
class SearchQuerysetMixin()
```

searches�� ���� url query parameter���� �˻��� ���� Ű����� �ʵ带 ������ �� �ֽ��ϴ�.<br>
�Ʒ� ������ ��� ?category=main&search=keyword�� ���� ��û�� ����<br>
���� category, title/contents �ʵ忡 ���� queryset filter�� �����մϴ�.<br>
type(optional) : �˻��� ���� �ʵ忡 ���� lookup�� ������ �� ������, �������� ���� ��� ��ġ�ϴ� �׸��� �˻��մϴ�.<br>

**Example**:

��searches = {<br>
����'category': {<br>
������'fields': ['category'],<br>
����}<br>
����'search': {<br>
������'fields': ['title', 'contents'],<br>
������'type': 'icontains'<br>
����},<br>
��}<br>

