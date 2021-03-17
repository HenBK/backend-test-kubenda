from datetime import time

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import (
    permissions,
    status,
)

from backend_test.utils import datetime_utils
from meal_api.models import (
    Employee,
    Menu,
    Order,
)
from meal_api.serializers import OrderSerializer


class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated | permissions.IsAdminUser]

    MAX_ALLOWED_ORDER_HOUR = time(hour=11)  # 11 AM

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
        elif datetime_utils.get_time_now() > self.MAX_ALLOWED_ORDER_HOUR:
            return Response(
                {
                    "detail": (
                        "Trying to make an order past to the allowed time,"
                        "you should consider ordering before "
                        f"{self.MAX_ALLOWED_ORDER_HOUR}"
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
