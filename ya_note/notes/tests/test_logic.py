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
        diff_notes = set(Note.objects.all()) - notes
        self.assertRedirects(response, conf.NOTES_SUCCESS_URL)
        self.assertEqual(len(diff_notes), 1)
        new_note = diff_notes.pop()
        self.assertEqual(new_note.title, self.note_form_data['title'])
        self.assertEqual(new_note.text, self.note_form_data['text'])
        self.assertEqual(new_note.slug, self.note_form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        notes = set(Note.objects.all())
        response = self.client.post(
            conf.NOTES_ADD_URL,
            data=self.note_form_data
        )
        self.assertRedirects(
            response,
            conf.REDIRECT_NOTES_ADD_URL
        )
        self.assertEqual(len(set(Note.objects.all()) - notes), 0)

    def test_not_unique_slug(self):
        self.note_form_data['slug'] = self.note.slug
        notes_before = set(Note.objects.all())
        response = self.author_client.post(
            conf.NOTES_ADD_URL,
            data=self.note_form_data
        )
        notes_after = set(Note.objects.all())
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(len(notes_after - notes_before), 0)

    def test_empty_slug(self):
        data = self.note_form_data
        notes = set(Note.objects.all())
        response = self.author_client.post(
            conf.NOTES_ADD_URL,
            data=data
        )
        diff_notes = set(Note.objects.all()) - notes
        self.assertRedirects(response, conf.NOTES_SUCCESS_URL)
        self.assertEqual(len(diff_notes), 1)
        new_note = diff_notes.pop()
        self.assertEqual(
            new_note.slug, slugify(self.note_form_data['title'])
        )
        self.assertEqual(new_note.author, self.author)
        self.assertEqual(new_note.text, self.note_form_data['text'])
        self.assertEqual(new_note.title, self.note_form_data['title'])

    def test_author_can_edit_note(self):
        self.assertRedirects(
            self.author_client.post(
                conf.NOTES_EDIT_URL,
                self.note_form_data
            ),
            conf.NOTES_SUCCESS_URL
        )
        new_note = Note.objects.get(id=self.note.id)
        self.assertEqual(new_note.text, self.note_form_data['text'])
        self.assertEqual(new_note.title, self.note_form_data['title'])
        self.assertEqual(new_note.author, self.note.author)
        self.assertEqual(new_note.slug, self.note_form_data['slug'])

    def test_other_user_cant_edit_note(self):
        self.assertEqual(
            self.not_author_client.post(
                conf.NOTES_EDIT_URL,
                self.note_form_data
            ).status_code,
            HTTPStatus.NOT_FOUND
        )
        new_note = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.text, new_note.text)
        self.assertEqual(self.note.title, new_note.title)
        self.assertEqual(self.note.author, new_note.author)
        self.assertEqual(self.note.slug, new_note.slug)

    def test_author_can_delete_note(self):
        count_before = Note.objects.count()
        self.assertRedirects(
            self.author_client.post(conf.NOTES_DELETE_URL),
            conf.NOTES_SUCCESS_URL
        )
        self.assertEqual(count_before - Note.objects.count(), 1)
        self.assertEqual(Note.objects.filter(id=self.note.id).exists(), False)

    def test_other_user_cant_delete_note(self):
        self.assertEqual(
            self.not_author_client.post(
                conf.NOTES_DELETE_URL
            ).status_code,
            HTTPStatus.NOT_FOUND
        )
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note, self.note)
