from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_limiter.depends import RateLimiter

from src.database.models import User
from src.database.db import get_db
from src.repository import contacts as repositories_contacts
from src.schemas.contact import ContactSchema, ContactUpdateSchema, ContactResponse, ContactCreate
from src.services.auth import auth_service


router = APIRouter(prefix='/contacts', tags=['contacts'])

@router.get('/upcoming_birthdays', response_model=list[ContactResponse])
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):

    """
    Retrieves a list of contacts with upcoming birthdays within the next week.

    :param db: The database session.
    :type db: AsyncSession
    :param user: The current authenticated user.
    :type user: User
    :return: A list of contacts with birthdays in the next 7 days.
    :rtype: list[ContactResponse]
    """

    contacts = await repositories_contacts.get_upcoming_birthdays(db, user)
    return contacts



@router.get('/', response_model=list[ContactResponse])
async def get_contacts(limit: int = Query(default=1, ge=1, le=500), offset: int = Query(default=0, ge=0),
                       db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    
    """
    Retrieves a paginated list of contacts for the current user.

    :param limit: The maximum number of contacts to return (default is 1, max is 500).
    :type limit: int
    :param offset: The number of contacts to skip before starting to collect the result set.
    :type offset: int
    :param db: The database session.
    :type db: AsyncSession
    :param user: The current authenticated user.
    :type user: User
    :return: A paginated list of contacts.
    :rtype: list[ContactResponse]
    """

    contacts = await repositories_contacts.get_contacts(limit, offset, db, user)
    return contacts



@router.get('/{contact_id}', response_model=ContactResponse)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):

    """
    Retrieves a specific contact by its ID.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param db: The database session.
    :type db: AsyncSession
    :param user: The current authenticated user.
    :type user: User
    :return: The contact with the specified ID.
    :rtype: ContactResponse
    :raises HTTPException: If the contact is not found.
    """

    contact = await repositories_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='NOT FOUND')
    return contact



@router.get('/search/', response_model=list[ContactResponse])
async def search_contacts(query: str, db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):

    """
    Searches for contacts based on a query string (matches first name, surname, or email).

    :param query: The search query string.
    :type query: str
    :param db: The database session.
    :type db: AsyncSession
    :param user: The current authenticated user.
    :type user: User
    :return: A list of contacts matching the search query.
    :rtype: list[ContactResponse]
    """

    contacts = await repositories_contacts.search_contacts(query, db, user)
    return contacts



@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def create_contact(body: ContactCreate, db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):

    """
    Creates a new contact for the current user.

    :param body: The schema containing the details of the contact to create.
    :type body: ContactCreate
    :param db: The database session.
    :type db: AsyncSession
    :param user: The current authenticated user.
    :type user: User
    :return: The newly created contact.
    :rtype: ContactResponse
    :raises HTTPException: If the rate limit is exceeded.
    """

    contact = await repositories_contacts.create_contact(body, db, user)
    return contact



@router.put('/{contact_id}')
async def update_contact(body: ContactUpdateSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):

    """
    Updates an existing contact for the current user.

    :param body: The schema containing the updated details of the contact.
    :type body: ContactUpdateSchema
    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param db: The database session.
    :type db: AsyncSession
    :param user: The current authenticated user.
    :type user: User
    :return: The updated contact.
    :rtype: ContactResponse or None
    :raises HTTPException: If the contact is not found.
    """

    contact= await repositories_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='NOT FOUND')
    return contact



@router.delete('/{contact_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):

    """
    Deletes a specific contact by its ID.

    :param contact_id: The ID of the contact to delete.
    :type contact_id: int
    :param db: The database session.
    :type db: AsyncSession
    :param user: The current authenticated user.
    :type user: User
    :return: No content if the deletion is successful.
    :rtype: None
    :raises HTTPException: If the contact is not found.
    """

    contact = await repositories_contacts.delete_contact(contact_id, db, user)
    return contact