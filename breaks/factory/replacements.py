from django.db.models import Count, Q

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

        qs = self.model.objects.select_related().annotate(
            all_pax=Count('breaks', distinct=True),
        ).annotate(**annotates_stats)
        return qs
