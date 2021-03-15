from django.contrib.auth.models import BaseUserManager


class EmployeeManager(BaseUserManager):

    def create_employee(self, email, password=None, **extra_fields):
        """Creates and saves a new employee and returns the instance"""

        if email is None:
            raise ValueError("The email address field is mandatory")

        employee = self.model(email=self.normalize_email(email), **extra_fields)
        employee.set_password(password)
        employee.save()

        return employee

    def create_superuser(self, email, password=None):
        superuser = self.create_employee(email, password=password)
        superuser.is_superuser = True
        superuser.is_staff = True
        superuser.save()

        return superuser
