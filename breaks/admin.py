from django.contrib import admin
from django.contrib.admin import TabularInline
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html

from breaks.models import organisations, groups, replacements, dicts, breaks


##############################
# INLINES
##############################
class ReplacementEmployeeInline(TabularInline):
    model = replacements.ReplacementEmployee
    fields = ('employee', 'status',)


##############################
# MODELS
##############################
@admin.register(organisations.Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'director',)
    filter_vertical = ('employees',)


@admin.register(groups.Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'manager', 'min_active', 'replacement_count',)
    list_display_links = ('id', 'name',)
    search_fields = ('name',)

    def replacement_count(self, obj):
        return obj.replacement_count

    replacement_count.short_description = 'Кол-во смен'

    def get_queryset(self, request):
        queryset = groups.Group.objects.annotate(
            replacement_count=Count('replacements__id')
        )
        return queryset


@admin.register(dicts.ReplacementStatus)
class ReplacementStatusAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'name', 'sort', 'is_active',
    )


@admin.register(dicts.BreakStatus)
class BreakStatusAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'name', 'sort', 'is_active',
    )


@admin.register(replacements.Replacement)
class ReplacementAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'group', 'date', 'break_start', 'break_end', 'break_max_duration',
    )
    autocomplete_fields = ('group',)
    inlines = (
        ReplacementEmployeeInline,
    )


@admin.register(breaks.Break)
class BreakAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'replacement_link', 'break_start', 'break_end', 'status',
    )
    list_filter = ('status',)
    empty_value_display = 'Unknown'
    radio_fields = {'status': admin.VERTICAL}

    def replacement_link(self, obj):
        link = reverse(
            'admin:breaks_replacement_change', args=[obj.replacement.id]
        )
        return format_html('<a href="{}">{}</a>', link, obj.replacement)

