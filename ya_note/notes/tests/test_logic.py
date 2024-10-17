from http import HTTPStatus

from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.conf import NOTES_SUCCESS_URL, NOTES_ADD_URL, UsersTestCase


class TestNote(UsersTestCase):
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновленный текст заметки'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = Note.objects.create(
            title='Заголовок заметки',
            text=cls.NOTE_TEXT,
            slug='note-slug',
            author=cls.author
        )
        cls.add_note_form_data = {
            'title': 'Новая заметка',
            'text': 'Текст заметки',
            'slug': 'note-slug1'
        }
        cls.edit_note_form_data = {
            'title': 'Новый заголовок',
            'text': cls.NEW_NOTE_TEXT,
        }
        cls.url_note_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_note_delete = reverse('notes:delete', args=(cls.note.slug,))

    def test_user_can_create_note(self):
        count_notes_before = Note.objects.count()
        response = self.author_client.post(
            NOTES_ADD_URL,
            data=self.add_note_form_data
        )
        self.assertRedirects(response, NOTES_SUCCESS_URL)
        self.assertEqual(Note.objects.count() - count_notes_before, 1)
        new_note = Note.objects.get(slug=self.add_note_form_data['slug'])
        self.assertEqual(new_note.title, self.add_note_form_data['title'])
        self.assertEqual(new_note.text, self.add_note_form_data['text'])
        self.assertEqual(new_note.slug, self.add_note_form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        count_notes_before = Note.objects.count()
        response = self.client.post(
            NOTES_ADD_URL,
            data=self.add_note_form_data
        )
        self.assertRedirects(
            response,
            f'{reverse("users:login")}?next={NOTES_ADD_URL}'
        )
        self.assertEqual(Note.objects.count() - count_notes_before, 0)

    def test_not_unique_slug(self):
        self.add_note_form_data['slug'] = self.note.slug
        count_notes_before = Note.objects.count()
        response = self.author_client.post(
            NOTES_ADD_URL,
            data=self.add_note_form_data
        )
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count() - count_notes_before, 0)

    def test_empty_slug(self):
        data = self.add_note_form_data
        data.pop('slug')
        count_notes_before = Note.objects.count()
        response = self.author_client.post(
            NOTES_ADD_URL,
            data=data
        )
        self.assertRedirects(response, NOTES_SUCCESS_URL)
        self.assertEqual(Note.objects.count() - count_notes_before, 1)
        new_note = Note.objects.get(slug=slugify(data['title']))
        self.assertEqual(
            new_note.slug, slugify(self.add_note_form_data['title'])
        )
        self.assertEqual(new_note.author, self.author)
        self.assertEqual(new_note.text, self.add_note_form_data['text'])
        self.assertEqual(new_note.title, self.add_note_form_data['title'])

    def test_author_can_edit_note(self):
        self.assertRedirects(
            self.author_client.post(
                self.url_note_edit,
                self.edit_note_form_data
            ),
            NOTES_SUCCESS_URL
        )
        new_note = Note.objects.get(id=self.note.id)
        self.assertEqual(new_note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(new_note.title, self.edit_note_form_data['title'])
        self.assertEqual(new_note.author, self.author)
        self.assertEqual(
            new_note.slug,
            slugify(self.edit_note_form_data['title'])
        )

    def test_other_user_cant_edit_note(self):
        self.assertEqual(
            self.not_author_client.post(
                self.url_note_edit,
                self.edit_note_form_data
            ).status_code,
            HTTPStatus.NOT_FOUND
        )
        new_note = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.text, new_note.text)
        self.assertEqual(self.note.title, new_note.title)
        self.assertEqual(self.note.author, new_note.author)
        self.assertEqual(self.note.slug, new_note.slug)

    def test_author_can_delete_note(self):
        count_notes_before = Note.objects.count()
        self.assertRedirects(
            self.author_client.post(self.url_note_delete),
            NOTES_SUCCESS_URL
        )
        self.assertEqual(Note.objects.count() - count_notes_before, -1)

    def test_other_user_cant_delete_note(self):
        count_notes_before = Note.objects.count()
        self.assertEqual(
            self.not_author_client.post(
                self.url_note_delete
            ).status_code,
            HTTPStatus.NOT_FOUND
        )
        self.assertEqual(Note.objects.count() - count_notes_before, 0)
