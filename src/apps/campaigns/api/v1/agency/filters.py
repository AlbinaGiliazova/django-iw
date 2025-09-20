from datetime import datetime, time

import django_filters
import pytz
from django.utils import timezone

from models.models import Campaign


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class CampaignFilter(django_filters.FilterSet):
    created_after = django_filters.DateFilter(method="filter_created_after")
    created_before = django_filters.DateFilter(method="filter_created_before")
    ids = NumberInFilter(field_name="id", lookup_expr="in")

    def filter_created_after(self, queryset, _, value):  # noqa: PLR6301
        dt = datetime.combine(value, time.min)
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, pytz.utc)
        return queryset.filter(created_at__gte=dt)

    def filter_created_before(self, queryset, _, value):  # noqa: PLR6301
        dt = datetime.combine(value, time.max)
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, pytz.utc)
        return queryset.filter(created_at__lte=dt)

    class Meta:
        model = Campaign
        fields = ["created_after", "created_before"]
