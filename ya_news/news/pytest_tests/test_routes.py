from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_django.fixtures import client


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        (
            'news:detail',
            pytest.lazy_fixture('news_id_for_args')
        ),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None)
    )
)
def test_pages_availability(
    name,
    args,
    not_author_client
):
    assert not_author_client.get(
        reverse(name, args=args)
    ).status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (
            pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            pytest.lazy_fixture('comment_author_client'),
            HTTPStatus.OK
        )
    ),
)
@pytest.mark.parametrize(
    'url',
    (pytest.lazy_fixture('comment_edit_url'), pytest.lazy_fixture('comment_delete_url'))
)
def test_availability_for_comment_edit_and_delete(
        parametrized_client,
        expected_status,
        comment_id_for_args,
        url
):
    assert parametrized_client.get(
        url
    ).status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_redirect_for_anonymous_client(
        client,
        comment_id_for_args,
        name
):
    url = reverse(name, args=comment_id_for_args)
    assertRedirects(
        client.get(url),
        f'{reverse("users:login")}?next={url}'
    )
