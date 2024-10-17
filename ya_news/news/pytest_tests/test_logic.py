from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

FORM_DATA_FOR_COMMENT = {'text': 'Комментарий'}
FORM_DATA_FOR_UPDATE_COMMENT = {'text': 'Обновленный комментарий'}

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(
    client,
    news_detail_url
):
    client.post(news_detail_url, data=FORM_DATA_FOR_COMMENT)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    news_author,
    news_author_client,
    news_detail_url,
    news_detail_url_comments,
    one_news,
):
    response = news_author_client.post(
        news_detail_url,
        data=FORM_DATA_FOR_COMMENT
    )
    assertRedirects(response, news_detail_url_comments)
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == FORM_DATA_FOR_COMMENT['text']
    assert comment.news == one_news
    assert comment.author == news_author


@pytest.mark.parametrize(
    'bad_word',
    BAD_WORDS
)
def test_user_cant_use_bad_words(
    news_author_client,
    news_detail_url,
    bad_word
):
    comment_count_before = Comment.objects.count()
    response = news_author_client.post(
        news_detail_url,
        data={'text': f'Текст, {bad_word}'}
    )
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert (
        Comment.objects.count() - comment_count_before
        == 0
    )


def test_author_can_delete_comment(
        comment_delete_url,
        comment_author_client,
        url_to_comments,
        comment
):
    comment_count_before = Comment.objects.count()
    response = comment_author_client.delete(comment_delete_url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() - comment_count_before == -1


def test_user_cant_delete_comment_of_another_user(
    news_author_client,
    comment_delete_url,
    comment
):
    comment_count_before = Comment.objects.count()
    response = news_author_client.delete(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert (
        Comment.objects.count() - comment_count_before
        == 0
    )
    new_comment = Comment.objects.get(id=comment.id)
    assert new_comment.text == comment.text
    assert new_comment.author == comment.author
    assert new_comment.news == comment.news


def test_author_can_edit_comment(
    comment_edit_url,
    comment_author_client,
    comment,
    url_to_comments
):
    response = comment_author_client.post(
        comment_edit_url,
        data=FORM_DATA_FOR_UPDATE_COMMENT
    )
    assertRedirects(response, url_to_comments)
    new_comment = Comment.objects.get(id=comment.id)
    assert new_comment.text == FORM_DATA_FOR_UPDATE_COMMENT['text']
    assert new_comment.author == comment.author
    assert new_comment.news == comment.news


def test_user_cant_edit_comment_of_another_user(
    comment_edit_url,
    news_author_client,
    comment
):
    response = news_author_client.post(
        comment_edit_url,
        data=FORM_DATA_FOR_UPDATE_COMMENT
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    new_comment = Comment.objects.get(id=comment.id)
    assert comment.text == new_comment.text
    assert comment.author == new_comment.author
    assert comment.news == new_comment.news
