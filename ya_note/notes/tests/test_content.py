from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note
from notes.tests.conf import NOTES_LIST_URL, NOTES_ADD_URL, UsersTestCase


class TestContent(UsersTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )
        cls.notes_edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_notes_list_for_author(self):
        notes = self.author_client.get(
            NOTES_LIST_URL
        ).context['object_list']
        self.assertIn(self.note, notes)
        note = notes.get(id=self.note.id)
        self.assertEquals(self.note.text, note.text)
        self.assertEquals(self.note.author, note.author)
        self.assertEquals(self.note.title, note.title)
        self.assertEqual(self.note.slug, note.slug)

    def test_notes_list_for_not_author(self):
        notes = self.not_author_client.get(
            NOTES_LIST_URL
        ).context['object_list']
        self.assertNotIn(self.note, notes)

    def test_pages_contains_form(self):
        urls = (NOTES_ADD_URL, self.notes_edit_url)
        for url in urls:
            self.assertIsInstance(
                self.author_client.get(url).context.get('form'),
                NoteForm
            )
