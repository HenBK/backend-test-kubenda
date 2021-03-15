from rest_framework import serializers

from .models import (
    Menu,
    MenuOption,
    Order,
)


class MenuSerializer(serializers.ModelSerializer):

    class Meta:
        model = Menu
        fields = '__all__'
        extra_kwargs = {
            'uuid': {'read_only': True},
        }


class MenuOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = MenuOption
        fields = (
            'option_number',
            'description',
        )


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        exclude = ('employee',)
