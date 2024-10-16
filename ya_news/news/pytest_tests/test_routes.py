from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db

NEWS_HOME_URL = pytest.lazy_fixture('news_home_url')
NEWS_DETAIL_URL = pytest.lazy_fixture('news_detail_url')
USERS_LOGIN_URL = pytest.lazy_fixture('users_login_url')
USERS_LOGOUT_URL = pytest.lazy_fixture('users_logout_url')
USERS_SIGNUP_URL = pytest.lazy_fixture('users_signup_url')
COMMENT_EDIT_URL = pytest.lazy_fixture('comment_edit_url')
COMMENT_DELETE_URL = pytest.lazy_fixture('comment_delete_url')

CLIENT = pytest.lazy_fixture('client')
NEWS_AUTHOR_CLIENT = pytest.lazy_fixture('news_author_client')
COMMENT_AUTHOR_CLIENT = pytest.lazy_fixture('comment_author_client')


@pytest.mark.parametrize(
    'url, params_client, expected_status',
    (
        (NEWS_HOME_URL, CLIENT, HTTPStatus.OK),
        (NEWS_DETAIL_URL, CLIENT, HTTPStatus.OK),
        (USERS_LOGIN_URL, CLIENT, HTTPStatus.OK),
        (USERS_LOGOUT_URL, CLIENT, HTTPStatus.OK),
        (USERS_SIGNUP_URL, CLIENT, HTTPStatus.OK),
        (COMMENT_EDIT_URL, NEWS_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (COMMENT_EDIT_URL, COMMENT_AUTHOR_CLIENT, HTTPStatus.OK),
        (COMMENT_DELETE_URL, NEWS_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (COMMENT_DELETE_URL, COMMENT_AUTHOR_CLIENT, HTTPStatus.OK)
    )
)
def test_pages_availability(url, params_client, expected_status):
    assert (params_client.get(url)
            .status_code == expected_status)


@pytest.mark.parametrize(
    'url',
    (COMMENT_EDIT_URL, COMMENT_DELETE_URL)
)
def test_redirect_for_anonymous_client(client, url, users_login_url):
    assertRedirects(
        client.get(url),
        f'{users_login_url}?next={url}'
    )
