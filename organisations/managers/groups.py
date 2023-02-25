from crum import get_current_user
from django.db import models
from django.db.models import Q


class GroupManager(models.Manager):
    def my_groups(self):
        user = get_current_user()
        return self.filter(
            Q(organisation__director=user)
            | Q(organisation__employees=user)
        )

    def my_groups_admin(self):
        user = get_current_user()
        return self.filter(
            Q(organisation__director=user)
            | Q(manager__user=user)
        )
