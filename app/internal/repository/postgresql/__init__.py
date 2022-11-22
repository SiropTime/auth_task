from dependency_injector import containers, providers

from .access_tokens import AccessTokenRepository
from .refresh_tokens import RefreshTokenRepository
from .user import UserRepository


class Repositories(containers.DeclarativeContainer):
    user_repository = providers.Factory(UserRepository)
    refresh_token_repository = providers.Factory(RefreshTokenRepository)
    access_token_repository = providers.Factory(AccessTokenRepository)
