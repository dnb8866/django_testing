from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.template.defaultfilters import title
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class AuthorTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.url_success = reverse('notes:success')


class TestNoteCreate(AuthorTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse('notes:add')
        cls.add_note_form_data = {
            'title': 'Новая заметка',
            'text': 'Текст заметки',
            'slug': 'note-slug'
        }

    def test_user_can_create_note(self):
        response = self.author_client.post(
            self.url,
            data=self.add_note_form_data
        )
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(
            (new_note.title, new_note.text, new_note.slug),
            (self.add_note_form_data['title'], self.add_note_form_data['text'], self.add_note_form_data['slug'])
        )

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(
            self.url,
            data=self.add_note_form_data
        )
        self.assertRedirects(
            response,
            f'{reverse("users:login")}?next={self.url}'
        )
        self.assertEqual(Note.objects.count(), 0)

    def test_not_unique_slug(self):
        note = Note.objects.create(
            title='Заголовок заметки',
            text="Текст заметки",
            slug='note-slug',
            author=self.author
        )
        self.add_note_form_data['slug'] = note.slug
        response = self.author_client.post(
            self.url,
            data=self.add_note_form_data
        )
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)


    def test_empty_slug(self):
        self.add_note_form_data.pop('slug')
        response = self.author_client.post(
            self.url,
            data=self.add_note_form_data
        )
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(
            new_note.slug, slugify(self.add_note_form_data['title'])
        )


class TestNoteEditDelete(AuthorTestCase):
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновленный текст заметки'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.not_author = User.objects.create(username='Не автор')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title='Заголовок заметки',
            text=cls.NOTE_TEXT,
            slug='note-slug',
            author=cls.author
        )
        cls.edit_note_form_data = {
            'title': 'Новый заголовок',
            'text': cls.NEW_NOTE_TEXT,
        }
        cls.url_note_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_note_delete = reverse('notes:delete', args=(cls.note.slug,))


    def test_author_can_edit_note(self):
        self.assertRedirects(
            self.author_client.post(
                self.url_note_edit,
                self.edit_note_form_data
            ),
            self.url_success
        )
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_other_user_cant_edit_note(self):
        self.assertEqual(
            self.not_author_client.post(
                self.url_note_edit,
                self.edit_note_form_data
            ).status_code,
            HTTPStatus.NOT_FOUND
        )
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)

    def test_author_can_delete_note(self):
        self.assertRedirects(
            self.author_client.post(self.url_note_delete),
            self.url_success
        )
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        self.assertEqual(
            self.not_author_client.post(
                self.url_note_delete
            ).status_code,
            HTTPStatus.NOT_FOUND
        )
        self.assertEqual(Note.objects.count(), 1)
