import datetime
import pdb
from datetime import timedelta

from crum import get_current_user
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from breaks.constants import REPLACEMENT_MEMBER_ONLINE, \
    REPLACEMENT_MEMBER_OFFLINE, REPLACEMENT_MEMBER_BUSY, \
    REPLACEMENT_MEMBER_BREAK
from breaks.models.replacements import Replacement, GroupInfo, ReplacementMember
from breaks.serializers.internal.replacements import ReplacementStatsSerializer, \
    ReplacementGeneralSerializer, ReplacementPersonalStatsSerializer, \
    ReplacementBreakSerializer
from breaks.serializers.nested.replacements import \
    ReplacementMemberShortSerializer
from common.serializers.mixins import InfoModelSerializer, DictMixinSerializer
from organisations.models.groups import Member, Group
from organisations.serializers.nested.groups import GroupShortSerializer

User = get_user_model()


class ReplacementListSerializer(InfoModelSerializer):
    group = GroupShortSerializer(source='group.group')
    stats = ReplacementStatsSerializer(source='*')

    class Meta:
        model = Replacement
        fields = (
            'id',
            'group',
            'date',
            'break_start',
            'break_end',
            'break_max_duration',
            'min_active',
            'stats',
        )


class ReplacementRetrieveSerializer(InfoModelSerializer):
    group = GroupShortSerializer(source='group.group')
    # stats = ReplacementStatsSerializer(source='*')

    stats = serializers.SerializerMethodField()
    general = ReplacementGeneralSerializer(source='*')
    personal_stats = serializers.SerializerMethodField()
    breaks = ReplacementBreakSerializer(source='*')
    actions = serializers.SerializerMethodField()
    members = ReplacementMemberShortSerializer(source='members_info', many=True)

    class Meta:
        model = Replacement
        fields = (
            'id',
            'group',
            'date',
            'break_start',
            'break_end',
            'break_max_duration',
            'min_active',
            'stats',
            'personal_stats',
            'breaks',
            'actions',
            'members',
            'general',
        )

    def get_personal_stats(self, instance):
        user = get_current_user()
        member = instance.get_member_by_user(user)
        return ReplacementPersonalStatsSerializer(member).data

    def get_stats(self, instance):
        result = self.Meta.model.objects.filter(pk=instance.pk).aggregate(
            members_count=Count('members', distinct=True),
            breaks_count=Count('breaks', distinct=True),
            members_online=Count('members', filter=Q(members_info__status_id=REPLACEMENT_MEMBER_ONLINE), distinct=True),
            members_offline=Count('members', filter=Q(members_info__status_id=REPLACEMENT_MEMBER_OFFLINE), distinct=True),
            members_busy=Count('members', filter=Q(members_info__status_id=REPLACEMENT_MEMBER_BUSY), distinct=True),
            members_break=Count('members', filter=Q(members_info__status_id=REPLACEMENT_MEMBER_BREAK), distinct=True),
        )
        return result

    def get_actions(self, instance):
        result = {
            'replacement_button': None,
            'break_button': None,
        }
        now = datetime.datetime.now().astimezone()
        if instance.date != now.date():
            return result
        user = get_current_user()
        member = instance.get_member_by_user(user)
        if not member:
            return result

        # replacement_button
        if not member.time_online:
            result['replacement_button'] = 'online'
        elif not member.time_offline:
            result['replacement_button'] = 'offline'

        # breaks_button
        break_obj = instance.get_break_for_user(user)
        if not break_obj:
            replacement_finish = datetime.datetime.combine(
                instance.date, instance.break_end
            ).astimezone()
            if replacement_finish - datetime.timedelta(minutes=30) >= now:
                result['break_button'] = 'create'
        else:
            member_break_start = datetime.datetime.combine(
                now.date(), break_obj.break_start
            ).astimezone()

            if not member.time_break_start:
                if now + timedelta(minutes=5) < member_break_start:
                    result['break_button'] = 'coming'
                else:
                    result['break_button'] = 'start'
            elif not member.time_break_end:
                result['break_button'] = 'finish'

            return result


class ReplacementCreateSerializer(InfoModelSerializer):
    group =serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all()
    )
    members = serializers.PrimaryKeyRelatedField(
        queryset=Member.objects.all(), many=True, allow_null=True, required=False,
    )
    all_group_members = serializers.BooleanField(default=False)
    remember_default_data = serializers.BooleanField(default=False)

    class Meta:
        model = Replacement
        fields = (
            'id',
            'group',
            'date',
            'break_start',
            'break_end',
            'break_max_duration',
            'min_active',
            'members',
            'all_group_members',
            'remember_default_data',
        )
        extra_kwargs = {
            'break_start': {'required': False, 'allow_null': True},
            'break_end': {'required': False, 'allow_null': True},
            'break_max_duration': {'required': False, 'allow_null': True},
            'min_active': {'required': False, 'allow_null': True},
        }

    def create(self, validated_data):
        remember_data = validated_data.pop('remember_default_data', False)
        all_group_members = validated_data.pop('all_group_members', False)

        with transaction.atomic():
            if hasattr(validated_data['group'], 'breaks_info'):
                validated_data['group'] = validated_data['group'].breaks_info
            else:
                validated_data['group'] = GroupInfo.objects.create(
                    group=validated_data['group'],
                )

            if all_group_members:
                validated_data.pop('members', list())
                members = validated_data['group'].group.members_info.all()
            else:
                members = validated_data.pop('members')
            instance = super().create(validated_data)

            instance.members.set(
                members, through_defaults={'status_id': 'offline'}
            )

            if remember_data:
                defaults = {
                    'break_start': validated_data['break_start'],
                    'break_end': validated_data['break_end'],
                    'break_max_duration': validated_data['break_max_duration'],
                    'min_active': validated_data['min_active'],
                }
                group = instance.group
                for key, value in defaults.items():
                    setattr(group, key, value)
                group.save()

            return instance

    def validate(self, attrs):

        # Check params
        required_fields = (
            'break_start', 'break_end', 'break_max_duration', 'min_active',
        )
        for field in required_fields:
            try:
                from_default = getattr(attrs['group'].breaks_info, field)
            except:
                from_default = None

            from_request = attrs.get(field)
            field_data = from_request or from_default

            if not field_data:
                field_name = getattr(self.Meta.model, field).field.verbose_name
                raise ParseError(
                    f'{field_name} - обязательное поле для заполнения.'
                )
            else:
                attrs[field] = field_data

        # Check times
        if attrs.get('break_start') and attrs.get('break_end'):
            if attrs.get('break_start') >= attrs.get('break_end'):
                raise ParseError(
                    'Время начала перерыва должно быть меньше времени окончания.'
                )

        # Check duplicates
        if self.Meta.model.objects.filter(
            group_id=attrs['group'].pk, date=attrs['date']
        ).exists():
            raise ParseError(
                'На этот день уже существует активная смена.'
            )
        return attrs

    def validate_group(self, value):
        my_groups = Group.objects.my_groups_admin()
        if value not in my_groups:
            raise ParseError(
                'У вас нет полномочий создавать смены в этой группе.'
            )
        return value

    def validate_date(self, value):
        now = timezone.now().date()
        if value < now:
            raise ParseError(
                'Дата смены должна быть больше или равна текущей дате.'
            )
        return value

    def validate_break_start(self, value):
        if value.minute % 15 > 0:
            raise ParseError(
                'Время начала перерыва должно быть кратно 15 минутам.'
            )
        return value

    def validate_break_end(self, value):
        if value.minute % 15 > 0:
            raise ParseError(
                'Время окончания перерыва должно быть кратно 15 минутам.'
            )
        return value


class ReplacementUpdateSerializer(InfoModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        queryset=Member.objects.all(), many=True, allow_null=True,
        required=False,
    )
    all_group_members = serializers.BooleanField(default=False)
    remember_default_data = serializers.BooleanField(default=False)

    class Meta:
        model = Replacement
        fields = (
            'id',
            'date',
            'break_start',
            'break_end',
            'break_max_duration',
            'min_active',
            'members',
            'all_group_members',
            'remember_default_data',
        )

    def update(self, instance, validated_data):
        remember_data = validated_data.pop('remember_default_data', False)
        all_group_members = validated_data.pop('all_group_members', False)

        with transaction.atomic():
            if all_group_members:
                validated_data.pop('members', list())
                members = self.instance.group.members_info.all()
            else:
                members = validated_data.pop('members', None)
            instance = super().update(instance, validated_data)

            if members:
                instance.members.set(
                    members, through_defaults={'status_id': 'created'}
                )

            if remember_data:
                defaults = {
                    'break_start': (
                            validated_data.get('break_start')
                            or self.instance.break_start
                    ),
                    'break_end': (
                            validated_data.get('break_end')
                            or self.instance.break_end
                    ),
                    'break_max_duration': (
                            validated_data.get('break_max_duration')
                            or self.instance.break_max_duration
                    ),
                    'min_active': (
                            validated_data.get('min_active')
                            or self.instance.min_active
                    ),
                }
                group = instance.group
                for key, value in defaults.items():
                    setattr(group, key, value)
                group.save()

            return instance

    def validate(self, attrs):
        # Check times

        if attrs.get('break_start') or attrs.get('break_end'):
            break_start = attrs.get('break_start') or self.instance.break_start
            break_end = attrs.get('break_end') or self.instance.break_end
            if break_start >= break_end:
                raise ParseError(
                    'Время начала перерыва должно быть меньше времени окончания.'
                )

        # Check duplicates
        if attrs.get('date') and self.Meta.model.objects.filter(
                group_id=self.instance.group.pk, date=attrs['date']
        ).exclude(pk=self.instance.pk).exists():
            raise ParseError(
                'На этот день уже существует активная смена.'
            )
        return attrs

    def validate_date(self, value):
        now = timezone.now().date()
        if value < now:
            raise ParseError(
                'Дата смены должна быть больше или равна текущей дате.'
            )
        return value

    def validate_break_start(self, value):
        if value.minute % 15 > 0:
            raise ParseError(
                'Время начала перерыва должно быть кратно 15 минутам.'
            )
        return value

    def validate_break_end(self, value):
        if value.minute % 15 > 0:
            raise ParseError(
                'Время окончания перерыва должно быть кратно 15 минутам.'
            )
        return value


class ReplacementMemberListSerializer(InfoModelSerializer):
    status = DictMixinSerializer()

    class Meta:
        model = ReplacementMember
        fields = (
            'id',
            'status',
        )


class ReplacementMemberUpdateSerializer(InfoModelSerializer):

    class Meta:
        model = ReplacementMember
        fields = (
            'id',
            'status',
        )

    #TODO: доделать валидацию статусов
