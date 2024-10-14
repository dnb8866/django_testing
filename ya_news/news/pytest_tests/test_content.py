import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

HOME_URL = reverse('news:home')


@pytest.mark.django_db
@pytest.mark.usefixtures('all_news')
def test_homepage_news_count(client):
    assert (
        client.get(HOME_URL)
        .context['news_list']
        .count() == settings.NEWS_COUNT_ON_HOME_PAGE
    )


@pytest.mark.django_db
@pytest.mark.usefixtures('all_news')
def test_homepage_news_order(client):
    response = client.get(HOME_URL)
    news = response.context['news_list']
    all_dates = [one_news.date for one_news in news]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
@pytest.mark.usefixtures('all_comments_for_news')
def test_comments_order(client, one_news, news_detail_url):
    response = client.get(news_detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_timestamps = [
        comment.created
        for comment in news.comment_set.all()
    ]
    assert all_timestamps == sorted(all_timestamps)


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news_detail_url):
    assert (
        'form' not in
        client.get(
            news_detail_url
        )
    )


def test_authorized_client_has_form(
    news_author_client,
    news_detail_url
):
    response = news_author_client.get(news_detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
