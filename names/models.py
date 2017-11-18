from django import forms
from django.db import models
from django.utils.text import slugify

from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.models import register_snippet

from modelcluster.fields import ParentalKey, ParentalManyToManyField

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
    categories = ParentalManyToManyField('PersonCategory', blank=True)
    friends = ParentalManyToManyField('self', blank=True)
    # family_members = ParentalManyToManyField('self', blank=True) # necessary?

    parent_page_types = ['names.PersonIndex', 'names.Organization']
    search_fields = Agent.search_fields + [
        index.SearchField('gender'),
    ]
    content_panels = Agent.content_panels + [
        FieldPanel('gender'),
        FieldPanel('friends', widget=forms.CheckboxSelectMultiple),
    ]

    def split_title(self):
        pass # TODO

    class Meta:
        verbose_name_plural = 'people'


class Organization(Agent):
    schema = 'http://schema.org/Organization'

    nonprofit = models.BooleanField(default=True)
    categories = ParentalManyToManyField('OrganizationCategory', blank=True)
    # owners = ParentalManyToManyField('Person', blank=True,
    #     related_name='organizations_owned') # necessary?
    employees = ParentalManyToManyField('Person',
        blank=True, related_name='employers')
    members = ParentalManyToManyField('Person',
        blank=True, related_name='member_of')

    parent_page_types = [
        'names.OrganizationIndex', 'names.Organization']
    search_fields = Agent.search_fields + []
    content_panels = Agent.content_panels + [
        FieldPanel('nonprofit'),
        FieldPanel('employees', widget=forms.CheckboxSelectMultiple),
        FieldPanel('members', widget=forms.CheckboxSelectMultiple),
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


@register_snippet
class PersonCategory(models.Model):
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
        verbose_name_plural = 'person categories'


@register_snippet
class OrganizationCategory(models.Model):
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
        verbose_name_plural = 'organization categories'
