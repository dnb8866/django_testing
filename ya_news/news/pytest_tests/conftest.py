from datetime import datetime, timedelta

import pytest
from django.conf import settings

from django.test.client import Client
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from news.models import News, Comment


@pytest.fixture
def news_author(django_user_model):
    return django_user_model.objects.create(username='Автор новости')


@pytest.fixture
def comment_author(django_user_model):
    return django_user_model.objects.create(username='Автор комментария')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


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
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def one_news():
    one_news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return one_news


@pytest.fixture
def all_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def comment(one_news, comment_author):
    comment = Comment.objects.create(
        news=one_news,
        author=comment_author,
        text='Текст комментария'
    )
    return comment


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
def news_id_for_args(one_news):
    return (one_news.id,)


@pytest.fixture
def news_detail_url(one_news, news_id_for_args):
    return reverse('news:detail', args=news_id_for_args)


@pytest.fixture
def comment_id_for_args(comment):
    return (comment.id,)


@pytest.fixture
def comment_edit_url(comment_id_for_args):
    return reverse('news:edit', args=comment_id_for_args)


@pytest.fixture
def comment_delete_url(comment_id_for_args):
    return reverse('news:delete', args=comment_id_for_args)


@pytest.fixture
def url_to_comments(news_detail_url):
    return f'{news_detail_url}#comments'


@pytest.fixture
def form_data_for_new_comment():
    return {'text': 'Новый комментарий'}


@pytest.fixture
def form_data_for_update_comment():
    return {'text': 'Обновленный комментарий'}