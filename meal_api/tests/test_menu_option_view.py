import pytest

from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestMenuOptionView:

    def test_requests_by_unallowed_users(
        self,
        client,
        menu,
        menu_option,
        normal_user,
    ):
        """
        Tests that all http requests managed by MenuOptionViewSet class are
        refused if they are requested by a unauthenticated user or by a
        user that is authenticated but does not have superuser status
        """
        request_url = reverse(
            'meal_api:menu-option-detail',
            args=(menu.uuid, menu_option.option_number),
        )
        payload = {
            'option_number': 1,
            'description': 'Corn pie, Salad and Dessert',
        }

        tested_http_methods = [
            client.post,
            client.get,
            client.put,
            client.patch,
            client.delete,
        ]

        unauthenticated_user_responses = [
            method(request_url, payload).status_code
            for method in tested_http_methods
        ]

        # forces user authentication
        client.force_login(user=normal_user)

        authenticated_user_responses = [
            method(request_url, payload).status_code
            for method in tested_http_methods
        ]

        assert (
            unauthenticated_user_responses.count(status.HTTP_403_FORBIDDEN)
            == len(tested_http_methods)
        )
        assert (
            authenticated_user_responses.count(status.HTTP_403_FORBIDDEN)
            == len(tested_http_methods)
        )

    def test_requests_by_allowed_user(
        self,
        client,
        menu,
        menu_option,
        super_user,
    ):
        """
        Tests that the super_user is able to access all http request methods
        for the requests handled by MenuOptionViewSet class
        """
        request_url = reverse(
            'meal_api:menu-option-detail',
            args=(menu.uuid, menu_option.option_number),
        )
        payload = {
            'option_number': 1,
            'description': 'Corn pie, Salad and Dessert',
        }

        client.force_login(user=super_user)

        tested_http_methods = [
            client.get,
            client.put,
            client.patch,
            client.delete,
        ]

        responses = [
            method(request_url, payload).status_code
            for method in tested_http_methods
        ]

        # Post request is made separately due to the difference in the endpoint
        post_response = client.post(
            reverse('meal_api:menu-option-list', args=(menu.uuid,)),
            payload,
        ).status_code

        responses += [post_response]

        expected_status_codes = [
            status.HTTP_200_OK,  # get
            status.HTTP_200_OK,  # put
            status.HTTP_200_OK,  # patch
            status.HTTP_204_NO_CONTENT,  # delete
            status.HTTP_201_CREATED,  # post
        ]

        assert responses == expected_status_codes

    def test_unexisting_menu_options_request(self, client, menu, super_user):
        """
        Test that an http404 is returned  when requesting for a menu_option
        record that does not exist
        """
        unexisting_menu_option = 9999

        request_url = reverse(
            'meal_api:menu-option-detail',
            args=(menu.uuid, unexisting_menu_option),
        )
        payload = {
            'option_number': 1,
            'description': 'Corn pie, Salad and Dessert',
        }

        tested_http_methods = [
            client.get,
            client.put,
            client.patch,
            client.delete,
        ]

        client.force_login(user=super_user)

        responses = [
            method(request_url, payload).status_code
            for method in tested_http_methods
        ]

        assert (
            responses.count(status.HTTP_404_NOT_FOUND)
            == len(tested_http_methods)
        )
