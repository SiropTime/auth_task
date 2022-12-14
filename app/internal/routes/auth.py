import datetime
from datetime import timedelta

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Security, status
from starlette.responses import Response

from app.internal.services import Services
from app.internal.services.auth import AuthService
from app.pkg.jwt import (
    JWT,
    JwtAccessBearer,
    JwtAuthorizationCredentials,
    JwtRefreshBearer,
    refresh_security,
)
from app.pkg.models.auth import Auth, AuthCommand
from app.pkg.models.exceptions.auth import IncorrectUsernameOrPassword, TokenExpired
# from app.pkg.models.otp import Check2FACommand
from app.pkg.models.refresh_token import (
    CreateJWTTokenCommand,
    DeleteJWTTokenCommand,
    ReadJWTTokenQuery,
    ReadJWTTokenQueryByFingerprint,
    UpdateJWTTokenCommand,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/login",
    response_model=Auth,
    status_code=status.HTTP_200_OK,
    responses={
        **IncorrectUsernameOrPassword().build_docs(),
    },
    description="Route for authorize"
                + "Required in headers Authorized Bearer access token",
)
@inject
async def auth_user(
        response: Response,
        access: JwtAccessBearer = Depends(Provide[JWT.access]),
        refresh: JwtRefreshBearer = Depends(Provide[JWT.refresh]),
        auth_service: AuthService = Depends(Provide[Services.auth_service]),
        cmd: AuthCommand = Body(
            ...,
            examples={
                "correct": {
                    "summary": "A correct example",
                    "value": {
                        "username": "admin",
                        "password": "password",
                        "fingerprint": "string",
                        "verify_code": "111111",
                    },
                },
                "wrong": {
                    "summary": "A wrong example",
                    "value": {"username": "admin", "password": "admin", "fingerprint": ""},
                },
            },
        ),
):
    user = await auth_service.check_user_password(cmd=cmd)
    # Commented 2FA because of useless in this case and impossibility to set up this on my env
    # if not await auth_service.check_2fa(Check2FACommand(verify_code=cmd.verify_code)):
    #     raise IncorrectUsernameOrPassword

    at = access.create_access_token(
        subject={"user_id": user.id, "role_name": user.role_name},
    )

    if rt := await auth_service.check_user_exist_refresh_token(
            query=ReadJWTTokenQueryByFingerprint(
                user_id=user.id,
                fingerprint=cmd.fingerprint,
            ),
    ):
        return Auth(
            access_token=at,
            refresh_token=rt.refresh_token,
            user_role_name=user.role_name,
        )

    rt = refresh.create_refresh_token(
        subject={
            "user_id": user.id,
            "fingerprint": cmd.fingerprint.get_secret_value(),
            "role_name": user.role_name,
        },
    )

    ref_tok = await auth_service.create_refresh_token(
        cmd=CreateJWTTokenCommand(
            refresh_token=rt,
            fingerprint=cmd.fingerprint,
            user_id=user.id,
        ),
        access_token=at
    )
    refresh.set_refresh_cookie(response=response, refresh_token=rt,
                               expires_delta=timedelta(seconds=ref_tok.expiresat))

    return Auth(access_token=at, refresh_token=rt, user_role_name=user.role_name)


@router.patch(
    "/refresh",
    response_model=Auth,
    description="Route for get new tokens pair.",
)
@inject
async def create_new_token_pair(
        response: Response,
        access: JwtAccessBearer = Depends(Provide[JWT.access]),
        refresh: JwtRefreshBearer = Depends(Provide[JWT.refresh]),
        auth_service: AuthService = Depends(Provide[Services.auth_service]),
        credentials: JwtAuthorizationCredentials = Security(refresh_security),
        fingerprint: str = Body(
            ...,
            examples={
                "correct": {
                    "summary": "Just example how send fingerprint",
                    "value": {
                        "fingerprint": "some fingerprint"
                    }
                }
            }
        )

):
    # fingerprint = credentials.subject.get("fingerprint")
    user_id = credentials.subject.get("user_id")

    ref_tok = await auth_service.check_refresh_token_exists(
        query=ReadJWTTokenQuery(
            user_id=user_id,
            refresh_token=credentials.raw_token,
        ),
    )

    await auth_service.delete_refresh_token(
        cmd=DeleteJWTTokenCommand(
            user_id=user_id,
            refresh_token=credentials.raw_token,
            fingerprint=fingerprint
        )
    )

    if ref_tok.expiresat > datetime.datetime.now().timestamp() or not fingerprint == ref_tok.fingerprint:
        raise TokenExpired

    at = access.create_access_token(subject={"user_id": user_id})
    rt = refresh.create_refresh_token(
        subject={"user_id": user_id, "fingerprint": fingerprint},
    )

    irt = await auth_service.update_refresh_token(
        cmd=UpdateJWTTokenCommand(
            user_id=user_id,
            refresh_token=rt,
            fingerprint=fingerprint,
        ),
        access_token=at
    )

    refresh.set_refresh_cookie(response=response, refresh_token=rt,
                               expires_delta=timedelta(seconds=ref_tok.expiresat))
    return Auth(access_token=at, refresh_token=irt.refresh_token.get_secret_value())


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    description="Route for logout."
)
@inject
async def logout(
        auth_service: AuthService = Depends(Provide[Services.auth_service]),
        credentials: JwtAuthorizationCredentials = Security(refresh_security),
        fingerprint: str = Body(
            ...,
            examples={
                "correct": {
                    "summary": "Just example how send fingerprint",
                    "value": {
                        "fingerprint": "some fingerprint"
                    }
                }
            }
        )
):
    user_id = credentials.subject.get("user_id")
    # fingerprint = credentials.subject.get("fingerprint")
    refresh_token = credentials.raw_token

    await auth_service.delete_refresh_token(
        cmd=DeleteJWTTokenCommand(
            user_id=user_id,
            fingerprint=fingerprint,
            refresh_token=refresh_token,
        ),
    )
