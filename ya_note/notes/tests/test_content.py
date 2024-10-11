from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Не автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )
        cls.note_slug = (cls.note.slug,)

    def test_notes_list_for_different_users(self):
        params = (
            (self.author, True),
            (self.not_author, False)
        )
        for user, result in params:
            self.client.force_login(user)
            objects = self.client.get(
                reverse('notes:list')
            ).context['object_list']
            self.assertEqual((self.note in objects), result)

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', self.note_slug),
        )
        self.client.force_login(self.author)
        for name, args in urls:
            response = self.client.get(reverse(name, args=args))
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)
