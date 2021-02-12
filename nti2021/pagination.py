from rest_framework.pagination import LimitOffsetPagination


class OurPagination(LimitOffsetPagination):
    max_limit = 200
