from __future__ import unicode_literals

from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.models import Image, AbstractImage, AbstractRendition
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel


class Record(Page):
    schema = 'http://schema.org/Thing'

    body = RichTextField(blank=True, null=True)
    same_as = models.URLField(blank=True, null=True)

    oclc_fast_id = models.IntegerField(blank=True, null=True)
    in_cpl_artistfiles = models.BooleanField(default=False)

    # copyright_status = models.TextField() # TODO: better way?
    source = models.ForeignKey('visualist.Source', blank=True, null=True,
        on_delete=models.PROTECT,)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full"),
        FieldPanel('same_as'),
        FieldPanel('oclc_fast_id'),
        SnippetChooserPanel('source'),
    ]

    def citation(self): # TODO
        pass

    def date(self): # TODO
        pass

    class Meta:
        abstract = True

    def cpl_url(self):
        if self.in_cpl_artistfiles:
            return 'https://www.chipublib.org/fa-chicago-artists-archive/'
        return None


@register_snippet
class Source(models.Model):
    # TODO this clearly needs work
    title       = models.CharField(max_length=250)
    authors     = models.CharField(max_length=250, blank=True, null=True) # list, etc.
    editors     = models.CharField(max_length=250, blank=True, null=True)
    translators = models.CharField(max_length=250, blank=True, null=True)
    identifiers = models.CharField(max_length=250, blank=True, null=True) # e.g. ISBN
    archive     = models.CharField(max_length=250, blank=True, null=True)
    edition     = models.CharField(max_length=250, blank=True, null=True)
    pages       = models.CharField(max_length=250, blank=True, null=True)
    volume      = models.CharField(max_length=250, blank=True, null=True)
    series      = models.CharField(max_length=250, blank=True, null=True)
    same_as     = models.URLField(blank=True, null=True)

    panels = [
        FieldPanel('title'),
        FieldPanel('authors'),
        FieldPanel('editors'),
        FieldPanel('translators'),
        FieldPanel('identifiers'),
        FieldPanel('archive'),
        FieldPanel('edition'),
        FieldPanel('pages'),
        FieldPanel('volume'),
        FieldPanel('series'),
    ]

    def __str__(self):
        return '{} by {}'.format(self.title, self.authors)


# TODO: Modifying Images (following) will require editing the admin templates.
# class CustomImage(AbstractImage):
#     schema = 'http://schema.org/ImageObject'
#     caption = models.CharField(max_length=250, blank=True, null=True) # doesn't it already have one? confirm
#     # checksum = models.CharField(max_length=250) # TODO
#     # version = models.CharField(max_length=25) # TODO: necessary?
#     # copyright_status = models.TextField() # TODO: better way?
#     source = models.ForeignKey('visualist.Source', blank=True, null=True,
#         on_delete=models.PROTECT,)
#     admin_form_fields = Image.admin_form_fields + (
#         # Then add the field names here to make them appear in the form:
#         'caption',
#     )
# class CustomRendition(AbstractRendition):
#     image = models.ForeignKey('visualist.CustomImage', related_name='renditions')
#     class Meta:
#         unique_together = (
#             ('image', 'filter_spec', 'focal_point_key'),
#         )
