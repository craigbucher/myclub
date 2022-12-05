from django.contrib import admin
from .models import Venue
from .models import Event
from .models import MyClubUser
from django.contrib.auth.models import Group

# admin.site.register(Venue)
# admin.site.register(Event)
admin.site.register(MyClubUser)
# removes groups from admin panel (since we don't use them)
admin.site.unregister(Group)


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone')
    ordering = ('name',)  # <-- tuple, so have to add comma or will error
    search_fields = ('name', 'address')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    fields = (('name', 'venue'), 'date', 'description', 'manager', 'approved')
    list_display = ('name', 'date', 'venue')
    list_filter = ('date', 'venue')
    # <-- tuple, so have to add a comma or will error
    ordering = ('-date',)
