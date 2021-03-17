import os
import pytest

from django.contrib.auth import get_user_model
from django.test import TestCase, TransactionTestCase
from mixer.backend.django import mixer

from meal_api.models import (
    Menu, MenuOption,
    Nationality,
    Order,
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend_test.settings")

TestCase.databases = ["default"]
TransactionTestCase.databases = ["default"]


@pytest.fixture
def menu_with_various_employees_nationalities_orders():
    menu = mixer.blend(Menu)
    nationality = mixer.blend(Nationality, iso2_code='CL')
    random_nationality = mixer.blend(Nationality)

    for _ in range(10):
        mixer.blend(
            Order,
            employee=mixer.blend(get_user_model(), nationality=nationality),
            menu=menu,
        )
        mixer.blend(
            Order,
            employee=mixer.blend(
                get_user_model(),
                nationality=random_nationality
            ),
            menu=menu,
        )

    return menu


@pytest.fixture
def menu_with_meal_options():
    menu = mixer.blend(Menu)

    for idx in range(1, 4):
        mixer.blend(
            MenuOption,
            menu=menu,
            option_number=idx,
        )
    return menu
