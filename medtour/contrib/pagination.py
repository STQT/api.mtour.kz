import random

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class TourStandardResultsSetPagination(PageNumberPagination):
    page_size = 9
    max_page_size = 9

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'count': {
                    'type': 'integer',
                    'example': 123,
                },
                'next': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'example': 'https://mtour.kz/v1/tours/?{page_query_param}=4'.format(
                        page_query_param=self.page_query_param)
                },
                'previous': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'example': 'https://mtour.kz/v1/tours/?{page_query_param}=2'.format(
                        page_query_param=self.page_query_param)
                },
                'results': schema,
                'result_id': {
                    'type': 'string',
                    'nullable': False,
                    'format': 'string',
                    'example': '7074ed94-b4c4-4a15-aac2-5288f1ee96b3'
                }
            },
        }


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 10
