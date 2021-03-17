import requests
import json
import logging

from backend_test.celery import app
from .exceptions import SlackMessageException

from meal_api.models import Menu


LOGGER = logging.getLogger(__name__)


def get_employees_slack_web_hooks(menu, iso2_code):
    LOGGER.info(
        "Getting slack web_hooks of employees "
        f"with [{iso2_code}] nationality..."
    )

    employees_slack_web_hooks = []

    for order in menu.orders:
        if order.employee.nationality.iso2_code == iso2_code:
            employees_slack_web_hooks.append(order.employee.slack_web_hook)

    return employees_slack_web_hooks


def generate_menu_message(menu):
    LOGGER.info("Generating menu...")

    menu_meal_options = ''
    meal_options_queryset = menu.meal_options.order_by('option_number')

    for idx, meal_option in enumerate(meal_options_queryset, start=1):
        menu_meal_options += (
            f"Option {idx}: {meal_option.description}\n"
        )

    menu_message = (
        "Hello!\n"
        "I share with you today's menu :)\n\n"
        f"{menu_meal_options}\n"
        "Have a nice day!"
    )

    return menu_message


def send_slack_message(menu_message, web_hook_url):
    headers = {
        'Content-type': 'application/json',
    }
    payload = {
        'text': menu_message,
    }

    response = requests.post(
        url=web_hook_url,
        headers=headers,
        data=json.dumps(payload),
    )

    if not response.ok:
        raise SlackMessageException(response)


@app.task
def send_menu_notification_by_slack(menu_id, iso2_code='CL'):
    """
    Sends a slack message to all employees that have ordered in a menu,
    employees are filtered by their nationality iso2_code,
    default iso2_code value is for Chilean nationality :)
    param menu: <Menu model object>
    param iso2_code: str
    """
    menu = Menu.objects.get(pk=menu_id)
    employees_slack_web_hooks = get_employees_slack_web_hooks(menu, iso2_code)
    menu_mesage = generate_menu_message(menu)

    LOGGER.info("Sending slack messages...")

    for web_hook_url in employees_slack_web_hooks:
        try:
            send_slack_message(
                menu_message=menu_mesage,
                web_hook_url=web_hook_url,
            )
        except SlackMessageException as e:
            LOGGER.error(
                "Failure when trying to send slack message",
                exc_info=True,
                extra={
                    'raised_exception': e,
                },
            )
            continue
