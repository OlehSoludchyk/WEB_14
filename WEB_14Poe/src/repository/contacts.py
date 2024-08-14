from datetime import datetime, timedelta

from sqlalchemy import select, and_, cast, DATE, func, Date
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):

    """
    Retrieves a list of contacts for a specific user with specified pagination parameters.

    :param offset: The number of contactss to skip.
    :type offset: int
    :param limit: The maximum number of contacts to return.
    :type limit: int
    :param user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: A list of contacts.
    :rtype: List[Contact]
    """

    statmnt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    contacts = await db.execute(statmnt)
    return contacts.scalars().all()


async def search_contacts(query, db: AsyncSession, user: User):

    """
    Searches for contacts based on a query string in the first name, surname, or email.

    :param query: The search query string.
    :type query: str
    :param db: The database session.
    :type db: AsyncSession
    :param user: The user to search contacts for.
    :type user: User
    :return: A list of contacts matching the query.
    :rtype: List[Contact]
    """

    statmnt = select(Contact).filter_by(user=user).filter((Contact.firstname.ilike(query))
                                     | (Contact.surname.ilike(query))
                                     | (Contact.email.ilike(query)))
    results = await db.execute(statmnt)
    return results.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):

    """
    Retrieves a specific contact by its ID for a given user.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param db: The database session.
    :type db: AsyncSession
    :param user: The user to retrieve the contact for.
    :type user: User
    :return: The contact with the specified ID, or None if not found.
    :rtype: Contact or None
    """

    statmnt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(statmnt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession, user: User):

    """
    Creates a new contact for a specific user.

    :param body: The schema containing the contact details.
    :type body: ContactSchema
    :param db: The database session.
    :type db: AsyncSession
    :param user: The user for whom the contact is created.
    :type user: User
    :return: The newly created contact.
    :rtype: Contact
    """

    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactUpdateSchema, db: AsyncSession, user: User):

    """
    Updates an existing contact for a specific user.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param body: The schema containing the updated contact details.
    :type body: ContactUpdateSchema
    :param db: The database session.
    :type db: AsyncSession
    :param user: The user who owns the contact.
    :type user: User
    :return: The updated contact, or None if not found.
    :rtype: Contact or None
    """

    statmnt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(statmnt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.firstname = body.firstname
        contact.surname = body.surname
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.details = body.details
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):

    """
    Deletes a specific contact by its ID for a given user.

    :param contact_id: The ID of the contact to delete.
    :type contact_id: int
    :param db: The database session.
    :type db: AsyncSession
    :param user: The user who owns the contact.
    :type user: User
    :return: The deleted contact, or None if not found.
    :rtype: Contact or None
    """

    statmnt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(statmnt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact



async def get_upcoming_birthdays(db: AsyncSession, user: User):

    """
    Retrieves a list of contacts whose birthdays are within the next 7 days.

    :param db: The database session.
    :type db: AsyncSession
    :param user: The user to retrieve upcoming birthdays for.
    :type user: User
    :return: A list of contacts with upcoming birthdays.
    :rtype: List[Contact]
    """

    today = datetime.now().date()
    week_from_today = today + timedelta(days=7)
    statmnt = select(Contact).filter_by(user=user).filter(
        and_(
            cast(Contact.birthday, Date) >= today,
            cast(Contact.birthday, Date) <= week_from_today
        )
    )
    contacts = await db.execute(statmnt)
    return contacts.scalars().all()