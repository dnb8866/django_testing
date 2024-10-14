from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client,
    news_detail_url,
    form_data_for_new_comment
):
    client.post(news_detail_url, data=form_data_for_new_comment)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    news_author,
    news_author_client,
    news_detail_url,
    one_news,
    form_data_for_new_comment
):
    response = news_author_client.post(
        news_detail_url,
        data=form_data_for_new_comment
    )
    assertRedirects(response, f'{news_detail_url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert (
        (comment.text, comment.news, comment.author) ==
        (form_data_for_new_comment['text'], one_news, news_author)
    )


def test_user_cant_use_bad_words(
    news_author_client,
    news_detail_url
):
    bad_words_data = {'text': f'Текст, {BAD_WORDS[0]}, еще текст'}
    response = news_author_client.post(news_detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.usefixtures('comment')
def test_author_can_delete_comment(
        comment_delete_url,
        comment_author_client,
        url_to_comments
):
    response = comment_author_client.delete(comment_delete_url)
    assertRedirects(response, url_to_comments)


@pytest.mark.django_db
@pytest.mark.usefixtures('comment')
def test_user_cant_delete_comment_of_another_user(
    not_author_client,
    comment_delete_url
):
    response = not_author_client.delete(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_author_can_edit_comment(
    form_data_for_update_comment,
    comment_edit_url,
    comment_author_client,
    comment,
    url_to_comments
):
    comment_text = form_data_for_update_comment.get('text')
    response = comment_author_client.post(
        comment_edit_url,
        data=form_data_for_update_comment
    )
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == comment_text


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    form_data_for_update_comment,
    comment_edit_url,
    not_author_client,
    comment
):
    comment_text = comment.text
    response = not_author_client.post(
        comment_edit_url,
        data=form_data_for_update_comment
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == comment_text
