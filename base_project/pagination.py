from rest_framework import pagination
from rest_framework.response import Response
from functools import lru_cache


class PageNumberPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            "links": {
                "next": self.get_next_link(),
                "previous": self.get_previous_link()
            },
            "count": self.page.paginator.count,
            "page_count": self.page.paginator.num_pages,
            "page_number": self.page.number,
            "page_size": self.page.paginator.per_page,
            "results": data,
        })


@lru_cache
def get_pagination_class(page_size):
    return type('DynamicPageNumberPagination', (PageNumberPagination, ), {"page_size": page_size})
