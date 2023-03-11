from django.db.models import Q, Count

from breaks import constants
from breaks.models.replacements import Replacement


class ReplacementFactory:
    model = Replacement

    def list(self):
        all_statuses = constants.BREAK_ALL_STATUSES
        annotates_stats = dict()
        for status in all_statuses:
            annotates_stats[f'{status}_pax'] = Count(
                'breaks', distinct=True, filter=Q(breaks__status_id=status),
            )

        qs = self.model.objects.prefetch_related(
            'group',
            'group__group__manager',
            'group__group__manager__user',
            'group__group__organisation',
            'members',
            'members__employee',
            'members__employee__user',
        ).annotate(
            all_pax=Count('breaks', distinct=True),
        ).annotate(**annotates_stats)
        return qs