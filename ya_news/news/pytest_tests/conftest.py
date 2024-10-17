from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import News, Comment


@pytest.fixture
def news_home_url():
    return reverse('news:home')


@pytest.fixture
def users_login_url():
    return reverse('users:login')


@pytest.fixture
def users_logout_url():
    return reverse('users:logout')


@pytest.fixture
def users_signup_url():
    return reverse('users:signup')


@pytest.fixture
def news_author(django_user_model):
    return django_user_model.objects.create(username='Автор новости')


@pytest.fixture
def comment_author(django_user_model):
    return django_user_model.objects.create(username='Автор комментария')


@pytest.fixture
def news_author_client(news_author):
    client = Client()
    client.force_login(news_author)
    return client


@pytest.fixture
def comment_author_client(comment_author):
    client = Client()
    client.force_login(comment_author)
    return client


@pytest.fixture
def one_news():
    return News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )


@pytest.fixture
def all_news():
    today = datetime.today()
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comment(one_news, comment_author):
    return Comment.objects.create(
        news=one_news,
        author=comment_author,
        text='Текст комментария'
    )


@pytest.fixture
def all_comments_for_news(one_news, comment_author):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=one_news, author=comment_author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def news_detail_url(one_news):
    return reverse('news:detail', args=(one_news.id,))


@pytest.fixture
def news_detail_url_comments(news_detail_url):
    return f'{news_detail_url}#comments'


@pytest.fixture
def comment_edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def comment_delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def login_redirect_from_comment_edit_url(users_login_url, comment_edit_url):
    return f'{users_login_url}?next={comment_edit_url}'


@pytest.fixture
def login_redirect_from_comment_delete_url(users_login_url, comment_delete_url):
    return f'{users_login_url}?next={comment_delete_url}'


@pytest.fixture
def url_to_comments(news_detail_url):
    return f'{news_detail_url}#comments'
