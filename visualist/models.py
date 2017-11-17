from __future__ import unicode_literals

from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel


class Record(Page):
    body = RichTextField(blank=True)
    same_as = models.URLField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full"),
        FieldPanel('same_as'),
    ]

    def citation(self): # TODO
        pass

    def date(self): # TODO
        pass

    class Meta:
        abstract = True
