import django_filters

from models.models import Campaign


class CampaignFilter(django_filters.FilterSet):
    created_after = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Campaign
        fields = ["created_after", "created_before"]
