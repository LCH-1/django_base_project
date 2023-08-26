# django base project<br>
새로운 장고 프로젝트를 시작할 때 기반으로 사용 하기 위한 프로젝트 <br><br>

## 기능
* ## fields.py
  * **FileField** : serializer를 통해 직렬화 될 때 파일의 url의 형태를 다르게 지정합니다.

* ## middleware.py
  * **RequestLogMiddleware** : Client 요청이 들어왔을 때 `request body, user info, content type` 등의 정보를 출력해 디버깅을 용이하게 합니다.
  * **ResponseFormattingMiddleware** : django의 error response 포맷을 `{"error": "message"}`로 통일시킵니다.

* ## models.py
  * **Model** : `__str__`을 설정하지 않을 경우 linting 에러를 발생시키며, pk를 기본 ordering으로 설정합니다.
  * **CheckVerboseNameAttributeMixin** : `verbose_name` 옵션이 존재하지 않을 경우 에러를 발생시킵니다.
  * **CheckRelatedNameAttributeMixin** : `related_name` 옵션이 존재하지 않을 경우 에러를 발생시킵니다.
  * **FileField** : `upload_to` 옵션을 사용하지 않으며 기본 업로드 경로를 `MEDIA_URL/${model_name}/${field_name}` 으로 설정합니다. <br>
  protected 옵션을 지원합니다. `protected=True` 옵션이 존재할 경우 해당 파일은 권한이 있는 사용자만 접근할 수 있습니다. <br>
  protected 설정을 할 경우 해당 모델에 `has_${field_name}_permission` 메소드를 생성해 권한을 지정해야 합니다.

* ## logger.py
  * rich 라이브러리를 사용해 더 가독성 좋은 형태로 logging 해주며, console logging과 함께 별도의 파일에도 로그 데이터를 쌓습니다.

* ## pagination.py
  * **PageNumberPagination** : PageNumberPagination을 상속받으며, pagination에 필요한 정보들을 함께 리턴합니다.
  * **get_pagination_class** : pagi_size를 임의로 지정해 동적으로 PageNumberPagination를 생성합니다.

* ## permissions.py
  * **GenericAPIException** : `APIException`을 상속받아 status code를 유동적으로 변경할 수 있습니다.
  * **BasePermission** : `BasePermission`을 상속받아 default message를 유동적으로 변경할 수 있습니다.
  * **check_login** : class method의 decorator로 사용하며, 사용자의 로그인 여부를 판단합니다. `safe_methods`를 인자로 받아 특정 요청에 대해서는 login check를 pass합니다.

* ## router.py
  * **CustomRouter** : `DefaultRouter`를 상속받아 viewsets의 router를 지정할 때 url 구조를 변경시킨 router입니다. 로그인 한 사용자 본인의 데이터를 다룰 때와 같이 model의 pk를 지정하지 않고 CRUD를 다룰 때 사용됩니다.
  
* ## serializers.py
  * **ModelSerializer** : ModelSerializer를 상속받으며, error message를 기본적으로 설정해줍니다.
  * **WritableSerializerMethodField** : SerializerMethodField를 상속받으며, 기본적으로 read_only 속성으로만 사용 가능한 것과는 다르게 read/write 모두 가능합니다.
  * **PrimaryKeyRelatedWriteField** : PrimaryKeyRelatedField를 상속받으며, model에서 fk 혹은 oto으로 정의된 필드의 id를 지정할 때 사용됩니다.

* ## validator.py
  * **PHONE_VALIDATOR** : 핸드폰번호의 유효성을 검증합니다.
