from django.db import models
from django.utils.text import slugify

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailsearch import index

from visualist.models import Record


class Entity(Page):
    pass


class Person(Entity):
    GENDERS = (
        ('m', 'male'),
        ('f', 'female'),
        ('x', 'other'),
    )
    gender = models.CharField(choices=GENDERS,
        max_length=1, blank=True, null=True)

    search_fields = Entity.search_fields + [
        index.SearchField('gender'),
    ]

    content_panels = Entity.content_panels + [
        FieldPanel('gender'),
    ]


class Organization(Entity):
    nonprofit = models.BooleanField(default=True)

    search_fields = Entity.search_fields + []

    content_panels = Entity.content_panels + [
        FieldPanel('nonprofit'),
    ]


class PersonIndex(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        peoplepages = self.get_children().live().order_by('-first_published_at')
        context['peoplepages'] = peoplepages
        return context


class OrganizationIndex(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        organizations = self.get_children().live().order_by('-first_published_at')
        context['organizations'] = organizations
        return context
