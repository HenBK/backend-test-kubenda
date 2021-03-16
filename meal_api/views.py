from django.shortcuts import get_object_or_404

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import (
    permissions,
    status,
)

from .models import (
    Employee, Menu,
    MenuOption,
    Order,
)
from .serializers import (
    MenuSerializer,
    MenuOptionSerializer,
    OrderSerializer,
)


class MenuViewSet(ModelViewSet):
    serializer_class = MenuSerializer
    queryset = Menu.objects.all()
    permission_classes = (permissions.IsAdminUser,)
    lookup_field = 'uuid'

    @action(detail=True)
    def orders(self, request, uuid=None):
        menu = self.get_object()
        orders = [
            OrderSerializer(order).data
            for order in menu.orders
        ]

        if len(orders):
            return Response(orders, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": f"No orders found for {menu}"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=['POST'])
    def publish(self, request, uuid=None):
        menu = self.get_object()

        if len(menu.meal_options):
            menu.is_published = True
            menu.save()
            return Response(
                {"detail": f"{menu} published successfully!"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "detail": (
                        f"Oops, you are trying to publish {menu} but it has "
                        "no meal options assigned yet"
                    ),
                },
                status=status.HTTP_304_NOT_MODIFIED,
            )


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


class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated | permissions.IsAdminUser]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Order.objects.all()
        else:
            return Order.objects.filter(employee__id=self.request.user.id)

    def create(self, request, pk=None):
        employee = Employee.objects.get(pk=request.user.id)
        selected_menu_option = request.data.get('selected_option')
        order_customizations = request.data.get('customizations')
        menu = get_object_or_404(Menu, uuid=request.data.get('menu'))

        order_already_exists = Order.objects.filter(
            employee=employee,
            menu=menu,
        ).exists()

        if order_already_exists:
            return Response(
                {
                    "detail": (
                        f"{menu} already has an order registered for employee "
                        f"{employee}, you might want to edit the existing order."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            order = Order.objects.create(
                employee=employee,
                menu=menu,
                selected_option=selected_menu_option,
                customizations=order_customizations,
            )
            order.save()

            return Response(
                self.serializer_class(order).data,
                status=status.HTTP_201_CREATED,
            )
