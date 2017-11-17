from django import forms
from django.db import models
from django.utils.text import slugify

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailsearch import index

from visualist.models import Record


class Agent(Record):
    schema = 'http://xmlns.com/foaf/spec/#term_Agent'

    getty_ulan_id = models.IntegerField(blank=True, null=True)

    parent_page_types = []
    content_panels = Page.content_panels + [
        FieldPanel('getty_ulan_id'),
        FieldPanel('oclc_fast_id'),

        # following not currently possible, as per https://goo.gl/nNfNWQ # TODO
        # FieldPanel('organizer_of', widget=forms.CheckboxSelectMultiple),
    ]


class Person(Agent):
    schema = 'http://schema.org/Person'

    GENDERS = (
        ('m', 'male'),
        ('f', 'female'),
        ('x', 'other'),
    )
    gender = models.CharField(choices=GENDERS,
        max_length=1, blank=True, null=True)

    parent_page_types = ['names.PersonIndex', 'names.Organization']
    search_fields = Agent.search_fields + [
        index.SearchField('gender'),
    ]
    content_panels = Agent.content_panels + [
        FieldPanel('gender'),
    ]

    def split_title(self):
        pass # TODO

    class Meta:
        verbose_name_plural = 'people'


class Organization(Agent):
    schema = 'http://schema.org/Organization'

    nonprofit = models.BooleanField(default=True)

    parent_page_types = [
        'names.OrganizationIndex', 'names.Organization']
    search_fields = Agent.search_fields + []
    content_panels = Agent.content_panels + [
        FieldPanel('nonprofit'),
    ]


class PersonIndex(Page):
    schema = 'http://schema.org/ItemList'

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        people = self.get_children().live().order_by('-first_published_at')
        context['people'] = people
        return context


class OrganizationIndex(Page):
    schema = 'http://schema.org/ItemList'

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
