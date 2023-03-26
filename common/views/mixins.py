from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import GenericViewSet

from common.constants import roles
from common.serializers.mixins import DictMixinSerializer


class ExtendedView:
    multi_permission_classes = None
    multi_serializer_class = None
    request = None

    def get_serializer_class(self):
        assert self.serializer_class or self.multi_serializer_class, (
            '"%s" should either include `serializer_class`, '
            '`multi_serializer_class`, attribute, or override the '
            '`get_serializer_class()` method.' % self.__class__.__name__
        )
        if not self.multi_serializer_class:
            return self.serializer_class

        # define user role codes
        user = self.request.user
        if user.is_anonymous:
            user_roles = (roles.PUBLIC_GROUP,)
        elif user.is_superuser:
            user_roles = (roles.ADMIN_GROUP,)
        else:
            user_roles = set(user.groups.all().values_list('code', flat=True))

        # define request action or method
        if hasattr(self, 'action') and self.action:
            action = self.action
        else:
            action = self.request.method

        # Trying to get role + action serializer
        for role in user_roles:
            serializer_key = f'{role}__{action}'
            if self.multi_serializer_class.get(serializer_key):
                return self.multi_serializer_class.get(serializer_key)

        # Trying to get role serializer
        for role in user_roles:
            serializer_key = role
            if self.multi_serializer_class.get(serializer_key):
                return self.multi_serializer_class.get(serializer_key)

        # Trying to get action serializer or default
        return self.multi_serializer_class.get(action) or self.serializer_class

    def get_permissions(self):
        # define request action or method
        if hasattr(self, 'action'):
            action = self.action
        else:
            action = self.request.method

        if self.multi_permission_classes:
            permissions = self.multi_permission_classes.get(action)
            if permissions:
                return [permission() for permission in permissions]

        return [permission() for permission in self.permission_classes]


class ExtendedGenericViewSet(ExtendedView, GenericViewSet):
    pass


class ListViewSet(ExtendedGenericViewSet, mixins.ListModelMixin):
    pass


class UpdateViewSet(ExtendedGenericViewSet, mixins.UpdateModelMixin):
    pass


class DictListMixin(ListViewSet):
    serializer_class = DictMixinSerializer
    pagination_class = None
    model = None

    def get_queryset(self):
        assert self.model, (
            '"%s" should either include attribute `model`' % self.__class__.__name__
        )
        return self.model.objects.filter(is_active=True)


class LCRUViewSet(ExtendedGenericViewSet,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin, ):
    pass


class LCRUDViewSet(LCRUViewSet,
                   mixins.DestroyModelMixin, ):
    pass


class LCUViewSet(ExtendedGenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 mixins.UpdateModelMixin, ):
    pass


class LCDViewSet(ExtendedGenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 mixins.DestroyModelMixin, ):
    pass


class ExtendedGenericAPIView(ExtendedView, GenericAPIView):
    pass


class ExtendedRetrieveUpdateAPIView(mixins.RetrieveModelMixin,
                                    mixins.UpdateModelMixin,
                                    ExtendedGenericAPIView,
                                    ):
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ExtendedCRUAPIView(mixins.RetrieveModelMixin,
                         mixins.CreateModelMixin,
                         mixins.UpdateModelMixin,
                         ExtendedGenericAPIView):
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
