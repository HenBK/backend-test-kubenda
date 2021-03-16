import pytest

from django.urls import reverse
from rest_framework import status

from meal_api.models import Order


@pytest.mark.django_db
class TestOrdersView:

    def test_orders_visibility(
        self,
        client,
        menu_with_related_orders,
        normal_user,
        order,
        super_user,
    ):
        """
        Tests that normal users can only see the orders made by themselves
        by verifying that all elements returned by order requests correspond
        to the pk of the user requesting the orders, and also by asserting that
        length of the returned orders corresponds the count of orders related
        to the user database model instance, finally checks that the super_user
        is able to see what everyone else ordered by querying all order objects
        """
        orders_request_url = reverse('meal_api:order-list', args=())

        client.force_login(user=normal_user)
        normal_user_orders_response = client.get(orders_request_url)

        client.force_login(user=super_user)
        super_user_orders_response = client.get(orders_request_url)

        # Will hold a boolean value for every order to check if each order
        # corresponds to the normal_user or not i.e [True, False, True, True]
        normal_user_orders = []

        for order_json in normal_user_orders_response.json():
            order = Order.objects.get(pk=order_json['id'])
            order_belongs_to_normal_user = order.employee.id == normal_user.pk
            normal_user_orders.append(order_belongs_to_normal_user)

        assert all(normal_user_orders)
        assert len(normal_user_orders_response.json()) == Order.objects.filter(
            employee__pk=normal_user.pk,
        ).count()
        assert (
            len(super_user_orders_response.json())
            == Order.objects.all().count()
        )

    def test_requests_by_unallowed_users(self, client, order):
        """
        Tests that all http requests managed by OrderOptionViewSet class are
        refused if they are requested by a unauthenticated user
        """
        request_url = reverse(
            'meal_api:order-detail',
            args=(order.pk,),
        )

        payload = {
            'employee': order.employee.pk,
            'selected_option': order.selected_option,
            'customizations': order.customizations,
            'menu': order.menu.uuid,
        }

        tested_http_methods = [
            client.post,
            client.get,
            client.put,
            client.patch,
            client.delete,
        ]

        authenticated_user_responses = [
            method(request_url, payload).status_code
            for method in tested_http_methods
        ]

        assert (
            authenticated_user_responses.count(status.HTTP_403_FORBIDDEN)
            == len(tested_http_methods)
        )

    def test_requests_by_allowed_user(self, client, normal_user, order):
        """
        Tests that the super_user is able to access all http request methods
        for the requests handled by MenuOptionViewSet class
        """
        request_url = reverse(
            'meal_api:order-detail',
            args=(order.pk,),
        )

        payload = {
            'employee': order.employee.pk,
            'selected_option': order.selected_option,
            'customizations': order.customizations,
            'menu': order.menu.uuid,
        }

        client.force_login(user=normal_user)

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
            reverse('meal_api:order-list', args=()),
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

    def test_unexisting_order_request(self, client, normal_user):
        """
        Test that an http404 is returned  when requesting for a order
        record that does not exist
        """
        unexisting_order_pk = 9999

        request_url = reverse(
            'meal_api:order-detail',
            args=(unexisting_order_pk,),
        )
        payload = {
            'employee': 'TEST',
            'selected_option': 'TEST',
            'customizations': 'TEST',
            'menu': 'TEST',
        }

        client.force_login(user=normal_user)

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

        assert (
            responses.count(status.HTTP_404_NOT_FOUND)
            == len(tested_http_methods)
        )