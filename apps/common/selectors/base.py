class BaseSelector:
    def __init__(self, queryset):
        self.queryset = queryset

class FilteringSelector(BaseSelector):
    def filter_by_kwargs(self, **kwargs):
        return self.queryset.filter(**kwargs)

class SearchSelector(BaseSelector):
    def search(self, query, fields):
        from django.db.models import Q
        q_objects = Q()
        for field in fields:
            q_objects |= Q(**{f"{field}__icontains": query})
        return self.queryset.filter(q_objects)

class OrderingSelector(BaseSelector):
    def order_by(self, field):
        return self.queryset.order_by(field)

class PaginationSelector(BaseSelector):
    def paginate(self, page, page_size):
        start = (page - 1) * page_size
        end = start + page_size
        return self.queryset[start:end]
