import pytest
from django.urls import reverse
from datetime import datetime, timedelta
from core.models import Campaign

try:
    from freezegun import freeze_time
except ImportError:
    freeze_time = None

@pytest.mark.django_db
def test_created_before_after_filters(as_anon):
    base_date = datetime(2023, 1, 1, 12, 0, 0)

    # Создаем 3 кампании с разными датами
    if freeze_time:
        with freeze_time(base_date):
            campaign1 = Campaign.objects.create(name='first')
        with freeze_time(base_date + timedelta(days=1)):
            campaign2 = Campaign.objects.create(name='second')
        with freeze_time(base_date + timedelta(days=2)):
            campaign3 = Campaign.objects.create(name='third')
    else:
        campaign1 = Campaign.objects.create(
            name='first', created_at=base_date
        )
        campaign2 = Campaign.objects.create(
            name='second', created_at=base_date + timedelta(days=1)
        )
        campaign3 = Campaign.objects.create(
            name='third', created_at=base_date + timedelta(days=2)
        )

    url = reverse('campaign-list')

    # created_before=2023-01-02T12:00:00  включает кампании с датой <= указанной
    response = as_anon.get(
        url,
        {'created_before': '2023-01-02T12:00:00'}
    )
    assert response.status_code == 200
    names = {c['name'] for c in response.json()}
    assert names == {'first', 'second'}

    # created_after=2023-01-01T12:00:00 включает кампании c датой >= указанной
    response = as_anon.get(
        url,
        {'created_after': '2023-01-01T12:00:00'}
    )
    assert response.status_code == 200
    names = {c['name'] for c in response.json()}
    assert names == {'first', 'second', 'third'}

    # created_after=2023-01-02T12:00:00  включает second+third
    response = as_anon.get(
        url,
        {'created_after': '2023-01-02T12:00:00'}
    )
    assert response.status_code == 200
    names = {c['name'] for c in response.json()}
    assert names == {'second', 'third'}

# Тест на комбинацию фильтров
@pytest.mark.django_db
def test_created_filters_combined(as_anon):
    base_date = datetime(2023, 1, 1, 12, 0, 0)

    if freeze_time:
        with freeze_time(base_date):
            Campaign.objects.create(name='first')
        with freeze_time(base_date + timedelta(days=1)):
            Campaign.objects.create(name='second')
    with freeze_time(base_date + timedelta(days=2)):
            Campaign.objects.create(name='third')
    else:
        Campaign.objects.create(name='first', created_at=base_date)
        Campaign.objects.create(name='second', created_at=base_date + timedelta(days=1))
        Campaign.objects.create(name='third', created_at=base_date + timedelta(days=2))

    url = reverse('campaign-list')

    query = {
        'created_after': '2023-01-01T12:00:00',
        'created_before': '2023-01-02T12:00:00',
    }
    response = as_anon.get(url, query)
    assert response.status_code == 200
    names = {c['name'] for c in response.json()}
    assert names == {'first', 'second'}      
