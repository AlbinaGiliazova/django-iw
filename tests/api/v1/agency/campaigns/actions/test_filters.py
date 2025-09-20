from datetime import datetime, timedelta

import pytest
import pytz
from django.urls import reverse

from apps.campaigns.api.v1.agency.filters import CampaignFilter
from models.models import Campaign

try:
    from freezegun import freeze_time
except ImportError:
    freeze_time = None


@pytest.mark.django_db
def test_created_before_after_filters(as_anon):
    base_date = datetime(2023, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)

    if freeze_time:
        with freeze_time(base_date):
            Campaign.objects.create(name="first")
        with freeze_time(base_date + timedelta(days=1)):
            Campaign.objects.create(name="second")
        with freeze_time(base_date + timedelta(days=2)):
            Campaign.objects.create(name="third")
    else:
        Campaign.objects.create(name="first", created_at=base_date)
        Campaign.objects.create(name="second", created_at=base_date + timedelta(days=1))
        Campaign.objects.create(name="third", created_at=base_date + timedelta(days=2))

    url = reverse("campaign-list")

    response = as_anon.get(url, {"created_before": "2023-01-02"})
    names = {c["name"] for c in response["results"]}
    assert names == {"first", "second"}

    response = as_anon.get(url, {"created_after": "2023-01-01"})
    names = {c["name"] for c in response["results"]}
    assert names == {"first", "second", "third"}

    # created_after=2023-01-02T12:00:00  включает second+third
    response = as_anon.get(url, {"created_after": "2023-01-02"})
    names = {c["name"] for c in response["results"]}
    assert names == {"second", "third"}


# Тест на комбинацию фильтров
@pytest.mark.django_db
def test_created_filters_combined(as_anon):
    base_date = datetime(2023, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)

    if freeze_time:
        with freeze_time(base_date):
            Campaign.objects.create(name="first")
        with freeze_time(base_date + timedelta(days=1)):
            Campaign.objects.create(name="second")
        with freeze_time(base_date + timedelta(days=2)):
            Campaign.objects.create(name="third")
    else:
        Campaign.objects.create(name="first", created_at=base_date)
        Campaign.objects.create(name="second", created_at=base_date + timedelta(days=1))
        Campaign.objects.create(name="third", created_at=base_date + timedelta(days=2))

    url = reverse("campaign-list")

    query = {
        "created_after": "2023-01-01",
        "created_before": "2023-01-02",
    }
    response = as_anon.get(url, query)
    names = {c["name"] for c in response["results"]}
    assert names == {"first", "second"}


@pytest.fixture
def campaigns(db):  # noqa: ARG001
    camp1 = Campaign.objects.create(name="Campaign 1")
    camp2 = Campaign.objects.create(name="Campaign 2")
    camp3 = Campaign.objects.create(name="Campaign 3")
    return camp1, camp2, camp3


@pytest.mark.django_db
def test_ids_filter_single(campaigns):
    camp1, _, _ = campaigns
    data = {"ids": f"{camp1.id}"}
    queryset = Campaign.objects.all()
    filtered = CampaignFilter(data=data, queryset=queryset)
    result_ids = list(filtered.qs.values_list("id", flat=True))
    assert result_ids == [camp1.id]


@pytest.mark.django_db
def test_ids_filter_multiple(campaigns):
    camp1, _, camp3 = campaigns
    data = {"ids": f"{camp1.id},{camp3.id}"}
    queryset = Campaign.objects.all()
    filtered = CampaignFilter(data=data, queryset=queryset)
    result_ids = sorted(filtered.qs.values_list("id", flat=True))
    assert result_ids == sorted([camp1.id, camp3.id])


@pytest.mark.django_db
def test_ids_filter_no_match():
    data = {"ids": "999999"}
    queryset = Campaign.objects.all()
    filtered = CampaignFilter(data=data, queryset=queryset)
    assert list(filtered.qs) == []


@pytest.mark.django_db
def test_filter_by_ids_single(as_anon, campaigns):
    camp1, _, _ = campaigns
    url = reverse("campaign-list")
    response = as_anon.get(url, {"ids": str(camp1.id)})
    returned_ids = {c["id"] for c in response["results"]}
    assert returned_ids == {camp1.id}


@pytest.mark.django_db
def test_filter_by_ids_multiple(as_anon, campaigns):
    camp1, _, camp3 = campaigns
    url = reverse("campaign-list")
    ids = f"{camp1.id},{camp3.id}"
    response = as_anon.get(url, {"ids": ids})
    returned_ids = {c["id"] for c in response["results"]}
    assert returned_ids == {camp1.id, camp3.id}


@pytest.mark.django_db
def test_filter_by_ids_no_match(as_anon):
    url = reverse("campaign-list")
    response = as_anon.get(url, {"ids": "999999"})
    assert len(response["results"]) == 0
