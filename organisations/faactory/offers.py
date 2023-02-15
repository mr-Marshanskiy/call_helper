from django.db.models import Case, When, Q, F

from organisations.models.offers import Offer


class OfferFactory:
    model = Offer

    def org_list(self):
        qs = self.model.objects.select_related(
            'user',
        ).prefetch_related(
            'organisation',
        ).annotate(
            offer_type=Case(
                When(~Q(created_by=F('user')), then='sent'), default='receive'
            ),
            can_accept=Case(
                When(
                    Q(offer_type='sent', user_accept__isnull=True, org_accept=False),
                    then=True,
                ),
                When(
                    Q(offer_type='receive', user_accept=True, org_accept__isnull=True),
                    then=True,
                ),
                default=False,
            ),
            can_reject=Case(
                When(
                    Q(offer_type='sent', user_accept__isnull=True, org_accept=True),
                    then=True,
                ),
                When(
                    Q(offer_type='receive', user_accept=True, org_accept__isnull=True),
                    then=True,
                ),
                default=False,
            ),
        )
        return qs

    def user_list(self):
        qs = Offer.objects.select_related(
            'user',
        ).prefetch_related(
            'organisation',
        ).filter(
            user=self.request.user,
        ).annotate(
            offer_type=Case(
                When(created_by=F('user'), then='sent'), default='receive'
            ),
            can_accept=Case(
                When(
                    Q(offer_type='sent', org_accept__isnull=True, user_accept=False),
                    then=True,
                ),
                When(
                    Q(offer_type='receive', org_accept=True, user_accept__isnull=True),
                    then=True,
                ),
                default=False,
            ),
            can_reject=Case(
                When(
                    Q(offer_type='sent', org_accept__isnull=True, user_accept=True),
                    then=True,
                ),
                When(
                    Q(offer_type='receive', org_accept=True, user_accept__isnull=True),
                    then=True,
                ),
                default=False,
            ),

        )
        return qs