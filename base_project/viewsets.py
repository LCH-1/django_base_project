from django.core.exceptions import FieldError
from django.db.models import Q

from rest_framework import viewsets
from rest_framework.viewsets import mixins

from base_project.logger import logger


class SearchQuerysetMixin:
    """
    searches를 통해 url query parameter에서 검색에 사용될 키워드와 필드를 지정할 수 있습니다.
    아래 예시의 경우 ?category=main&search=keyword와 같은 요청에 대해
    각각 category, title/contents 필드에 대해 queryset filter를 적용합니다.
    type(optional) : 검색에 사용될 필드에 대해 lookup을 지정할 수 있으며, 지정하지 않을 경우 일치하는 항목을 검색합니다.

    Example:
      searches = {
          'category': {
              'fields': ['category'],
          }
          'search': {
              'fields': ['title', 'contents'],
              'type': 'icontains'
          },
      }
    """
    searches = {}

    def get_queryset(self):
        queryset = super().get_queryset()

        if not (searches := self.searches):
            return queryset

        query_params = self.request.query_params
        q = Q()

        for param, value in query_params.items():
            if param not in searches:
                continue

            q_ = Q()

            fields = searches[param]["fields"]
            type_ = searches[param].get("type")
            for field in fields:
                if type_:
                    lookup = f"{field}__{type_}"
                else:
                    lookup = field

                q_ |= Q(**{lookup: value})

            q &= q_

        try:
            queryset = queryset.filter(q)
        except FieldError as e:
            logger.error(f"Queryset filter error : {e}")

        return queryset


class GenericViewSet(SearchQuerysetMixin, viewsets.GenericViewSet):
    pass


class ReadOnlyModelViewSet(SearchQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    pass


class ModelViewSet(SearchQuerysetMixin, viewsets.ModelViewSet):
    pass
