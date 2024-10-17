from http import HTTPStatus as HTTPSt

from django.urls import reverse

from notes.models import Note
from notes.tests import conf


class TestRoutes(conf.UsersTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )
        cls.url_note_detail = reverse('notes:detail', args=(cls.note.slug,))
        cls.url_note_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_note_delete = reverse('notes:delete', args=(cls.note.slug,))

    def test_pages_availability(self):
        urls = (
            (conf.NOTES_HOME_URL, self.client, HTTPSt.OK),
            (conf.USERS_LOGIN_URL, self.client, HTTPSt.OK),
            (conf.USERS_LOGOUT_URL, self.client, HTTPSt.OK),
            (conf.USERS_SIGNUP_URL, self.client, HTTPSt.OK),
            (conf.NOTES_LIST_URL, self.not_author_client, HTTPSt.OK),
            (conf.NOTES_ADD_URL, self.not_author_client, HTTPSt.OK),
            (conf.NOTES_SUCCESS_URL, self.not_author_client, HTTPSt.OK),
            (self.url_note_edit, self.author_client, HTTPSt.OK),
            (self.url_note_edit, self.not_author_client, HTTPSt.NOT_FOUND),
            (self.url_note_delete, self.author_client, HTTPSt.OK),
            (self.url_note_delete, self.not_author_client, HTTPSt.NOT_FOUND),
            (self.url_note_detail, self.author_client, HTTPSt.OK),
            (self.url_note_detail, self.not_author_client, HTTPSt.NOT_FOUND)
        )
        for url, user, expected_status in urls:
            with self.subTest(url=url):
                self.assertEqual(user.get(url).status_code, expected_status)

    def test_redirect_for_anonymous_client(self):
        urls = (
            self.url_note_edit,
            self.url_note_delete,
            self.url_note_detail,
            conf.NOTES_LIST_URL,
            conf.NOTES_ADD_URL
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{conf.USERS_LOGIN_URL}?next={url}'
                self.assertRedirects(self.client.get(url), redirect_url)
