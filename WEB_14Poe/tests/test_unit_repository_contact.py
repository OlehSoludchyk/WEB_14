
import unittest
from unittest.mock import MagicMock, AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession


from src.database.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema
from src.repository.contacts import get_contacts, search_contacts, get_contact, create_contact, update_contact, delete_contact



class TestAsyncContact(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.user = User(id=1, username='test_user', password='qwerty', confirmed=True)
        self.session = AsyncMock(spec=AsyncSession)
    
    async def test_get_contacts(self):
        limit = 10
        offset = 0
        contacts = [Contact(id=1, firstname='firstname1', surname='surname1', email='test1@example.com', 
                            phone='phone1', birthday='2002-02-02', details='details1', user=self.user),
                    Contact(id=2, firstname='firstname2', surname='surname2', email='test2@example.com', 
                            phone='phone2', birthday='2003-03-03', details='details3', user=self.user)]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit, offset, self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        contact_id = 1
        contacts = [Contact(id=contact_id, firstname='firstname1', surname='surname1', email='test1@example.com',
                            phone='phone1', birthday='2002-02-02', details='details1', user=self.user),
                    Contact(id=2, firstname='firstname2', surname='surname2', email='test1@example.com',
                            phone='phone2', birthday='2003-03-03', details='details3', user=self.user)]
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contacts[0]
        self.session.execute.return_value = mocked_contact
    
        result = await get_contact(contact_id, self.session, self.user)  # Передайте contact_id як перший аргумент
        self.assertEqual(result, contacts[0])



    # async def test_get_contact(self):
    #     contacts = [Contact(id=1, firstname='firstname1', surname='surname1', email='test1@example.com', 
    #                         phone='phone1', birthday='2002-02-02', details='details1', user=self.user),
    #                 Contact(id=2, firstname='firstname2', surname='surname2', email='test1@example.com', 
    #                         phone='phone2', birthday='2003-03-03', details='details3', user=self.user)]
    #     mocked_contacts = MagicMock()
    #     mocked_contacts.scalars.return_value.all.return_value = contacts
    #     self.session.execute.return_value = mocked_contacts
    #     result = await get_contact(self.session, self.user)
    #     self.assertEqual(result, contacts)


    async def test_create_contact(self):
        body = ContactSchema(firstname='test_firstname', surname='test_surname', email='test1@example.com', 
                             phone='test_phone', birthday='2002-02-02', details='test_details')
        result = await create_contact(body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.firstname, body.firstname)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birthday, body.birthday)
        self.assertEqual(result.details, body.details)


    async def test_update_contact(self):
        body = ContactUpdateSchema(firstname='test_firstname', surname='test_surname', email='test1@example.com', 
                                   phone='test_phone', birthday='2002-02-02', details='test_details')
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(firstname='test_firstname', surname='test_surname', 
                                                                 email='test1@example.com', phone='test_phone', birthday='2002-02-02', 
                                                                 details='test_details', user=self.user)
        self.session.execute.return_value = mocked_contact
        result = await update_contact(1, body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.firstname, body.firstname)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birthday, body.birthday)
        self.assertEqual(result.details, body.details)


    async def test_delete_contact(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(id=1, firstname='test_firstname', surname='test_surname', 
                                                                 email='test1@example.com', phone='test_phone', birthday='2002-02-02', 
                                                                 details='test_details', user=self.user)
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(1, self.session, self.user)
        self.assertIsInstance(result, Contact)


    async def test_search_contacts(self):
        query = 'test'
        contacts = [
        Contact(id=1, firstname='test_firstname1', surname='surname1', email='test1@example.com', 
                phone='phone1', birthday='2002-02-02', details='details1', user=self.user),
        Contact(id=2, firstname='firstname2', surname='test_surname2', email='test2@example.com', 
                phone='phone2', birthday='2003-03-03', details='details2', user=self.user)
                ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
    
        result = await search_contacts(query, self.session, self.user)
        self.assertEqual(result, contacts)


if __name__ == '__main__':
    unittest.main()