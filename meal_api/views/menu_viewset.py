from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import (
    permissions,
    status,
)

from meal_api.serializers import (
    OrderSerializer,
    MenuSerializer,
)
from meal_api.models import Menu


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
