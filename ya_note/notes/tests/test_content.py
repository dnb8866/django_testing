from notes.forms import NoteForm
from notes.tests import conf


class TestContent(conf.UsersTestCase):

    def test_notes_list_for_author(self):
        notes = self.author_client.get(
            conf.NOTES_LIST_URL
        ).context['object_list']
        self.assertIn(self.note, notes)
        note = notes.get(id=self.note.id)
        self.assertEquals(self.note.text, note.text)
        self.assertEquals(self.note.author, note.author)
        self.assertEquals(self.note.title, note.title)
        self.assertEqual(self.note.slug, note.slug)

    def test_notes_list_for_not_author(self):
        self.assertNotIn(
            self.note,
            self.not_author_client.get(
                conf.NOTES_LIST_URL
            ).context['object_list']
        )

    def test_pages_contains_form(self):
        for url in (conf.NOTES_ADD_URL, conf.NOTES_EDIT_URL):
            with self.subTest(url=url):
                self.assertIsInstance(
                    self.author_client.get(
                        url
                    ).context.get('form'),
                    NoteForm
                )
