from typing import Optional

from app.internal.pkg.password import password
from app.internal.repository.exceptions import EmptyResult, UniqueViolation
from app.internal.repository.postgresql import RefreshTokenRepository
from app.internal.repository.postgresql.access_tokens import AccessTokenRepository
from app.internal.services.user import UserService
from app.pkg.jwt import UnAuthorized, WrongToken
from app.pkg.models.access_token import AccessToken
from app.pkg.models.auth import AuthCommand
from app.pkg.models.exceptions.auth import IncorrectUsernameOrPassword
from app.pkg.models.otp import Check2FACommand
from app.pkg.models.refresh_token import (
    CreateJWTTokenCommand,
    DeleteJWTTokenCommand,
    JWTToken,
    ReadJWTTokenQuery,
    ReadJWTTokenQueryByFingerprint,
    UpdateJWTTokenCommand,
)
from app.pkg.models.user import ReadUserByUserNameQuery, User
from app.pkg.otp.otp import OTPService

__all__ = ["AuthService"]


class AuthService:
    refresh_token_repository: RefreshTokenRepository
    access_token_repository: AccessTokenRepository
    user_service: UserService
    otp_service: OTPService

    def __init__(
        self,
        user_service: UserService,
        refresh_token_repository: RefreshTokenRepository,
        access_token_repository: AccessTokenRepository,
        otp_service: OTPService,
    ):
        self.user_service = user_service
        self.refresh_token_repository = refresh_token_repository
        self.access_token_repository = access_token_repository
        self.otp_service = otp_service

    def check_2fa(self, cmd: Check2FACommand):
        return self.otp_service.verify_2fa_auth(cmd)

    async def check_user_password(self, cmd: AuthCommand) -> User:
        user = await self.user_service.read_specific_user_by_username(
            query=ReadUserByUserNameQuery(username=cmd.username),
        )
        if user is None or not password.check_password(cmd.password, user.password):
            raise IncorrectUsernameOrPassword

        return user

    async def check_user_exist_refresh_token(
        self,
        query: ReadJWTTokenQueryByFingerprint,
    ) -> Optional[JWTToken]:
        try:
            return await self.refresh_token_repository.read_by_fingerprint(
                query=query,
            )
        except EmptyResult:
            return

    async def check_refresh_token_exists(self, query: ReadJWTTokenQuery) -> JWTToken:
        try:
            return await self.refresh_token_repository.read(
                query=query,
            )
        except UniqueViolation:
            raise WrongToken
        except EmptyResult:
            raise UnAuthorized

    async def create_refresh_token(self, cmd: CreateJWTTokenCommand, access_token: str) -> JWTToken:
        try:
            rt: JWTToken = await self.refresh_token_repository.create(cmd=cmd)
            at: AccessToken = await self.access_token_repository.create(cmd=AccessToken(refresh_id=rt.id,
                                                                                        access_token=access_token))
            return rt
        except UniqueViolation:
            return await self.refresh_token_repository.update(
                cmd=UpdateJWTTokenCommand(
                    user_id=cmd.user_id,
                    refresh_token=cmd.refresh_token,
                    fingerprint=cmd.fingerprint,
                ),
            )

    async def update_refresh_token(self, cmd: UpdateJWTTokenCommand, access_token: str) -> JWTToken:
        rt: JWTToken = await self.refresh_token_repository.update(cmd)
        at: AccessToken = await self.access_token_repository.update(
            cmd=AccessToken(refresh_id=rt.id, access_token=access_token)
        )
        return rt

    async def delete_refresh_token(self, cmd: DeleteJWTTokenCommand) -> JWTToken:
        try:
            return await self.refresh_token_repository.delete(
                cmd=cmd,
            )
        except EmptyResult:
            raise UnAuthorized
