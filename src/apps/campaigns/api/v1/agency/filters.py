import django_filters
from datetime import datetime, time
from django.utils import timezone

from models.models import Campaign


class CampaignFilter(django_filters.FilterSet):
    created_after = django_filters.DateFilter(method='filter_created_after')
    created_before = django_filters.DateFilter(method='filter_created_before')

    def filter_created_after(self, queryset, name, value):
        dt = datetime.combine(value, time.min)
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.utc)
        return queryset.filter(created_at__gte=dt)

    def filter_created_before(self, queryset, name, value):
        dt = datetime.combine(value, time.max)
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.utc)
        return queryset.filter(created_at__lte=dt)

    class Meta:
        model = Campaign
        fields = ['created_after', 'created_before']
