from django.contrib import admin

from breaks.models.replacements import GroupInfo
from organisations.models import dicts, groups, offers, organisations


##############################
# INLINES
##############################
class EmployeeInline(admin.TabularInline):
    model = organisations.Employee
    fields = ('user', 'position', 'date_joined',)


class OfferInline(admin.TabularInline):
    model = offers.Offer
    fields = ('org_accept', 'user', 'user_accept',)


class MemberInline(admin.TabularInline):
    model = groups.Member
    fields = ('employee', 'date_joined',)


class ProfileBreakInline(admin.StackedInline):
    model = GroupInfo
    fields = (
        'min_active',
        'break_start',
        'break_end',
        'break_max_duration',
    )


##############################
# MODELS
##############################
@admin.register(dicts.Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'name', 'sort', 'is_active',
    )


@admin.register(organisations.Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'director',)
    filter_vertical = ('employees',)
    inlines = (EmployeeInline, OfferInline,)
    readonly_fields = (
        'created_at', 'created_by', 'updated_at', 'updated_by',
    )


@admin.register(groups.Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'manager', )
    list_display_links = ('id', 'name',)
    search_fields = ('name',)
    inlines = (
        ProfileBreakInline,
        MemberInline,
    )
    readonly_fields = (
        'created_at', 'created_by', 'updated_at', 'updated_by',
    )


@admin.register(offers.Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'organisation', 'org_accept', 'user', 'user_accept',)
    search_fields = ('organisation__name', 'user__last_name',)

    readonly_fields = (
        'created_at', 'created_by', 'updated_at', 'updated_by',
    )
