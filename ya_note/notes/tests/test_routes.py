from http import HTTPStatus as HTTPSt

from notes.tests import conf


class TestRoutes(conf.UsersTestCase):

    def test_pages_availability(self):
        urls = (
            (conf.NOTES_HOME_URL, self.client, HTTPSt.OK),
            (conf.USERS_LOGIN_URL, self.client, HTTPSt.OK),
            (conf.USERS_LOGOUT_URL, self.client, HTTPSt.OK),
            (conf.USERS_SIGNUP_URL, self.client, HTTPSt.OK),
            (conf.NOTES_LIST_URL, self.not_author_client, HTTPSt.OK),
            (conf.NOTES_ADD_URL, self.not_author_client, HTTPSt.OK),
            (conf.NOTES_SUCCESS_URL, self.not_author_client, HTTPSt.OK),
            (conf.NOTES_EDIT_URL, self.author_client, HTTPSt.OK),
            (conf.NOTES_EDIT_URL, self.not_author_client, HTTPSt.NOT_FOUND),
            (conf.NOTES_DELETE_URL, self.author_client, HTTPSt.OK),
            (conf.NOTES_DELETE_URL, self.not_author_client, HTTPSt.NOT_FOUND),
            (conf.NOTES_DETAIL_URL, self.author_client, HTTPSt.OK),
            (conf.NOTES_DETAIL_URL, self.not_author_client, HTTPSt.NOT_FOUND),
            (conf.NOTES_EDIT_URL, self.client, HTTPSt.FOUND),
            (conf.NOTES_DELETE_URL, self.client, HTTPSt.FOUND),
            (conf.NOTES_DETAIL_URL, self.client, HTTPSt.FOUND),
            (conf.NOTES_LIST_URL, self.client, HTTPSt.FOUND),
            (conf.NOTES_ADD_URL, self.client, HTTPSt.FOUND)
        )
        for url, user, expected_status in urls:
            with self.subTest(url=url):
                self.assertEqual(user.get(url).status_code, expected_status)

    def test_redirect_for_anonymous_client(self):
        urls = (
            (conf.NOTES_EDIT_URL, conf.REDIRECT_NOTES_EDIT_URL),
            (conf.NOTES_DELETE_URL, conf.REDIRECT_NOTES_DELETE_URL),
            (conf.NOTES_DETAIL_URL, conf.REDIRECT_NOTES_DETAIL_URL),
            (conf.NOTES_LIST_URL, conf.REDIRECT_NOTES_LIST_URL),
            (conf.NOTES_ADD_URL, conf.REDIRECT_NOTES_ADD_URL)
        )
        for url, redirect_url in urls:
            with self.subTest(url=url):
                self.assertRedirects(self.client.get(url), redirect_url)
