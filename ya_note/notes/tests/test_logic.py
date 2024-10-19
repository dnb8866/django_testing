from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests import conf


class TestNote(conf.UsersTestCase):

    def test_user_can_create_note(self):
        notes = set(Note.objects.all())
        response = self.author_client.post(
            conf.NOTES_ADD_URL,
            data=self.note_form_data
        )
        notes = set(Note.objects.all()) - notes
        self.assertRedirects(response, conf.NOTES_SUCCESS_URL)
        self.assertEqual(len(notes), 1)
        note = notes.pop()
        self.assertEqual(note.title, self.note_form_data['title'])
        self.assertEqual(note.text, self.note_form_data['text'])
        self.assertEqual(note.slug, self.note_form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        notes = set(Note.objects.all())
        self.assertRedirects(
            self.client.post(
                conf.NOTES_ADD_URL,
                data=self.note_form_data
            ),
            conf.REDIRECT_NOTES_ADD_URL
        )
        self.assertEqual(notes, set(Note.objects.all()))

    def test_not_unique_slug(self):
        self.note_form_data['slug'] = self.note.slug
        notes = set(Note.objects.all())
        response = self.author_client.post(
            conf.NOTES_ADD_URL,
            data=self.note_form_data
        )
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(notes, set(Note.objects.all()))

    def test_empty_slug(self):
        data = self.note_form_data
        notes = set(Note.objects.all())
        response = self.author_client.post(
            conf.NOTES_ADD_URL,
            data=data
        )
        notes = set(Note.objects.all()) - notes
        self.assertRedirects(response, conf.NOTES_SUCCESS_URL)
        self.assertEqual(len(notes), 1)
        note = notes.pop()
        self.assertEqual(
            note.slug, slugify(self.note_form_data['title'])
        )
        self.assertEqual(note.author, self.author)
        self.assertEqual(note.text, self.note_form_data['text'])
        self.assertEqual(note.title, self.note_form_data['title'])

    def test_author_can_edit_note(self):
        self.assertRedirects(
            self.author_client.post(
                conf.NOTES_EDIT_URL,
                self.note_form_data
            ),
            conf.NOTES_SUCCESS_URL
        )
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.text, self.note_form_data['text'])
        self.assertEqual(note.title, self.note_form_data['title'])
        self.assertEqual(note.author, self.note.author)
        self.assertEqual(note.slug, self.note_form_data['slug'])

    def test_other_user_cant_edit_note(self):
        self.assertEqual(
            self.not_author_client.post(
                conf.NOTES_EDIT_URL,
                self.note_form_data
            ).status_code,
            HTTPStatus.NOT_FOUND
        )
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.text, note.text)
        self.assertEqual(self.note.title, note.title)
        self.assertEqual(self.note.author, note.author)
        self.assertEqual(self.note.slug, note.slug)

    def test_author_can_delete_note(self):
        count_before = Note.objects.count()
        self.assertRedirects(
            self.author_client.post(conf.NOTES_DELETE_URL),
            conf.NOTES_SUCCESS_URL
        )
        self.assertEqual(count_before - Note.objects.count(), 1)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_other_user_cant_delete_note(self):
        notes = set(Note.objects.all())
        self.assertEqual(
            self.not_author_client.post(
                conf.NOTES_DELETE_URL
            ).status_code,
            HTTPStatus.NOT_FOUND
        )
        self.assertEqual(set(Note.objects.all()), notes)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.text, note.text)
        self.assertEqual(self.note.title, note.title)
        self.assertEqual(self.note.author, note.author)
        self.assertEqual(self.note.slug, note.slug)
