from django.db.models import Q

from core.models import TimestampedModel, models


class CampaignQuerySet(models.QuerySet):
    def search_by_campaign_or_strategy_name(self, value):
        value = value.strip()
        if not value:
            return self.none()
        return self.filter(Q(name__icontains=value) | Q(strategies__name__icontains=value)).distinct()


class Campaign(TimestampedModel):
    objects = CampaignQuerySet.as_manager()

    name = models.CharField(max_length=1024)

    class Meta:
        default_related_name = "campaigns"
