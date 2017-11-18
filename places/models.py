from django.db import models

from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailadmin.edit_handlers import FieldPanel

from modelcluster.fields import ParentalKey, ParentalManyToManyField

from visualist.models import Record


class Place(Record):
    schema = 'http://schema.org/Place'

    categories = ParentalManyToManyField('PlaceCategory', blank=True)

    # TODO: think on this
    latitude = models.DecimalField(
        decimal_places=7,
        max_digits=10,
    )
    longitude = models.DecimalField(
        decimal_places=7,
        max_digits=10,
    )
    altitude = models.DecimalField(
        decimal_places=7,
        max_digits=10,
        blank=True,
        null=True,
    )
    street = models.TextField(
        blank=True,
        null=True,
    )
    locality = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        default='Chicago',
    )
    REGIONS = (
        ('IL','Illinois'),
        ('IN','Indiana'),
        ('MI','Michigan'),
        ('WI','Wisconsin'),
    )
    region = models.CharField(
        choices=REGIONS,
        max_length=250,
        default="IL",
        blank=True,
        null=True,
    )
    postal_code = models.CharField(
        max_length=250,
        blank=True,
        null=True,
    )
    COUNTRIES = (
        ('CA','Canada'),
        ('FR','France'),
        ('MX','Mexico'),
        ('US','United States'),
    )
    countries = models.CharField(
        choices=COUNTRIES,
        max_length=250,
        default="US",
        blank=True,
        null=True,
    )

    def __str__(self):
        street_single_line = self.street.replace('\r\n', ', ')
        return '{}, {} {}'.format(street_single_line, self.locality, self.region)

    class Meta:
        unique_together = (
            ("latitude", "longitude", "altitude"),
        )


@register_snippet
class PlaceCategory(models.Model):
    name = models.CharField(max_length=255)
    icon = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )

    panels = [
        FieldPanel('name'),
        ImageChooserPanel('icon'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'place categories'
