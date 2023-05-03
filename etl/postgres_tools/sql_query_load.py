class RoleType:
    ACTOR = {'name': 'actor', 'name_plural': 'actors', 'explanatory_name': 'actors_names', }
    WRITER = {'name': 'writer', 'name_plural': 'writers', 'explanatory_name': 'writers_names', }
    DIRECTOR = {'name': 'director', }


def get_updated_genres(last_update_time):
    return f"""
    SELECT g.id, g.name, g.updated_at
    FROM content.genre g
    WHERE g.updated_at > '{last_update_time}'
        ORDER BY updated_at
    """


def get_updated_ids_query(table_name: str, last_update_time: str, limit: int) -> str:
    query = f"""
    SELECT id, updated_at
    FROM {table_name}
    WHERE updated_at > '{last_update_time}'
    ORDER BY updated_at
    """
    return query


def get_films_by_related_ids_query(table_name: str, related_ids: list[str], limit: int) -> str:
    related_ids_line = ', '.join(f"'{id_}'" for id_ in related_ids)
    if table_name not in ('person', 'genre'):
        raise ValueError("Invalid table name. Supported tables are 'person' and 'genre'.")

    related_table = 'content.person_film_work' if table_name == 'person' else 'content.genre_film_work'
    related_id_field = 'person_id' if table_name == 'person' else 'genre_id'

    query = f"""
    SELECT fw.id
    FROM content.film_work fw
    LEFT JOIN {related_table} r ON r.film_work_id = fw.id
    WHERE r.{related_id_field} IN ({related_ids_line})
    ORDER BY fw.updated_at
    """
    return query


def get_film_data_query(film_ids: list[str], limit: int) -> str:
    film_ids_line = ', '.join(f"'{id_}'" for id_ in film_ids)
    query = f"""
    SELECT fw.id, fw.title, fw.description, fw.rating as imdb_rating,
        COALESCE(json_agg(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) 
            FILTER (WHERE pfw.role = '{RoleType.ACTOR['name']}'), '[]') as {RoleType.ACTOR['name_plural']},
        COALESCE(json_agg(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) 
            FILTER (WHERE pfw.role = '{RoleType.WRITER['name']}'), '[]') as {RoleType.WRITER['name_plural']},
        COALESCE(json_agg(DISTINCT p.full_name)
            FILTER (WHERE pfw.role = '{RoleType.ACTOR['name']}'), '[]') as {RoleType.ACTOR['explanatory_name']},
        COALESCE(json_agg(DISTINCT p.full_name)
            FILTER (WHERE pfw.role = '{RoleType.DIRECTOR['name']}'), '[]') as {RoleType.DIRECTOR['name']},
        COALESCE(json_agg(DISTINCT p.full_name)
            FILTER (WHERE pfw.role = '{RoleType.WRITER['name']}'), '[]') as {RoleType.WRITER['explanatory_name']},
        array_agg(DISTINCT g.name) as genre
    FROM content.film_work fw
    LEFT JOIN content.genre_film_work gfw ON fw.id = gfw.film_work_id
    LEFT JOIN content.genre g ON gfw.genre_id = g.id
    LEFT JOIN content.person_film_work pfw ON fw.id = pfw.film_work_id
    LEFT JOIN content.person p ON pfw.person_id = p.id
    WHERE fw.id IN ({film_ids_line})
    GROUP BY fw.id
    """
    return query
