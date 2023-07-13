from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .genre import Genre
from .mixins import TimeStampedMixin, UUIDMixin
from .person import Person


class FilmWork(UUIDMixin, TimeStampedMixin):
    class TypeChoices(models.TextChoices):
        movie = 'movie'
        tv_show = 'tv_show'

    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)
    creation_date = models.DateField(_('creation_date'), blank=True, null=True)
    rating = models.FloatField(
        _('rating'),
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    type = models.TextField(_('type'), choices=TypeChoices.choices)
    genres = models.ManyToManyField(Genre, through='GenreFilmWork')
    people = models.ManyToManyField(Person, through='PersonFilmWork')
    certificate = models.CharField(
        _('certificate'), max_length=512, blank=True, null=True
    )
    file_path = models.FileField(_('file'), blank=True, null=True, upload_to='movies/')

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = _('film_work')
        verbose_name_plural = _('film_works')
        indexes = [
            models.Index(
                fields=['creation_date', 'rating'], name='film_work_date_rating_idx'
            ),
        ]

    def __str__(self):
        return self.title
