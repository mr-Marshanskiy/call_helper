from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Group(models.Model):
    organisation = models.ForeignKey(
        'breaks.Organisation', models.RESTRICT, 'groups',
        verbose_name='Организация',
    )
    name = models.CharField('Название', max_length=255,)
    manager = models.ForeignKey(
        User, models.RESTRICT, 'group_managers',
        verbose_name='Менеджер',
    )
    employees = models.ManyToManyField(
        User, 'group_employees', verbose_name='Сотрудники',
        blank=True,
    )
    min_active = models.PositiveSmallIntegerField(
        'Минимальное количество активных сотрудников', null=True, blank=True,
    )
    break_start = models.TimeField('Начало обеда', null=True, blank=True,)
    break_end = models.TimeField('Конец обеда', null=True, blank=True,)
    break_max_duration = models.PositiveSmallIntegerField(
        'Максимальная длительность обеда', null=True, blank=True,
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.pk})'
