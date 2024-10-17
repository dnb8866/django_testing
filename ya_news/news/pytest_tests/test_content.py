import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_homepage_news_count(client, news_home_url, all_news):
    assert (
        client.get(news_home_url)
        .context['news_list']
        .count() == settings.NEWS_COUNT_ON_HOME_PAGE
    )


def test_homepage_news_order(client, news_home_url, all_news):
    all_dates = [
        one_news.date
        for one_news in client.get(news_home_url).context['news_list']
    ]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_order(
        client,
        one_news,
        news_detail_url,
        all_comments_for_news
):
    response = client.get(news_detail_url)
    assert 'news' in response.context
    all_timestamps = [
        comment.created
        for comment in response.context['news'].comment_set.all()
    ]
    assert all_timestamps == sorted(all_timestamps)


def test_anonymous_client_has_no_form(client, news_detail_url):
    assert (
        'form' not in
        client.get(news_detail_url)
    )


def test_authorized_client_has_form(
        news_author_client,
        news_detail_url
):
    assert isinstance(
        news_author_client.get(news_detail_url).context.get('form'),
        CommentForm
    )
