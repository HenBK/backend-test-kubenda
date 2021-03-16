import pytest
import uuid

from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestPublicMenuView:

    def test_public_menu_retrieval(self, client, public_menu):
        """
        Tests that a unauthenticated can make an http GET request handled
        by the PublicMenuView class to retrieve a published menu by uuid
        """
        request_url = reverse('public-menu', args=(public_menu.uuid,))
        response = client.get(request_url)

        assert response.status_code == status.HTTP_200_OK

    def test_invalid_public_menu_retrival(self, client, menu):
        """
        Tests that an http404 is returned when requesting a menu that does not
        exist or when requesting a menu that exists but has not been published
        """
        random_uuid = uuid.uuid4()

        not_published_menu_request_url = reverse(
            'public-menu',
            args=(menu.uuid,),
        )
        unexisting_menu_request_url = reverse(
            'public-menu',
            args=(random_uuid,),
        )

        not_published_menu_response = client.get(
            not_published_menu_request_url,
        )
        unexisting_menu_response = client.get(
            unexisting_menu_request_url,
        )

        assert (
            not_published_menu_response.status_code
            == status.HTTP_404_NOT_FOUND
        )
        assert (
            unexisting_menu_response.status_code
            == status.HTTP_404_NOT_FOUND
        )
