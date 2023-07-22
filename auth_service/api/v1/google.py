from typing import Annotated

from async_fastapi_jwt_auth import AuthJWT
from constants import GOOGLE_SCOPES
from core.settings import settings
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.logger import logger
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from models import History, User
from schemas import (
    GoogleToken,
    GoogleUserCreate,
    Tokens,
    UserCreated,
    UserInfo,
    UserResponse,
)
from sqlalchemy.exc import IntegrityError
from starlette import status


router = APIRouter()


@router.post('/auth', response_model=GoogleToken)
async def auth():
    flow = Flow.from_client_config(
        client_config=settings.google_client_config,
        scopes=GOOGLE_SCOPES,
        redirect_uri=settings.google_redirect_uri,
    )
    auth_uri = flow.authorization_url()

    logger.info(f"GOOGLE AUTH REDIRECT: {auth_uri[0]}")
    return RedirectResponse(auth_uri[0])


@router.get('/auth_return', response_model=Tokens)
async def auth_return(
    code: Annotated[str | None, Query()] = None,
    error: Annotated[str | None, Query()] = None,
    state: Annotated[str | None, Query()] = None,
    scope: Annotated[str | None, Query()] = None,
    authuser: Annotated[int | None, Query()] = None,
    prompt: Annotated[str | None, Query()] = None,
    user_agent: str = Header(default=None),
    authorize: AuthJWT = Depends(),
) -> Tokens:
    if error is not None:
        HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization not allowed'
        )

    if code is None:
        HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Authorization code not got'
        )

    flow = Flow.from_client_config(
        client_config=settings.google_client_config,
        scopes=GOOGLE_SCOPES,
        redirect_uri=settings.google_redirect_uri,
    )
    try:
        flow.fetch_token(code=code)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    credentials = flow.credentials
    user_info_service = build('oauth2', 'v2', credentials=credentials)
    raw_user_info = user_info_service.userinfo().get().execute()
    user_info = UserInfo.parse_obj(raw_user_info)

    db_user = await User.get_by_google_id(google_id=user_info.id)
    if db_user is None:
        google_user_create = GoogleUserCreate(
            google_id=user_info.id,
            email=user_info.email,
            first_name=user_info.given_name,
            last_name=user_info.family_name,
        )
        user_dto = jsonable_encoder(google_user_create)
        try:
            db_user = await User.create(**user_dto)

        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='User with such login is registered already',
            )

    user_in_db = UserCreated.from_orm(db_user)
    user = UserResponse.parse_obj(user_in_db)
    tokens = await Tokens.create(
        authorize=authorize,
        user=user,
        user_agent=user_agent,
    )

    db_history = History(
        user_id=db_user.id,
        user_agent=user_agent,
    )
    await db_history.save()

    return tokens
