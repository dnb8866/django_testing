from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

NOTE_SLUG = 'zagolovok'
NOTES_HOME_URL = reverse('notes:home')
NOTES_LIST_URL = reverse('notes:list')
NOTES_ADD_URL = reverse('notes:add')
NOTES_EDIT_URL = reverse(
    'notes:edit',
    args=(NOTE_SLUG,))
NOTES_DELETE_URL = reverse(
    'notes:delete',
    args=(NOTE_SLUG,))
NOTES_DETAIL_URL = reverse(
    'notes:detail',
    args=(NOTE_SLUG,))
NOTES_SUCCESS_URL = reverse('notes:success')
USERS_LOGIN_URL = reverse('users:login')
USERS_LOGOUT_URL = reverse('users:logout')
USERS_SIGNUP_URL = reverse('users:signup')
REDIRECT_NOTES_HOME_URL = f'{USERS_LOGIN_URL}?next={NOTES_HOME_URL}'
REDIRECT_NOTES_LIST_URL = f'{USERS_LOGIN_URL}?next={NOTES_LIST_URL}'
REDIRECT_NOTES_ADD_URL = f'{USERS_LOGIN_URL}?next={NOTES_ADD_URL}'
REDIRECT_NOTES_EDIT_URL = f'{USERS_LOGIN_URL}?next={NOTES_EDIT_URL}'
REDIRECT_NOTES_DELETE_URL = f'{USERS_LOGIN_URL}?next={NOTES_DELETE_URL}'
REDIRECT_NOTES_DETAIL_URL = f'{USERS_LOGIN_URL}?next={NOTES_DETAIL_URL}'

User = get_user_model()


class UsersTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='Не автор')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug=NOTE_SLUG
        )
        cls.note_form_data = {
            'title': 'Новая заметка',
            'text': 'Текст заметки',
            'slug': 'novaya-zametka'
        }
