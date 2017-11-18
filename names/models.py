from django import forms
from django.db import models
from django.utils.text import slugify

from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, InlinePanel, FieldRowPanel)
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
    emails = models.ManyToManyField('names.Email', blank=True)
    phones = models.ManyToManyField('names.Phone', blank=True)
    social_accounts = models.ManyToManyField('names.SocialAccount', blank=True)

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

    locations = ParentalManyToManyField('places.Place', blank=True)

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


LABELS = (
    ('primary', 'primary'),
    ('secondary', 'secondary'),
    ('work', 'work'),
    ('personal', 'personal'),
)


@register_snippet
class PersonCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
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
    name = models.CharField(max_length=255, unique=True)
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


class Email(models.Model):
    label = models.CharField(max_length=25, choices=LABELS, default="primary")
    address = models.EmailField(unique=True)
    description = models.TextField(blank=True, null=True)

    panels = [
        FieldPanel('label'),
        FieldPanel('address'),
        FieldPanel('description'),
    ]

    def __str__(self):
        return "{} ({})".format(self.address, self.label)


class Phone(models.Model):
    label = models.CharField(max_length=25, choices=LABELS, default="primary")
    country = models.IntegerField(default=1)
    area_code = models.IntegerField()
    exchange_code = models.IntegerField()
    number = models.IntegerField()
    extension = models.CharField(max_length=25, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    panels = [
        FieldPanel('label'),
        FieldRowPanel([
            FieldPanel('country'),
            FieldPanel('area_code'),
            FieldPanel('exchange_code'),
            FieldPanel('number'),
            FieldPanel('extension'),
        ]),
        FieldPanel('description'),
    ]

    def __str__(self):
        ext = ""
        if self.extension:
            ext = "x{}".format(self.extension)
        return "{} ({}) {}-{}{}".format(
            self.country, self.area_code, self.exchange_code,
            self.number, ext,
        )

    class Meta:
        unique_together = (
            ('country', 'area_code', 'exchange_code', 'number', 'extension'),
        )


class SocialAccount(models.Model):
    SERVICES = (
        ('askfm',     'Ask.fm'),
        ('facebook',  'Facebook'),
        ('flickr',    'Flickr'),
        ('foursquare','Foursquare'),
        ('github',    'GitHub'),
        ('googleplus','Google+'),
        ('instagram', 'Instagram'),
        ('linkedin',  'LinkedIn'),
        ('meetup',    'Meetup'),
        ('pinterest', 'Pinterest'),
        ('reddit',    'Reddit'),
        ('snapchat',  'SnapChat'),
        ('tumblr',    'Tumblr'),
        ('twitter',   'Twitter'),
        ('vine',      'Vine'),
        ('whatsapp',  'WhatsApp'),
        ('yelp',      'Yelp'),
        ('youtube',   'YouTube'),
    )
    service = models.CharField(max_length=25, choices=SERVICES, default="primary")
    account = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)

    panels = [
        FieldPanel('service'),
        FieldPanel('account'),
        FieldPanel('description'),
    ]

    def __str__(self):
        return "{}: {}".format(self.service, self.account)

    class Meta:
        unique_together = (
            ('service', 'account'),
        )
