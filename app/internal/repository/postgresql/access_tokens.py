from typing import List

from app.pkg.models.access_token import AccessToken
from .connection import get_connection
from app.internal.repository.repository import Repository
from .handlers.collect_response import collect_response


class AccessTokenRepository(Repository):

    @collect_response
    async def create(self, cmd: AccessToken) -> AccessToken:
        query = """
                INSERT INTO access_tokens(refresh_id, access_token)
                    VALUES (%(refresh_id)s, %(access_token)s)
                RETURNING *;
                """
        async with get_connection() as cur:
            await cur.execute(query, cmd.to_dict(show_secrets=True))
            return await cur.fetchone()

    @collect_response
    async def read(self, query: AccessToken) -> AccessToken:
        q = """
            SELECT refresh_id, access_token from access_tokens
            WHERE access_token = %(access_token)s and refresh_id = %(refresh_id)s;
            """
        async with get_connection() as cur:
            await cur.execute(q, query.to_dict(show_secrets=True))
            return await cur.fetchone()

    async def read_all(self) -> List[AccessToken]:
        raise NotImplementedError

    @collect_response
    async def update(self, cmd: AccessToken) -> AccessToken:
        q = """
            UPDATE access_tokens SET access_token = %(access_token)s
                WHERE refresh_id = %(refresh_id)s
            RETURNING *;
            """

        async with get_connection() as cur:
            await cur.execute(q, cmd.to_dict(show_secrets=True))
            return await cur.fetchone()

    @collect_response
    async def delete(self, cmd: AccessToken) -> AccessToken:
        q = """
            DELETE FROM access_tokens
                WHERE refresh_id = %(refresh_id)s
            RETURNING *;
            """

        async with get_connection() as cur:
            await cur.execute(q, cmd.to_dict(show_secrets=True))
            return await cur.fetchone()
