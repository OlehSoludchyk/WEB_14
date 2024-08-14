from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import users as repositories_users
from src.schemas.user import UserSchema, TokenSchema, UserResponse, RequestEmail
from src.services.auth import auth_service
from src.services.email import send_email
from src.conf import messages

router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, bt: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):

    """
    Registers a new user, hashes the password, and sends a confirmation email.

    :param body: The schema containing the user's signup details.
    :type body: UserSchema
    :param bt: Background tasks for sending the confirmation email.
    :type bt: BackgroundTasks
    :param request: The HTTP request object.
    :type request: Request
    :param db: The database session.
    :type db: AsyncSession
    :return: The newly created user.
    :rtype: UserResponse
    :raises HTTPException: If the user already exists.
    """

    exist_user = await repositories_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=messages.ACCOUNT_EXIST)
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repositories_users.create_user(body, db)
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user



@router.post("/login", response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):

    """
    Authenticates a user and returns access and refresh tokens.

    :param body: The login form containing the user's credentials.
    :type body: OAuth2PasswordRequestForm
    :param db: The database session.
    :type db: AsyncSession
    :return: The access and refresh tokens.
    :rtype: TokenSchema
    :raises HTTPException: If the user does not exist, email is not confirmed, or password is incorrect.
    """

    user = await repositories_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email is not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}



@router.get('/refresh_token', response_model=TokenSchema)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(get_refresh_token), 
                        db: AsyncSession = Depends(get_db)):
    
    """
    Refreshes the access and refresh tokens for a user.

    :param credentials: The HTTP authorization credentials containing the refresh token.
    :type credentials: HTTPAuthorizationCredentials
    :param db: The database session.
    :type db: AsyncSession
    :return: The new access and refresh tokens.
    :rtype: TokenSchema
    :raises HTTPException: If the refresh token is invalid.
    """

    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repositories_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}



@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):

    """
    Confirms a user's email address using a confirmation token.

    :param token: The confirmation token sent to the user's email.
    :type token: str
    :param db: The database session.
    :type db: AsyncSession
    :return: A message indicating whether the email was confirmed or if it was already confirmed.
    :rtype: dict
    :raises HTTPException: If the user does not exist or the token is invalid.
    """

    email = await auth_service.get_email_from_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repositories_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}



@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    
    """
    Requests an email confirmation by sending a new confirmation email.

    :param body: The schema containing the user's email address.
    :type body: RequestEmail
    :param background_tasks: Background tasks for sending the confirmation email.
    :type background_tasks: BackgroundTasks
    :param request: The HTTP request object.
    :type request: Request
    :param db: The database session.
    :type db: AsyncSession
    :return: A message indicating that the confirmation email has been sent.
    :rtype: dict
    """

    user = await repositories_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}
