import pytest
import requests

from mockito import (
    when,
    mock,
    unstub,
)

from backend_test.tasks import (
    generate_menu_message,
    get_employees_slack_web_hooks,
    send_slack_message,
)
from backend_test.exceptions import SlackMessageException
from meal_api.models import Employee


@pytest.mark.django_db
class TestSlackMenuNotificationTest:

    def test_send_slack_message_unsuccessful(self):
        """
        Tests that an SlackMessageException is raised when the POST request
        made in send_slack_message function returns an http response with a
        status_code different from 200
        """
        TEST_VALUE = 'TEST_VALUE'

        unsuccessful_response_mock = mock({
            'ok': False,
            'status_code': 404,
            'request': mock({
                'url': TEST_VALUE,
                'headers': TEST_VALUE,
                'payload': TEST_VALUE,
            }),
        })

        when(requests).post(...).thenReturn(unsuccessful_response_mock)

        with pytest.raises(SlackMessageException):
            send_slack_message(TEST_VALUE, TEST_VALUE)

        unstub()

    def test_get_employees_slack_web_hooks(
        self,
        menu_with_various_employees_nationalities_orders,
    ):
        """
        Tests that the slack_web_hooks retrieved by the
        get_employees_slack_web_hooks function just get the slack web hooks of
        the employees with the nationality specified on the method's iso2_code
        parameter
        """
        expected_nationality = 'CL'

        employees_slack_web_hooks = get_employees_slack_web_hooks(
            menu=menu_with_various_employees_nationalities_orders,
            iso2_code=expected_nationality,
        )

        # Will hold a boolean value for each returned employee nationality
        # assiging False to any employee that does not match the expected
        # nationality i.e [True, False, True, True...]
        employee_matched_nationalities = []

        for slack_web_hook in employees_slack_web_hooks:
            employee = Employee.objects.get(slack_web_hook=slack_web_hook)
            employee_matches_expected_nationality = (
                employee.nationality.iso2_code
                == expected_nationality
            )
            employee_matched_nationalities.append(
                employee_matches_expected_nationality,
            )

        assert all(employee_matched_nationalities)

    def test_generate_menu_message(self, menu_with_meal_options):
        """
        Tests that the menu notifications message is build correctly
        when calling the fuction generate_menu_message
        """
        meal_option_1 = menu_with_meal_options.meal_options[0]
        meal_option_2 = menu_with_meal_options.meal_options[1]
        meal_option_3 = menu_with_meal_options.meal_options[2]

        expected_notification_message = (
            "Hello!\n"
            "I share with you today's menu :)\n\n"
            f"Option 1: {meal_option_1.description}\n"
            f"Option 2: {meal_option_2.description}\n"
            f"Option 3: {meal_option_3.description}\n"
            "\nHave a nice day!"
        )

        assert (
            expected_notification_message
            == generate_menu_message(menu=menu_with_meal_options)
        )
