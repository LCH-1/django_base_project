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

model을 admin에서 수정할 수 없도록 함

<a id="admin.ReadonlyInlineMixin"></a>

## ReadonlyInlineMixin Objects

```python
class ReadonlyInlineMixin(ReadonlyMixin)
```

Inline model을 admin에서 수정할 수 없도록 함

<a id="admin.AdminMixin"></a>

## AdminMixin Objects

```python
class AdminMixin()
```

admin에 기본적으로 사용되는 mixin

<a id="admin.AdminMixin.get_inlines"></a>

#### get\_inlines

```python
def get_inlines(request, obj)
```

데이터 생성 시 readonly로 지정된 mixin을 작성할 수 없도록 함

<a id="admin.AdminMixin.get_fields"></a>

#### get\_fields

```python
def get_fields(request, obj=None)
```

admin 페이지에서 보여지는 field의 순서를 models.py에 정의된 순서대로 변경

<a id="admin.AdminMixin.add_view"></a>

#### add\_view

```python
def add_view(request, form_url="", extra_context=None)
```

특정 상황에서 admin add 페이지에서 pk가 추가되는 문제 방지

<a id="admin.AdminMixin.change_view"></a>

#### change\_view

```python
def change_view(request, object_id, form_url="", extra_context=None)
```

get_readonly_fields에서 사용될 _fields 저장

<a id="admin.AdminMixin.get_readonly_fields"></a>

#### get\_readonly\_fields

```python
def get_readonly_fields(request, obj=None)
```

ModelAdmin에서 model field에 존재하지 않는 field를 추가해서 사용할 경우
자동으로 read_only_fields하여 에러가 발생하는 것을 방지

<a id="admin.SingletonModelAdmin"></a>

## SingletonModelAdmin Objects

```python
class SingletonModelAdmin(ModelAdmin)
```

admin 페이지에서 record를 하나만 생성할 수 있도록 함

<a id="admin.AdminSite"></a>

## AdminSite Objects

```python
class AdminSite(admin.AdminSite)
```

admin 페이지에서 보여지는 model 순서 변겅
- 기존 : a~z
- 변경 : admin.site.register()에 등록된 순서

<a id="decorators"></a>

# decorators

<a id="decorators.caching_view"></a>

#### caching\_view

```python
def caching_view(caching_request_data=True, alias=None)
```

view에 들어오는 동일한 요청에 대해 응답을 캐싱하는 데코레이터

**Arguments**:

- `caching_request_data` _bool, optional_ - request.GET의 parameter를 캐싱 키에 포함할지 여부. Defaults to True.
- `alias` _str, optional_ - 캐싱 키를 직접 지정할 경우 사용. Defaults to None.
  

**Example**:

  class UserViewSet(viewsets.ModelViewSet):<br>
　　...<br>
　　@caching_view(alias="${some alias}", caching_request_data=False)<br>
　　@action(detail=False, methods=["GET"])<br>
　　def some_function(self, request):<br>
　　　　...<br>

<a id="fields"></a>

# fields

<a id="fields.DefaultErrorMessageMixin"></a>

## DefaultErrorMessageMixin Objects

```python
class DefaultErrorMessageMixin()
```

rest framework에서 사용되는 error message에
field의 verbose_name, capital_verbose_name, 한글 조사 추가 지원

<a id="logger"></a>

# logger

<a id="logger.DefaultLogHandler"></a>

## DefaultLogHandler Objects

```python
class DefaultLogHandler(RichHandler)
```

기본적으로 사용되는 핸들러

<a id="logger.ConsoleLogHandler"></a>

## ConsoleLogHandler Objects

```python
class ConsoleLogHandler(RichHandler)
```

콘솔에 로그를 출력하는 핸들러

<a id="logger.NoOutputLogHandler"></a>

## NoOutputLogHandler Objects

```python
class NoOutputLogHandler(RichHandler)
```

로그를 출력하지 않는 핸들러

<a id="logger.TimedRotatingFileHandler"></a>

## TimedRotatingFileHandler Objects

```python
class TimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler)
```

로그 파일을 날짜별로 생성하는 핸들러

<a id="logger.LogFileHandler"></a>

## LogFileHandler Objects

```python
class LogFileHandler(RichHandler)
```

파일에 로그를 출력하는 핸들러

<a id="logger.CustomLogger"></a>

## CustomLogger Objects

```python
class CustomLogger(logging.Logger)
```

로그를 로그 출력 시 pretty format 적용

<a id="logger.DefaultFormatter"></a>

## DefaultFormatter Objects

```python
class DefaultFormatter(logging.Formatter)
```

logging에 user 정보를 추가하는 formatter

<a id="logger.ConsoleFormatter"></a>

## ConsoleFormatter Objects

```python
class ConsoleFormatter(DefaultFormatter)
```

console에 출력하는 log의 color style 설정

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

user info를 logging 하기 위해 사용

<a id="models"></a>

# models

<a id="models.Model"></a>

## Model Objects

```python
class Model(models.Model)
```

__str__이 작성되지 않은 경우 raise
default ordering을 -pk로 설정

<a id="models.SingletonManager"></a>

## SingletonManager Objects

```python
class SingletonManager(models.Manager)
```

singleton model의 객체를 반환하고 없는 경우 None을 반환

<a id="models.SingletonModel"></a>

## SingletonModel Objects

```python
class SingletonModel(Model)
```

record를 한개 이상 생성하지 못하도록 하는 모델

<a id="models.CheckVerboseNameAttributeMixin"></a>

## CheckVerboseNameAttributeMixin Objects

```python
class CheckVerboseNameAttributeMixin()
```

필드에 verbose_name이 정의되어 있는지 체크하는 mixin

<a id="models.CheckRelatedNameAttributeMixin"></a>

## CheckRelatedNameAttributeMixin Objects

```python
class CheckRelatedNameAttributeMixin()
```

외래 키 필드에 related_name이 정의되어 있는지 체크하는 mixin

<a id="models.FileField"></a>

## FileField Objects

```python
class FileField(CheckVerboseNameAttributeMixin, models.FileField)
```

기존 FileField에서 확장자, 용량 관련 옵션 추가
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

pagination 양식 정의
get_pagination_class 함수를 통해 동적으로 page_size를 설정하여 사용

<a id="parsers"></a>

# parsers

<a id="parsers.RemoveEmptyValueMixin"></a>

## RemoveEmptyValueMixin Objects

```python
class RemoveEmptyValueMixin()
```

Json, Form parser의 empty value 제거 mixin

<a id="parsers.RemoveEmptyValueMultiPartParser"></a>

## RemoveEmptyValueMultiPartParser Objects

```python
class RemoveEmptyValueMultiPartParser(MultiPartParser)
```

MultiPartParser의 empty value 제거

<a id="permissions"></a>

# permissions

<a id="permissions.check_login"></a>

#### check\_login

```python
def check_login(*args, **kwargs)
```

사용자의 로그인 여부를 체크하는 decorator
kwargs:
safe_methods(optional): 권한에 상관 없이 허용할 http method 지정

<a id="permissions.IsAuthenticated"></a>

## IsAuthenticated Objects

```python
class IsAuthenticated(BasePermission)
```

로그인 한 사용자만 사용 가능

<a id="permissions.IsAuthenticatedOrCreateOnly"></a>

## IsAuthenticatedOrCreateOnly Objects

```python
class IsAuthenticatedOrCreateOnly(BasePermission)
```

로그인 한 사용자가 아니라면 생성만 가능

<a id="permissions.IsAdminUser"></a>

## IsAdminUser Objects

```python
class IsAdminUser(BasePermission)
```

admin 사용자만 접근 가능

<a id="routers"></a>

# routers

<a id="routers.UserRouter"></a>

## UserRouter Objects

```python
class UserRouter(DefaultRouter)
```

UserViewSet을 위한 router
사용자 정보(retrieve) 조회 시 request.user를 사용, pk 불필요

<a id="routers.CustomActionUrlRouter"></a>

## CustomActionUrlRouter Objects

```python
class CustomActionUrlRouter(DefaultRouter)
```

action(detail=True)로 설정 시 url 구조 변경
기본 url 구조
- \${pk}/${action_url}/
수정된 url 구조
- \${action_url}/${pk(optional)}/

<a id="serializers"></a>

# serializers

<a id="serializers.ResponseErrorSerializerMixin"></a>

## ResponseErrorSerializerMixin Objects

```python
class ResponseErrorSerializerMixin()
```

error response 시 list가 아닌 string 형태로 반환

<a id="serializers.ModelSerializer"></a>

## ModelSerializer Objects

```python
class ModelSerializer(ResponseErrorSerializerMixin,
                      serializers.ModelSerializer)
```

default error message 및 커스텀 옵션들을 적용하기 위해 serializer field mapping 재정의

<a id="utils"></a>

# utils

<a id="utils.FilenameObfusecate"></a>

## FilenameObfusecate Objects

```python
@deconstructible
class FilenameObfusecate()
```

filefield에 업로드 되는 파일의 파일명을 무작위로 변경할 때 사용

<a id="utils.get_cached_list"></a>

#### get\_cached\_list

```python
def get_cached_list(view_info)
```

특정 view의 캐싱 목록 확인

<a id="utils.clear_cached_view"></a>

#### clear\_cached\_view

```python
def clear_cached_view(view_info)
```

특정 view의 캐싱 데이터 삭제

<a id="utils.clear_all_cache"></a>

#### clear\_all\_cache

```python
def clear_all_cache()
```

모든 캐싱 데이터 삭제

<a id="utils.get_client_ip"></a>

#### get\_client\_ip

```python
def get_client_ip(request)
```

사용자 ip 주소 반환

<a id="views"></a>

# views

<a id="views.static_serve"></a>

#### static\_serve

```python
async def static_serve(request, path, insecure=False, **kwargs)
```

async용 static_server 함수 재정의

<a id="views.static_view"></a>

#### static\_view

```python
async def static_view(request, path, document_root=None, show_indexes=False)
```

async용 static_view 함수 재정의

<a id="views.list_to_string_exception_handler"></a>

#### list\_to\_string\_exception\_handler

```python
def list_to_string_exception_handler(exc, context)
```

list 형태의 exception info를 string으로 변환

<a id="viewsets"></a>

# viewsets

<a id="viewsets.SearchQuerysetMixin"></a>

## SearchQuerysetMixin Objects

```python
class SearchQuerysetMixin()
```

searches를 통해 url query parameter에서 검색에 사용될 키워드와 필드를 지정할 수 있습니다.<br>
아래 예시의 경우 ?category=main&search=keyword와 같은 요청에 대해<br>
각각 category, title/contents 필드에 대해 queryset filter를 적용합니다.<br>
type(optional) : 검색에 사용될 필드에 대해 lookup을 지정할 수 있으며, 지정하지 않을 경우 일치하는 항목을 검색합니다.<br>

**Example**:

　searches = {<br>
　　'category': {<br>
　　　'fields': ['category'],<br>
　　}<br>
　　'search': {<br>
　　　'fields': ['title', 'contents'],<br>
　　　'type': 'icontains'<br>
　　},<br>
　}<br>

