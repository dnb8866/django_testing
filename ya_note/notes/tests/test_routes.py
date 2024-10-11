from http import HTTPStatus

import pytils.translit
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )
        cls.note_slug = (cls.note.slug,)

    def test_pages_availability(self):
            urls = (
                ('notes:home', None),
                ('users:login', None),
                ('users:logout', None),
                ('users:signup', None),
            )
            for name, args in urls:
                with self.subTest(name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        self.client.force_login(self.reader)
        for name in ('notes:list', 'notes:add', 'notes:success'):
            with self.subTest(name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_comment_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=self.note_slug)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        urls = (
            ('notes:edit', self.note_slug),
            ('notes:delete', self.note_slug),
            ('notes:detail', self.note_slug),
            ('notes:list', None),
            ('notes:add', None)
        )
        login_url = reverse('users:login')
        for name, slug in urls:
            with self.subTest(name=name):
                url = reverse(name, args=slug)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
