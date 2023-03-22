from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import (Count, DateTimeField, ExpressionWrapper, F,
                              OuterRef, Q, Subquery)
from django.utils import timezone
from django_generate_series.models import generate_series

from breaks.constants import (REPLACEMENT_MEMBER_BREAK,
                              REPLACEMENT_MEMBER_OFFLINE,
                              REPLACEMENT_MEMBER_ONLINE)
from breaks.models.breaks import Break
from common.models.mixins import InfoMixin

User = get_user_model()


class GroupInfo(models.Model):
    group = models.OneToOneField(
        'organisations.Group', models.CASCADE, related_name='breaks_info',
        verbose_name='Группа', primary_key=True,
    )
    min_active = models.PositiveSmallIntegerField(
        'Мин. число активных сотрудников', null=True, blank=True,
    )
    break_start = models.TimeField('Начало обеда', null=True, blank=True, )
    break_end = models.TimeField('Конец обеда', null=True, blank=True, )
    break_max_duration = models.PositiveSmallIntegerField(
        'Макс. длительность обеда', null=True, blank=True,
    )

    class Meta:
        verbose_name = 'Параметр обеденных перерывов'
        verbose_name_plural = 'Параметры обеденных перерывов'

    def __str__(self):
        return 'Break Info'


class Replacement(InfoMixin):
    group = models.ForeignKey(
        'breaks.GroupInfo', models.CASCADE, 'replacements',
        verbose_name='Группа',
    )
    date = models.DateField('Дата смены')
    break_start = models.TimeField('Начало обеда')
    break_end = models.TimeField('Конец обеда')
    break_max_duration = models.PositiveSmallIntegerField(
        'Макс. продолжительность обеда',
    )
    min_active = models.PositiveSmallIntegerField(
        'Мин. число активных сотрудников', null=True, blank=True,
    )

    members = models.ManyToManyField(
        'organisations.Member', related_name='replacements',
        verbose_name='Участники смены', through='ReplacementMember'
    )

    class Meta:
        verbose_name = 'Смена'
        verbose_name_plural = 'Смены'
        ordering = ('-date',)

    def __str__(self):
        return f'Смена №{self.pk} для {self.group}'

    def free_breaks_available(self, break_start, break_end, exclude_break_id=None):
        breaks_sub_qs = Subquery(
            Break.objects
            .filter(replacement=OuterRef('pk'))
            .exclude(pk=exclude_break_id)
            .annotate(
                start_datetime=ExpressionWrapper(OuterRef('date') + F('break_start'), output_field=DateTimeField()),
                end_datetime=ExpressionWrapper(OuterRef('date') + F('break_end'), output_field=DateTimeField()),
            )
            .filter(
                start_datetime__lte=OuterRef('timeline'),
                end_datetime__gt=OuterRef('timeline'),
            )
            .values('pk')
        )

        replacement_sub_qs = (
            self.__class__.objects
            .filter(pk=self.pk)
            .annotate(timeline=OuterRef('term'))
            .order_by()
            .values('timeline')
            .annotate(
                pk=F('pk'),
                breaks=Count('breaks', filter=Q(breaks__id__in=breaks_sub_qs), distinct=True),
                members_count=Count('members', distinct=True),
                free_breaks=F('members_count') - F('breaks')
            )

        )
        start_datetime = datetime.combine(self.date, break_start)
        end_datetime = datetime.combine(self.date, break_end) - timedelta(minutes=15)
        data_seq_qs = generate_series(
            start_datetime, end_datetime, '15 minutes', output_field=DateTimeField
        ).annotate(
            breaks=Subquery(replacement_sub_qs.values('free_breaks')),
        ).order_by(
            'breaks'
        )
        return data_seq_qs.first().breaks

    def get_member_by_user(self, user):
        return self.members_info.filter(
            member__employee__user=user
        ).first()

    def get_break_for_user(self, user):
        return self.breaks.filter(member__member__employee__user=user).first()

    def get_break_status_for_user(self, user):
        member = self.get_member_by_user(user)
        break_obj = self.get_break_for_user(user)
        now = timezone.now().astimezone()
        if not member or self.date != now.date():
            return None
        if not break_obj:
            return 'create'
        return 'update'


class ReplacementMember(models.Model):
    member = models.ForeignKey(
        'organisations.Member', models.CASCADE, 'replacements_info',
        verbose_name='Сотрудник'
    )
    replacement = models.ForeignKey(
        'breaks.Replacement', models.CASCADE, 'members_info',
        verbose_name='Смена'
    )
    status = models.ForeignKey(
        'breaks.ReplacementStatus', models.RESTRICT, 'members',
        verbose_name='Статус'
    )

    time_online = models.DateTimeField(
        'Начал смену', null=True, blank=True, editable=False
    )
    time_offline = models.DateTimeField(
        'Закончил смену', null=True, blank=True, editable=False
    )
    time_break_start = models.DateTimeField(
        'Ушел на обед', null=True, blank=True, editable=False
    )
    time_break_end = models.DateTimeField(
        'Вернулся с обеда', null=True, blank=True, editable=False
    )

    class Meta:
        verbose_name = 'Смена - участник группы'
        verbose_name_plural = 'Смены - участники группы'

    def __str__(self):
        return f'Участник смены {self.member.employee.user.full_name} ({self.pk})'

    def save(self, *args, **kwargs):
        if self.pk:
            now = timezone.now()

            if self.status_id == REPLACEMENT_MEMBER_ONLINE:
                if not self.time_online:
                    self.time_online = now
                if self.time_break_start and not self.time_break_end:
                    self.time_break_end = now

            if self.status_id == REPLACEMENT_MEMBER_BREAK and not self.time_break_start:
                self.time_break_start = now

            if self.status_id == REPLACEMENT_MEMBER_OFFLINE:
                if not self.time_offline:
                    self.time_offline = now
                if self.time_break_start and not self.time_break_end:
                    self.time_break_end = now
        super().save(*args, **kwargs)
