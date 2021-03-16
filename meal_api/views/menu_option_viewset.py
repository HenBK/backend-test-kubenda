from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import (
    permissions,
    status,
)

from meal_api.models import (
    Menu,
    MenuOption,
)
from meal_api.serializers import MenuOptionSerializer


class MenuOptionViewSet(ModelViewSet):
    serializer_class = MenuOptionSerializer
    queryset = MenuOption.objects.all()
    permission_classes = (permissions.IsAdminUser,)
    lookup_field = 'option_number'

    def list(self, request, menu_uuid):
        menu = get_object_or_404(Menu, uuid=menu_uuid)
        menu_meal_options = [
            self.serializer_class(menu_option).data
            for menu_option in menu.meal_options
        ]

        if len(menu_meal_options):
            return Response(menu_meal_options, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": f"No meal options assigned to {menu} yet"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request, menu_uuid):
        menu = get_object_or_404(Menu, uuid=menu_uuid)
        menu_option_description = request.data.get('description')
        menu_option_number = request.data.get('option_number')

        menu_option = MenuOption.objects.create(
            description=menu_option_description,
            option_number=menu_option_number,
            menu=menu,
        )
        menu_option.save()

        return Response(
            self.serializer_class(menu_option).data,
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, option_number, menu_uuid):
        menu_option = get_object_or_404(
            MenuOption,
            menu__uuid=menu_uuid,
            option_number=option_number,
        )

        return Response(
            self.serializer_class(menu_option).data,
            status=status.HTTP_200_OK,
        )

    def update(self, request, option_number, menu_uuid, partial=None):
        menu_option = get_object_or_404(
            MenuOption,
            menu__uuid=menu_uuid,
            option_number=option_number,
        )
        menu_option.option_number = request.data.get('option_number')
        menu_option.description = request.data.get('description')
        menu_option.save()

        return Response(
            self.serializer_class(menu_option).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, option_number, menu_uuid):
        menu_option = get_object_or_404(
            MenuOption,
            menu__uuid=menu_uuid,
            option_number=option_number,
        )
        menu_option.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
