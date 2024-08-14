from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.db import get_db
from src.database.models import User
from src.schemas.user import UserSchema, UserResponse



async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):

    """
    Retrieves a user by their email address.

    :param email: The email address of the user to retrieve.
    :type email: str
    :param db: The database session.
    :type db: AsyncSession
    :return: The user with the specified email, or None if not found.
    :rtype: User or None
    """

    statmnt = select(User).filter_by(email=email)
    user = await db.execute(statmnt)
    user = user.scalar_one_or_none()
    return user



async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):

    """
    Creates a new user and assigns a Gravatar avatar based on their email.

    :param body: The schema containing the user's details.
    :type body: UserSchema
    :param db: The database session.
    :type db: AsyncSession
    :return: The newly created user.
    :rtype: User
    """

    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)

    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db. refresh(new_user)
    return new_user



async def update_token(user: User, token: str | None, db: AsyncSession):

    """
    Updates the refresh token for a user.

    :param user: The user whose token is being updated.
    :type user: User
    :param token: The new refresh token, or None to clear it.
    :type token: str or None
    :param db: The database session.
    :type db: AsyncSession
    """

    user.refresh_token = token
    await db.commit()



async def confirmed_email(email: str, db: AsyncSession):

    """
    Confirms a user's email address.

    :param email: The email address to confirm.
    :type email: str
    :param db: The database session.
    :type db: AsyncSession
    """

    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()



async def update_avatar(email, url: str, db: AsyncSession):

    """
    Updates the avatar URL for a user.

    :param email: The email address of the user whose avatar is being updated.
    :type email: str
    :param url: The new avatar URL.
    :type url: str
    :param db: The database session.
    :type db: AsyncSession
    :return: The updated user.
    :rtype: User
    """

    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user