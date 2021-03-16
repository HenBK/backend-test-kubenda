from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework import (
    permissions,
    status,
    generics,
)

from meal_api.serializers import MenuOptionSerializer
from meal_api.models import (
    Menu,
    MenuOption,
)


class PublicMenuView(generics.RetrieveAPIView):
    serializer_class = MenuOptionSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = MenuOption.objects.all()

    def retrieve(self, request=None, menu_uuid=None):
        menu = get_object_or_404(
            Menu,
            uuid=menu_uuid,
            is_published=True,
        )

        data = {
            'Requested menu': str(menu),
            'Menu meal options': [
                self.serializer_class(meal_option).data
                for meal_option in menu.meal_options
            ],
        }

        return Response(data, status=status.HTTP_200_OK)
