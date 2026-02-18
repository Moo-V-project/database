from datetime import date
from typing import Literal

from numpy import int_
from numpy.typing import NDArray

Gender = Literal["male", "female", "non-binary"] | None


class Genre:
    def __init__(self, tmdb_id: int, name: str):
        self.name = name


class Country:
    def __init__(self, name: str, iso_3166_1: str):
        self.name = name
        self.iso_3166_1 = iso_3166_1


class Company:
    def __init__(self, tmdb_id: int, name: str, country_id: int | None):
        self.name = name
        self.country_id = country_id


class Job:
    def __init__(self, name: str):
        self.name = name


class Collection:
    def __init__(self, tmdb_id: int, name: str):
        self.name = name


class Person:
    def __init__(
        self,
        name: str,
        birth_date: date | None,
        profile_image: str | None,
        popularity: float | None,
        gender: Gender | None,
        birth_country_id: int | None,
    ):
        self.name = name
        self.birth_date = birth_date
        self.profile_image = profile_image
        self.popularity = popularity
        self.gender = gender
        self.birth_country_id = birth_country_id


class Movie:
    def __init__(
        self,
        tmdb_id: int,
        title: str,
        adult: bool | None,
        overview: str | None,
        overview_vector: NDArray[int_] | None,
        tagline: str | None,
        budget: int | None,
        revenue: int | None,
        runtime: int | None,
        release_date: date | None,
        homepage: str | None,
        poster_url: str | None,
        vote_count: int | None,
        avg_vote: float | None,
        popularity: float | None,
        reviews_sum_vector: NDArray[int_] | None,
        collection_id: int | None,
    ):
        self.tmdb_id = tmdb_id
        self.title = title
        self.adult = adult
        self.overview = overview
        self.overview_vector = overview_vector
        self.tagline = tagline
        self.budget = budget
        self.revenue = revenue
        self.runtime = runtime
        self.release_date = release_date
        self.homepage = homepage
        self.poster_url = poster_url
        self.vote_count = vote_count
        self.avg_vote = avg_vote
        self.popularity = popularity
        self.reviews_sum_vector = reviews_sum_vector
        self.collection_id = collection_id


class CastCreditData:
    def __init__(
        self,
        person_id: int,
        job_id: int,
        character_name: str,
    ):
        self.person_id = person_id
        self.job_id = job_id
        self.character_name = character_name


class CrewCreditData:
    def __init__(
        self,
        person_id: int,
        job_id: int,
    ):
        self.person_id = person_id
        self.job_id = job_id
