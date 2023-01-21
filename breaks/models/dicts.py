from django.contrib.auth import get_user_model

from common.models.mixins import BaseDictModelMixin

User = get_user_model()


class ReplacementStatus(BaseDictModelMixin):

    class Meta:
        verbose_name = 'Статус смены'
        verbose_name_plural = 'Статусы смены'


class BreakStatus(BaseDictModelMixin):
    class Meta:
        verbose_name = 'Статус обеда'
        verbose_name_plural = 'Статусы обеда'
