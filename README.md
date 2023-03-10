# django base project<br>
새로운 장고 프로젝트를 시작할 때 기반으로 사용 하기 위한 프로젝트 <br><br>

## 기능
* ## middleware.py
  * **RequestLogMiddleware** : Client 요청이 들어왔을 때 request body, user info, content type 등을 출력해 디버깅을 용이하게 합니다.
  * **ResponseFormattingMiddleware** : django의 error response 포맷을 {"error": "message"}로 통일시킵니다.

* ## logger.py
  * rich 라이브러리를 사용해 더 가독성 좋은 형태로 logging 해주며, console logging과 함께 별도의 파일에도 로그 데이터를 쌓습니다.

* ## permission.py
  * **GenericAPIException** : APIException을 상속받아 status code를 유동적으로 변경할 수 있습니다.
  * **BasePermission** : BasePermission을 상속받아 default message를 유동적으로 변경할 수 있습니다.
  * **check_login** : class method의 decorator로 사용하며, 사용자의 로그인 여부를 판단합니다. safe_methods를 인자로 받아 특정 요청에 대해서는 login check를 pass합니다.

* ## router.py
  * **CustomRouter** : DefaultRouter를 상속받아 viewsets의 router를 지정할 때 url 구조를 변경시킨 router입니다. 로그인 한 사용자 본인의 데이터를 다룰 때와 같이 model의 pk를 지정하지 않고 CRUD를 다룰 때 사용됩니다.
  
* ## serializer.py
  * **WritableSerializerMethodField** : SerializerMethodField를 상속받으며, 기본적으로 read_only 속성으로만 사용 가능한 것과는 다르게 read/write 모두 가능합니다.
  * **PrimaryKeyRelatedWriteField** : PrimaryKeyRelatedField를 상속받으며, model에서 fk 혹은 oto으로 정의된 필드의 id를 지정할 때 사용됩니다.

* ## validator.py
  * **PHONE_VALIDATOR** : 핸드폰번호의 유효성을 검증합니다.

* ## pagination.py
  * **PageNumberPagination** : PageNumberPagination을 상속받으며, pagination에 필요한 정보들을 함께 리턴합니다.

* ## utils.py
  * **FilenameObfusecate** : 데이터 보호가 필요한 파일들을 위해 파일 명을 난독화 합니다.

  * **ends_with_jong** : 은/는, 을/를과 같이 한국어를 다룰 때 종성에 맞는 조사를 사용할 수 있도록 합니다.

  * **set_default_error_messages** : ModelSerializer의 extra_kwargs를 지정할 때 default error message를 설정합니다.<br>
    ```python
    class MySerializer(serializers.ModelSerializer):
      class Meta:
          model = MyModel
          fields = "__all__"

          extra_kwargs = {}
          set_default_error_messages(model, fields, extra_kwargs)
    ```
  
  * **get_select_related_fields** : queryset의 select_related에 사용 가능한 모든 필드들을 리턴합니다.<br>
  
  * **get_prefetch_related_fields** : queryset의 prefetch_related에 사용 가능한 모든 필드들을 리턴합니다.<br>
    ```python
    queryset = MyModel.objects.filter(query) \
            .select_related(*get_select_related_fields(MyModel)) \
            .prefetch_related(*get_prefetch_related_fields(MyModel))
    ```
    (TODO: 현재는 지정한 모델의 필드만 리턴하고 있지만, 필드들을 재귀적으로 탐색하며 related field들 또한 리턴하도록 추가 할 예정입니다.)
