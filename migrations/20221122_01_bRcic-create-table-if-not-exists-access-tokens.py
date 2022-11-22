

from yoyo import step

__depends__ = {'20220921_02_T4QNa-create-refresh-tokens-table'}

steps = [
    step("""
create table if not exists access_tokens(
         id serial primary key,
         refresh_id int references refresh_tokens(id) ON DELETE CASCADE,
         access_token text not null unique,
         constraint all_values_in_access_are_unique unique (
                    refresh_id, access_token
                )
         
         );
""")
]
