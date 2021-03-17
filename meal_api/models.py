import uuid

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)
from django.db import models
from django.db.models.base import Model
from django.db.models.deletion import DO_NOTHING

from .managers import EmployeeManager


class Nationality(Model):
    iso2_code = models.CharField(max_length=2, unique=True)
    country_name = models.CharField(max_length=50)


class Employee(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that supports using email instead of a
    username and supports nationality and slack_web_hook fields
    """
    email = models.EmailField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    slack_web_hook = models.CharField(
        max_length=100,
        null=True,
        help_text="This field is used to send slack messages to the employee"
    )
    nationality = models.ForeignKey(
        Nationality,
        to_field='iso2_code',
        default='CL',
        on_delete=DO_NOTHING,
        null=True,
    )

    objects = EmployeeManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.name or self.email


class Menu(Model):
    date = models.DateField()
    uuid = models.UUIDField(unique=True, default=uuid.uuid4)
    is_published = models.BooleanField(default=False)

    @property
    def meal_options(self):
        return self.menuoption_set.all()

    @property
    def orders(self):
        return self.order_set.all()

    def __str__(self):
        return f"Menu of day: {self.date.isoformat()}"


class MenuOption(Model):
    description = models.CharField(max_length=100)
    menu = models.ForeignKey(Menu, on_delete=DO_NOTHING)
    option_number = models.IntegerField()

    def __str__(self):
        return self.description


class Order(Model):
    employee = models.ForeignKey(Employee, on_delete=DO_NOTHING)
    selected_option = models.IntegerField()
    customizations = models.CharField(max_length=200)
    menu = models.ForeignKey(Menu, to_field='uuid', on_delete=DO_NOTHING)
