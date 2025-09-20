import pytest
from django.urls import reverse

from models.models import Campaign, Strategy


@pytest.fixture
def campaigns_with_strategies(db):
    camp1 = Campaign.objects.create(name="Alpha Promo")
    camp2 = Campaign.objects.create(name="Beta Launch")
    camp3 = Campaign.objects.create(name="Gamma")
    Strategy.objects.create(name="Red Strategy", campaign=camp2)
    Strategy.objects.create(name="Gamma Strat", campaign=camp3)
    return camp1, camp2, camp3


@pytest.mark.django_db
def test_filter_search_by_campaign_name(campaigns_with_strategies):
    camp1, camp2, camp3 = campaigns_with_strategies
    qs = Campaign.objects.search_by_campaign_or_strategy_name('alpha')
    assert camp1 in qs
    assert camp2 not in qs
    assert camp3 not in qs


@pytest.mark.django_db
def test_filter_search_by_strategy_name(campaigns_with_strategies):
    camp1, camp2, camp3 = campaigns_with_strategies
    qs = Campaign.objects.search_by_campaign_or_strategy_name('gamma strat')
    assert camp3 in qs
    assert camp1 not in qs
    assert camp2 not in qs


@pytest.mark.django_db
def test_filter_search_case_insensitive_and_strip(campaigns_with_strategies):
    camp1, camp2, camp3 = campaigns_with_strategies
    qs = Campaign.objects.search_by_campaign_or_strategy_name('  ALPHA Promo ')
    assert camp1 in qs
    assert camp2 not in qs
    assert camp3 not in qs


@pytest.mark.django_db
def test_filter_search_no_duplicates(campaigns_with_strategies, db):
    _, _, camp3 = campaigns_with_strategies
    qs = Campaign.objects.search_by_campaign_or_strategy_name("gamma")
    # В выдаче только один экземпляр кампании
    assert list(qs).count(camp3) == 1


@pytest.mark.django_db
def test_search_campaign_name(as_anon, campaigns_with_strategies):
    camp1, camp2, _ = campaigns_with_strategies
    url = reverse("campaign-list")
    response = as_anon.get(url, {"search": "alpha"})
    returned_ids = {c["id"] for c in response['results']}
    assert camp1.id in returned_ids
    assert camp2.id not in returned_ids

@pytest.mark.django_db
def test_search_strategy_name(as_anon, campaigns_with_strategies):
    camp1, _, camp3 = campaigns_with_strategies
    url = reverse("campaign-list")
    response = as_anon.get(url, {"search": "gamma strat"})
    returned_ids = {c["id"] for c in response['results']}
    assert camp3.id in returned_ids
    assert camp1.id not in returned_ids

@pytest.mark.django_db
def test_search_case_insensitive_and_strip(as_anon, campaigns_with_strategies):
    camp1, _, _ = campaigns_with_strategies
    url = reverse("campaign-list")
    response = as_anon.get(url, {"search": "  ALPHA promo "})
    returned_ids = {c["id"] for c in response['results']}
    assert camp1.id in returned_ids

@pytest.mark.django_db
def test_search_no_duplicates(as_anon, db):
    # Одна кампания с совпадением по имени и по имени стратегии
    _, _, camp3 = campaigns_with_strategies
    url = reverse("campaign-list")
    response = as_anon.get(url, {"search": "gamma"})
    returned_ids = [c["id"] for c in response['results']]
    # В ответе кампания только один раз
    assert returned_ids.count(camp3.id) == 1
