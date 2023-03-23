from django.db.models import Subquery, OuterRef, Prefetch

from breaks.models.breaks import Break
from breaks.models.replacements import Replacement, ReplacementMember


class ReplacementFactory:
    model = Replacement

    def list(self):
        break_subquery = Break.objects.filter(
                member=OuterRef('id'),
                replacement=OuterRef('replacement'),
            )

        members_qs = ReplacementMember.objects.annotate(
            break_start=Subquery(break_subquery.values('break_start')[:1]),
            break_end=Subquery(break_subquery.values('break_end')[:1]),
        ).select_related(
            'member__employee',
            'member__employee__user',
            'status',
        )
        qs = self.model.objects.prefetch_related(
            'group',
            'group__group__manager',
            'group__group__manager__user',
            'group__group__organisation',
            Prefetch(
                lookup='members_info',
                queryset=members_qs,
            )
        )
        return qs
