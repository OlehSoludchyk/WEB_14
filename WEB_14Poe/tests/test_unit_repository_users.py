import unittest
from unittest.mock import MagicMock, AsyncMock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas.user import UserSchema, UserResponse, TokenSchema
from src.repository.users import get_user_by_email, update_token, confirmed_email, update_avatar



class TestAsyncContact(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.user = User(id=1, username='test_user', password='qwerty', email='test_email', confirmed=True)
        self.session = AsyncMock(spec=AsyncSession)

    
    async def test_get_user_by_email(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mocked_contact
        result = await get_user_by_email(self.user.email, self.session)
        self.assertEqual(result.email, self.user.email)


    async def test_update_token(self):
        token = 'new_token'
        self.user.refresh_token = None

        await update_token(self.user, token, self.session)
        self.assertEqual(self.user.refresh_token, token)


    async def test_confirmed_email(self):
        self.user.confirmed = False

        with patch('src.repository.users.get_user_by_email', return_value=self.user):
            await confirmed_email(self.user.email, self.session)
            self.assertTrue(self.user.confirmed)