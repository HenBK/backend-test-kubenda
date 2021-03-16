import pytest

from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestMenuView:

    def test_menu_orders_retrieval(
        self,
        client,
        menu,
        menu_with_related_orders,
        super_user,
    ):
        """
        Tests the custom "orders" action implemented in the MenuViewSet class
        by verifying that an http404 response is returned when requesting all
        the orders of a menu that does not exists or when the menu does exists
        but does not have any orders associated with it, finally it verifies
        that an http200 response is returned when the menu exists and it does
        have orders assigned
        """
        client.force_login(user=super_user)

        menu_with_no_orders_request_url = reverse(
            'meal_api:menu-orders',
            args=(menu.uuid,),
        )
        unexisting_menu_request_url = reverse(
            'meal_api:menu-orders',
            args=('UNEXISTING-MENU-UUID',),
        )
        menu_with_orders_request_url = reverse(
            'meal_api:menu-orders',
            args=(menu_with_related_orders.uuid,),
        )

        menu_with_no_orders_response = client.get(
            menu_with_no_orders_request_url,
        )
        unexisting_menu_response = client.get(
            unexisting_menu_request_url,
        )
        menu_with_orders_response = client.get(
            menu_with_orders_request_url,
        )

        assert (
            menu_with_no_orders_response.status_code
            == status.HTTP_404_NOT_FOUND
        )
        assert (
            unexisting_menu_response.status_code
            == status.HTTP_404_NOT_FOUND
        )
        assert menu_with_orders_response.status_code == status.HTTP_200_OK

    def test_menu_publishing(
        self,
        client,
        menu,
        menu_option,
        menu_with_no_meal_options,
        super_user,
    ):
        """
        Tests that a menu has meal options assigned before publishing it,
        in case it does not have them an http304 should be returned, otherwise
        a http200 is expected
        """
        client.force_login(user=super_user)

        menu_with_meal_options_request_url = reverse(
            'meal_api:menu-publish',
            args=(menu.uuid,),
        )
        menu_with_no_meal_options_request_url = reverse(
            'meal_api:menu-publish',
            args=(menu_with_no_meal_options.uuid,),
        )

        menu_with_meal_options_response = client.post(
            menu_with_meal_options_request_url,
        )
        menu_with_no_meal_options_response = client.post(
            menu_with_no_meal_options_request_url,
        )

        assert (
            menu_with_meal_options_response.status_code == status.HTTP_200_OK
        )
        assert (
            menu_with_no_meal_options_response.status_code
            == status.HTTP_304_NOT_MODIFIED
        )

    def test_requests_by_unallowed_users(self, client, menu, normal_user):
        """
        Tests that all http requests managed by MenuViewSet class are
        refused if they are requested by an unauthenticated user or by
        a user that is authenticated but does not have superuser status
        """
        request_url = reverse('meal_api:menu-detail', args=(menu.uuid,))
        payload = {
            'date': '2021-01-01',
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

    def test_requests_by_allowed_user(self, client, menu, super_user):
        """
        Tests that the super_user is able to access all http request methods
        for the requests handled by MenuViewSet class
        """
        request_url = reverse('meal_api:menu-detail', args=(menu.uuid,))
        payload = {
            'date': '2021-01-01',
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
            reverse('meal_api:menu-list', args=()),
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
