from __future__ import absolute_import

from django.contrib import admin

from .models import Band, Concert, Song


site = admin.AdminSite(name="admin")


class ConcertInline(admin.TabularInline):
    model = Concert
    fk_name = 'main_band'


class SongInline(admin.TabularInline):
    model = Song


class BandAdmin(admin.ModelAdmin):
    inlines = [
        ConcertInline,
        SongInline,
    ]

    def get_formsets(self, request, obj=None):
        for inline in self.get_inline_instances(request):
            # Only in change view.
            if obj is None:
                continue
            # Do not return the concert inline
            if isinstance(inline, SongInline):
                yield inline.get_formset(request, obj), inline


site.register(Band, BandAdmin)
