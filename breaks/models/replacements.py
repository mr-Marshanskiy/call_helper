from datetime import datetime, timedelta
import pdb

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import TimeField, OuterRef, Count, Q, F, Subquery, \
    IntegerField, ExpressionWrapper, DateTimeField
from django.db.models.functions import Coalesce
from django_generate_series.models import generate_series

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
        return f'Break Info'


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

    class Meta:
        verbose_name = 'Смена - участник группы'
        verbose_name_plural = 'Смены - участники группы'

    def __str__(self):
        return f'Участник смены {self.member.employee.user} ({self.pk})'
