from django.contrib.auth import get_user_model
from django.db import models

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
        return f'{self.group}'


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
