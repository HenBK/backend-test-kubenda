import pytest

from django.contrib.auth import get_user_model
from mixer.backend.django import mixer
from rest_framework.test import APIClient

from meal_api.models import (
    Nationality,
    Menu,
    MenuOption,
    Order,
)


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def menu():
    return mixer.blend(Menu, is_published=False)


@pytest.fixture
def public_menu():
    return mixer.blend(Menu, is_published=True)


@pytest.fixture
def menu_with_related_orders():
    menu = mixer.blend(Menu)

    for _ in range(10):
        random_employee = mixer.blend(
            get_user_model(),
            nationality=mixer.blend(Nationality),
        )
        mixer.blend(
            Order,
            employee=random_employee,
            menu=menu,
        )

    return menu


@pytest.fixture
def menu_option(menu):
    return mixer.blend(MenuOption, menu=menu, option_number=1)


@pytest.fixture
def menu_with_no_meal_options():
    return mixer.blend(Menu)


@pytest.fixture
def order(normal_user):
    return mixer.blend(
        Order,
        menu=mixer.blend(Menu),
        employee=normal_user,
    )


@pytest.fixture
def normal_user():
    return mixer.blend(
        get_user_model(),
        is_superuser=False,
        is_staff=False,
        nationality=mixer.blend(Nationality),
    )


@pytest.fixture
def super_user():
    return mixer.blend(
        get_user_model(),
        is_superuser=True,
        is_staff=True,
        nationality=mixer.blend(Nationality),
    )
