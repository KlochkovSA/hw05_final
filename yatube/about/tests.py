from http import HTTPStatus

from django.test import TestCase


class StaticURLTests(TestCase):
    def test_about_urls(self):
        urls = [
            '/about/author/',
            '/about/tech/'
        ]
        for url in urls:
            with self.subTest(url):
                response = self.client.get(url)
                self.assertEqual(HTTPStatus.OK, response.status_code)

    def test_nonexisting_url(self):
        response = self.client.get('/about/')
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
