from schemas import (
    Genre,
    Movie,
    MoviePerson,
    Person,
    RoleType,
    SourceGenre,
    SourceMovie,
    SourcePerson,
)


class Transformator:
    def __init__(
        self,
        source_movies: list[SourceMovie] = None,
        source_genres: list[SourceGenre] = None,
        source_people: list[SourcePerson] = None,
    ):
        self.source_movies = source_movies
        self.source_genres = source_genres
        self.source_people = source_people

    def get_movies(self) -> list[Movie]:
        movies = {}
        for source_movie in self.source_movies:
            movie_id = source_movie.id

            if movie_id not in movies:
                movies[movie_id] = Movie(
                    id=str(movie_id),
                    imdb_rating=source_movie.rating,
                    genre=source_movie.genre_name,
                    title=source_movie.title,
                    description=source_movie.description,
                )

            if source_movie.role == RoleType.DIRECTOR:
                movies[movie_id].director = source_movie.full_name

            elif source_movie.role == RoleType.ACTOR:
                person_id = str(source_movie.person_id)
                full_name = source_movie.full_name
                if person_id not in {actor.id for actor in movies[movie_id].actors}:
                    movies[movie_id].actors_names.append(full_name)
                    movies[movie_id].actors.append(
                        MoviePerson(
                            id=person_id,
                            name=full_name,
                        )
                    )

            elif source_movie.role == RoleType.WRITER:
                person_id = str(source_movie.person_id)
                full_name = source_movie.full_name
                if person_id not in {writer.id for writer in movies[movie_id].writers}:
                    movies[movie_id].writers_names.append(full_name)
                    movies[movie_id].writers.append(
                        MoviePerson(
                            id=person_id,
                            name=full_name,
                        )
                    )

        return list(movies.values())

    def get_genres(self) -> list[Genre]:
        genres = {}
        for source_genre in self.source_genres:
            movie_id = source_genre.id

            if movie_id not in genres:
                genres[movie_id] = Genre(
                    id=str(movie_id),
                    name=source_genre.name,
                )

        return list(genres.values())

    def get_people(self) -> list[Person]:
        people = {}
        for source_person in self.source_people:
            person_id = source_person.id

            if person_id not in people:
                people[person_id] = Person(
                    id=str(person_id),
                    full_name=source_person.full_name,
                )

        return list(people.values())
